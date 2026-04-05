import datetime

from db import get_connection, get_transaction, pick_from_list, print_table, input_date, input_time


def make_reservation(user_id):
    """UC0002: Make a Resource Reservation."""
    print("\n=== Make a Resource Reservation ===\n")

    # Step 1: Select resource
    resources = _fetch_all_resources()
    if not resources:
        print("  No resources available.")
        return

    items = []
    for r in resources:
        loc = f"{r['building']} / {r['room']}" if r["building"] else "Digital"
        items.append(f"{r['name']} [{r['type_name']}] - {loc}")
    idx = pick_from_list("  Select a resource to reserve: ", items)
    if idx is None:
        return

    resource = resources[idx]
    rid = resource["resource_id"]

    # Step 2: Show resource details and upcoming reservations
    print(f"\n  === {resource['name']} ===")
    print(f"  Available: {resource['available_from'].strftime('%H:%M')} - {resource['available_to'].strftime('%H:%M')}")
    print(f"  Weekends:  {'Yes' if resource['available_weekends'] else 'No'}")

    _show_upcoming(rid)

    # Step 3: Enter reservation details
    while True:
        print()
        date = input_date("  Reservation date (YYYY-MM-DD): ")
        start = input_time("  Start time (HH:MM): ")
        end = input_time("  End time (HH:MM): ")

        if end <= start:
            print("  End time must be after start time.")
            continue

        purpose = input("  Purpose: ").strip()
        if not purpose:
            print("  Purpose is required.")
            continue
        if len(purpose) > 512:
            purpose = purpose[:512]

        # Step 4: Validate availability window
        day_of_week = date.isoweekday()
        if day_of_week > 5 and not resource["available_weekends"]:
            print(f"\n  ERROR: {resource['name']} is not available on weekends.")
            if not _retry():
                return
            continue

        if start < resource["available_from"] or end > resource["available_to"]:
            print(
                f"\n  ERROR: {resource['name']} is only available "
                f"{resource['available_from'].strftime('%H:%M')} - {resource['available_to'].strftime('%H:%M')}."
            )
            if not _retry():
                return
            continue

        # Step 5: Check conflicts
        start_dt = datetime.datetime.combine(date, start)
        end_dt = datetime.datetime.combine(date, end)
        conflicts = _check_conflicts(rid, start_dt, end_dt)

        if conflicts:
            print(f"\n  CONFLICT: {len(conflicts)} overlapping reservation(s) found:")
            print_table(
                ["ID", "Start", "End", "Purpose", "Reserved by"],
                [
                    (c[0], c[1].strftime("%Y-%m-%d %H:%M"), c[2].strftime("%Y-%m-%d %H:%M"), c[3][:30], c[4])
                    for c in conflicts
                ],
            )
            if not _retry():
                return
            continue

        # Step 6: Confirm
        print(f"\n  --- Reservation Summary ---")
        print(f"  Resource: {resource['name']}")
        print(f"  Date:     {date}")
        print(f"  Time:     {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
        print(f"  Purpose:  {purpose}")
        confirm = input("\n  Confirm reservation? (y/n): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("  Reservation cancelled.")
            return

        # Step 7: INSERT (transaction: re-check conflicts + insert atomically)
        try:
            with get_transaction() as conn:
                with conn.cursor() as cur:
                    # Re-check conflicts inside the transaction to prevent
                    # race conditions (another user inserting between our
                    # check and insert)
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM reservations
                        WHERE resource_id = %s
                          AND status IN ('approved', 'pending')
                          AND start_time < %s AND end_time > %s
                        """,
                        (rid, end_dt, start_dt),
                    )
                    if cur.fetchone()[0] > 0:
                        raise RuntimeError("Conflict: another reservation was just created for this time slot")

                    cur.execute(
                        """
                        INSERT INTO reservations
                            (start_time, end_time, status, purpose, created_at, user_id, resource_id)
                        VALUES (%s, %s, 'pending', %s, CURRENT_TIMESTAMP, %s, %s)
                        RETURNING reservation_id, status, created_at
                        """,
                        (start_dt, end_dt, purpose, user_id, rid),
                    )
                    result = cur.fetchone()
            # Transaction committed automatically
            print(f"\n  Reservation created successfully!")
            print(f"  Reservation ID: {result[0]}")
            print(f"  Status: {result[1]} (awaiting administrator approval)")
            print(f"  Created at: {result[2].strftime('%Y-%m-%d %H:%M')}")
            return
        except Exception as e:
            # Transaction rolled back automatically
            print(f"\n  Error creating reservation: {e}")
            return


def _fetch_all_resources():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.resource_id, r.name, r.description,
                       r.available_from, r.available_to, r.available_weekends,
                       rt.type_name, l.building, l.room
                FROM resources r
                JOIN resource_types rt ON r.type_id = rt.type_id
                LEFT JOIN locations l ON r.location_id = l.location_id
                ORDER BY rt.type_name, r.name
            """)
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def _show_upcoming(resource_id):
    today = datetime.date.today()
    week_end = today + datetime.timedelta(days=7)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT res.start_time, res.end_time, res.status, res.purpose,
                       u.first_name || ' ' || u.last_name AS reserved_by
                FROM reservations res
                JOIN users u ON res.user_id = u.user_id
                WHERE res.resource_id = %s
                  AND res.status IN ('approved', 'pending')
                  AND res.start_time >= %s AND res.start_time < %s
                ORDER BY res.start_time
                """,
                (resource_id, today, week_end),
            )
            rows = cur.fetchall()
    if rows:
        print(f"\n  Reservations in the next 7 days:")
        print_table(
            ["Start", "End", "Status", "Purpose", "By"],
            [
                (r[0].strftime("%Y-%m-%d %H:%M"), r[1].strftime("%Y-%m-%d %H:%M"), r[2], r[3][:30], r[4])
                for r in rows
            ],
        )
    else:
        print("\n  No reservations in the next 7 days.")


def _check_conflicts(resource_id, start_dt, end_dt):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT res.reservation_id, res.start_time, res.end_time,
                       res.purpose,
                       u.first_name || ' ' || u.last_name AS reserved_by
                FROM reservations res
                JOIN users u ON res.user_id = u.user_id
                WHERE res.resource_id = %s
                  AND res.status IN ('approved', 'pending')
                  AND res.start_time < %s
                  AND res.end_time > %s
                """,
                (resource_id, end_dt, start_dt),
            )
            return cur.fetchall()


def _retry():
    choice = input("  Try a different time? (y/n): ").strip().lower()
    return choice in ("y", "yes")
