import logging
from contextlib import closing
from pathlib import Path
from typing import Any, List

import duckdb
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

from mcp_server_duckdb import Config

logger = logging.getLogger("mcp-server-duckdb")
logger.info("Starting MCP DuckDB Server")


class DuckDBDatabase:
    def __init__(self, db_path: str):
        path = Path(db_path).expanduser()
        dir_path = path.parent
        if not dir_path.exists():
            logger.info(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True)

        if not path.exists():
            logger.info(f"Creating DuckDB database: {path}")
            duckdb.connect(str(path)).close()

        self.db_path = str(path)

    def connect(self):
        return duckdb.connect(self.db_path)

    def execute_query(self, query: object, parameters: object = None) -> List[Any]:
        with closing(self.connect()) as connection:
            return connection.execute(query, parameters).fetchall()


async def main(config: Config):
    logger.info(f"Starting SQLite MCP Server with DB path: {config.db_path}")

    db = DuckDBDatabase(config.db_path)
    server = Server("mcp-duckdb-server")

    logger.debug("Registering handlers")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        """
        List available duckdb resources.
        """
        return []

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        """
        Read a specific note's content by its URI.
        """
        return "No data"

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        """
        List available prompts.
        """
        return []

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        """
        Generate a prompt by combining arguments with server state.
        """

        return types.GetPromptResult(
            description="No",
            messages=[],
        )

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="read-query",
                description="Execute a SELECT query on the DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SELECT SQL query to execute",
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="write-query",
                description="Execute an INSERT, UPDATE, or DELETE query on the DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute",
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="create-table",
                description="Create a new table in the DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "CREATE TABLE SQL statement",
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list-tables",
                description="List all tables in the DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe-table",
                description="Get the schema information for a specific table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to describe",
                        },
                    },
                    "required": ["table_name"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "list-tables":
                results = db.execute_query("SELECT * FROM information_schema.tables;")
                return [types.TextContent(type="text", text=str(results))]

            elif name == "describe-table":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                results = db.execute_query("PRAGMA table_info(?)", [arguments["table_name"]])
                return [types.TextContent(type="text", text=str(results))]

            if not arguments:
                raise ValueError("Missing arguments")

            if name == "read-query":
                if not arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries are allowed for read-query")
                results = db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "write-query":
                if arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("SELECT queries are not allowed for write-query")
                results = db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "create-table":
                if not arguments["query"].strip().upper().startswith("CREATE TABLE"):
                    raise ValueError("Only CREATE TABLE statements are allowed")
                db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text="Table created successfully")]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except duckdb.Error as e:
            return [types.TextContent(type="text", text=f"Database error: {str(e)}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("DuckDB MCP Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-duckdb",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
