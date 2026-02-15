# SWE-Master

## Overview
**SWE-Master** is an agent framework that uses LSP for "Structural Exploration" to solve coding tasks. It moves beyond "grep" interactions to "symbolic" interactions.

## Source
https://github.com/RUCAIBox/SWE-Master

## Relevance to WYRD
SWE-Master is the "Power User" persona for WYRD.

### 1. Verification of Graph Value
*   SWE-Master demonstrates that **Structural Exploration** (Call Hierarchy, Type Definitions) is critical for solving complex tasks.
*   **Current Limit:** Standard LSPs are often slow or single-file limited.
*   **WYRD's Value:** WYRD's FalkorDB backend allows *instant* global queries. "Find all classes that implement interface I" is a costly operation in standard LSPs (requires scanning all files). In WYRD/FalkorDB, it is a millisecond index lookup.
*   **Conclusion:** WYRD enables frameworks like SWE-Master to run faster and with broader scope.

### 2. Structure-Aware Editing
*   SWE-Master agents try to understand the "Public Contract" of a module.
*   WYRD's PDG (Program Dependence Graph) explicitly maps these contracts. WYRD can visualize "What depends on this function?" immediately, giving the agent (or human) the confidence to refactor.

## Key Takeaway
*   **Validation:** The existence of SWE-Master validates WYRD's core hypothesis: **Structure > Text**. Treating code as a graph is the future of automated engineering.