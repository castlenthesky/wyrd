from pathlib import Path
from typing import Optional

from server.uast.models import GraphPayload, UASTEdge, UASTNode
from tree_sitter import Node


class UASTBuilder:
    def __init__(self):
        self._graph = GraphPayload()

    def _handle_file_structure(self, file_path: str) -> str:
        path_obj = Path(file_path).resolve()

        # Create File Node
        file_id = f"file:{path_obj}"
        self._graph.add_node(
            UASTNode(
                id=file_id,
                type="File",
                properties={"name": path_obj.name, "path": str(path_obj)},
            )
        )

        # Walk up the directory tree
        # We can stop at some arbitrary point or root.
        # For now, let's go up to the system root or until we hit a specific marker (like .git, but we don't scan for it here)
        # To avoid creating nodes for /usr, /, etc in a simple script, let's limit depth or rely on the user providing a relevant root.
        # Without a workspace root, we'll just go up 2-3 levels or until we hit root.
        # User example: /home/bmoney/projects/demos/temp -> we probably want temp, demos, projects?
        # Let's enforce a simple logic: recurse until we hit the root of the path provided if relative, or just go up.
        # Better: create directories for all parents up to 3 levels for this POC, or just the immediate parent chain until we hit a "project root" heuristic?
        # The user request implies "One Directory can CONTAIN another Directory".

        current_path = path_obj.parent
        child_id = file_id

        # Guard against infinite loops or going too high.
        # Let's just go up to the root, but maybe in real usage we'd stop at workspace root.
        # Since I don't have workspace root here yet, I'll just go up until I hit the root or a reasonable limit (e.g. 10 levels).
        # But wait, main.py passes absolute paths.

        steps = 0
        while steps < 10:
            dir_id = f"dir:{current_path}"

            # Create Directory Node
            self._graph.add_node(
                UASTNode(
                    id=dir_id,
                    type="Directory",
                    properties={"name": current_path.name, "path": str(current_path)},
                )
            )

            # Link Directory -> Child (File or Directory)
            self._graph.add_edge(
                UASTEdge(source_id=dir_id, target_id=child_id, type="CONTAINS")
            )

            child_id = dir_id
            if current_path == current_path.parent:  # Hit root
                break

            current_path = current_path.parent
            steps += 1

            # Heuristic to stop: if we are in /tmp, stop at /tmp?
            # If we are in /home/user/project, stop at /home/user?
            # For now, let's just go all the way to root or a safe depth.
            # Actually, creating nodes for / and /home is probably fine for a graph, but maybe noisy.
            # User specifically mentioned /home/bmoney/projects/demos/temp
            # If I stop at /home/bmoney that might be good.

        return file_id

    def build(self, cst_root: Node, source_code: bytes, file_path: str) -> GraphPayload:
        """
        Main entry point.
        1. Creates Directory and File nodes.
        2. Traverses CST recursively.
        3. Returns a distinct list of Nodes and Edges.
        """
        file_id = self._handle_file_structure(file_path)
        self._traverse(cst_root, source_code, parent_id=file_id)
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
            # If parent is File, use DEFINES. If parent is Class/Function, use CONTAINS?
            # User expectation: "File/Module node, a DEFINES relationship pointing toward two function nodes"
            edge_type = (
                "DEFINES"
                if "file:" in parent_id or "module:" in parent_id
                else "CONTAINS"
            )
            self._graph.add_edge(
                UASTEdge(source_id=parent_id, target_id=node_id, type=edge_type)
            )

        # Handle parameters as Variables
        params_node = node.child_by_field_name("parameters")
        if params_node:
            for child in params_node.children:
                if child.type == "identifier":
                    arg_name = source_code[child.start_byte : child.end_byte].decode()
                    # Create Variable node
                    var_id = f"var:{child.start_point}:{arg_name}"
                    self._graph.add_node(
                        UASTNode(
                            id=var_id, type="Variable", properties={"name": arg_name}
                        )
                    )
                    # Link Function -> Variable (DEFINES)
                    self._graph.add_edge(
                        UASTEdge(source_id=node_id, target_id=var_id, type="DEFINES")
                    )

        return node_id

    def handle_assignment(
        self, node: Node, source_code: bytes, parent_id: Optional[str]
    ) -> str:
        # greeting = "Hello"
        # left: identifier (variable)
        # right: string (literal)
        left_node = node.child_by_field_name("left")
        right_node = node.child_by_field_name("right")

        if left_node and left_node.type == "identifier":
            var_name = source_code[left_node.start_byte : left_node.end_byte].decode()
            var_id = f"var:{left_node.start_point}:{var_name}"

            # Create Variable Node
            self._graph.add_node(
                UASTNode(id=var_id, type="Variable", properties={"name": var_name})
            )

            # Link Parent (Function/Module) -> Variable (DEFINES)
            if parent_id:
                self._graph.add_edge(
                    UASTEdge(source_id=parent_id, target_id=var_id, type="DEFINES")
                )

            # Handle RHS Literal
            if right_node and right_node.type == "string":
                # Extract string content (including quotes for now, or strip them)
                literal_value = source_code[
                    right_node.start_byte : right_node.end_byte
                ].decode()
                # Create unique ID for literal
                lit_id = f"lit:{right_node.start_point}:{literal_value}"

                # Create Literal Node
                self._graph.add_node(
                    UASTNode(
                        id=lit_id,
                        type="Literal",
                        properties={"value": literal_value, "kind": "String"},
                    )
                )

                # Link Variable -> Literal
                self._graph.add_edge(
                    UASTEdge(source_id=var_id, target_id=lit_id, type="ASSIGNED_FROM")
                )

        return f"assignment:{node.start_point[0]}"

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

        # Handle arguments
        args_node = node.child_by_field_name("arguments")
        if args_node:
            for child in args_node.children:
                if child.type == "identifier":
                    arg_name = source_code[child.start_byte : child.end_byte].decode()
                    arg_id = f"arg:{child.start_point}:{arg_name}"
                    # Create Identifier Node for the argument usage
                    self._graph.add_node(
                        UASTNode(
                            id=arg_id, type="Identifier", properties={"name": arg_name}
                        )
                    )
                    # Link Call -> Identifier
                    self._graph.add_edge(
                        UASTEdge(
                            source_id=node_id, target_id=arg_id, type="HAS_ARGUMENT"
                        )
                    )
                elif child.type == "string":
                    # Handle literal arguments if any
                    val = source_code[child.start_byte : child.end_byte].decode()
                    arg_id = f"arg_lit:{child.start_point}:{val}"
                    self._graph.add_node(
                        UASTNode(
                            id=arg_id,
                            type="Literal",
                            properties={"value": val, "kind": "String"},
                        )
                    )
                    self._graph.add_edge(
                        UASTEdge(
                            source_id=node_id, target_id=arg_id, type="HAS_ARGUMENT"
                        )
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
