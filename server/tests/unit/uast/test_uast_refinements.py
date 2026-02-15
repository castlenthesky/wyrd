from server.parser import TreeSitterParser
from server.uast.builder import UASTBuilder


def test_uast_refinements():
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
    file_path = "/tmp/project/src/module/repro.py"
    graph = builder.build(tree.root_node, bytes(code, "utf8"), file_path)

    types = [n.type for n in graph.nodes]
    edge_types = [e.type for e in graph.edges]

    # Assert Nodes
    assert "Directory" in types
    assert "File" in types
    assert "Variable" in types
    assert "Literal" in types
    assert "Identifier" in types
    assert "Function" in types
    assert "Call" in types

    # Assert Edges
    assert "CONTAINS" in edge_types
    assert "DEFINES" in edge_types
    assert "ASSIGNED_FROM" in edge_types
    assert "REFERS_TO" in edge_types
    assert "HAS_ARGUMENT" in edge_types

    # Check directory nesting
    # Expected: /tmp/project/src/module -> CONTAINS -> repro.py
    #           /tmp/project/src -> CONTAINS -> /tmp/project/src/module

    dir_module = next(
        n
        for n in graph.nodes
        if n.type == "Directory" and n.properties["name"] == "module"
    )
    dir_src = next(
        n
        for n in graph.nodes
        if n.type == "Directory" and n.properties["name"] == "src"
    )

    nesting_edges = [
        e
        for e in graph.edges
        if e.type == "CONTAINS"
        and e.source_id == dir_src.id
        and e.target_id == dir_module.id
    ]
    assert len(nesting_edges) == 1, "Directory nesting should be captured"

    # Find specific relationships
    # File DEFINES Function
    file_node = next(n for n in graph.nodes if n.type == "File")
    func_node = next(
        n
        for n in graph.nodes
        if n.type == "Function" and n.properties["name"] == "main"
    )

    defines_edges = [
        e
        for e in graph.edges
        if e.type == "DEFINES"
        and e.source_id == file_node.id
        and e.target_id == func_node.id
    ]
    assert len(defines_edges) == 1, "File should DEFINE main function"

    # Function DEFINES Variable (parameter)
    concat_node = next(
        n
        for n in graph.nodes
        if n.type == "Function" and n.properties["name"] == "concat_greeting"
    )
    greeting_param = next(
        n
        for n in graph.nodes
        if n.type == "Variable"
        and n.properties["name"] == "greeting"
        and "row=0" in str(n.id)
    )  # heuristic

    param_edges = [
        e
        for e in graph.edges
        if e.type == "DEFINES"
        and e.source_id == concat_node.id
        and e.target_id == greeting_param.id
    ]
    assert len(param_edges) == 1, "Function should DEFINE parameter"

    # Variable assigned from Literal
    main_greeting = next(
        n
        for n in graph.nodes
        if n.type == "Variable"
        and n.properties["name"] == "greeting"
        and "row=5" in str(n.id)
    )
    hello_lit = next(
        n
        for n in graph.nodes
        if n.type == "Literal" and n.properties["value"] == '"Hello"'
    )

    assign_edges = [
        e
        for e in graph.edges
        if e.type == "ASSIGNED_FROM"
        and e.source_id == main_greeting.id
        and e.target_id == hello_lit.id
    ]
    assert len(assign_edges) == 1, "Variable should be ASSIGNED_FROM literal"
