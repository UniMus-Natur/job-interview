"""Extract module for Species Observation ETL.

Reads raw observation records from the SQLite database.
"""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List


def extract_raw_observations(db_path: str | Path) -> List[Dict[str, Any]]:
    """Extracts all records from the raw_observations table in SQLite database.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        List of dictionaries containing column name to value mappings.

    Raises:
        FileNotFoundError: If the database file does not exist.
        sqlite3.Error: If a database operation fails.
    """
    path = Path(db_path)
    if not path.is_file():
        raise FileNotFoundError(f"SQLite database not found at path: {path}")

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_observations ORDER BY id ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
