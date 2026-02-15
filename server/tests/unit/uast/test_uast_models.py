from server.uast.models import GraphPayload, UASTEdge, UASTNode


def test_uast_node_creation():
    node = UASTNode(id="file:main.py", type="File", properties={"path": "main.py"})
    assert node.id == "file:main.py"
    assert node.type == "File"
    assert node.properties["path"] == "main.py"


def test_uast_edge_creation():
    edge = UASTEdge(
        source_id="file:main.py", target_id="func:main.py:foo", type="DEFINES"
    )
    assert edge.source_id == "file:main.py"
    assert edge.target_id == "func:main.py:foo"
    assert edge.type == "DEFINES"


def test_graph_payload_operations():
    payload = GraphPayload()
    node = UASTNode(id="n1", type="Test")
    edge = UASTEdge(source_id="n1", target_id="n2", type="LINK")

    payload.add_node(node)
    payload.add_edge(edge)

    assert len(payload.nodes) == 1
    assert len(payload.edges) == 1
    assert payload.nodes[0] == node
    assert payload.edges[0] == edge
