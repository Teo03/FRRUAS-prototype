from db import get_connection, pick_from_list, print_table


def view_analytics():
    """UC0007: View Resource Usage Analytics."""
    while True:
        print("\n=== Resource Usage Analytics ===\n")
        options = [
            "Summary Overview",
            "Reservations per Resource",
            "Most Active Users",
            "Reservation Status Distribution",
            "Busiest Days of the Week",
            "Resource Type Utilization",
            "Monthly Reservation Trends",
            "Show All Reports",
        ]
        idx = pick_from_list("  Choose a report: ", options)
        if idx is None:
            return

        reports = [
            _summary_overview,
            _reservations_per_resource,
            _most_active_users,
            _status_distribution,
            _busiest_days,
            _resource_type_utilization,
            _monthly_trends,
        ]

        if idx == 7:  # All reports
            for report in reports:
                report()
        else:
            reports[idx]()


def _summary_overview():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total_reservations,
                    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
                    COUNT(*) FILTER (WHERE status = 'pending') AS pending,
                    COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
                    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
                    COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled,
                    COUNT(DISTINCT user_id) AS unique_users,
                    COUNT(DISTINCT resource_id) AS unique_resources
                FROM reservations
            """)
            row = cur.fetchone()
    print("\n  --- Summary Overview ---")
    labels = ["Total", "Approved", "Pending", "Rejected", "Completed", "Cancelled", "Unique Users", "Unique Resources"]
    for label, val in zip(labels, row):
        print(f"  {label + ':':<20} {val}")


def _reservations_per_resource():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.name, rt.type_name,
                       COUNT(res.reservation_id) AS total,
                       COUNT(res.reservation_id) FILTER (WHERE res.status = 'approved') AS approved,
                       COUNT(res.reservation_id) FILTER (WHERE res.status = 'completed') AS completed,
                       COUNT(res.reservation_id) FILTER (WHERE res.status = 'rejected') AS rejected
                FROM resources r
                JOIN resource_types rt ON r.type_id = rt.type_id
                LEFT JOIN reservations res ON r.resource_id = res.resource_id
                GROUP BY r.resource_id, r.name, rt.type_name
                HAVING COUNT(res.reservation_id) > 0
                ORDER BY total DESC
            """)
            rows = cur.fetchall()
    print("\n  --- Reservations per Resource ---")
    print_table(["Resource", "Type", "Total", "Approved", "Completed", "Rejected"], rows)


def _most_active_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.first_name || ' ' || u.last_name, ut.type_name,
                       COUNT(res.reservation_id) AS total,
                       COUNT(res.reservation_id) FILTER (WHERE res.status IN ('approved', 'completed')) AS successful,
                       COUNT(res.reservation_id) FILTER (WHERE res.status = 'rejected') AS rejected
                FROM users u
                JOIN user_types ut ON u.type_id = ut.type_id
                LEFT JOIN reservations res ON u.user_id = res.user_id
                GROUP BY u.user_id, u.first_name, u.last_name, ut.type_name
                HAVING COUNT(res.reservation_id) > 0
                ORDER BY total DESC
            """)
            rows = cur.fetchall()
    print("\n  --- Most Active Users ---")
    print_table(["User", "Role", "Total", "Successful", "Rejected"], rows)


def _status_distribution():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT status, COUNT(*) AS count,
                       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
                FROM reservations
                GROUP BY status
                ORDER BY count DESC
            """)
            rows = cur.fetchall()
    print("\n  --- Reservation Status Distribution ---")
    print_table(["Status", "Count", "Percentage (%)"], rows)


def _busiest_days():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TRIM(TO_CHAR(res.start_time, 'Day')),
                       COUNT(*) AS reservation_count
                FROM reservations res
                JOIN resources r ON res.resource_id = r.resource_id
                JOIN resource_types rt ON r.type_id = rt.type_id
                WHERE rt.is_physical = TRUE
                  AND res.status IN ('approved', 'completed')
                GROUP BY TO_CHAR(res.start_time, 'Day'), EXTRACT(ISODOW FROM res.start_time)
                ORDER BY EXTRACT(ISODOW FROM res.start_time)
            """)
            rows = cur.fetchall()
    print("\n  --- Busiest Days of the Week (Physical Resources) ---")
    print_table(["Day", "Reservations"], rows)


def _resource_type_utilization():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT rt.type_name,
                       CASE WHEN rt.is_physical THEN 'Physical' ELSE 'Digital' END,
                       COUNT(DISTINCT r.resource_id) AS total_resources,
                       COUNT(res.reservation_id) AS total_reservations,
                       ROUND(COUNT(res.reservation_id)::NUMERIC /
                             NULLIF(COUNT(DISTINCT r.resource_id), 0), 1)
                FROM resource_types rt
                LEFT JOIN resources r ON rt.type_id = r.type_id
                LEFT JOIN reservations res ON r.resource_id = res.resource_id
                GROUP BY rt.type_id, rt.type_name, rt.is_physical
                ORDER BY total_reservations DESC
            """)
            rows = cur.fetchall()
    print("\n  --- Resource Type Utilization ---")
    print_table(["Type", "Category", "Resources", "Reservations", "Avg/Resource"], rows)


def _monthly_trends():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM'),
                       COUNT(*) AS created,
                       COUNT(*) FILTER (WHERE status IN ('approved', 'completed')) AS successful,
                       COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
                       COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled
                FROM reservations
                GROUP BY DATE_TRUNC('month', created_at)
                ORDER BY DATE_TRUNC('month', created_at)
            """)
            rows = cur.fetchall()
    print("\n  --- Monthly Reservation Trends ---")
    print_table(["Month", "Created", "Successful", "Rejected", "Cancelled"], rows)
