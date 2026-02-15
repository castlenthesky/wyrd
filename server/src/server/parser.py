from tree_sitter import Language, Parser
import tree_sitter_python


class TreeSitterParser:
    def __init__(self):
        self.language = Language(tree_sitter_python.language())
        self.parser = Parser(self.language)

    def parse(self, content: str):
        return self.parser.parse(bytes(content, "utf8"))

    def extract_graph(self, tree, file_path):
        nodes = []
        edges = []

        cursor = tree.walk()

        visited_children = False
        while True:
            if not visited_children:
                # Process node
                node = cursor.node
                # Create a unique ID for the node
                # FalkorDB / RedisGraph nodes usually need properties.
                # We'll use a hash or just the location string for POC.
                node_id = f"{file_path}:{node.start_point}:{node.end_point}:{node.type}"
                nodes.append(
                    {
                        "id": node_id,
                        "label": "Node",  # Generic label for now, or use node.type
                        "properties": {
                            "type": node.type,
                            "start_line": node.start_point[0],
                            "start_col": node.start_point[1],
                            "end_line": node.end_point[0],
                            "end_col": node.end_point[1],
                            "file": file_path,
                            # "text": node.text.decode('utf8') # text might be too large for properties sometimes
                        },
                    }
                )

                # Create edge from parent
                if node.parent:
                    parent_id = f"{file_path}:{node.parent.start_point}:{node.parent.end_point}:{node.parent.type}"
                    edges.append((parent_id, "PARENT", node_id))

            if not visited_children and cursor.goto_first_child():
                visited_children = False
            elif cursor.goto_next_sibling():
                visited_children = False
            elif cursor.goto_parent():
                visited_children = True
            else:
                break

        return nodes, edges
