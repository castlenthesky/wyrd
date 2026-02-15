# Multilspy

## Overview
**Multilspy** is a Python library from Microsoft Research that wraps LSP clients, making it easy to script static analysis tasks across languages.

## Source
https://github.com/microsoft/multilspy

## Relevance to WYRD
Multilspy is a **Client Implementation Reference**.

### 1. Testing Framework
*   **Use Case:** WYRD is building a Server. To test it, we need a Client.
*   **Strategy:** Instead of launching VS Code to test WYRD manually, we can use `multilspy` (or a similar Python LSP client library) to write **Integration Tests**.
    *   Test: `client.open_file('main.py')` -> `client.request_definition(pos)` -> Assert response matches FalkorDB state.

### 2. The "Unified Interface" Goal
*   Multilspy tries to hide the differences between `pylance` and `jdtls`.
*   WYRD tries to hide the differences between `Python` and `Java` *data*.
*   They converge on the same goal: Polyglot abstraction. Multilspy abstracts the *Tool*, WYRD abstracts the *Data*.

## Key Takeaway
*   **Action Item:** Use a Python-based LSP client wrapper for the WYRD CI/CD pipeline to verify the server handles requests correctly without a UI.