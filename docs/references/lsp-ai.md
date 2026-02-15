# LSP-AI

## Overview
**LSP-AI** is an open-source language server that acts as a backend for AI features (completions, chat), abstracting specific LLM APIs.

## Source
https://github.com/SilasMarvin/lsp-ai

## Relevance to WYRD
LSP-AI represents the "Consumer" side of the equation, while WYRD is the "Provider."

### 1. Semantic Context
*   **Problem:** LLMs have small context windows. They need relevant context.
*   **LSP-AI Approach:** Use LSP features (Go to Definition) to fetch context.
*   **WYRD Synergy:** WYRD can provide **Super-Context**. Instead of just "the file definition," WYRD can provide "The 2-hop dependency subgraph" or "The data flow slice."
*   **Integration:** WYRD could expose a custom LSP method `textDocument/contextGraph` that tools like LSP-AI consumption could use to ground their LLM prompts in reality, reducing hallucinations.

### 2. Bridge Architecture
*   LSP-AI bridges multiple editors to multiple LLMs.
*   WYRD bridges multiple languages to a single Graph DB.
*   Both share the philosophy of "N-to-1" adapters to solve the matrix explosion problem of tooling.

## Key Takeaway
*   **Future Feature:** "Context Export." WYRD should make it easy to dump a subgraph as a Markdown/Mermaid snippet. This allows the user (or an agent like LSP-AI) to paste the *structure* of the code into an LLM prompt.
