# mcp-server-duckdb

A Model Context Protocol (MCP) server implementation for DuckDB, providing database interaction capabilities through MCP tools.
It would be interesting to have LLM analyze it. DuckDB is suitable for local analysis.

## Overview

This server enables interaction with a DuckDB database through the Model Context Protocol, allowing for database operations like querying, table creation, and schema inspection.

## Components

### Resources

Currently, no custom resources are implemented.

### Prompts

Currently, no custom prompts are implemented.

### Tools

The server implements the following database interaction tools:

- **read-query**: Execute SELECT queries to read data from the database
  - Input: `query` (string) - Must be a SELECT statement
  - Output: Query results as text

- **write-query**: Execute INSERT, UPDATE, or DELETE queries to modify data
  - Input: `query` (string) - Must be a non-SELECT statement
  - Output: Query results as text

- **create-table**: Create new tables in the database
  - Input: `query` (string) - Must be a CREATE TABLE statement
  - Output: Success confirmation message

- **list-tables**: List all tables in the database
  - Input: None required
  - Output: List of tables from information_schema

- **describe-table**: Get schema information for a specific table
  - Input: `table_name` (string) - Name of the table to describe
  - Output: Table schema information

## Configuration

### Required Parameters

- **db-path** (string): Path to the DuckDB database file
  - The server will automatically create the database file and parent directories if they don't exist

## Installation

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
npx @modelcontextprotocol/inspector uv --directory ~/mcp-server-duckdb run mcp-server-duckdb
```

2. Open the provided URL in your browser to access the debugging interface

The inspector provides visibility into:
- Request/response communication
- Tool execution
- Server state
- Error messages
