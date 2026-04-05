import sys
import getpass

import bcrypt

from db import get_connection, close_pool, pick_from_list
from uc_browse import browse_resources
from uc_reserve import make_reservation
from uc_approve import approve_reservations
from uc_analytics import view_analytics
from uc_users import register_user


def login():
    """Authenticate user with email and password. Returns (user_id, first_name, last_name, role) or None."""
    print("\n=== FRRUAS - Login ===\n")
    while True:
        email = input("  Email: ").strip()
        if not email:
            return None
        password = getpass.getpass("  Password: ").strip()
        if not password:
            return None

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT u.user_id, u.first_name, u.last_name, u.password, ut.type_name
                        FROM users u
                        JOIN user_types ut ON u.type_id = ut.type_id
                        WHERE u.email = %s
                        """,
                        (email,),
                    )
                    row = cur.fetchone()
        except Exception as e:
            print(f"\n  Database error: {e}")
            print("  Is the database running? (docker compose up -d)\n")
            return None

        if row and bcrypt.checkpw(password.encode(), row[3].encode()):
            user_id, first_name, last_name, _, role = row
            print(f"\n  Welcome, {first_name} {last_name} ({role})!\n")
            return (user_id, first_name, last_name, role)

        print("  Invalid email or password. Please try again.\n")


def main_menu(user_id, first_name, last_name, role):
    """Role-based main menu loop."""
    while True:
        print(f"\n=== Main Menu ({first_name} {last_name} - {role}) ===\n")
        options = []
        actions = []

        options.append("Browse Available Resources")
        actions.append(lambda: browse_resources())

        if role == "Teaching Staff":
            options.append("Make a Resource Reservation")
            actions.append(lambda uid=user_id: make_reservation(uid))

        if role == "Administrator":
            options.append("Approve or Reject Reservations")
            actions.append(lambda uid=user_id: approve_reservations(uid))
            options.append("View Resource Usage Analytics")
            actions.append(lambda: view_analytics())
            options.append("Register a New User")
            actions.append(lambda: register_user())

        options.append("Logout")

        idx = pick_from_list("  Choose an option: ", options)
        if idx is None or options[idx] == "Logout":
            print("  Logged out.\n")
            return


def main():
    print("\n" + "=" * 55)
    print("  FRRUAS - Faculty Resource Reservation")
    print("         and Usage Analytics System")
    print("=" * 55)

    try:
        while True:
            user = login()
            if user is None:
                print("  Goodbye.")
                break
            user_id, first_name, last_name, role = user
            main_menu(user_id, first_name, last_name, role)
    except KeyboardInterrupt:
        print("\n\n  Goodbye.")
    finally:
        close_pool()


if __name__ == "__main__":
    main()
