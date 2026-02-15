from typing import Any, Dict

from server.db import FalkorDBClient
from server.uast.models import GraphPayload


class UASTIngester:
    def __init__(self, db_client: FalkorDBClient):
        self.db_client = db_client

    def ingest(self, payload: GraphPayload):
        """
        Writes the GraphPayload to FalkorDB.
        Transacts node creations and edge creations.
        """
        # 1. Merge Nodes
        for node in payload.nodes:
            self._merge_node(node)

        # 2. Merge Edges
        for edge in payload.edges:
            self._merge_edge(edge)

    def _merge_node(self, node: Any):
        # Format properties for Cypher
        props_str = self._format_props(node.properties, extra={"id": node.id})
        query = f"MERGE (n:{node.type} {{id: '{node.id}'}}) SET n += {{{props_str}}}"
        self.db_client.query(query)

    def _merge_edge(self, edge: Any):
        # MATCH source and target, then MERGE edge
        props_str = self._format_props(edge.properties)
        query = f"""
        MATCH (a {{id: '{edge.source_id}'}}), (b {{id: '{edge.target_id}'}})
        MERGE (a)-[r:{edge.type}]->(b)
        """
        if props_str:
            query += f" SET r += {{{props_str}}}"

        self.db_client.query(query)

    def _format_props(self, props: Dict[str, Any], extra: Dict[str, Any] = None) -> str:
        all_props = props.copy()
        if extra:
            all_props.update(extra)

        parts = []
        for k, v in all_props.items():
            if isinstance(v, str):
                # Simple escaping
                safe_v = v.replace("'", "\\'")
                parts.append(f"{k}: '{safe_v}'")
            elif isinstance(v, bool):
                parts.append(f"{k}: {str(v).lower()}")
            else:
                parts.append(f"{k}: {v}")
        return ", ".join(parts)
