
import requests
from django.conf import settings

PROKERALA_BASE = "https://api.prokerala.com/v2/astrology"

def get_access_token():
    response = requests.post(
        "https://api.prokerala.com/token",
        data={
            "grant_type": "client_credentials",
            "client_id": settings.PROKERALA_CLIENT_ID,
            "client_secret": settings.PROKERALA_CLIENT_SECRET,
        }
    )
    return response.json().get("access_token")

def get_kundali(birth_date, birth_time, latitude, longitude):
    token = get_access_token()
    datetime_str = f"{birth_date}T{birth_time}+05:45"

    response = requests.get(
        f"{PROKERALA_BASE}/kundli",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )
    return response.json()

def get_panchang(date, latitude=27.7172, longitude=85.3240):
    token = get_access_token()

    response = requests.get(
        f"{PROKERALA_BASE}/panchang",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": f"{date}T06:00:00+05:45",
        }
    )
    return response.json()