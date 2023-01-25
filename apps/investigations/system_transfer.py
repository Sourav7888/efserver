"""
This file is meant to transition the high consumption investigation
to enerfrog.com portal. Temporary solution.

*Require a sytem to system token as it makes the api call
"""
import os
import requests


TOKEN = os.environ.get("ENERFROG_PORTAL_TOKEN")
ENDPOINT = os.environ.get("ENERFROG_PORTAL_HC_ENDPOINT")


def create_hc_investigation_enerfrog_portal(
    company: str = None,
    location_id: str = None,
    hc_date: str = None,
    hc_type: str = None,
    hc_description: str = None,
    hc_document: str = "",
    metadata: dict = {},
):
    try:
        req = requests.post(
            ENDPOINT + "/create-high_consumptions",
            json={
                "company": company,
                "location_id": location_id,
                "hc_date": hc_date,
                "hc_type": hc_type,
                "hc_description": hc_description,
                "hc_document": hc_document,
                "metadata": metadata,
            },
            headers={"Authorization": f"Token {TOKEN}"},
        )

    except Exception as e:
        print(e)
