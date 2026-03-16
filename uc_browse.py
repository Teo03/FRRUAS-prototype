import datetime

from db import get_connection, pick_from_list, print_table, input_date, input_time


def browse_resources():
    """UC0001: Browse Available Resources."""
    type_filter = None
    building_filter = None

    while True:
        resources = _fetch_resources(type_filter, building_filter)

        filters_active = []
        if type_filter:
            filters_active.append(f"Type: {type_filter}")
        if building_filter:
            filters_active.append(f"Building: {building_filter}")

        print(f"\n=== Browse Resources ({len(resources)} found) ===")
        if filters_active:
            print(f"  Active filters: {', '.join(filters_active)}")
        print()

        for i, r in enumerate(resources, start=1):
            loc = f"{r['building']} / {r['room']}" if r["building"] else "Digital"
            print(f"  {i:>3}. {r['name']} [{r['type_name']}] - {loc}")

        print()
        options = [
            "Filter by Resource Type",
            "Filter by Building",
            "View Resource Details",
            "Check Availability for a Time Slot",
            "Clear Filters",
        ]
        idx = pick_from_list("  Choose an option: ", options)
        if idx is None:
            return

        if idx == 0:
            type_filter = _select_type_filter()
        elif idx == 1:
            building_filter = _select_building_filter()
        elif idx == 2:
            _view_details(resources)
        elif idx == 3:
            _check_availability(resources)
        elif idx == 4:
            type_filter = None
            building_filter = None
            print("  Filters cleared.")


def _fetch_resources(type_filter=None, building_filter=None):
    query = """
        SELECT r.resource_id, r.name, r.description,
               r.available_from, r.available_to, r.available_weekends,
               rt.type_name, rt.is_physical,
               l.building, l.room
        FROM resources r
        JOIN resource_types rt ON r.type_id = rt.type_id
        LEFT JOIN locations l ON r.location_id = l.location_id
        WHERE TRUE
    """
    params = []
    if type_filter:
        query += " AND rt.type_name = %s"
        params.append(type_filter)
    if building_filter:
        query += " AND l.building = %s"
        params.append(building_filter)
    query += " ORDER BY rt.type_name, r.name"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def _select_type_filter():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT type_name FROM resource_types ORDER BY type_name")
            types = [row[0] for row in cur.fetchall()]
    print("\n  Select resource type:")
    idx = pick_from_list("  Choose: ", types)
    return types[idx] if idx is not None else None


def _select_building_filter():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT building FROM locations ORDER BY building")
            buildings = [row[0] for row in cur.fetchall()]
    print("\n  Select building:")
    idx = pick_from_list("  Choose: ", buildings)
    return buildings[idx] if idx is not None else None


def _view_details(resources):
    if not resources:
        print("  No resources to show.")
        return
    print("\n  Select a resource to view details:")
    items = [r["name"] for r in resources]
    idx = pick_from_list("  Choose: ", items)
    if idx is None:
        return

    r = resources[idx]
    print(f"\n  === {r['name']} ===")
    print(f"  Type:        {r['type_name']}")
    print(f"  Description: {r['description']}")
    if r["building"]:
        print(f"  Location:    {r['building']} / {r['room']}")
    else:
        print(f"  Location:    Digital (no physical location)")
    print(f"  Available:   {r['available_from'].strftime('%H:%M')} - {r['available_to'].strftime('%H:%M')}")
    print(f"  Weekends:    {'Yes' if r['available_weekends'] else 'No'}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT res.start_time, res.end_time, res.status, res.purpose
                FROM reservations res
                WHERE res.resource_id = %s
                  AND res.status IN ('approved', 'pending')
                  AND res.end_time > CURRENT_TIMESTAMP
                ORDER BY res.start_time
                """,
                (r["resource_id"],),
            )
            reservations = cur.fetchall()

    if reservations:
        print(f"\n  Upcoming reservations:")
        print_table(
            ["Start", "End", "Status", "Purpose"],
            [
                (
                    row[0].strftime("%Y-%m-%d %H:%M"),
                    row[1].strftime("%Y-%m-%d %H:%M"),
                    row[2],
                    row[3][:40],
                )
                for row in reservations
            ],
        )
    else:
        print("\n  No upcoming reservations.")


def _check_availability(resources):
    if not resources:
        print("  No resources to check.")
        return
    print("\n  Select a resource to check availability:")
    items = [r["name"] for r in resources]
    idx = pick_from_list("  Choose: ", items)
    if idx is None:
        return

    r = resources[idx]
    date = input_date("  Date (YYYY-MM-DD): ")
    start = input_time("  Start time (HH:MM): ")
    end = input_time("  End time (HH:MM): ")

    if end <= start:
        print("  End time must be after start time.")
        return

    # Check availability window
    day_of_week = date.isoweekday()  # 1=Mon, 7=Sun
    if day_of_week > 5 and not r["available_weekends"]:
        print(f"\n  NOT AVAILABLE: {r['name']} is not available on weekends.")
        return
    if start < r["available_from"] or end > r["available_to"]:
        print(
            f"\n  NOT AVAILABLE: {r['name']} is only available "
            f"{r['available_from'].strftime('%H:%M')} - {r['available_to'].strftime('%H:%M')}."
        )
        return

    # Check conflicts
    start_dt = datetime.datetime.combine(date, start)
    end_dt = datetime.datetime.combine(date, end)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM reservations
                WHERE resource_id = %s
                  AND status IN ('approved', 'pending')
                  AND start_time < %s
                  AND end_time > %s
                """,
                (r["resource_id"], end_dt, start_dt),
            )
            conflicts = cur.fetchone()[0]

    if conflicts == 0:
        print(f"\n  AVAILABLE: {r['name']} is free on {date} from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}.")
    else:
        print(f"\n  NOT AVAILABLE: {conflicts} conflicting reservation(s) found.")
