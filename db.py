import datetime
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "frruas_db",
    "user": "frruas_user",
    "password": "frruas_pass",
    "options": "-c search_path=project,public",
}

# -- Connection Pool ----------------------------------------------------------
# Reuses database connections instead of opening a new one per query.
# SimpleConnectionPool maintains between minconn and maxconn connections.

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(minconn=2, maxconn=10, **DB_CONFIG)
    return _pool


@contextmanager
def get_connection():
    """Get a read-only connection from the pool.
    Autocommit is enabled so SELECTs don't need explicit commit.
    Connection is returned to the pool on exit."""
    p = _get_pool()
    conn = p.getconn()
    try:
        conn.autocommit = True
        yield conn
    finally:
        conn.autocommit = False
        p.putconn(conn)


@contextmanager
def get_transaction():
    """Get a connection with explicit transaction management.
    Commits on successful exit, rolls back on exception.
    Connection is returned to the pool in both cases."""
    p = _get_pool()
    conn = p.getconn()
    try:
        conn.autocommit = False
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


def close_pool():
    """Close all connections in the pool."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


# -- UI Helpers ---------------------------------------------------------------


def pick_from_list(prompt, items):
    """Display items as a numbered list, return selected 0-based index or None."""
    if not items:
        print("  (no items)")
        return None
    for i, item in enumerate(items, start=1):
        print(f"  {i}. {item}")
    print(f"  0. Cancel / Go back")
    while True:
        choice = input(prompt).strip()
        if choice == "0" or choice == "":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return idx
        except ValueError:
            pass
        print("  Invalid choice. Please try again.")


def print_table(headers, rows):
    """Print a formatted ASCII table."""
    if not rows:
        print("  (no data)")
        return
    str_rows = [[str(v) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(val))
    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(f"  {header_line}")
    print(f"  {'-+-'.join('-' * w for w in widths)}")
    for row in str_rows:
        print(f"  {' | '.join(val.ljust(widths[i]) for i, val in enumerate(row))}")


def input_date(prompt):
    """Prompt until valid YYYY-MM-DD entered. Returns datetime.date."""
    while True:
        val = input(prompt).strip()
        try:
            return datetime.datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            print("  Invalid date format. Please use YYYY-MM-DD.")


def input_time(prompt):
    """Prompt until valid HH:MM entered. Returns datetime.time."""
    while True:
        val = input(prompt).strip()
        try:
            return datetime.datetime.strptime(val, "%H:%M").time()
        except ValueError:
            print("  Invalid time format. Please use HH:MM.")
