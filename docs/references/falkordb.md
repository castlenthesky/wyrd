# FalkorDB

## Overview
**FalkorDB** is a high-performance, low-latency graph database implemented as a Redis module. It serves as the persistence and query layer for the WYRD extension, replacing slower or more complex alternatives like Neo4j or in-memory NetworkX graphs for this use case.

## Why FalkorDB for CPG?
In the context of a Code Property Graph (CPG) extension for VS Code, FalkorDB offers specific architectural advantages:

## Source
https://github.com/falkordb/falkordb
https://github.com/FalkorDB/FalkorDB-MCPServer

### 1. Ultra-Low Latency (Redis Protocol)
*   **Performance:** Built on Redis, it inherits the high-throughput, low-latency characteristics of in-memory data stores.
*   **Relevance:** VS Code extensions require near-instant feedback. When a user hovers over a function or asks "Find all references," the query response must appear in milliseconds to avoid UI blocking. Network-heavy databases often introduce noticeable lag.

### 2. Sparse Matrix Graph Representation
*   **Architecture:** Unlike pointer-chasing graph databases (like Neo4j), FalkorDB usually represents graphs using sparse adjacency matrices and performs graph traversals via linear algebra operations (Matrix-Vector Multiplication).
*   **Relevance:** This architecture is particularly efficient for **reachability analysis** (e.g., "Can Function A reach Function B?"), which translates to matrix powers or aggregations. This allows WYRD to perform complex static analysis (like taint analysis) much faster than traditional traversals.

### 3. OpenCypher Support
*   **Query Language:** Full support for the OpenCypher standard.
*   **CPG Queries:** Complex static analysis questions can be expressed elegantly in Cypher:
    ```cypher
    // Example: Find all functions calling 'deprecated_api'
    MATCH (f:Function)-[:CALLS]->(d:Function {name: 'deprecated_api'})
    RETURN f.name, f.file_path
    ```
    ```cypher
    // Example: Recursively find dependencies (Transitive Closure)
    MATCH (a:Module {name: 'MyMod'})-[:DEPENDS_ON*]->(dep)
    RETURN DISTINCT dep.name
    ```

### 4. Vector Search & GraphRAG (Future Proofing)
*   **Feature:** FalkorDB supports vector indexing on node properties.
*   **Relevance:** This enables "Semantic Search" over the CPG. Not only can you query exact structural matches (AST), but you can also embed the source code of a function and query: "Find functions that look like they perform encryption." This bridges the gap between precise Static Analysis and fuzzy AI reasoning.

## Usage in WYRD
*   **Nodes:** Universal Nodes (AST + CFG + PDG mixed).
    *   Labels: `:Function`, `:Class`, `:Variable`, `:BasicBlock`.
    *   Properties: `source_code`, `line_number`, `type_signature`.
*   **Edges:** Semantic relationships.
    *   Types: `[:CALLS]`, `[:INHERITS]`, `[:MODIFIES]`, `[:FLOWS_TO]`.
*   **Architecture:** The LSP Server will spin up a local FalkorDB container (or embedded instance) and push mostly-write operations during indexing (`didSave`), while the VS Code client pushes read-heavy operations during exploration.
