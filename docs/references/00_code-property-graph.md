# Code Property Graph (CPG)

A **Code Property Graph (CPG)** is a comprehensive data structure that represents a software program by merging multiple graph representations—specifically the **Abstract Syntax Tree (AST)**, **Control Flow Graph (CFG)**, and **Program Dependence Graph (PDG)**—into a single, layered property graph.

In a CPG, nodes and edges are enriched with key-value pairs (properties), allowing for sophisticated static analysis, security vulnerability detection, and code optimization through efficient graph traversals and queries.

## 1. Layer 1: Abstract Syntax Tree (AST)
**Role:** Represents the syntactic structure of the code.
**Mechanism:** It provides the "skeleton" of the graph. AST nodes (like `Function`, `Assignment`, `Identifier`) serve as the backbone upon which other graphs are overlaid.
-   **Nodes**: Structural elements (blocks, statements, expressions).
-   **Edges**: Containment relationships (e.g., a generic `File` node contains `Class` nodes, which contain `Method` nodes).

*See [Abstract Syntax Tree](./01_abstract-syntax-tree.md) for a detailed breakdown.*

## 2. Layer 2: Control Flow Graph (CFG)
**Role:** Represents the execution order of statements.
**Mechanism:** Edges are added between AST nodes to model the sequence of operations.
-   **Nodes**: Basic blocks or individual statements from the AST.
-   **Edges**: Flow control (unconditional jumps, conditional branches like `true`/`false` edges).

*See [Control Flow Graph](./02_control-flow-graph.md) for a detailed breakdown.*

## 3. Layer 3: Program Dependence Graph (PDG)
**Role:** Represents the data and control dependencies between statements.
**Mechanism:** Edges connect nodes based on how data is generated and consumed, and how execution is controlled.
-   **Nodes**: Statements and expressions from the AST.
-   **Edges**:
    -   **Data Dependency**: Connects a definition of a variable to its usage.
    -   **Control Dependency**: Connects a predicate (e.g., `if (x > 0)`) to the statements that execute only if that predicate is true.

*See [Program Dependence Graph](./03_program-dependence-graph.md) for a detailed breakdown.*

## 4. Where do Imports and Dependencies fit?
Imports and cross-file dependencies are handled in two stages:
1.  **Syntactic Stage (AST)**: The `import` statement itself is just a node in the AST (e.g., `ImportDeclaration`). It tells us *that* a file is requested, but not *what* it resolves to.
2.  **Semantic Stage (Linking/Overlay)**: The CPG build process resolves these imports to actual nodes in other files. This creates a **Call Graph** or **Type Hierarchy** overlay.
    -   *Example*: `import utils` in `main.py` creates a semantic edge from the `ImportDeclaration` in `main.py` to the `File` node of `utils.py`.
    -   *Example*: Calling `utils.foo()` creates a **Call Edge** from the call site in `main.py` to the `Method` node `foo` in `utils.py`.

## 5. Practical Queries (Holistic CPG)
*The power of the CPG is combining these layers to answer complex questions.*

-   **"Find all HTTP endpoints that write to the file system."**
    -   *Layers:* **AST** (identifies endpoints via annotations) + **Call Graph/CFG** (traces execution) + **AST** (identifies file write calls).
-   **"Is there a path from a public API to this deprecated function?"**
    -   *Layers:* **AST** (public API) + **Call Graph** (reachability).
-   **"Show me the data flow from `request.body` to `database.save` only within the `Payment` module."**
    -   *Layers:* **PDG** (data flow) + **AST** (module boundary constraints).
-   **"Refactor: Renaming `User.name` to `User.fullName`."**
    -   *Layers:* **AST** (declarations and accessors) + **PDG** (ensure logic isn't broken by semantic changes).
