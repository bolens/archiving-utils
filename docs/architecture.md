# Architecture

[Interactive Archify diagram](https://bolens.github.io/archiving-utils/diagrams/architecture.html) · [Diagram source](diagrams/architecture.json)

`bin/archiving-utils` dispatches to `lib/core.py`. Per-tool Bash scripts and Makefiles are generated from `lib/catalog.json`. The catalog owns names, descriptions, extensions, output formats, and operation types.

The shared core parses flags and JSON config, discovers regular files, plans destinations, rejects collisions, and submits work to a bounded thread pool with at most two outstanding operations per worker. File discovery and result collection still use memory proportional to the input count. Domain operations live in `lib/domain.py`. A writer creates temporary output, validates it, and calls no-clobber publication. Read-only operations return structured records. Library operations such as hashing and tree comparison run in the shared core.

`mcp/server.py` shares that engine but exposes a smaller read-only catalog. It requires allowed roots at startup and never accepts arbitrary CLI arguments. The MCP server is local stdio only.

`make generate` builds command wrappers, CLI reference pages, the catalog, and `site/index.html`. Site search and theme controls run locally in the browser. The website never accesses media files. GitHub Pages deploys the checked `site/` directory after CI succeeds on main.

The Archify specification is maintained separately from the website generator. `deliver` receipts and browser checks are stored in the documentation evidence directory. Generated HTML stays unchanged after delivery.
