# PRD: Python AST to Kythe-Compliant Service

## 1. Executive Summary
**Objective:** Build a robust Python source code analysis service that extracts semantic information and stores it as a generic code property graph (CPG) in FalkorDB.
**Standard:** Align strictly with the [Kythe Scheme](https://kythe.io/docs/schema/) for semantic nodes and edges to ensure language-agnosticism and future compatibility.
**Current State:** Existing `parser.py` uses `tree-sitter` but emits generic `Node` types and simple `PARENT` edges.
**Target State:** A `KytheTransformer` that emits strongly-typed Semantic Nodes (`function`, `record`, `variable`) and Semantic Edges (`defines`, `refers/to`, `calls`).

## 2. Standards Alignment

We will adopt the following Kythe standards for our Graph Schema:

### 2.1 Nodes (Semantic Objects)
| Kythe Node Kind | Python Equivalent | Description |
| :--- | :--- | :--- |
| `record` | `class` | Use for Class definitions. |
| `function` | `def`, `lambda` | Use for Function definitions. |
| `variable` | `variable`, `parameter` | Use for arguments and variable assignments. |
| `file` | `module` | The top-level file node. |
| `anchor` | `Text Range` | A spanning region of text in the source file. |

### 2.2 Edges (Relationships)
| Kythe Edge Kind | Description | Usage Example |
| :--- | :--- | :--- |
| `defines/binding` | Binds an Anchor to a Semantic Node. | `(Anchor: "def foo") -[defines/binding]-> (Function: foo)` |
| `refers/to` | Links a usage Anchor to a Semantic Node. | `(Anchor: "foo()") -[refers/to]-> (Function: foo)` |
| `childof` | Structural containment. | `(Function: foo) -[childof]-> (Class: Bar)` |
| `generates` | Macro expansion (decorators). | `(Decorator) -[generates]-> (FunctionWrapper)` |
| `param` | Function parameters. | `(Function: foo) -[param.0]-> (Variable: arg1)` |
| `depends/on` | File-level dependency (import). | `(File: A.py) -[depends/on]-> (File: B.py)` |

### 2.3 Universal AST (UAST) *[New]*
To align with **CodePrism** concepts, we will normalize nodes to a generic schema:
*   Instead of `PythonFunction`, use `Function` with property `language: "python"`.
*   Establish **Polyglot Edges**: `(:Function {lang: "py"}) -[:CALLS]-> (:Function {lang: "rust"})`.


## 3. Architecture

### 3.1 Components
1.  **Parser (Input)**: Leverage existing `tree-sitter-python` integration in `server/src/server/parser.py`.
2.  **UAST Normalizer (Transformation)**: *[Inspired by CodePrism]*
    *   Convert language-specific Tree-sitter nodes (`FunctionDef`, `ClassDef`) into a generic **Universal AST (UAST)**.
    *   **Why?** Decouples the Graph Schema from Python specifics, enabling multi-language support (JS/TS in future) without schema migration.
    *   **Node types**: `uast.Function`, `uast.Class`, `uast.Variable`, `uast.Import`.
3.  **Kythe Emitter (Graph Generation)**:
    *   **Input**: UAST Nodes.
    *   **Logic**:
        *   **Pass 1 (Declarations)**: Walk UAST to identify `defines` and generate VNames.
        *   **Pass 2 (Scopes)**: Build a local symbol table.
        *   **Pass 3 (References)**: Resolution and Linking.
    *   **Output**: Semantic Nodes and Edges for FalkorDB.
4.  **Incremental Indexer (Update Strategy)**: *[Inspired by Source Atlas/CodePrism]*
    *   **Dirty Set Tracking**: Only re-index files that have changed since the last graph update.
    *   **Impact Analysis (Future)**: Usage graph traversal to invalidate dependent nodes in other files.
5.  **Storage (Output)**: FalkorDB (RedisGraph).

### 3.2 VName Strategy (Identity)
To ensure idempotency in the graph, we need deterministic IDs (VNames).
*   **Format**: `signature#corpus#root#path#language`
*   **Signature Generation**:
    *   Files: `path/to/file.py`
    *   Functions: `path/to/file.py:ClassName:FunctionName`
    *   Variables: `path/to/file.py:ClassName:FunctionName:varName@startOffset` (Variables are harder to uniquely identify without full offset or scope index).

## 4. Delivery Plan

### Phase 1: Foundation (Definitions & Hierarchy)
**Goal**: Accurately index all definitions (Classes/Functions) using UAST normalization.
*   [ ] Refactor `parser.py` to separate AST walking from Graph generation.
*   [ ] Implement **UAST Normalizer** for Python.
    *   Map `FunctionDef` -> `uast.Function`.
    *   Map `ClassDef` -> `uast.Class`.
*   [ ] Implement `defines/binding` and `childof` edges using UAST specifics.
*   [ ] Update `docs/references/kythe.md` with VName strategy.

### Phase 2: Incremental Indexing & Variables
**Goal**: Performance optimization and detailed variable tracking.
*   [ ] Implement **Dirty Set** logic: Only parse changed files on `textDocument/didSave`.
*   [ ] Maintain a separate lookup for "Files defined in Graph" to compare against disk state.
*   [ ] Handle `parameters` and `variables` in the UAST.


### Phase 3: References & Call Graph (Local)
**Goal**: Enable "Find Usages" and "Go to Definition" within a single file.
*   [ ] Implement a simple Scope Manager (Stack of Scopes).
*   [ ] Track variable declarations in the Scope Manager.
*   [ ] Resolve simple identifier usages to the active Scope.
*   [ ] Emit `refers/to` edges for resolved references.
*   [ ] Emit `call` edges (derived from `refers/to` on CallExpressions).

### Phase 4: Cross-File Resolution (Imports)
**Goal**: Link references across files.
*   [ ] index `import` statements.
*   [ ] Resolve imported names to their source files (requires mapping import paths to file VNames).

## 5. Technology Stack
*   **Language**: Python 3.11+
*   **Parsing**: `tree-sitter`, `tree-sitter-python`
*   **Database**: FalkorDB
