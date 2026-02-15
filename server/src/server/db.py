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
