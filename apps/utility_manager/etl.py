"""
This is for bulk updates operations
"""
from typing import Any
from django.db import connection


def bulk_create_utility(data: list[Any]) -> None:
    """
    Insert in bulk energy and update whatever is in
    """
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
        try:
            cursor.executemany(query, data)
            return {
                "detail": f"{cursor.rowcount} row of energy data have been successfully created.",
                "success": True,
            }
        except Exception as error:
            return {"detail": f"Something went wrong: {str(error)}.", "success": False}
