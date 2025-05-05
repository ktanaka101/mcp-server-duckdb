# mcp-server-duckdb

[![PyPI - Version](https://img.shields.io/pypi/v/mcp-server-duckdb)](https://pypi.org/project/mcp-server-duckdb/)
[![PyPI - License](https://img.shields.io/pypi/l/mcp-server-duckdb)](LICENSE)
[![smithery badge](https://smithery.ai/badge/mcp-server-duckdb)](https://smithery.ai/server/mcp-server-duckdb)

A Model Context Protocol (MCP) server implementation for DuckDB, providing database interaction capabilities through MCP tools.
It would be interesting to have LLM analyze it. DuckDB is suitable for local analysis.

<a href="https://glama.ai/mcp/servers/fwggl49w22"><img width="380" height="200" src="https://glama.ai/mcp/servers/fwggl49w22/badge" alt="mcp-server-duckdb MCP server" /></a>

## Overview

This server enables interaction with a DuckDB database through the Model Context Protocol, allowing for database operations like querying, table creation, and schema inspection.

## Components

### Resources

Currently, no custom resources are implemented.

### Prompts

Currently, no custom prompts are implemented.

### Tools

The server implements the following database interaction tool:

- **query**: Execute any SQL query on the DuckDB database
  - **Input**: `query` (string) - Any valid DuckDB SQL statement
  - **Output**: Query results as text (or success message for operations like CREATE/INSERT)

> [!NOTE]
> The server provides a single unified `query` function rather than separate specialized functions, as modern LLMs can generate appropriate SQL for any database operation (SELECT, CREATE TABLE, JOIN, etc.) without requiring separate endpoints.

> [!NOTE]
> When the server is running in `readonly` mode, DuckDB's native readonly protection is enforced.
> This ensures that the Language Model (LLM) cannot perform any write operations (CREATE, INSERT, UPDATE, DELETE), maintaining data integrity and preventing unintended changes.

## Configuration

### Required Parameters

- **db-path** (string): Path to the DuckDB database file
  - The server will automatically create the database file and parent directories if they don't exist
  - If `--readonly` is specified and the database file doesn't exist, the server will fail to start with an error

### Optional Parameters

- **--readonly**: Run server in read-only mode (default: `false`)
  - **Description**: When this flag is set, the server operates in read-only mode. This means:
    - The DuckDB database will be opened with `read_only=True`, preventing any write operations.
    - If the specified database file does not exist, it **will not** be created.
    - **Security Benefit**: Prevents the Language Model (LLM) from performing any write operations, ensuring that the database remains unaltered.
  - **Reference**: For more details on read-only connections in DuckDB, see the [DuckDB Python API documentation](https://duckdb.org/docs/api/python/dbapi.html#read_only-connections).
- **--keep-connection**: Re-uses a single DuckDB connection mode (default: `false`)
  - **Description**: When this flag is set, Re-uses a single DuckDB connection for the entire server lifetime. Enables TEMP objects & slightly faster queries, but can hold an exclusive lock on the file.

## Installation

### Installing via Smithery

To install DuckDB Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-server-duckdb):

```bash
npx -y @smithery/cli install mcp-server-duckdb --client claude
```

### Claude Desktop Integration

Configure the MCP server in Claude Desktop's configuration file:

#### MacOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Windows
Location: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "duckdb": {
      "command": "uvx",
      "args": [
        "mcp-server-duckdb",
        "--db-path",
        "~/mcp-server-duckdb/data/data.db"
      ]
    }
  }
}
```

* Note: `~/mcp-server-duckdb/data/data.db` should be replaced with the actual path to the DuckDB database file.

## Development

### Prerequisites

- Python with `uv` package manager
- DuckDB Python package
- MCP server dependencies

### Debugging

Debugging MCP servers can be challenging due to their stdio-based communication. We recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) for the best debugging experience.

#### Using MCP Inspector

1. Install the inspector using npm:
```bash
npx @modelcontextprotocol/inspector uv --directory ~/codes/mcp-server-duckdb run mcp-server-duckdb --db-path ~/mcp-server-duckdb/data/data.db
```

2. Open the provided URL in your browser to access the debugging interface

The inspector provides visibility into:
- Request/response communication
- Tool execution
- Server state
- Error messages
