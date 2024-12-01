import argparse
import asyncio

from mcp_server_duckdb.config import Config

from . import server


def main():
    """Main entry point for the package."""

    parser = argparse.ArgumentParser(description="DuckDB MCP Server")
    parser.add_argument(
        "--db-path",
        help="Path to DuckDB database file",
        required=True,
    )

    config = Config.from_arguments()
    asyncio.run(server.main(config))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
