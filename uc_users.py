import getpass

import bcrypt

from db import get_connection, get_transaction, pick_from_list


def register_user():
    """UC0009: Register a New User."""
    print("\n=== Register a New User ===\n")

    # Step 1: Show available roles
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT type_id, type_name, description FROM user_types ORDER BY type_id")
            roles = cur.fetchall()

    print("  Available roles:")
    role_items = [f"{r[1]} - {r[2]}" for r in roles]
    role_idx = pick_from_list("  Select role: ", role_items)
    if role_idx is None:
        return
    type_id = roles[role_idx][0]
    role_name = roles[role_idx][1]

    # Step 2: Enter user details
    first_name = input("  First name: ").strip()
    if not first_name:
        print("  First name is required.")
        return

    last_name = input("  Last name: ").strip()
    if not last_name:
        print("  Last name is required.")
        return

    email = input("  Email: ").strip()
    if not email:
        print("  Email is required.")
        return

    # Step 3: Enter password
    password = getpass.getpass("  Initial password: ").strip()
    if not password:
        print("  Password is required.")
        return
    password_confirm = getpass.getpass("  Confirm password: ").strip()
    if password != password_confirm:
        print("  Passwords do not match.")
        return

    # Step 4: Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Step 5: Transaction — check email uniqueness + insert atomically
    # This prevents a race condition where two users register with the
    # same email simultaneously (one check passes, both insert).
    try:
        with get_transaction() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
                if cur.fetchone()[0] > 0:
                    raise ValueError(f"A user with email '{email}' already exists.")

                cur.execute(
                    """
                    INSERT INTO users (first_name, last_name, email, password, type_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING user_id, first_name, last_name, email
                    """,
                    (first_name, last_name, email, hashed, type_id),
                )
                result = cur.fetchone()

        # Transaction committed automatically — Step 6: Confirmation
        print(f"\n  User created successfully!")
        print(f"  User ID:  {result[0]}")
        print(f"  Name:     {result[1]} {result[2]}")
        print(f"  Email:    {result[3]}")
        print(f"  Role:     {role_name}")
    except ValueError as e:
        print(f"\n  ERROR: {e}")
    except Exception as e:
        print(f"\n  Error creating user: {e}")
