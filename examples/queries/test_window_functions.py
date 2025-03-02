test_query = {
    "name": "testing window functions",
    "query": {
        "select": {
            "Reservation": {
                "id": {},
                "date_time_start": {},
                "date_time_end": {},
                "over(lag(date_time_end), order_by=resource_id.desc())": {
                    "label": "gap_minutes_before"
                },
                "over(lead(date_time_start), order_by=resource_id.desc())": {
                    "label": "gap_minutes_after"
                },
            }
        }
    },
    "expected_sql": """
SELECT reservation.id,
       reservation.date_time_start,
       reservation.date_time_end,
       lag(reservation.date_time_end) OVER (ORDER BY reservation.resource_id desc) as gap_minutes_before,
       lead(reservation.date_time_start) OVER (ORDER BY reservation.resource_id desc) as gap_minutes_after
FROM   reservation
    """,
}
