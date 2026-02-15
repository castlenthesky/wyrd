from server.db import FalkorDBClient


def debug_graph():
    client = FalkorDBClient()
    if not client.connect():
        print("Could not connect to FalkorDB")
        return

    print("Connected to FalkorDB.")

    # Check node count
    res = client.query("MATCH (n) RETURN count(n)")
    print(f"Total nodes: {res[0][0]}")

    # dump some nodes
    res = client.query("MATCH (n) RETURN labels(n), n.id, n.name LIMIT 5")
    print("\nSample Nodes:")
    for row in res:
        print(row)

    # Check edges
    res = client.query("MATCH ()-[r]->() RETURN type(r), count(r)")
    print("\nEdge Counts:")
    for row in res:
        print(row)


if __name__ == "__main__":
    debug_graph()
