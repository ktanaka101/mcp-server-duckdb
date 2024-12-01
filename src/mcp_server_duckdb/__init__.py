import argparse
import asyncio
from dataclasses import dataclass

from . import server


@dataclass
class Config:
    """
    Configuration for the server.
    """

    db_path: str
    """
    Path to DuckDB database file.
    """


def parse_arguments() -> Config:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="DuckDB MCP Server")

    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to DuckDB database file",
        required=True,
    )

    args = parser.parse_args()
    return Config(db_path=args.db_path)


def main():
    """Main entry point for the package."""

    parser = argparse.ArgumentParser(description="DuckDB MCP Server")
    parser.add_argument(
        "--db-path",
        help="Path to DuckDB database file",
        required=True,
    )

    config = parse_arguments()
    asyncio.run(server.main(config))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
