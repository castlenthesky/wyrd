# Abstract Syntax Tree (AST)

An **Abstract Syntax Tree (AST)** is a tree representation of the abstract syntactic structure of source code written in a programming language. Each node of the tree denotes a construct occurring in the source code.

## Definition
The syntax is "abstract" because it does not represent every detail appearing in the real syntax, but rather just the structural, content-related details. For instance, grouping parentheses are implicit in the tree structure, and a syntactic construct like an `if-condition-then` expression usage may be denoted by a single node with three branches.

## Key Components

### Nodes
-   **Root Node**: Represents the entire program or file.
-   **Internal Nodes**: Represent operators, statements, or control structures (e.g., `IfStatement`, `ForLoop`, `BinaryExpression`).
-   **Leaf Nodes**: Represent operands or atomic values (e.g., `Identifier` "x", `IntegerLiteral` "42").
-   **Import/Package Nodes**: Represents the file's context (e.g., `ImportDeclaration`, `PackageDeclaration`). These are crucial for linking code across files.

### Abstraction
-   **Punctuation**: Semicolons, braces, and parentheses are usually omitted as the tree structure inherently defines grouping and scope.
-   **Comments & Whitespace**: Typically discarded unless the AST is intended for refactoring tools that need to preserve formatting (c.f. Concrete Syntax Tree vs Abstract Syntax Tree).

### Semantic Enrichment
While a pure AST is syntactic, in the context of a CPG, AST nodes are often enriched with semantic information:
-   **Type Information**: e.g., variable `x` is an `int`.
-   **Scope**: Which variables are visible in this block.
-   **Declaration Links**: Linking a usage of `x` back to where `x` was defined.

## Example Use Cases
1.  **Compilers**: To generate intermediate code and optimize program structure.
2.  **Linters/Static Analysis**: To check for patterns (e.g., "unused variable", "infinite loop").
3.  **Refactoring Tools**: To safely rename variables or extract methods by understanding the code's structure rather than just text.

## Practical Queries (AST)
*Use the AST when you have questions about the static structure, hierarchy, or composition of the code.*

-   **"Where is `MyClass` defined?"**
    -   *Why AST:* It maps the file structure to class definitions.
-   **"Does the API layer import from the DB layer?"**
    -   *Why AST:* It holds the `ImportDeclaration` nodes to check for forbidden dependencies.
-   **"List all public methods in `UserController`."**
    -   *Why AST:* It contains the `MethodDeclaration` nodes and their access modifiers.
-   **"Which classes inherit from `BaseService`?"**
    -   *Why AST:* It captures the inheritance syntax (`class A extends B`).
-   **"Find all string literals that match this regex."**
    -   *Why AST:* It distinguishes string literals from variable names or comments.