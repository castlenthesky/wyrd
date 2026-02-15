# WYRD: The Graph-Based Code Intelligence Extension

**WYRD** is an experimental VS Code extension that visualizes the hidden relationships within your code. By converting language-specific Abstract Syntax Trees (ASTs) into a normalized **Universal AST (UAST)** and persisting them in a high-performance graph database (**FalkorDB**), WYRD enables powerful semantic queries and visualizations that go far beyond standard "Go to Definition."

---

## 🚀 Overview

Traditional IDE intelligence is often limited to file-level analysis or simple text search. WYRD treats your codebase as a **Code Property Graph (CPG)**—a layered graph merging structure, control flow, and data dependencies.

**Current Status:** *Pre-Alpha / Conceptual Phase*

### Key Objectives
*   **Visualize Complexity:** See how functions, classes, and modules interact across your entire repository.
*   **Universal Understanding:** Analyze relationships between different languages (e.g., Python calling Rust) using a unified graph schema.
*   **Low-Latency Queries:** Leverage [FalkorDB](https://falkordb.com/) (a Redis-based Graph DB) for instant graph traversals, capable of answering questions like "Which API endpoints are affected if I change this database model?"

---

## 🏗 Architecture

WYRD follows a decoupled **Client-Server** architecture based on the Language Server Protocol (LSP).

1.  **Client (VS Code Extension):**
    *   Handles UI/UX, file events (`didOpen`, `didSave`), and renders the Graph Webview.
    *   Acts as the LSP Client.
2.  **Analysis Engine (LSP Server):**
    *   A standalone process (Python/Rust) that parses code using **Tree-sitter**.
    *   Normalizes language-specific nodes into **Universal Nodes**.
    *   Manages the connection to FalkorDB.
3.  **Storage Layer (FalkorDB):**
    *   Stores the persistent CPG.
    *   Enables complex OpenCypher queries for static analysis.

![Architecture Diagram](docs/images/architecture_placeholder.png) *(To be added)*

---

## 🛠 Technology Stack

*   **Frontend:** TypeScript, VS Code API, React (Webview)
*   **Backend:** Python (`pygls`) or Rust (`tower-lsp`)
*   **Parsing:** [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) (Incremental Parsing)
*   **Database:** [FalkorDB](https://github.com/FalkorDB/FalkorDB) (Redis Module)
*   **Protocol:** [LSP](https://microsoft.github.io/language-server-protocol/) (Language Server Protocol)

---

## 🛣 Roadmap

### Phase 1: The Skeleton MVP (Python AST)
*   [ ] Initialize VS Code Extension & Python LSP Server.
*   [ ] Set up local FalkorDB Docker container.
*   [ ] **Ingestion:** Parse Python files on save (`textDocument/didSave`) using Tree-sitter.
*   [ ] **Persistence:** Store the AST nodes and `[:PARENT]` edges in FalkorDB.
*   [ ] **Visualization:** Verify the graph by rendering the AST of a single file in a Webview.

### Phase 2: The Code Property Graph (CPG)
*   [ ] **Control Flow:** Calculate and store CFG edges (`[:FLOWS_TO]`).
*   [ ] **Data Flow:** Implement PDG analysis to trace variable usage (`[:DATA_DEPENDENCY]`).
*   [ ] **Polyglot Support:** Add a second language (e.g., TypeScript) and map it to the Universal AST schema.

### Phase 3: Advanced Intelligence
*   [ ] **Symbol Resolution:** Link identifiers to their definitions across files.
*   [ ] **Impact Analysis:** Query the graph to show "Blast Radius" of code changes.
*   [ ] **Natural Language Querying:** "Show me all auth-related functions."

---

## 📖 Documentation

*   [Implementation Outline](docs/prds/planned/00_outline.md)
*   [Reference: Code Property Graph](docs/references/00_code-property-graph.md)
*   [Reference: FalkorDB](docs/references/falkordb.md)

---

## 👥 Contributing

This project is currently in the planning/research phase. Contributions to the documentation or architectural design discussions are welcome.

## 📄 License

[MIT](LICENSE)
