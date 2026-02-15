from unittest.mock import MagicMock

import pytest
from server.uast.builder import UASTBuilder
from server.uast.models import GraphPayload
from tree_sitter import Node


@pytest.fixture
def uast_builder():
    return UASTBuilder()


def test_builder_initialization(uast_builder):
    assert isinstance(uast_builder._graph, GraphPayload)


def test_build_returns_payload(uast_builder):
    mock_root = MagicMock(spec=Node)
    mock_root.children = []
    mock_root.type = "module"
    result = uast_builder.build(mock_root, b"")
    assert isinstance(result, GraphPayload)


def test_handler_dispatch(uast_builder):
    mock_node = MagicMock(spec=Node)
    mock_node.type = "function_definition"
    mock_node.children = []
    mock_node.start_point = (0, 0)

    # Mock the specific handler to verify dispatch
    uast_builder.handle_function_definition = MagicMock(return_value="func_node")

    uast_builder._handle_node(mock_node, b"def foo(): pass")
    uast_builder.handle_function_definition.assert_called_once()


def test_handle_function_definition_creates_nodes_and_edges(uast_builder):
    mock_node = MagicMock(spec=Node)
    mock_node.type = "function_definition"
    mock_node.start_point = (10, 0)
    mock_node.parent = None

    mock_name_node = MagicMock(spec=Node)
    mock_name_node.start_byte = 4
    mock_name_node.end_byte = 7
    mock_node.child_by_field_name.side_effect = lambda name: (
        mock_name_node if name == "name" else None
    )

    source_code = b"def foo(): pass"

    node_id = uast_builder.handle_function_definition(
        mock_node, source_code, parent_id="module:0"
    )

    assert node_id == "func:10:foo"
    assert len(uast_builder._graph.nodes) == 1
    assert uast_builder._graph.nodes[0].type == "Function"
    assert uast_builder._graph.nodes[0].properties["name"] == "foo"

    assert len(uast_builder._graph.edges) == 1
    assert uast_builder._graph.edges[0].type == "CONTAINS"
    assert uast_builder._graph.edges[0].source_id == "module:0"
    assert uast_builder._graph.edges[0].target_id == node_id


def test_handle_call_creates_nodes_and_edges(uast_builder):
    mock_node = MagicMock(spec=Node)
    mock_node.type = "call"
    mock_node.start_point = (20, 5)

    mock_func_node = MagicMock(spec=Node)
    mock_func_node.start_byte = 0
    mock_func_node.end_byte = 3
    mock_node.child_by_field_name.return_value = mock_func_node

    source_code = b"bar()"

    node_id = uast_builder.handle_call(mock_node, source_code, parent_id="func:10:foo")

    assert "call:20:bar" in node_id
    assert len(uast_builder._graph.nodes) == 1
    assert uast_builder._graph.nodes[0].type == "Call"

    # Check edges: 1 CONTAINS (from parent), 1 REFERS_TO (to symbol)
    assert len(uast_builder._graph.edges) == 2
    types = [e.type for e in uast_builder._graph.edges]
    assert "CONTAINS" in types
    assert "REFERS_TO" in types


def test_handle_import_statement(uast_builder):
    mock_node = MagicMock(spec=Node)
    mock_node.type = "import_statement"
    mock_node.start_point = (5, 0)

    mock_dotted_name = MagicMock(spec=Node)
    mock_dotted_name.type = "dotted_name"
    mock_dotted_name.start_byte = 7
    mock_dotted_name.end_byte = 9

    mock_node.children = [mock_dotted_name]

    source_code = b"import os"

    uast_builder.handle_import_statement(mock_node, source_code, parent_id="file:1")

    assert len(uast_builder._graph.nodes) == 1
    assert uast_builder._graph.nodes[0].type == "Import"
    assert uast_builder._graph.nodes[0].properties["module"] == "os"

    assert len(uast_builder._graph.edges) == 1
    assert uast_builder._graph.edges[0].type == "IMPORTS"
