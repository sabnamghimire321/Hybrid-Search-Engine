import sqlite3
import time

class QueryHistoryStore:
    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_schema()

    def _create_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                query TEXT NOT NULL,
                result_count INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def record(
        self, api_key: str, query: str, result_count: int, timestamp: float | None = None
    ) -> None:
        ts = timestamp if timestamp is not None else time.time()
        self._conn.execute(
            "INSERT INTO query_history (api_key, query, result_count, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (api_key, query, result_count, ts),
        )
        self._conn.commit()

    def history_for(self, api_key: str, limit: int = 50) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT query, result_count, timestamp FROM query_history "
            "WHERE api_key = ? ORDER BY timestamp DESC LIMIT ?",
            (api_key, limit),
        )
        return [
            {"query": row[0], "result_count": row[1], "timestamp": row[2]}
            for row in cursor.fetchall()
        ]

    def total_queries(self, api_key: str | None = None) -> int:
        if api_key is None:
            cursor = self._conn.execute("SELECT COUNT(*) FROM query_history")
        else:
            cursor = self._conn.execute(
                "SELECT COUNT(*) FROM query_history WHERE api_key = ?", (api_key,)
            )
        return cursor.fetchone()[0]

    def top_queries(self, limit: int = 10) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT query, COUNT(*) as count FROM query_history "
            "GROUP BY query ORDER BY count DESC LIMIT ?",
            (limit,),
        )
        return [{"query": row[0], "count": row[1]} for row in cursor.fetchall()]

    def queries_per_user(self) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT api_key, COUNT(*) as count FROM query_history "
            "GROUP BY api_key ORDER BY count DESC"
        )
        return [{"api_key": row[0], "count": row[1]} for row in cursor.fetchall()]

    def average_result_count(self) -> float:
        cursor = self._conn.execute("SELECT AVG(result_count) FROM query_history")
        result = cursor.fetchone()[0]
        return result if result is not None else 0.0

    def close(self) -> None:
        self._conn.close()