# PRD: Universal Abstract Syntax Tree (UAST) Service

## 1. Executive Summary
**Objective:** Create a dedicated service that normalizes language-specific Abstract Syntax Trees (initially Python via Tree-sitter) into a **Universal AST (UAST)**. This layer is the "Rosetta Stone" of WYRD, enabling the graph database (FalkorDB) to store a clean, queryable, and language-agnostic representation of code.

**Scope:**
1.  Defining the **UAST Schema** (Nodes & Edges).
2.  Implementing the **Normalization Logic** (mapping Python CST nodes -> UAST nodes).
3.  Preparing the data for efficient **FalkorDB Ingestion**.

**Success Criteria:**
*   A Python function definition and a (future) JavaScript function definition both map to the same `Function` node type in FalkorDB.
*   Graph queries for "Find all functions" return results from all supported languages.
*   The graph is "Clean": No noise from syntax-only tokens (e.g., colons, parentheses, whitespace) unless they hold semantic value.

---

## 2. The UAST Schema (Graph Model)

The UAST is a **property graph**. Its goal is to be **semantic-first**, not syntax-first.

### 2.1 Universal Nodes (Entities)
These are the "nouns" of our code graph.

| UAST Node Type | Description | Key Properties |
| :--- | :--- | :--- |
| `Repository` | Represents a source repository. | `name`, `url`, `commit_hash` |
| `Branch` | Represents a repository branch. | `name`, `commit_hash` |
| `Directory` | Represents a source directory. | `name`, `path` |
| `File` | Represents a source file. | `path`, `language`, `hash` (for change detection) |
| `Module` | A logical grouping of code (package/namespace). | `name` (dotted path, e.g., `os.path`) |
| `Class` | A class definition. | `name`, `docstring`, `is_abstract` |
| `Function` | A function or method definition. | `name`, `signature`, `docstring`, `is_async`, `is_static` |
| `Variable` | A variable declaration or parameter. | `name`, `type_hint`, `default_value` |
| `Call` | An invocation of a function/method. | `dispatch_type` (static/dynamic - inferred) |
| `Block` | A scope container (e.g., loop body, if-block). | `type` (loop, condition, try) |
| `Import` | An external dependency. | `module`, `alias` |
| `Literal` | Hardcoded semantic values (strings, numbers). | `value`, `kind` (string, int) |

### 2.2 Universal Edges (Relationships)
These are the "verbs" linking the nouns. We use a **Kythe-aligned** edge vocabulary where possible.

| Edge Label | Source -> Target | Description |
| :--- | :--- | :--- |
| `CONTAINS` | `Class` -> `Method` | Structural parent/child relationship (The "Skeleton"). |
| `DEFINES` | `File` -> `Class` | Where an entity is defined. |
| `CALLS` | `Function` -> `Function` | Caller invokes Callee. |
| `IMPORTS` | `File` -> `Module` | Dependency linkage. |
| `INHERITS` | `Class` -> `Class` | Inheritance hierarchy. |
| `READS` | `Function` -> `Variable` | Variable usage. |
| `WRITES` | `Function` -> `Variable` | Variable assignment/mutation. |
| `TYPE` | `Variable` -> `Class` | Type annotation linkage (e.g., `x: User`). |

---

## 3. Normalization Logic (Python Adapter)

The service acts as an **Adapter Pattern**, translating Tree-sitter's Concrete Syntax Tree (CST) into our UAST.

### 3.1 Input vs. Output
*   **Input**: `tree_sitter.Tree` (Raw, noisy, language-specific).
    *   *Example*: `FunctionDef(name="foo", body=[...], decorator_list=[...])`
*   **Output**: List of `UASTNode` and `UASTEdge` objects (Clean, generic).
    *   *Example*: `Node(type="Function", name="foo", id="...")`

### 3.2 Mapping Rules (The "Brain")

#### A. Functions
*   **Tree-sitter**: `function_definition`
*   **UAST**: `Function` node.
*   **Logic**:
    *   Extract `name` node -> `Function.name`.
    *   Extract parameters -> `Variable` nodes + `CONTAINS` edges.
    *   Analyze decorators -> If `@staticmethod`, set `is_static=True`.
    *   Analyze `async def` -> Set `is_async=True`.

