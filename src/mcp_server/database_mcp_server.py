"""Read-only MCP tools for the SQLite database shipped with this package."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer


mcp = MCPServer("database-server")
DATABASE_PATH = Path(__file__).resolve().parent / "db" / "db.sqlite3"
DEFAULT_ROW_LIMIT = 100
MAX_ROW_LIMIT = 1000


def _connect() -> sqlite3.Connection:
    """Open the packaged database in SQLite's enforced read-only mode."""
    if not DATABASE_PATH.is_file():
        raise RuntimeError(f"Database file does not exist: {DATABASE_PATH}")
    connection = sqlite3.connect(
        f"{DATABASE_PATH.as_uri()}?mode=ro", uri=True, timeout=5
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


@mcp.tool()
def list_tables() -> str:
    """List user tables in the bundled SQLite database, with their columns."""
    try:
        with _connect() as connection:
            tables = connection.execute(
                """SELECT name FROM sqlite_master
                   WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                   ORDER BY name"""
            ).fetchall()
            result = []
            for row in tables:
                name = row["name"]
                columns = connection.execute(
                    f"PRAGMA table_info({_quote_identifier(name)})"
                ).fetchall()
                result.append(
                    {
                        "table": name,
                        "columns": [
                            {
                                "name": col["name"],
                                "type": col["type"],
                                "not_null": bool(col["notnull"]),
                                "primary_key": bool(col["pk"]),
                            }
                            for col in columns
                        ],
                    }
                )
        return _json(result)
    except sqlite3.Error as exc:
        raise RuntimeError(f"Could not inspect database: {exc}") from exc


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


@mcp.tool()
def read_query(
    sql: str,
    parameters: list[str | int | float | bool | None] | None = None,
    limit: int = DEFAULT_ROW_LIMIT,
) -> str:
    """Run one read-only SELECT query and return rows as JSON.

    Use SQLite `?` placeholders and pass matching values in `parameters`.
    Results are capped at 100 rows by default and at 1000 rows maximum.
    Only SELECT statements (including read-only WITH queries) are accepted.
    """
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("sql must be a non-empty SELECT query")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_ROW_LIMIT:
        raise ValueError(f"limit must be an integer from 1 to {MAX_ROW_LIMIT}")
    # Accept a single SELECT or WITH query only. The connection is also opened
    # read-only, so SQLite independently prevents any database mutation.
    statement = sql.strip()
    if statement.endswith(";"):
        statement = statement[:-1].rstrip()
    if ";" in statement or not re.match(r"^(SELECT|WITH)\b", statement, re.IGNORECASE):
        raise ValueError("Only a single SELECT or WITH query is allowed")
    if parameters is not None and not isinstance(parameters, list):
        raise TypeError("parameters must be a list or None")

    try:
        with _connect() as connection:
            cursor = connection.execute(statement, parameters or [])
            columns = [description[0] for description in cursor.description or []]
            rows = cursor.fetchmany(limit + 1)
            truncated = len(rows) > limit
            return _json(
                {
                    "columns": columns,
                    "rows": [dict(row) for row in rows[:limit]],
                    "row_count": min(len(rows), limit),
                    "truncated": truncated,
                }
            )
    except (sqlite3.Error, OSError) as exc:
        raise RuntimeError(f"Database query failed: {exc}") from exc


if __name__ == "__main__":
    mcp.run()
