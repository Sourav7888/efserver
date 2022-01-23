"""
This is for bulk updates operations
"""
from typing import Any
from django.db import connection
from apps.shared.parsers import list_to_odr_list


def bulk_create_facility(data: list[Any]) -> None:
    """
    Insert in bulk facility and update whatever is in
    """
    try:
        query = """
                INSERT INTO core_facility (facility_name, facility_identifier, postal_code, latitude, longitude, area, address, category_type, closed) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT core_facility_facility_name_key
                DO UPDATE SET
                latitude=EXCLUDED.latitude,
                longitude=EXCLUDED.longitude,
                postal_code=EXCLUDED.postal_code,
                area=EXCLUDED.area,
                address=EXCLUDED.address,
                facility_identifier=EXCLUDED.facility_identifier,
                category_type=EXCLUDED.category_type,
                closed=EXCLUDED.closed
                """

        with connection.cursor() as cursor:

            cursor.executemany(
                query,
                list_to_odr_list(
                    data,
                    (
                        "facility_name",
                        "facility_identifier",
                        "postal_code",
                        "latitude",
                        "longitude",
                        "area",
                        "address",
                        "category_type",
                        "closed",
                    ),
                ),
            )
            desc = f"{cursor.rowcount} row of facility data have been successfully created."

            return {"success": True, "description": desc}

    except Exception as error:
        print(error)
        return {"success": False, "description": str(error)}
