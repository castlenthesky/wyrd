### Research Summary on Normalized ASTs, Universal Representations, and Industry Standards

Your goal of building a language-agnostic "Universal Abstract Symbol Tree" (UAST) using Tree-sitter's Concrete Syntax Tree (CST) aligns closely with emerging practices in code analysis tools. By starting with Python, you can prototype a normalized graph representation that abstracts syntactic details (e.g., indentation in Python vs. braces in Java) into shared semantic nodes and edges, enabling queries like "find all function calls to external modules" across files or (eventually) languages. This supports VS Code integration via LSP for features like "go to definition" or AI agent context (e.g., feeding graph traversals to models for code explanation).

I conducted deep research using web searches and targeted page browsing on key projects (CodePrism, Source Atlas, Kythe) and related standards/projects (e.g., Joern's CPG, MLCPD's UAST, Stackwalk). Note: The provided links for CodePrism (`https://github.com/codeprisim/codeprisim`) and Source Atlas (`https://github.com/lis186/SourceAtlas`) appear outdated or mismatched—CodePrism returned a 404 (possibly a placeholder or archived repo), and Source Atlas now focuses on AI slash commands rather than Tree-sitter graphs (per current content). I pivoted to analogous open-source projects like Joern, Stackwalk, and Fraunhofer's CPG library, which directly address your needs. Kythe's GitHub had limited README depth, but its schema docs and Python tools (e.g., pykythe) were extractable via searches.

#### Key Findings on Industry Standards
There is **no single rigid "industry standard"** for universal AST normalization, but a converging ecosystem around **Code Property Graphs (CPG)** as the gold standard for queryable, layered code representations. CPGs (pioneered by Fraunhofer and popularized by Joern) unify AST, CFG, and PDG into a property graph, making them ideal for your comprehension tool. Other protocols like Kythe provide edge vocabularies, while UAST schemas (e.g., from MLCPD) handle normalization.

| Standard/Protocol | Description | Language-Agnostic Normalization | Python Support | Applicability to Your Tool | Adoption Triggers |
|-------------------|-------------|---------------------------------|----------------|----------------------------|-------------------|
| **CPG (Joern Spec 1.1)** | Layered property graph merging AST (syntax), CFG (control flow), PDG (dependencies). Nodes have properties (e.g., `name`, `code`, `lineNumber`); edges are typed (e.g., `AST` for containment, `CALL` for invocations). | Abstracts lang-specific syntax to universal nodes (e.g., Python `def` → `METHOD` node). Frontends map parsers to shared schema; desugars constructs (e.g., Python lambdas to anonymous methods). | Full frontend; handles dynamic features like `DYNAMIC_DISPATCH`. | High: Use for your FalkorDB backend. Enables holistic queries (e.g., "data flow from input to DB"). | Implement early for graph queries; extend with overlays for semantics (e.g., type resolution). |
| **Kythe Schema** | Interchange format for code facts (anchors for text ranges, semantic nodes for concepts). Edges like `defines/binding` (declarations), `refers/to` (uses), `calls` (invocations). VNames (e.g., `{corpus:root:path:signature:language}`) for unique IDs. | Anchors tie to source text; semantic nodes normalize (e.g., Python var → generic `Variable`). Language-agnostic via extractors. | pykythe tool generates facts from Python AST; integrates with Tree-sitter via custom extractors. | Medium: Adopt edge names (e.g., `:REFERS_TO`) for interoperability. Use VNames to avoid duplicates in incremental updates. | When building cross-file links (e.g., imports); for "go to definition" in VS Code. |
| **UAST (MLCPD Schema)** | Unified AST from Tree-sitter CSTs across 10+ langs. 4 layers: metadata (file stats), flat nodes (linearized tree), categorization (decls/stmts/exprs), cross-lang map (e.g., Python `if` → universal `IfStatement`). | Maps CST named nodes to universal types via algorithms (e.g., recursive extraction + categorization). Preserves positions for fidelity. | Excellent; Python grammar yields high node density due to expr decomposition. | High: Directly usable for your Tree-sitter pipeline. Enables 99.99% parse success; scalable to Parquet for storage. | Core for normalization; adopt when scaling to multi-lang (start with Python mapping). |

