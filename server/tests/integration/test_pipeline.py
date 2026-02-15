import pytest
import time
from server.parser import TreeSitterParser
from server.db import FalkorDBClient
from server.main import did_save
from lsprotocol.types import DidSaveTextDocumentParams, TextDocumentIdentifier


# @pytest.mark.asyncio
def test_pipeline_integration():
    # 1. Setup
    db_client = FalkorDBClient()
    connected = db_client.connect()

    if not connected:
        pytest.skip("FalkorDB not available")

    # Clear DB
    db_client.query("MATCH (n) DETACH DELETE n")

    # 2. Parse and Extract
    code = """
def hello():
    print("world")
"""
    parser = TreeSitterParser()
    tree = parser.parse(code)
    nodes, edges = parser.extract_graph(tree, "file://test.py")

    assert len(nodes) > 0

    # 3. Simulate DB Insertion (Logic from main.py)
    # We can reuse the logic in main.py if we factor it out, but for now duplicate to verify

    for node in nodes:
        props = node["properties"]
        props["node_id"] = node["id"]
        props_str_parts = []
        for k, v in props.items():
            if isinstance(v, str):
                safe_v = v.replace("'", "\\'")
                props_str_parts.append(f"{k}: '{safe_v}'")
            else:
                props_str_parts.append(f"{k}: {v}")
        props_str = ", ".join(props_str_parts)
        query = f"CREATE (n:{node['label']} {{{props_str}}})"
        db_client.query(query)

    for src_id, rel_type, dst_id in edges:
        edge_query = f"MATCH (a {{node_id: '{src_id}'}}), (b {{node_id: '{dst_id}'}}) CREATE (a)-[:{rel_type}]->(b)"
        db_client.query(edge_query)

    # 4. Verify
    # Count nodes
    result = db_client.query("MATCH (n) RETURN count(n)")
    count = result[0][0]
    assert count == len(nodes)

    # Count edges
    result = db_client.query("MATCH ()-[r]->() RETURN count(r)")
    edge_count = result[0][0]
    assert edge_count == len(edges)

    print(f"Verified {count} nodes and {edge_count} edges in FalkorDB")
