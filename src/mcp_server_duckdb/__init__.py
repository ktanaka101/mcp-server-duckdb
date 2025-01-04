import asyncio

from mcp_server_duckdb.config import Config

from . import server


def main():
    """Main entry point for the package."""

    config = Config.from_arguments()
    asyncio.run(server.main(config))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
