# CodePrism

## Overview
**CodePrism** is an architectural reference for WYRD, specifically for its **Universal AST (UAST)** and **Incremental Indexing** capabilities. It demonstrates how to decouple code analysis from specific languages.

## Source
https://github.com/codeprisim/codeprisim

## Key Architectures for WYRD

### 1. Universal AST (UAST)
*   **Concept:** CodePrism does not store Python ASTs or JavaScript ASTs directly. It converts them into a normalized schema.
*   **Relevance:**
    *   **Polyglot Edges:** By normalizing `FunctionDef` (Python) and `FunctionDeclaration` (TS) to a generic `:Function` node, WYRD can create edges like `(:Function)-[:CALLS]->(:Function)` regardless of whether the caller is Python and the callee is Rust.
    *   **Simplifies Queries:** You don't need `MATCH (n:PythonFunction | TSFunction | JavaMethod)`. You just `MATCH (n:Function)`.

### 2. Relationship-First Design
*   **Concept:** CodePrism prioritizes *edges* (relationships) over *nodes* (code structure).
*   **Relevance:** WYRD's primary value constraint is "What connects to what?" not "What does this specific line of code look like?". The CPG schema should be optimized for traversing edges (`[:DEPENDS_ON]`, `[:IMPORTS]`) rather than perfectly reconstructing the source code text.

### 3. Bidirectional Dependency Graph (Incremental Indexing)
*   **Concept:** CodePrism maintains a graph of which files depend on which symbols.
*   **Mechanism:** When File A changes, CodePrism checks the dependency graph. "Who imports File A?" -> File B. "Does File B use the changed symbol?" -> No. -> Stop.
*   **Relevance:** This $O(k)$ update complexity (where $k$ is the number of affected nodes) is the target performance metric for WYRD's "Parse on Save" strategy. Without this, re-indexing a large repo on every save is too slow.

## Takeaways for WYRD Implementation
*   **Schema:** Adopting a UAST is mandatory for the multi-language goals.
*   **Indexing:** We must implement a "Dirty Set" logic. When `didSave` fires, calculate the diff, identify changed symbols, and only update the subgraph connected to those symbols.