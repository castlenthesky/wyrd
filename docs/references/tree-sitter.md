# Tree-sitter

## Overview
**Tree-sitter** is a parser generator tool and an incremental parsing library. It builds a concrete syntax tree (CST) for a source file and efficiently updates it as the user edits the file.

## Source
https://github.com/tree-sitter/tree-sitter
https://tree-sitter.github.io/tree-sitter/

## Why Tree-sitter for CPG?
For a tool like WYRD that sits inside an IDE, standard compiler parsers (like Python's `ast` module or `javac`) are insufficient because they typically require valid code and re-parse the entire file.

### 1. Incremental Parsing
*   **Mechanism:** When a user types a character, Tree-sitter does not re-parse the file. It patches the existing tree.
*   **Relevance:**
    *   **Performance:** Parsing happens in milliseconds, even for large files.
    *   **Graph Updates:** Because we know exactly *which* nodes changed, we can calculate a "Graph Delta." Instead of wiping the implementation of a function in FalkorDB and rewriting it, we can detect that only one `IfStatement` was added and send a targeted `UPSERT` to the database.

### 2. Error Tolerance
*   **Mechanism:** Tree-sitter is designed for code that is "in-progress." It can produce a valid syntax tree even if the code has missing semicolons or unmatched braces.
*   **Relevance:** A CPG that only works on compilable code is useless in an IDE (where code is broken 99% of the time while typing). Tree-sitter allows WYRD to provide graph insights *while* the user is fixing a bug.

### 3. Query API (S-Expressions)
*   **Mechanism:** Tree-sitter provides a Lisp-like query language to match patterns in the tree.
*   **Relevance:** This is the primary mechanism for extraction. We can write queries to extract the nodes we care about for the CPG:
    ```scm
    ; Example: Extract all function definitions and their names
    (function_definition
      name: (identifier) @func.name
      parameters: (parameters) @func.params
    ) @func.def
    ```
    This abstracts away the manual traversal logic.

### 4. Multi-Language Support
*   **Mechanism:** Tree-sitter has grammars for almost every major language.
*   **Relevance:** Using Tree-sitter decouples the *Parsing* logic from the *Analysis* logic. The "Universal AST" (UAST) adapter for WYRD simply translates Tree-sitter nodes (which share a common structure) into FalkorDB nodes.

## Integration Strategy
1.  **Ingestion:** On `textDocument/didSave` (or debounced `didChange`), the LSP server feeds the text to Tree-sitter.
2.  **Extraction:** Run Tree-sitter queries to identify key structures (Classes, Functions, Calls).
3.  **Normalization:** Map specific Tree-sitter types (e.g., `impl_item` in Rust, `MethodDefinition` in JS) to `UniversalMethod`.
4.  **Persistance:** Push the normalized nodes to FalkorDB.
