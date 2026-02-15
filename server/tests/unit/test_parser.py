import pytest
from server.parser import TreeSitterParser


def test_parser_init():
    parser = TreeSitterParser()
    assert parser is not None


def test_parser_parse():
    parser = TreeSitterParser()
    result = parser.parse("def foo(): pass")
    assert result == "parsed_tree"
