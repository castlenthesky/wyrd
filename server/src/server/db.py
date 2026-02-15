from falkordb import FalkorDB


class FalkorDBClient:
    def __init__(self, host="localhost", port=6379):
        self.host = host
        self.port = port
        self.driver = None
        self.graph = None

    def connect(self):
        try:
            self.driver = FalkorDB(host=self.host, port=self.port)
            self.graph = self.driver.select_graph("wyrd")
            return True
        except Exception as e:
            print(f"Failed to connect to FalkorDB: {e}")
            return False

    def query(self, query: str, params=None):
        if not self.graph:
            self.connect()
        try:
            return self.graph.query(query, params).result_set
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def get_full_graph(self):
        """Fetch the entire graph for visualization."""
        if not self.graph:
            self.connect()
            
        try:
            # Query all nodes and relationships
            # Note: This is efficient for small graphs, but will need pagination/filtering for large ones.
            res = self.graph.query("MATCH (n)-[r]->(m) RETURN n, r, m").result_set
            
            nodes = {}
            links = []
            
            for record in res:
                src_node = record[0]
                rel = record[1]
                dst_node = record[2]
                
                # Add nodes if not already added
                if src_node.id not in nodes:
                    nodes[src_node.id] = {
                        "id": src_node.id,
                        "label": list(src_node.labels)[0] if src_node.labels else "Unknown",
                        **src_node.properties
                    }
                    
                if dst_node.id not in nodes:
                    nodes[dst_node.id] = {
                        "id": dst_node.id,
                        "label": list(dst_node.labels)[0] if dst_node.labels else "Unknown",
                        **dst_node.properties
                    }
                
                # Add relationship
                links.append({
                    "source": src_node.id,
                    "target": dst_node.id,
                    "label": rel.relation,
                    **rel.properties
                })
                
            return {
                "nodes": list(nodes.values()),
                "links": links
            }
            
        except Exception as e:
            print(f"Failed to fetch full graph: {e}")
            return {"nodes": [], "links": []}

