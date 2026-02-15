### **Project Title:** WYRD: The Graph-Based Code Intelligence Extension
**Objective:** To build a VS Code extension that visualizes code relationships (Call Graphs, Dependencies) by converting language-specific ASTs into a Universal AST (UAST) and persisting them in FalkorDB for low-latency graph querying.

---

### **1. System Architecture Overview**
The system will follow a **Client-Server model** to decouple the heavy analysis logic from the VS Code UI, avoiding performance penalties on the editor.

*   **Client (VS Code Extension):** Handles user input, renders the Webview graph, and acts as the Language Client.
*   **Server (Analysis Engine):** A standalone process (likely Python, Rust, or Node.js) running the Language Server Protocol (LSP). It handles parsing, UAST conversion, and database interactions.
*   **Storage Layer (FalkorDB):** A high-performance graph database used to store the Universal AST and semantic relationships (Edges).

---

### **2. Component Requirements**

#### **A. The Parsing Layer (ASTs & LSTs)**
**Goal:** Generate reliable syntax trees from source code.
*   **Tooling:** Use **Tree-sitter** to generate concrete syntax trees (LSTs). Tree-sitter is preferred over regex or standard compilers because it is error-tolerant (handles broken code while typing) and incremental (fast updates).
*   **Requirement 1 (LST Generation):** The system must generate a raw Language Syntax Tree (LST) for supported languages (e.g., Python, TypeScript) immediately upon file save.
*   **Requirement 2 (Incremental Parsing):** The parser will trigger on file save, ensuring that graph updates occur only when the user commits changes to disk, avoiding overhead during typing.

#### **B. The Normalization Layer (Universal AST)**
**Goal:** Abstract away language-specific syntax into a common schema so queries work across languages (Polyglot support).
*   **Concept:** Convert language-specific AST nodes into **Universal Nodes**.
*   **Schema Definition:**
    *   **Structural Nodes:** `Module`, `Class`, `Function`, `Interface`.
    *   **Universal Properties:** `name`, `start_position`, `end_position`, `source_code`.
*   **Requirement 3:** Implement **Language Adapters** (e.g., a Python Adapter and a JS Adapter) that map Tree-sitter nodes to Universal Nodes.
    *   *Example:* Map Python's `FunctionDef` and JavaScript's `FunctionDeclaration` to a single `UniversalFunction` node.

#### **C. The Graph Storage Layer (FalkorDB)**
**Goal:** Persist the code structure to enable complex relationship querying.
*   **Technology:** **FalkorDB** (replacing Neo4j or in-memory graphs used in similar architectures).
*   **Requirement 4 (Node Ingestion):** Store Universal Nodes as Graph Nodes.
*   **Requirement 5 (Edge Creation):** Analyze the UAST to create semantic edges:
    *   `(:Function)-[:CALLS]->(:Function)`
    *   `(:Class)-[:INHERITS]->(:Class)`
    *   `(:Module)-[:IMPORTS]->(:Module)`
    *   `(:Method)-[:MODIFIES]->(:Variable)`
    *   `(:Class)-[:IMPLEMENTS]->(:Interface)`
*   **Requirement 6 (Symbol Resolution):** Implement a symbol table strategy to resolve references (e.g., knowing that `User.get()` in File A refers to the `User` class in File B) before creating edges.

#### **D. The VS Code Extension (Client & Webview)**
**Goal:** Display the data to the user.
*   **Technology:** VS Code Webview API + React (or similar) + Graph Visualization Library (e.g., Force Graph).
*   **Requirement 7 (LSP Client):** The extension must start the Analysis Engine as a background process and communicate via JSON-RPC.
*   **Requirement 8 (Webview Visualization):** Create a panel that renders the data from FalkorDB.
    *   *Feature:* Clicking a node in the graph navigates the editor to the definition (LSP `textDocument/definition`).
    *   *Feature:* Live updates—when the graph changes in FalkorDB (triggered by a save), push a notification to the Webview to re-render.

---

### **3. Implementation Roadmap (Broad Strokes)**

#### **Phase 1: The LSP "Skeleton"**
1.  Create a standard VS Code extension using the `vscode-languageclient` node module.
2.  Create the server executable (in Python or Rust).
3.  Implement the standard LSP `initialize` handshake to negotiate capabilities.
4.  Implement `textDocument/didOpen` and `textDocument/didSave` to receive code content from the editor.

