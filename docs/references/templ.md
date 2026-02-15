# Templ (LSP Proxy Architecture)

## Overview
**Templ** is a Go library for HTML templating. Its LSP implementation is a **Proxy**: it sits between the editor and two other LSPs (`gopls` and an HTML LSP).

## Source
https://github.com/a-h/templ
https://deepwiki.com/a-h/templ/5.1-ide-support

## Relevance to WYRD
This is a critical architectural pattern for WYRD: **The Middleman Server**.

### 1. The Proxy Pattern
*   **Problem:** WYRD wants to provide Graph insights, but the user still needs standard features (Autosuggest, Linting) which are provided by the language's native LSP (e.g., `Pyright` or `TypeScript Server`).
*   **Solution (The Templ Way):**
    *   VS Code talks to WYRD LSP.
    *   WYRD LSP talks to FalkorDB (for Graph stuff).
    *   WYRD LSP *proxies* specific requests (like `textDocument/completion`) to the underlying Native LSP (`Pyright`).
*   **Benefit:** The user doesn't need to run two separate extensions that fight over the file. They run WYRD, and WYRD orchestrates the "Standard" features alongside the "Graph" features.

### 2. Multi-Language Files
*   Templ handles files with mixed Go/HTML.
*   WYRD handles "Projects" with mixed languages.
*   The logic of delegating "Zone A is Go, Zone B is HTML" is analogous to WYRD delegating "query X is for Pyright, query Y is for FalkorDB".

## Key Takeaway
*   **Architecture Decision:** Should WYRD be a "Sidecar" (running alongside Pyright) or a "Proxy" (wrapping Pyright)?
    *   *Sidecar:* Easier to build. VS Code supports multiple LSPs per file.
    *   *Proxy:* More control, but much harder to maintain.
    *   *Conclusion:* Start as **Sidecar** (VS Code Native), but keep the Proxy pattern in mind if we need to intercept/modify native behaviors.