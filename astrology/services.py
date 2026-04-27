import requests
from django.conf import settings
from django.core.cache import cache

PROKERALA_BASE = "https://api.prokerala.com/v2/astrology"


def _is_sandbox_jan1_only_error(response):
    try:
        payload = response.json()
    except ValueError:
        return False

    for err in payload.get("errors", []):
        detail = (err.get("detail") or "").lower()
        if "sandbox mode" in detail and "only january 1st" in detail:
            return True

    return False



def get_access_token():
    token = cache.get("prokerala_token")
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

    data = response.json()
    token = data.get("access_token")

    cache.set("prokerala_token", token, timeout=55 * 60)
    return token


def get_kundali(birth_date, birth_time, latitude, longitude):
    token = get_access_token()

    # FIX: use real datetime (NO sandbox date)
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

    # FIX: use actual date directly
    datetime_str = f"{date}T06:00:00+05:45"

    response = requests.get(
        f"{PROKERALA_BASE}/panchang",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )

    if response.status_code != 200 and _is_sandbox_jan1_only_error(response):
        sandbox_date = f"{date[:4]}-01-01"
        fallback_response = requests.get(
            f"{PROKERALA_BASE}/panchang",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "ayanamsa": 1,
                "coordinates": f"{latitude},{longitude}",
                "datetime": f"{sandbox_date}T06:00:00+05:45",
            }
        )

        if fallback_response.status_code == 200:
            data = fallback_response.json()
            if isinstance(data, dict):
                data["_sandbox_fallback"] = {
                    "requested_date": date,
                    "used_date": sandbox_date,
                    "active": True,
                }
            return data

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

def get_daily_horoscope(rashi_name):
    token = get_access_token()
    response=requests.get(
        f"{PROKERALA_BASE}/horoscope/daily",
        headers={"Authorization":f"Bearer{token}"},
        params={
            "rashi":rashi_name
            }
        )
    
    if response.status_code != 200:
        raise Exception(f"Daily horoscope fetch failed: {response.text}")

    api_data=response.json()
    
    parsed={
        "raw_response": api_data,
        "prediction": api_data.get("description") or api_data.get("prediction") or "",
        "love_score": parse_score(api_data.get("love")),
        "career_score": parse_score(api_data.get("career") or api_data.get("profession")),
        "health_score": parse_score(api_data.get("health")),
        "money_score": parse_score(api_data.get("money") or api_data.get("finance")),
        "lucky_color": api_data.get("lucky_color") or api_data.get("luckyColor") or "",
        "lucky_number": api_data.get("lucky_number") or api_data.get("luckyNumber") or "",
        "lucky_time": api_data.get("lucky_time") or api_data.get("luckyTime") or "",
        "advice": api_data.get("advice") or api_data.get("remedies") or "",


    }
    return parsed

def parse_score(score_text):
    if not score_text:
        return 3
    
    score_mapping={
        'poor':1,
        'fair':2,
        'good':3,
        'very good':4,
        'excellent':5
    }

    return score_mapping.get(score_text.lower(), 3 )


def get_monthly_horoscope(rashi_name, month=None):
    token=get_access_token()
    params={
        "rashi":rashi_name
    }
    if month:
        params["month"]=month
    
    response=requests.get(
        f"{PROKERALA_BASE}/horoscope/monthly",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )

    if response.status_code != 200:
        raise Exception(f"Monthly horoscope fetch failed: {response.text}")
    
    return response.json()

def get_yearly_horoscope(rashi_name, year=None):
    token=get_access_token()
    params={
        "rashi":rashi_name
    }
    if year:
        params["year"]=year
    
    response=requests.get(
        f"{PROKERALA_BASE}/horoscope/yearly",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )

    if response.status_code != 200:
        raise Exception(f"Yearly horoscope fetch failed: {response.text}")
    
    return response.json()