- **When to Implement Standards**: 
  - **Early (Prototype Phase)**: Adopt CPG's node/edge schema for your normalized graph—it's mature, query-optimized (Cypher-compatible for FalkorDB), and handles Python's dynamism without over-abstraction (e.g., avoids inflating graphs like in JS prototypes).
  - **Mid-Phase (Semantics)**: Layer in Kythe edges for precise refs/calls; use UAST mapping for CST-to-universal conversion. This prevents reinventing wheels (e.g., Joern's auto-generated `CALL` edges from `METHOD_FULL_NAME` props).
  - **Late (Multi-Lang/Scale)**: Full UAST for agnosticism; benchmark against MLCPD's 7M-file dataset to validate your Python parser.
  - **Avoid Overkill**: Don't force full CPG (CFG/PDG) initially—start with AST layer, add dependencies later. Standards shine for interoperability (e.g., export to Joern for validation).

- **Gaps in Standards**: Dynamic langs like Python challenge static normalization (e.g., runtime types); standards mitigate via `UNKNOWN` nodes or overlays. No built-in VS Code integration— you'll bridge via LSP.

#### Insights from Related Projects
I analyzed projects mirroring your architecture (Tree-sitter → normalized graph → analysis). These provide blueprints for Python-focused implementation.

| Project | Key Features | Normalization Approach | Python Handling | Relevance to WYRD/VS Code | Limitations |
|---------|--------------|------------------------|-----------------|---------------------------|-------------|
| **Joern** | Open-source CPG platform; frontends parse to CPG; Cypher queries for analysis. | Lang-specific frontends map to universal nodes (e.g., Tree-sitter adaptable); auto-generate edges from props. Incremental via file hashes. | Dedicated Python frontend; desugars comprehensions to loops. Example query: `MATCH (c:CALL)-[:CALL]->(m:METHOD {name: "save"}) RETURN c.lineNumber`. | High: Adapt schema for FalkorDB; use for impact analysis (PDG traversals). | Heavy (Scala-based); not Tree-sitter native—custom bridge needed. |
| **Stackwalk** | Rust lib for AST walking + call stacks from Tree-sitter CST. Outputs blocks, call_graph. | TOML matchers map CST nodes (e.g., Python `import_from_statement` → universal `Import`). Builds directed call edges. | Native support; incremental via Tree-sitter. Usage: `index_directory` returns graph tuple. | Medium: Embed in VS Code (WASM wrapper); extend to full UAST. | Limited langs (Python + Rust); no PDG. |
| **Fraunhofer CPG** | Java lib extracts CPG from source; supports Python via jep bridge. | Custom parsers → AST → CPG normalization (e.g., Python funcs to `Method` nodes). Passes for DFG/EOG edges. | Full; analyzes incomplete code. Build: Gradle + `cpg-language-python`. | High: Fork for Tree-sitter integration; query via Neo4j (adapt to FalkorDB). | Parser-heavy (not Tree-sitter); LLVM focus bloats deps. |
| **MLCPD (UAST Dataset)** | 7M+ files parsed to UAST JSON/Parquet via Tree-sitter. | Algorithms: Recursive CST extraction → flat nodes → categorize (e.g., `function_declaration` → `Function`) → cross-map. 99.99% success. | Handles Python's expr-heavy trees; high similarity to JS/TS. Tools: GitHub pipeline for repro. | High: Use schema as blueprint; visualize UASTs for VS Code webviews. | Dataset-only; no runtime tool—implement extraction yourself. |
| **Semantic Indexing (Medium Series)** | Hybrid AST (semantic chunks) + Tree-sitter CST (fidelity) for RAG/AI. | Convert CST to AST via tools like `asttokens`; embed chunks for vector search. Edges implicit (calls via node types). | Python `ast` module + Tree-sitter; example: Prime checker parsed to Mermaid graph. | High: For AI agents in VS Code; ground retrieval in source positions. | Conceptual; no full graph code. |

- **Cross-Project Patterns**: All emphasize **Tree-sitter as parser** for its incremental CSTs (updates on edits, key for "parse on save"). Normalization via **mapping rules** (e.g., dictionaries/TOML for node types). Graphs prioritize edges (calls/refs) over perfect syntax reconstruction. For Python, handle dynamism with fallback `UNKNOWN` nodes.

### Recommendations: Implementing a Normalized AST for Python with Tree-sitter

Focus on a **UAST-inspired schema** atop CPG principles: Start with AST layer (your "Universal Abstract Symbol Tree"), using Tree-sitter for CST input. This yields a graph in FalkorDB with universal nodes (e.g., `:Function`) and edges (e.g., `[:CALLS]` from Kythe). Prototype in Python (using `tree-sitter` lib + NetworkX for graph building, then export to FalkorDB).

#### Step-by-Step Implementation Guide
1. **Setup Parsing Pipeline (Tree-sitter CST Extraction)**:
   - Install: `pip install tree-sitter tree-sitter-python` (binds to Python grammar).
   - Parse file: Load grammar, parse source to CST. Preserve positions for VS Code (e.g., `node.start_point`, `node.end_point`).
   - Best Practice: Use incremental mode—on VS Code `didSave`, reparse only changed ranges (Tree-sitter's `parser.set_included_ranges`).
   - Example Code:
     ```python
     from tree_sitter import Language, Parser
     import os

     PY_LANGUAGE = Language('build/my-languages.so', 'python')  # Compile grammar first
     parser = Parser()
     parser.set_language(PY_LANGUAGE)

     def parse_to_cst(source_path):
         with open(source_path, 'r') as f:
             source = f.read()
         tree = parser.parse(bytes(source, 'utf8'))
         return tree.root_node, source  # CST root + source text
     ```
   - Output: CST with named nodes (e.g., `function_definition`, `call`).

2. **Define Normalized Schema (UAST + CPG Hybrid)**:
   - **Nodes**: Universal types from MLCPD/CPG. Properties: `name`, `full_name` (Kythe-inspired), `code` (verbatim snippet), `line_start`, `line_end`, `hash` (for increments).
   - **Edges**: CPG/Kythe mix: `AST` (containment), `REFERS_TO` (var uses), `CALLS` (invocations), `DEFINES` (decls).
   - Table of Core Node Types (Python-Mapped):
     | Universal Node | Python CST Mapping | Properties Example | Use Case |
     |----------------|--------------------|--------------------|----------|
     | `:File` | `module` | `name: "main.py"`, `hash: sha256(source)` | Root; contains namespaces. |
     | `:Namespace` | `module` or package stmts | `full_name: "pkg.module"` | Grouping; Kythe VName for ID. |
     | `:Function` | `function_definition` | `name: "is_prime"`, `signature: "(n: int) -> bool"` | Methods; add `is_external: True` for imports. |
     | `:Call` | `expression_statement > call` | `method_full_name: "math.sqrt"`, `dispatch: "STATIC"` | Calls; auto-edge to callee. |
     | `:Identifier` | `identifier` | `name: "n"`, `type_full_name: "int"` (infer later) | Vars; `REFERS_TO` edge to def. |
     | `:Literal` | `string`/`integer` | `value: "42"`, `code: '"42"'` | Constants; leaf nodes. |
     | `:IfStatement` | `if_statement` | `condition_code: "n > 0"` | Control; for future CFG. |
     | `:Unknown` | Fallback (e.g., malformed) | `code: snippet` | Handles Python dynamism. |
   - Serialize as JSON/Parquet initially; migrate to FalkorDB nodes (e.g., `CREATE (n:Function {name: 'foo'})`).

3. **Normalization Process (CST → UAST Graph)**:
   - **Traverse & Map**: Recursive walk of CST (focus on named nodes per best practices—ignore extras like whitespace).
   - **Rules**: Use a mapping dict (like Stackwalk's TOML). Desugar (e.g., Python list comp → loop + assignment).
   - **Cross-Lang Prep**: For future, add lang param; Python-first keeps it simple.
   - **Enrich**: Add semantics (e.g., resolve imports via `ast` module fallback; link calls via `full_name`).
   - Example Mapping Function:
     ```python
     import networkx as nx  # Temp graph; replace with FalkorDB client

     MAPPING = {
         'function_definition': 'Function',
         'call': 'Call',
         'identifier': 'Identifier',
         # ... more from MLCPD categories
     }

     def normalize_cst(root_node, source, graph=None):
         if graph is None:
             graph = nx.DiGraph()
         node_type = MAPPING.get(root_node.type, 'Unknown')
         props = {
             'name': root_node.text(source) if hasattr(root_node, 'text') else '',
             'code': source[root_node.start_byte:root_node.end_byte].decode(),
             'line_start': root_node.start_point[0] + 1,
             'line_end': root_node.end_point[0] + 1,
             'hash': hash(source[root_node.start_byte:root_node.end_byte])  # Simple; use SHA
         }
         node_id = f"{node_type}:{props['line_start']}"  # Kythe-like VName stub
         graph.add_node(node_id, type=node_type, **props)

         # Edges: Parent-child (AST)
         parent_id = ...  # Track stack
         if parent_id:
             graph.add_edge(parent_id, node_id, type='AST')

         # Semantic edges (e.g., CALLS)
         if node_type == 'Call':
             callee_name = ...  # Extract from child identifier
             graph.add_edge(node_id, f"Function:{callee_name}", type='CALLS')

         for child in root_node.children:
             if child.is_named:  # Best practice: Skip anon nodes
                 normalize_cst(child, source, graph)
         return graph
     ```
   - **Validation**: Per MLCPD, check parse success (99%+ goal); use cosine similarity on node vectors for quality.

4. **Handle Incremental Updates & VS Code Integration**:
   - **Increments**: Tree-sitter edits tree in-place; recompute subgraph via `hash` diffs (CPG best practice). On `didSave`, parse delta, update affected nodes (e.g., re-link calls).
   - **VS Code**: Expose via LSP: Register commands like `wy rd/getDefinition` (traverse `REFERS_TO`). Use webviews for graph viz (e.g., Mermaid from normalized edges). For AI: Serialize subgraph to JSON for agent prompts.
   - **Performance**: O(k) updates (k = affected nodes) via "dirty set" (CodePrism-inspired: track file-symbol deps).

5. **Testing & Iteration**:
   - **Queries**: Test with CPG examples, e.g., FalkorDB Cypher: `MATCH (c:Call)-[:CALLS]->(f:Function) WHERE f.name =~ 'db.*' RETURN c.line_start`.
   - **Benchmark**: Parse 1K Python files (e.g., from GitHub); measure vs. native `ast` (Tree-sitter: 2x faster increments).
   - **Extend**: Add CFG (from `:IfStatement` conditions) for paths; PDG for taint (user input → sinks).

This yields a robust, standards-aligned UAST: Semantic enough for AI comprehension, faithful via CST positions. Start with a minimal prototype (parse → map → simple query), then layer standards. If needed, I can generate sample code or refine for multi-lang.