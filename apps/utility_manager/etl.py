"""
This is for bulk updates operations
"""
from typing import Any
from django.db import connection


def bulk_create_utility(data: list[Any]) -> None:
    """
    Insert in bulk energy and update whatever is in
    """
    try:
        query = """
                INSERT INTO utility_manager_utilitybill (facility, billing_date, utility_type, cost, usage, unit, billing_days) 
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT no_duplicate_utility_data
                DO UPDATE SET
                billing_days=EXCLUDED.billing_days,
                cost=EXCLUDED.cost,
                usage=EXCLUDED.usage
                """

        with connection.cursor() as cursor:

            cursor.executemany(query, data)
            desc = (
                f"{cursor.rowcount} row of energy data have been successfully created."
            )

            return {"success": True, "description": desc}

    except Exception as error:

        return {"success": False, "description": str(error)}
