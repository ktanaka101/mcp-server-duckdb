import argparse
import asyncio

from . import server


def main():
    """Main entry point for the package."""

    parser = argparse.ArgumentParser(description="DuckDB MCP Server")
    parser.add_argument(
        "--db-path",
        help="Path to DuckDB database file",
        required=True,
    )

    args = parser.parse_args()
    asyncio.run(server.main(args.db_path))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
