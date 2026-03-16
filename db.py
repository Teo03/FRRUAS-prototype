import datetime
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "frruas_db",
    "user": "frruas_user",
    "password": "frruas_pass",
    "options": "-c search_path=project,public",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


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
