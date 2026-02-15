from typing import Optional

from server.uast.models import GraphPayload, UASTEdge, UASTNode
from tree_sitter import Node


class UASTBuilder:
    def __init__(self):
        self._graph = GraphPayload()

    def build(self, cst_root: Node, source_code: bytes) -> GraphPayload:
        """
        Main entry point.
        1. Traverses CST recursively.
        2. Applies specific handlers for node types.
        3. Returns a distinct list of Nodes and Edges.
        """
        self._traverse(cst_root, source_code)
        return self._graph

    def _traverse(
        self, node: Node, source_code: bytes, parent_id: Optional[str] = None
    ):
        node_id = self._handle_node(node, source_code, parent_id)

        # If the handler returns a node_id, use it as parent for children
        # Otherwise keep the current parent_id
        current_parent_id = node_id if node_id else parent_id

        for child in node.children:
            if child.is_named:
                self._traverse(child, source_code, current_parent_id)

    def _handle_node(
        self, node: Node, source_code: bytes, parent_id: Optional[str] = None
    ) -> Optional[str]:
        # Dispatch to specific handlers
        handler_name = f"handle_{node.type}"
        handler = getattr(self, handler_name, None)

        if handler:
            return handler(node, source_code, parent_id)

        return None

    def handle_function_definition(
        self, node: Node, source_code: bytes, parent_id: Optional[str]
    ) -> str:
        name_node = node.child_by_field_name("name")

        func_name = (
            source_code[name_node.start_byte : name_node.end_byte].decode()
            if name_node
            else "anonymous"
        )

        # Unique ID generation (simplified for now)
        node_id = f"func:{node.start_point[0]}:{func_name}"

        is_async = node.type == "async_function_definition" or (
            node.parent and node.parent.type == "async_function_definition"
        )

        properties = {
            "name": func_name,
            "is_async": is_async,
        }

        uast_node = UASTNode(id=node_id, type="Function", properties=properties)
        self._graph.add_node(uast_node)

        if parent_id:
            # Connect to parent (e.g. Class or Module)
            self._graph.add_edge(
                UASTEdge(source_id=parent_id, target_id=node_id, type="CONTAINS")
            )

        return node_id

    def handle_call(
        self, node: Node, source_code: bytes, parent_id: Optional[str]
    ) -> str:
        func_node = node.child_by_field_name("function")

        callee_name = "unknown"
        if func_node:
            callee_name = source_code[
                func_node.start_byte : func_node.end_byte
            ].decode()

        node_id = f"call:{node.start_point[0]}:{callee_name}"

        properties = {"callee_name": callee_name}

        uast_node = UASTNode(id=node_id, type="Call", properties=properties)
        self._graph.add_node(uast_node)

        if parent_id:
            self._graph.add_edge(
                UASTEdge(source_id=parent_id, target_id=node_id, type="CONTAINS")
            )

        # Create a generic REFERS_TO edge to a symbol placeholder for now
        symbol_id = f"symbol:{callee_name}"
        self._graph.add_edge(
            UASTEdge(source_id=node_id, target_id=symbol_id, type="REFERS_TO")
        )

        return node_id

    def handle_import_statement(
        self, node: Node, source_code: bytes, parent_id: Optional[str]
    ) -> str:
        # import os
        # import os as my_os
        # tree-sitter-python structure for import_statement can vary
        for child in node.children:
            if child.type == "dotted_name":
                module_name = source_code[child.start_byte : child.end_byte].decode()
                self._create_import_node(
                    module_name, alias=None, node=node, parent_id=parent_id
                )
            elif child.type == "aliased_import":
                name_node = child.child_by_field_name("name")
                alias_node = child.child_by_field_name("alias")
                module_name = source_code[
                    name_node.start_byte : name_node.end_byte
                ].decode()
                alias = source_code[
                    alias_node.start_byte : alias_node.end_byte
                ].decode()
                self._create_import_node(
                    module_name, alias=alias, node=node, parent_id=parent_id
                )
        # Return a generic ID for the statement itself if needed, but imports are usually leaves or separate entities
        # We return it so it can be a "parent" if ever needed, though likely not.
        return f"import_stmt:{node.start_point[0]}"

    def handle_import_from_statement(
        self, node: Node, source_code: bytes, parent_id: Optional[str]
    ) -> str:
        # from os import path
        module_node = node.child_by_field_name("module_name")
        module_name = (
            source_code[module_node.start_byte : module_node.end_byte].decode()
            if module_node
            else "."
        )

        # Iterate over names being imported (aliased_import)
        for child in node.children:
            if child.type == "aliased_import":
                # from ... import foo as bar
                name_node = child.child_by_field_name("name")
                alias_node = child.child_by_field_name("alias")
                imported_name = source_code[
                    name_node.start_byte : name_node.end_byte
                ].decode()
                alias = source_code[
                    alias_node.start_byte : alias_node.end_byte
                ].decode()

                full_module = (
                    f"{module_name}.{imported_name}"
                    if module_name != "."
                    else imported_name
                )
                self._create_import_node(
                    full_module, alias=alias, node=node, parent_id=parent_id
                )

            elif child.type == "dotted_name" and child != module_node:
                # from ... import foo
                imported_name = source_code[child.start_byte : child.end_byte].decode()
                full_module = (
                    f"{module_name}.{imported_name}"
                    if module_name != "."
                    else imported_name
                )
                self._create_import_node(
                    full_module, alias=None, node=node, parent_id=parent_id
                )

        return f"import_from_stmt:{node.start_point[0]}"

    def _create_import_node(
        self, module: str, alias: Optional[str], node: Node, parent_id: Optional[str]
    ):
        # Use a unique ID that includes module name to avoid collision
        node_id = f"import:{node.start_point[0]}:{module}"
        properties = {"module": module, "alias": alias}
        uast_node = UASTNode(id=node_id, type="Import", properties=properties)
        self._graph.add_node(uast_node)

        if parent_id:
            self._graph.add_edge(
                UASTEdge(source_id=parent_id, target_id=node_id, type="IMPORTS")
            )
