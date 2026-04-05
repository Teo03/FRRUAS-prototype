from db import get_connection, get_transaction, pick_from_list, print_table


def approve_reservations(admin_user_id):
    """UC0003: Approve or Reject Reservations."""
    while True:
        pending = _fetch_pending()
        if not pending:
            print("\n  No pending reservations.")
            return

        print(f"\n=== Pending Reservations ({len(pending)}) ===\n")
        items = []
        for p in pending:
            loc = f"{p['building']} / {p['room']}" if p["building"] else "Digital"
            items.append(
                f"[#{p['reservation_id']}] {p['purpose'][:40]}\n"
                f"       by {p['requested_by']} ({p['requester_role']})\n"
                f"       {p['resource_name']} ({loc})\n"
                f"       {p['start_time'].strftime('%Y-%m-%d %H:%M')} - {p['end_time'].strftime('%Y-%m-%d %H:%M')}"
            )
        idx = pick_from_list("  Select a reservation to review: ", items)
        if idx is None:
            return

        reservation = pending[idx]
        _review_reservation(reservation, admin_user_id)


def _fetch_pending():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT res.reservation_id, res.start_time, res.end_time,
                       res.purpose, res.created_at, res.recurrence_group_id, res.resource_id,
                       u.first_name || ' ' || u.last_name AS requested_by,
                       u.email AS requester_email,
                       ut.type_name AS requester_role,
                       r.name AS resource_name,
                       rt.type_name AS resource_type,
                       l.building, l.room
                FROM reservations res
                JOIN users u ON res.user_id = u.user_id
                JOIN user_types ut ON u.type_id = ut.type_id
                JOIN resources r ON res.resource_id = r.resource_id
                JOIN resource_types rt ON r.type_id = rt.type_id
                LEFT JOIN locations l ON r.location_id = l.location_id
                WHERE res.status = 'pending'
                ORDER BY res.created_at ASC
            """)
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def _review_reservation(res, admin_user_id):
    print(f"\n  === Reservation #{res['reservation_id']} ===")
    print(f"  Purpose:     {res['purpose']}")
    print(f"  Requested by: {res['requested_by']} ({res['requester_role']})")
    print(f"  Email:       {res['requester_email']}")
    print(f"  Resource:    {res['resource_name']} ({res['resource_type']})")
    if res["building"]:
        print(f"  Location:    {res['building']} / {res['room']}")
    print(f"  Time:        {res['start_time'].strftime('%Y-%m-%d %H:%M')} - {res['end_time'].strftime('%Y-%m-%d %H:%M')}")
    print(f"  Created:     {res['created_at'].strftime('%Y-%m-%d %H:%M')}")

    # Show recurrence series if applicable
    if res["recurrence_group_id"]:
        print(f"\n  Part of recurring series:")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT reservation_id, start_time, end_time, status
                    FROM reservations
                    WHERE recurrence_group_id = %s
                    ORDER BY start_time
                    """,
                    (str(res["recurrence_group_id"]),),
                )
                series = cur.fetchall()
        print_table(
            ["ID", "Start", "End", "Status"],
            [(r[0], r[1].strftime("%Y-%m-%d %H:%M"), r[2].strftime("%Y-%m-%d %H:%M"), r[3]) for r in series],
        )

    # Check conflicts
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT res2.reservation_id, res2.start_time, res2.end_time,
                       res2.purpose,
                       u.first_name || ' ' || u.last_name AS reserved_by
                FROM reservations res2
                JOIN users u ON res2.user_id = u.user_id
                WHERE res2.resource_id = %s
                  AND res2.reservation_id != %s
                  AND res2.status = 'approved'
                  AND res2.start_time < %s
                  AND res2.end_time > %s
                """,
                (res["resource_id"], res["reservation_id"], res["end_time"], res["start_time"]),
            )
            conflicts = cur.fetchall()

    if conflicts:
        print(f"\n  WARNING: {len(conflicts)} conflict(s) with approved reservations:")
        print_table(
            ["ID", "Start", "End", "Purpose", "Reserved by"],
            [(c[0], c[1].strftime("%Y-%m-%d %H:%M"), c[2].strftime("%Y-%m-%d %H:%M"), c[3][:30], c[4]) for c in conflicts],
        )
    else:
        print("\n  No conflicts with approved reservations.")

    # Action
    print()
    action = pick_from_list("  Choose action: ", ["Approve", "Reject", "Skip"])
    if action is None or action == 2:
        return

    new_status = "approved" if action == 0 else "rejected"
    try:
        with get_transaction() as conn:
            with conn.cursor() as cur:
                # For approvals, re-check conflicts within the transaction
                # to prevent approving overlapping reservations
                if new_status == "approved":
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM reservations
                        WHERE resource_id = %s
                          AND reservation_id != %s
                          AND status = 'approved'
                          AND start_time < %s AND end_time > %s
                        """,
                        (res["resource_id"], res["reservation_id"],
                         res["end_time"], res["start_time"]),
                    )
                    if cur.fetchone()[0] > 0:
                        raise RuntimeError("Conflict: another reservation was approved for this time slot")

                cur.execute(
                    """
                    UPDATE reservations
                    SET status = %s, approved_by = %s
                    WHERE reservation_id = %s AND status = 'pending'
                    RETURNING reservation_id, status
                    """,
                    (new_status, admin_user_id, res["reservation_id"]),
                )
                result = cur.fetchone()
        # Transaction committed automatically
        if result:
            print(f"\n  Reservation #{result[0]} has been {result[1]}.")
        else:
            print("\n  Reservation was already processed by another administrator.")
    except Exception as e:
        # Transaction rolled back automatically
        print(f"\n  Error: {e}")
