import logging
from contextlib import closing
from typing import Any, List

import duckdb
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl

from mcp_server_duckdb import Config

logger = logging.getLogger("mcp-server-duckdb")
logger.info("Starting MCP DuckDB Server")


class DuckDBDatabase:
    def __init__(self, config: Config):
        self.config = config

        dir_path = config.db_path.parent
        if not dir_path.exists():
            if config.readonly:
                raise ValueError(f"Database directory does not exist: {dir_path} in read-only mode")

            logger.info(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True)

        if not config.db_path.exists():
            if config.readonly:
                raise ValueError(f"Database file does not exist: {dir_path} in read-only mode")

            logger.info(f"Creating DuckDB database: {config.db_path}")
            duckdb.connect(config.db_path).close()

        self.db_path = config.db_path

    def connect(self):
        return duckdb.connect(self.db_path, read_only=self.config.readonly)

    def execute_query(self, query: object, parameters: object = None) -> List[Any]:
        with closing(self.connect()) as connection:
            return connection.execute(query, parameters).fetchall()


async def main(config: Config):
    logger.info(f"Starting DuckDB MCP Server with DB path: {config.db_path}")

    db = DuckDBDatabase(config)
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
        tools = [
            types.Tool(
                name="query",
                description="Execute a query on the DuckDB database",
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
        ]

        return tools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if not arguments:
                raise ValueError("Missing arguments")

            if name == "query":
                results = db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except duckdb.Error as e:
            return [types.TextContent(type="text", text=f"Database error: {str(e)}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Run the server using stdin/stdout streams
    options = server.create_initialization_options()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("DuckDB MCP Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            options,
        )
