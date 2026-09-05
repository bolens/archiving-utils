# MCP server

Start the local stdio server with explicitly allowed roots:

```bash
python3 mcp/server.py --allow-root /path/to/library
```

Client configuration, with an absolute checkout path:

```json
{"mcpServers": {"archiving-utils": {"command": "python3", "args": ["/path/to/archiving-utils/mcp/server.py", "--allow-root", "/path/to/library"]}}}
```

The server supports initialize, ping, tools/list, and tools/call over newline-delimited JSON-RPC. It negotiates MCP 2024-11-05, 2025-03-26, 2025-06-18, or 2025-11-25. Each tool accepts only a `paths` array. Notifications receive no reply. Stdout contains protocol messages only.

Only read-only catalog operations are exposed. Compare, tree-diff, and hash-verify are excluded because they require additional path-bearing arguments. All requested paths must remain under roots granted at server startup. Symlink paths are rejected, and discovered symlink entries are skipped. Config files are not read by the server.

Messages are limited to 1 MiB, path lists to 100 entries, and serialized results to 4 MiB. Results exceeding that size return an error after execution. Large inspections still consume time and memory. There is no cancellation, background task protocol, HTTP transport, authentication layer, or write permission mode.

Protocol reference: [MCP tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
