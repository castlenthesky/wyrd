# Control Flow Graph (CFG)

A **Control Flow Graph (CFG)** is a representation, using graph notation, of all paths that might be traversed through a program during its execution.

## Definition
In a CFG, each node in the graph represents a basic block, i.e., a straight-line piece of code without any jumps or jump targets; jump targets start a block, and jumps end a block. Directed edges are used to represent jumps in the control flow.

## Key Components

### Basic Blocks (Nodes)
A sequence of instructions where:
-   Control enters only at the beginning of the sequence.
-   Control leaves only at the end of the sequence.
-   If one instruction is executed, all are executed.

### Edges
Directed edges represent the transfer of control:
-   **Unconditional Edge**: Control always flows from Block A to Block B (e.g., sequential statements).
-   **Conditional Edge**: Control flows to Block B if a condition is true, and Block C if false (e.g., `if`, `while`, `switch`).

### Special Nodes
-   **Entry Node**: Where control enters the function/method.
-   **Exit Node**: Where control leaves the function/method (e.g., `return`, `throw`).

## Example Use Cases
1.  **Reachability Analysis**: Determining if a piece of code can ever be executed (Dead Code Elimination).
2.  **Loop Optimization**: Identifying loops to move invariant code out of the loop body.
3.  **Cyclomatic Complexity**: Calculating the number of linearly independent paths through a program's source code.

## Practical Queries (CFG)
*Use the CFG when you have questions about execution paths, reachability, or complexity.*

-   **"Is this error handling block ever reachable?"**
    -   *Why CFG:* It models all possible paths; if no edge leads to the block, it's dead code.
-   **"Can this function return `null`?"**
    -   *Why CFG:* You can trace all paths to the Exit Node and check the return values.
-   **"What is the cyclomatic complexity of this method?"**
    -   *Why CFG:* It provides the exact number of edges and nodes needed for the calculation ($E - N + 2$).
-   **"Is there a path where the resource is not closed?"**
    -   *Why CFG:* You can search for a path from `open()` to `Exit` that does not pass through `close()`.
-   **"Which functions invoke `my_function`?"** (Call Graph, often derived from CFG + AST)
    -   *Why CFG:* It models the call sites as transfer of control.