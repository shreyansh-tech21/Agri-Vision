"""
SQLite-specific engine hooks so concurrent writers serialize like production Postgres.

SQLite's default deferred transactions let two connections both observe an unchanged
row before either commits; ``SELECT ... FOR UPDATE`` does not match Postgres row
locks. ``BEGIN IMMEDIATE`` reserves a write lock at transaction start.

See: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.engine import Engine


def configure_sqlite_immediate_transactions(engine: Engine) -> None:
    """Register connect/begin hooks so each transaction opens with BEGIN IMMEDIATE."""
    if engine.dialect.name != "sqlite":
        return

    def _on_connect(dbapi_conn, connection_record):
        dbapi_conn.isolation_level = None

    def _on_begin(conn):
        conn.exec_driver_sql("BEGIN IMMEDIATE")

    event.listen(engine, "connect", _on_connect, insert=True)
    event.listen(engine, "begin", _on_begin)