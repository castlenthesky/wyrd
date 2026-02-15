# Kythe

## Overview
**Kythe** is a Google-led open-source standard for code indexing. It provides a **schema** and **interchange format** for code graphs.

## Source
https://github.com/kythe/kythe

## Why Kythe for CPG?
Kythe is not a database (like FalkorDB) but a *specification* for how to represent code knowledge. It is the "Gold Standard" for semantic edges.

### 1. The Schema (Semantic Edges)
*   **Concept:** Kythe defines a rigorous vocabulary for edges.
*   **Relevance:** WYRD should adopt standard edge names where possible to avoid reinventing the wheel.
    *   `edge/generates`: A macro expansion.
    *   `edge/defines/binding`: A declaration of a variable.
    *   `edge/refers/to`: A usage of a variable.
    *   `edge/overrides`: A method overriding a parent class.
    *   `edge/param`: Linking a function to its parameters.

### 2. Language-Agnosticism
*   **Concept:** Kythe abstractly defines "Anchors" (ranges of text) and "Semantic Nodes" (the mental model of the code).
*   **Relevance:** This distinction is crucial for WYRD.
    *   **Anchor:** `start_line: 10, end_line: 10, content: "foo"` (Stored in AST layer).
    *   **Semantic Node:** `Function: foo` (Stored in CPG layer).
    *   **Edge:** `(Anchor)-[:DEFINES]->(SemanticNode)`.
    *   This allows the "Go to Definition" feature to work: Find the Anchor under cursor -> Follow `[:DEFINES]` edge -> Get Semantic Node.

### 3. VNames (Vector Names)
*   **Concept:** A robust way to uniquely identify a node globally: `{corpus, root, path, signature, language}`.
*   **Relevance:** WYRD needs a Primary Key strategy for FalkorDB nodes. Adopting a simplified VName strategy (e.g., `file_path::function_signature`) ensures that we can deterministically find a node to update it without creating duplicates.

## Integration Strategy
*   **Schema Adoption:** Use Kythe's edge types (`refers/to`, `defines`, `calls`) as the edge labels in FalkorDBQuery (`[:REFERS_TO]`, `[:DEFINES]`, `[:CALLS]`).
*   **Identity:** Implement a VName-like hash generation for every Universal Node to ensure idempotency during incremental updates.