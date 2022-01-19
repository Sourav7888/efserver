"""
This is for bulk updates operations
"""
from typing import Any
from django.db import connection


def bulk_create_waste_data(data: list[Any]) -> None:
    """
    Insert in bulk waste and update whatever is in
    """

    print(f"[INFO] Bulk insert {len(data)} rows")

    try:
        query = """
                INSERT INTO waste_manager_wastedata (pickup_date, facility, waste_name, weight, is_recycled, waste_category, provided_by) 
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT no_duplicate_waste_data
                DO UPDATE SET
                weight=EXCLUDED.weight,
                is_recycled=EXCLUDED.is_recycled
                """

        with connection.cursor() as cursor:

            cursor.executemany(query, data)
            desc = (
                f"{cursor.rowcount} row of waste data have been successfully created."
            )

            return {"success": True, "description": desc}

    except Exception as error:
        print(error)
        return {"success": False, "description": str(error)}
