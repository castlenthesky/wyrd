# Source Atlas

## Overview
**Source Atlas** is a multi-language code analyzer that builds "Knowledge Graphs" of code. It acts as a reference implementation for the **Tree-sitter + Graph DB** architecture.

## Architectual Parallels with WYRD
Source Atlas is arguably the closest existing open-source project to WYRD's architectural goals.

## Source
https://github.com/lis186/SourceAtlas

### 1. The "Tree-sitter -> Graph" Pipeline
*   **Implementation:** Source Atlas parses code with Tree-sitter and directly creates nodes in Neo4j.
*   **Relevance:** WYRD follows this exact path but swaps Neo4j for FalkorDB (for performance/Redis protocol) and emphasizes the LSP/VS Code integration more heavily. Examining Source Atlas's mapping logic (how they map a Tree-sitter `class_declaration` to a Graph Node) can save significant R&D time.

### 2. High-Level "Intelligence" Features
*   **Concept:** Source Atlas sells "Architectural Overviews" and "Impact Analysis."
*   **Relevance:** These are the end-user features WYRD wants to sell inside VS Code.
    *   **Impact Analysis:** "If I touch this interface, what breaks?" -> This is a PDG traversal.
    *   **Architectural Overview:** "Show me the relationship between the `Auth` module and the `User` module." -> This is a Coarse-Grained Graph query (collapsing function edges into module edges).

### 3. Information Theory Scanning
*   **Concept:** Source Atlas claims to scan <5% of files to get 80% understanding.
*   **Relevance:** While WYRD aims for 100% precision (via parsing every file on save), this heuristic approach is interesting for the *initial* indexing of a massive repository. Maybe we don't need to parse function bodies of `node_modules` dependencies, just their signatures.

## Takeaways
*   **Reference:** Look at Source Atlas's query structure for "Impact Analysis" to adapt for FalkorDB/Cypher.
*   **Feature Parity:** "Architectural Overview" is a strong candidate for a Webview visualization in WYRD.
