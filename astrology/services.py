import requests
from django.conf import settings
from django.core.cache import cache

PROKERALA_BASE = "https://api.prokerala.com/v2/astrology"

def get_access_token():
    token=cache.get("prokerala_token")
    if token:
        return token
    
    response = requests.post(
        "https://api.prokerala.com/token",
        data={
            "grant_type": "client_credentials",
            "client_id": settings.PROKERALA_CLIENT_ID,
            "client_secret": settings.PROKERALA_CLIENT_SECRET,
        }
    )
    if response.status_code != 200:
        raise Exception(f"Token fetch failed: {response.text}")
    
    data=response.json()
    token=data.get("access_token")


    cache.set("prokerala_token", token, timeout=55*60)  # Cache for 55 minutes
    return token

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

    if response.status_code != 200:
        raise Exception(f"Kundali fetch failed: {response.text}")
    return response.json()

def get_panchang(date, latitude=27.7172, longitude=85.3240):
    token = get_access_token()
    datetime_str = f"{date}T06:00:00+05:45"  # Default time for panchang

    response = requests.get(
        f"{PROKERALA_BASE}/panchang",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )

    if response.status_code != 200:
        raise Exception(f"Panchang fetch failed: {response.text}")
    
    return response.json()

def get_planet_positions(birth_date, birth_time, latitude, longitude):
    token = get_access_token()
    datetime_str = f"{birth_date}T{birth_time}+05:45"

    response = requests.get(
        f"{PROKERALA_BASE}/planet-position",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )

    if response.status_code != 200:
        raise Exception(f"Planet positions fetch failed: {response.text}")
    
    return response.json()