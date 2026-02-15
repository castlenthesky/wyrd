# 1. Implement a language server
Start with a python language server, then expand to other languages after the proof of concept is complete.

## Features

### Abstract Syntax Tree (AST)
Use this to build the ast layer of the code property graph
- Must convert from language-specific AST to a generic AST representation
- Must be able to query the AST for specific nodes

### Tree-sitter integration
Tree-sitter is a parser generator tool and an incremental parsing library. It can be used to build a parser for a programming language, and then use that parser to build an AST for a program written in that language. We only need this when a file is saved in an invalid state, or when a file is opened for the first time. This is not a replacement for the AST, but a way to build the AST when the AST is not functional for a broken file. (These assertions need to be validated)
