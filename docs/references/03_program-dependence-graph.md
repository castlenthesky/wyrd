# Program Dependence Graph (PDG)

A **Program Dependence Graph (PDG)** is a graph representation that explicitly represents both the data and control dependencies for each operation in a program.

## Definition
Unlike the CFG, which models the *order* of execution, the PDG models the *necessary relationships* between statements. If Statement B depends on Statement A, then A must execute before B (or affect B), regardless of whether there are 5 or 50 irrelevant lines of code between them.

## Key Components

### Nodes
Nodes typically represent statements, predicate expressions, or operations, similar to the nodes in a CFG or enriched AST nodes.

### Edges

#### 1. Data Dependency Edges
Provide a link from the definition of a variable to its use.
-   **Flow Dependence (True Dependence)**: Statement A writes a variable `x` that is later read by Statement B.
-   **Anti-Dependence**: Statement A reads `x` then Statement B writes `x`.
-   **Output Dependence**: Statement A writes `x` then Statement B writes `x`.

#### 2. Control Dependency Edges
Provide a link from a predicate (condition) to the statements whose execution depends on the value of that predicate.
-   Example: In `if (x > 0) { y = 1; }`, the statement `y = 1` is control-dependent on the evaluation of `x > 0`.

## Example Use Cases
1.  **Program Slicing**: Finding all statements that affect the value of a specific variable at a specific point (e.g., "Which lines of code contributed to this bug?").
2.  **Parallelization**: If two sets of statements have no data or control dependencies between them, they can safely be executed in parallel.
3.  **Code Optimization**: Instruction scheduling and code motion.

## Practical Queries (PDG)
*Use the PDG when you have questions about data flow, impact analysis, or the ripple effects of changes.*

-   **"If I update `my_method()`, which downstream code is affected?"**
    -   *Why PDG:* It traces specific data dependencies (outputs of your method) to their consumers.
-   **"Can user input flow into this SQL query?" (Taint Analysis)**
    -   *Why PDG:* It connects the source (input) to the sink (query) via data dependency edges.
-   **"Where did this `null` value originate?"**
    -   *Why PDG:* You can traverse backwards along data dependency edges to find the origin of the variable.
-   **"Which statements contribute to the calculation of `final_price`?" (Slicing)**
    -   *Why PDG:* A backward slice from `final_price` reveals every statement that mathematically or conditionally affected it.
-   **"Can these two loops run in parallel?"**
    -   *Why PDG:* If there are no data dependence edges between the loops, they are independent.