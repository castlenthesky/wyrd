from unittest.mock import MagicMock

import pytest
from server.uast.ingester import UASTIngester
from server.uast.models import GraphPayload, UASTEdge, UASTNode


@pytest.fixture
def mock_db_client():
    client = MagicMock()
    return client


@pytest.fixture
def ingester(mock_db_client):
    return UASTIngester(mock_db_client)


def test_ingest_nodes_calls_db(ingester, mock_db_client):
    payload = GraphPayload()
    node = UASTNode(id="file:1", type="File", properties={"name": "test.py"})
    payload.add_node(node)

    ingester.ingest(payload)

    # Check Cypher query
    mock_db_client.query.assert_called()
    args, _ = mock_db_client.query.call_args_list[0]
    query = args[0]
    assert "MERGE (n:File {id: 'file:1'})" in query
    assert "name: 'test.py'" in query


def test_ingest_edges_calls_db(ingester, mock_db_client):
    payload = GraphPayload()
    edge = UASTEdge(
        source_id="A", target_id="B", type="LINKS", properties={"weight": 1}
    )
    payload.add_edge(edge)

    ingester.ingest(payload)

    args, _ = mock_db_client.query.call_args_list[0]
    query = args[0]
    assert "MATCH (a {id: 'A'}), (b {id: 'B'})" in query
    assert "MERGE (a)-[r:LINKS]->(b)" in query
    assert "weight: 1" in query


def test_property_formatting(ingester):
    props = {"str": "val", "int": 1, "bool": True, "escaped": "O'Reilly"}
    formatted = ingester._format_props(props)
    assert "str: 'val'" in formatted
    assert "int: 1" in formatted
    assert "bool: true" in formatted
    assert "escaped: 'O\\'Reilly'" in formatted
