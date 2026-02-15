# Language Server Protocol (LSP)

## Overview
The **Language Server Protocol (LSP)** is an open, JSON-RPC-based standard for communication between code editors (Clients) and language analysis tools (Servers).

## Why LSP for CPG?
WYRD uses LSP not just for standard features (like Go to Definition) but as the backbone for the separate "Analysis Engine" process.

### 1. Architecture: Decoupling UI from Analysis
*   **Mechanism:** The heavy lifting (parsing, graph traversals, database writes) happens in the Server process. The Client (VS Code) only handles rendering.
*   **Relevance:**
    *   **Stability:** If the analysis engine crashes or hangs on a massive graph query, it doesn't crash VS Code.
    *   **Polyglot:** The same LSP server can communicate with VS Code, Neovim, or IntelliJ.

### 2. Standard Capabilities (The "Free" Stuff)
By implementing standard LSP methods backed by the CPG, WYRD acts as a "Super-LSP":
*   `textDocument/definition`: Query FalkorDB for the defining node (`MATCH (n {name: $symbol}) ...`).
*   `textDocument/references`: Query FalkorDB for usage edges (`MATCH (n)-[:CALLS]->(target) ...`).
*   `textDocument/hover`: Fetch rich documentation or "Complexity metrics" from the CFG properties in FalkorDB and display them in the hover tooltip.

### 3. Custom Commands (The Graph Visualization)
*   **Mechanism:** LSP allows `workspace/executeCommand` for custom interactions.
*   **Relevance:**
    *   **Command:** `wyrd.visualizeGraph`
    *   **Flow:**
        1.  User clicks "Visualize" in VS Code.
        2.  Client sends `workspace/executeCommand` with the current file/function ID.
        3.  Server receives command, runs a complex Cypher query (e.g., "Get the subgraph of 2-hop dependencies").
        4.  Server returns the JSON subgraph.
        5.  Client forwards this to the Webview for rendering.

### 4. Synchronization (`textDocument/*`)
*   **Events:**
    *   `didOpen`: Load the file into memory/Tree-sitter.
    *   `didChange`: Incremental updates (crucial for latency).
    *   `didSave`: Trigger the heavy "Graph Commit" to FalkorDB.
*   **Relevance:** These hooks are the triggers for the CPG Pipeline. The architecture relies on `didSave` to ensure the persistent graph state is consistent with the disk state.

## Implementation Details
*   **Library:** `pygls` (Python) or `tower-lsp` (Rust) or `vscode-languageserver-node`.
*   **Transport:** Stdio (standard input/output) is the default and simplest for local extensions.