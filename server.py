import sqlite3 
import sys
import os
import argparse
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
DB_PATH = os.path.normpath(os.getenv("ALERTS_DB", "dummy_tax_alerts.db"))
TABLE = "tax_alerts"

# Argument parser for transport
parser = argparse.ArgumentParser()
parser.add_argument("--transport", choices=["sse", "stdio"], default="sse", help="Transport mode: sse or stdio")
args = parser.parse_args()

# Initialize the MCP server
mcp = FastMCP("TaxAlertAgent", port=8001)

@mcp.tool()
def query(sql: str) -> str:
    """Run SELECT queries on tax_alerts table."""
    if not sql.strip().lower().startswith("select"):
        return "Only SELECT queries are allowed."
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
        return "\n".join(str(row) for row in rows) if rows else "No results found."
    except Exception as e:
        return f"Query error: {e}"

@mcp.tool()
def insert(title: str, date: str, jurisdiction: str, topics: str,
           summary: str, full_text: str, source_url: str, tags: str) -> str:
    """Insert a new tax alert."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"""
                INSERT INTO {TABLE}
                (title, date, jurisdiction, topics, summary, full_text, source_url, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (title, date, jurisdiction, topics, summary, full_text, source_url, tags))
            conn.commit()
        return "Tax alert inserted successfully."
    except Exception as e:
        return f"Insert error: {e}"

@mcp.tool()
def update(set_clause: str, condition: str) -> str:
    """Update tax alert rows with a condition."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"UPDATE {TABLE} SET {set_clause} WHERE {condition}")
            conn.commit()
        return "Update successful."
    except Exception as e:
        return f"Update error: {e}"

@mcp.tool()
def delete(condition: str) -> str:
    """Delete rows based on condition."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {TABLE} WHERE {condition}")
            conn.commit()
        return "Delete successful."
    except Exception as e:
        return f"Delete error: {e}"

@mcp.prompt()
def schema_info() -> str:
    """Returns the structure of the tax_alerts table."""
    return """
Table: tax_alerts

Columns:
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- title (TEXT)
- date (TEXT)
- jurisdiction (TEXT)
- topics (TEXT)
- summary (TEXT)
- full_text (TEXT)
- source_url (TEXT)
- tags (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
"""

if __name__ == "__main__":
    print("🔍 Checking SQLite DB connection...")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE}';")
            table_exists = cursor.fetchone()
            if table_exists:
                print(f"✅ Connection successful. Table '{TABLE}' exists.")
            else:
                print(f"⚠️ Connection successful, but table '{TABLE}' does NOT exist.")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    print(f"✅ Starting MCP SQLite server using `{args.transport}` transport...")
    mcp.run(transport=args.transport)
