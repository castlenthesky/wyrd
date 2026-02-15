# Lanser-CLI

## Overview
**Lanser-CLI** is a "CLI-first bridge" that exposes Language Server capabilities to AI agents. It acts as an orchestration layer, turning the ephemeral state of an LSP into deterministic, replayable artifacts.

## Relevance to WYRD
WYRD aims to be a tool for *humans* (VS Code extension), but its architecture (LSP + Graph) makes it an ideal backend for *agents* (like Lanser-CLI customers).

## Source
https://github.com/yifanzhang-pro/lanser-cli
https://yifanzhang-pro.github.io/lanser-cli/
https://huggingface.co/blog/yifAI/lanser-cli

### 1. Robust Selectors
*   **Concept:** Agents struggle with line numbers (which change after edits). Lanser-CLI uses "Robust Selectors" (likely AST paths or symbol names) to target edits.
*   **WYRD Synergy:** WYRD's FalkorDB graph uses **Universal IDs** (e.g., `pkg:src/main.py::function:foo`). If WYRD exposes these IDs via LSP, it gives agents a perfect "Robust Selector" system for free. An agent could say "Refactor node `0x123`" instead of "Refactor line 42".

### 2. The Use Case for "Graph-as-a-Service"
*   Lanser-CLI proves there is a market for "Headless LSP."
*   WYRD's "Analysis Engine" is effectively a "Headless Graph Server." By adhering to standard protocols (LSP), WYRD could theoretically be driven by Lanser-CLI, allowing an AI agent to "query the graph" to understand the potential impact of a change before making it.

## Key Takeaway
*   **Design Pattern:** WYRD should ensure its LSP methods are not *strictly* tied to the VS Code UI. If `wyrd/getCallers` returns a clean JSON array of node IDs, it becomes a tool for AI agents, not just a UI populate-r.