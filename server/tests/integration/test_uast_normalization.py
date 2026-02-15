import pytest
import tree_sitter_python
from server.uast.builder import UASTBuilder
from tree_sitter import Language, Parser


@pytest.fixture
def parser():
    PY_LANGUAGE = Language(tree_sitter_python.language())
    parser = Parser(PY_LANGUAGE)
    return parser


def test_full_python_file_normalization(parser):
    source_code = b"""
import os
from math import sqrt

def calculate_distance(x, y):
    return sqrt(x*x + y*y)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def dist(self):
        return calculate_distance(self.x, self.y)

dist = calculate_distance(3, 4)
"""
    tree = parser.parse(source_code)

    builder = UASTBuilder()
    graph = builder.build(tree.root_node, source_code)

    # Debug print
    # for n in graph.nodes:
    #     print(n)
    # for e in graph.edges:
    #     print(e)

    # Verify Imports
    imports = [n for n in graph.nodes if n.type == "Import"]
    assert len(imports) >= 2
    modules = set(n.properties["module"] for n in imports)
    assert "os" in modules
    assert (
        "math" in modules or "sqrt" in modules
    )  # Depending on how we handled from import

    # Verify Functions
    funcs = [n for n in graph.nodes if n.type == "Function"]
    func_names = [n.properties["name"] for n in funcs]
    assert "calculate_distance" in func_names
    assert "__init__" in func_names
    assert "dist" in func_names

    # Verify Calls
    calls = [n for n in graph.nodes if n.type == "Call"]
    callee_names = [n.properties["callee_name"] for n in calls]
    assert "sqrt" in callee_names
    assert "calculate_distance" in callee_names

    # Verify Edges
    # We expect DEFINES or CONTAINS edges
    # For now we use CONTAINS from the builder
    contains_edges = [e for e in graph.edges if e.type == "CONTAINS"]
    assert len(contains_edges) > 0
