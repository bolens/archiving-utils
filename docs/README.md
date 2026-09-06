# Documentation

Archive preservation contracts and generated command documentation.

## Start here

| Need | Owning document |
| --- | --- |
| Use the project | [README.md](../README.md) |
| Change the repository | [AGENTS.md](../AGENTS.md) |
| Deliver or recover | [RELEASING.md](../RELEASING.md) |
| Plan substantial changes | [.specify/memory/project-guide.md](../.specify/memory/project-guide.md) |
| Non-negotiable constraints | [.specify/memory/constitution.md](../.specify/memory/constitution.md) |

## Architecture

[Architecture](architecture.md) owns the shared engine and archive backend boundaries. The
[catalog](../lib/catalog.json) feeds generated wrappers and reference pages. Archive members are
untrusted: containment, link refusal, expansion bounds, checksums, and no-clobber publication must
survive changes to a codec or container.

## Deployment and recovery

[Requirements](requirements.md) owns backend availability. [Container usage](docker.md) owns bind
mounts and image operation. [RELEASING.md](../RELEASING.md) owns source, Pages, and container
delivery. Regenerate catalog-derived surfaces through the existing generator before checking drift.

## Database and state

The product operates on local archives and reports, without an application database. Source
retention and verified publication are the persistence contract. [CLI behavior](cli.md) owns
explicit writes and output handling. [MCP](mcp.md) exposes only read-only operations within
configured roots.

## Documentation maintenance

Keep decisions, invariants, failure modes, and recovery requirements in the owning document. Link to
commands, defaults, schemas, and generated catalogs instead of copying them. Change the owner and
affected references together. Update this index when adding or moving a guide, and verify relative
links and heading anchors. Historical specs and audits describe their recorded revision, not current
runtime proof. A topic without an implementation stays explicitly unimplemented.

## Topic guides

- [Contributing](../CONTRIBUTING.md)
- [Architecture](architecture.md)
- [Tool catalog](catalog.md)
- [CLI contract](cli.md)
- [Development environments](development-environments.md)
- [Docker](docker.md)
- [Formats and limits](formats.md)
- [MCP server](mcp.md)
- [Relationship to audio-utils](parity.md)
- [Release procedure](releasing.md)
- [Requirements](requirements.md)