#### B. Classes
*   **Tree-sitter**: `class_definition`
*   **UAST**: `Class` node.
*   **Logic**:
    *   Extract base classes -> Create `INHERITS` placeholders (edges to be resolved later).

#### C. Calls
*   **Tree-sitter**: `call`
*   **UAST**: `Call` node.
*   **Logic**:
    *   This is critical for "Call Graphs".
    *   Capture the *callee* name.
    *   *Challenge*: Initial UAST only knows the **name** (e.g., `my_func`). The **Linker** (separate service) resolves this name to the actual `Function` node ID later.
    *   Create a `REFERS_TO` edge from the Call node to a "Symbol" placeholder.

#### D. Imports
*   **Tree-sitter**: `import_statement`, `import_from_statement`
*   **UAST**: `Import` node.
*   **Logic**:
    *   `import os` -> `Import(module="os")`.
    *   `from math import sqrt` -> `Import(module="math", artifact="sqrt")`.

---

## 4. Architecture & Data Flow

### 4.1 Component Diagram
```mermaid
graph TD
    Client[LSP Server] -->|DidSave(code)| Parser[Tree-sitter Parser]
    Parser -->|CST| Normalizer[UAST Service]
    Normalizer -->|UAST Nodes/Edges| Ingester[FalkorDB Ingester]
    Ingester -->|Cypher Queries| DB[(FalkorDB)]
```

### 4.2 The `UASTBuilder` Class
We will implement a Builder pattern to traverse the CST and construct the graph.

```python
class UASTBuilder:
    def build(self, cst_root, source_code) -> GraphPayload:
        """
        Main entry point.
        1. Traverses CST recursively.
        2. Applies specific handlers for node types.
        3. Returns a distinct list of Nodes and Edges.
        """
        pass

    def handle_function_definition(self, node):
        # Create Function Node
        # Recurse into body
        pass

    def handle_call(self, node):
        # Create Call Node
        pass
```

### 4.3 Unique Identifier Strategy (VNames)
To ensure the graph can be updated incrementally (idempotency), every node needs a deterministic ID based on its location and content.

*   `Schema`: `file_path:semantic_path`
*   `Example`: `src/main.py:UserClass:get_user_method`
*   **Fallback**: If a semantic path is hard (e.g., inside a loop), use `file_path:start_byte`.

---

## 5. Implementation Roadmap

### Phase 1: Skeleton
1.  [ ] Define the Pydantic models for `UASTNode` and `UASTEdge`.
2.  [ ] Implement `UASTBuilder` with a simple "Pass-through" for unknown nodes (to avoid crashing on unhandled syntax).

### Phase 2: Core Entities
1.  [ ] Implement `handle_function_definition` (Name, Args, Docstring).
2.  [ ] Implement `handle_class_definition` (Name, Bases).
3.  [ ] Implement `handle_import` (Module resolution logic).

### Phase 3: The Call Graph
1.  [ ] Implement `handle_call`.
2.  [ ] Strategy for "Symbol Resolution" (linking a call `foo()` to the function `def foo()`).
    *   *Initial approach*: String matching within the same file.
    *   *Advanced approach*: Scope-aware resolution.

---

## 6. Integration with FalkorDB
The UAST Service outputs clear data structures. The **Ingestion Layer** (Consumer) translates these into Cypher queries.

**Example Cypher Output:**
```cypher
MERGE (f:File {path: "main.py"})
MERGE (func:Function {id: "main.py:foo", name: "foo"})
MERGE (f)-[:DEFINES]->(func)
```

## 7. Open Questions / Risks
*   **Expression Complexity**: Python expressions can be deeply nested (`a.b().c[0]`). Mapping fully granular expression trees might bloat the graph.
    *   *Mitigation*: Only map "Significant" expressions (Calls, property access, assignments) initially. Ignore binary operators (`+`, `-`) unless needed for data flow analysis.
*   **Dynamic Typing**: Python variable types are often unknown until runtime.
    *   *Mitigation*: Use `UNKNOWN` type or extract type hints (`a: int`) where available.