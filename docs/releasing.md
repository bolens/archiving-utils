# Release procedure

[Documentation](README.md)

1. Run `make generate check test-all` on a clean checkout. Record every optional delegate skip.
2. Review the catalog, examples, requirements, and limitations against the code. Update CHANGELOG.md and VERSION together.
3. Validate and deliver the Archify specification with the installed Archify skill. Preserve its exact delivered HTML under site/diagrams/. Review browser evidence and screenshots.
4. Audit tracked content and the history that will be published for secrets and private data.
5. Commit the release changes and push main. Wait for CI to succeed. The Pages workflow deploys only the same successful main revision.
6. Verify <https://bolens.github.io/archiving-utils/>, command filtering, and the architecture link. Create a version tag and GitHub release only when requested.

Initial publication creates the repository and main branch without a release tag. The site is plain static HTML/CSS/JavaScript with relative asset URLs and no external build service.