#### **Phase 2: Parsing & Database Integration**
1.  Integrate **Tree-sitter** bindings into the server to parse incoming text from `didSave` events.
2.  Spin up a local **FalkorDB** instance (via Docker or embedded if possible).
3.  On `didSave`, traverse the Tree-sitter tree, convert nodes to UAST objects, and perform an **UPSERT** query into FalkorDB.
    *   *Strategy:* Use file paths as unique keys to prevent duplicate subgraphs.

#### **Phase 3: Building the Graph Viewer**
1.  Register a custom command in VS Code (e.g., `CodeGraph: Show Graph`).
2.  When triggered, the Client sends a custom Request (e.g., `workspace/visualize`) to the Server.
3.  The Server queries FalkorDB (e.g., `MATCH (n)-[r]->(m) RETURN n,r,m`), formats the result as JSON, and returns it to the Client.
4.  The Client passes this JSON to the Webview to render the nodes and edges.

#### **Phase 4: Advanced Features (Interactivity)**
1.  **Bi-directional Sync:** When a user clicks a node in the Webview, send a command to VS Code to open that file and scroll to the specific line (using the `start_position` stored in FalkorDB).
2.  **Cross-File References:** Implement a "Find References" query in FalkorDB to show how different files connect, visualizing the "Import" or "Call" edges.

### **4. Key Challenges & Solutions**
*   **Latency:** Re-analyzing the whole project on every keypress is too slow.
    *   *Solution:* **Parse on Save**. By only triggering the analysis pipeline when the user saves the file (`didSave`), we avoid the overhead of constant re-parsing and graph updates during typing. The extension remains dormant until the user explicitly commits their changes to disk.
*   **Language Agnosticism:** How to handle Python and JS simultaneously?
    *   *Solution:* The **Universal AST** layer is critical here. By normalizing `function def` (Python) and `function` (JS) into a generic `Function` node in FalkorDB, your graph visualization logic remains identical regardless of the language.


## Delivery Plan

### **Phase 1: The Skeleton MVP (Python AST)**

**Goal:** Establish end-to-end connectivity between VS Code, the LSP Server, and FalkorDB for a single Python file, visualizing its AST.

#### **Epic 1: Infrastructure & Connectivity**
*   **Feature: Extension & Server Scaffold**
    *   [ ] **Story:** Initialize a VS Code extension with a dedicated "Output" channel for logging.
    *   [ ] **Story:** Initialize a Python LSP server (using `pygls`) that runs as a subprocess of the extension.
    *   [ ] **Story:** Implement the `initialize` LSP handshake to confirm Client-Server communication.
*   **Feature: Database Connection**
    *   [ ] **Story:** Create a Docker Compose file to spin up a local FalkorDB instance.
    *   [ ] **Story:** Implement a "Ping" check in the LSP Server startup to verify it can connect to FalkorDB.

#### **Epic 2: Parsing & Ingestion (Python Only)**
*   **Feature: Tree-sitter Integration**
    *   [ ] **Story:** Add `tree-sitter` and `tree-sitter-python` dependencies to the Server.
    *   [ ] **Story:** Implement `textDocument/didOpen` and `textDocument/didSave` handlers to receive file content.
    *   [ ] **Story:** On `didSave`, parse the document content into a Tree-sitter tree in memory.
*   **Feature: AST Persistence**
    *   [ ] **Story:** Create a `GraphClient` class to handle Cypher query execution.
    *   [ ] **Story:** Implement a recursive traversal to map Tree-sitter nodes to Cypher `CREATE` statements (Ingesting Nodes + `[:PARENT]` relationships).
    *   [ ] **Story:** Ensure the graph is cleared or updated correctly for the specific file on re-save (Idempotency).

#### **Epic 3: Visualization (Webview)**
*   **Feature: Webview Panel**
    *   [ ] **Story:** Register a command `wyrd.showGraph` that opens a Webview panel to the side.
    *   [ ] **Story:** Setup message passing: The Webview sends a `ready` message, and the Extension replies with `hello`.
*   **Feature: Graph Rendering**
    *   [ ] **Story:** Implement a custom LSP request `wyrd/getGraph` that fetches the AST nodes/edges from FalkorDB for the current file.
    *   [ ] **Story:** Pass this graph data to the Webview.
    *   [ ] **Story:** Use a graph library (e.g., `react-force-graph` or `cytoscape.js`) to render the nodes and parent-child edges in the pane.


