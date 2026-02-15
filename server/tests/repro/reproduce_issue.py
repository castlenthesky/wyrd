import os
import sys

# Add server/src to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)

from server.parser import TreeSitterParser
from server.uast.builder import UASTBuilder


def test_repro():
    code = """def concat_greeting(greeting, name):
    return greeting + " " + name


def main():
    greeting = "Hello"
    name = "World"
    print(concat_greeting(greeting, name))


if __name__ == "__main__":
    main()
"""
    parser = TreeSitterParser()
    tree = parser.parse(code)

    builder = UASTBuilder()
    # Pass a deep nested path
    # /tmp/project/src/module/repro.py
    # Should create:
    # Directory(/tmp/project) -> Directory(/tmp/project/src) -> Directory(/tmp/project/src/module) -> File(.../repro.py)
    file_path = "/tmp/project/src/module/repro.py"
    graph = builder.build(tree.root_node, bytes(code, "utf8"), file_path)

    print(f"Nodes: {len(graph.nodes)}")
    for node in graph.nodes:
        # Print relevant properties
        props = node.properties.copy()
        if "id" in props:
            del props["id"]  # redundant
        print(f"  {node.type} ({node.id}): {props}")

    print(f"Edges: {len(graph.edges)}")
    for edge in graph.edges:
        print(f"  {edge.source_id} -[{edge.type}]-> {edge.target_id}")

    # Basic assertions to ensure we have what we expect
    types = [n.type for n in graph.nodes]
    print(f"Found types: {set(types)}")
    assert "Directory" in types
    assert "File" in types
    assert "Variable" in types
    assert "Literal" in types

    # Assert Identifier type exists (from arguments)
    assert "Identifier" in types

    # Assert edges exist
    edge_types = [e.type for e in graph.edges]
    assert "DEFINES" in edge_types
    assert "CONTAINS" in edge_types
    assert "ASSIGNED_FROM" in edge_types
    assert "HAS_ARGUMENT" in edge_types


if __name__ == "__main__":
    test_repro()
