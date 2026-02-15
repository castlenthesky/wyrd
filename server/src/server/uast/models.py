from typing import Any, Dict, List

from pydantic import BaseModel, Field


class UASTNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the node (VName)")
    type: str = Field(..., description="Type of the node (e.g., Function, Class)")
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Key-value pairs of node properties"
    )


class UASTEdge(BaseModel):
    source_id: str = Field(..., description="ID of the source node")
    target_id: str = Field(..., description="ID of the target node")
    type: str = Field(
        ..., description="Type of the relationship (e.g., CALLS, DEFINES)"
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Key-value pairs of edge properties"
    )


class GraphPayload(BaseModel):
    nodes: List[UASTNode] = Field(default_factory=list)
    edges: List[UASTEdge] = Field(default_factory=list)

    def add_node(self, node: UASTNode):
        self.nodes.append(node)

    def add_edge(self, edge: UASTEdge):
        self.edges.append(edge)
