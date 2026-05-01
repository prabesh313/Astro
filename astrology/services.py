# astrology/services.py - STABLE VERSION WITH FALLBACK
import requests
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, date

def get_access_token():
    token = cache.get('prokerala_token')
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
    cache.set('prokerala_token', token, timeout=55*60)
    return token


def get_kundali(birth_date, birth_time, latitude, longitude):
    token = get_access_token()
    sandbox_date = f"{birth_date[:4]}-01-01"
    datetime_str = f"{sandbox_date}T{birth_time}+05:45"

    response = requests.get(
        "https://api.prokerala.com/v2/astrology/kundli",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )

    if response.status_code != 200:
        raise Exception(f"Kundali API error: {response.text}")

    return response.json()


def get_panchang(date_str, latitude=27.7172, longitude=85.3240):
    token = get_access_token()
    sandbox_date = f"{date_str[:4]}-01-01"
    datetime_str = f"{sandbox_date}T06:00:00+05:45"

    response = requests.get(
        "https://api.prokerala.com/v2/astrology/panchang",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )

    if response.status_code != 200:
        raise Exception(f"Panchang API error: {response.text}")

    return response.json()


def get_planet_positions(birth_date, birth_time, latitude, longitude):
    token = get_access_token()
    sandbox_date = f"{birth_date[:4]}-01-01"
    datetime_str = f"{sandbox_date}T{birth_time}+05:45"

    response = requests.get(
        "https://api.prokerala.com/v2/astrology/planet-position",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "ayanamsa": 1,
            "coordinates": f"{latitude},{longitude}",
            "datetime": datetime_str,
        }
    )

    if response.status_code != 200:
        raise Exception(f"Planet position API error: {response.text}")

    return response.json()

HOROSCOPE_DATABASE = {
    'aries': {
        'prediction': 'आज तपाईंको लागि उत्कृष्ट दिन हुनेछ। व्यवसायिक क्षेत्रमा सफलता मिल्नेछ। नयाँ अवसरहरू प्राप्त हुन सक्छन्। आत्मविश्वास र साहसले साथ दिनेछ।',
        'love_score': 4,
        'career_score': 5,
        'health_score': 4,
        'money_score': 4,
        'lucky_color': 'Red',
        'lucky_number': 7,
        'advice': 'आजको दिन तपाईंको लागि धेरै महत्वपूर्ण छ। नयाँ सुरुवात गर्ने राम्रो समय हो। सकारात्मक सोच राख्नुहोस्।'
    },
    'taurus': {
        'prediction': 'आर्थिक लाभ प्राप्त हुनेछ। नयाँ सम्भावनाहरू देखा पर्नेछन्। धैर्य र स्थिरता कायम राख्नुहोस्। शान्ति र सन्तुलन पाइनेछ।',
        'love_score': 3,
        'career_score': 4,
        'health_score': 5,
        'money_score': 5,
        'lucky_color': 'Green',
        'lucky_number': 6,
        'advice': 'धन व्यवस्थापनमा ध्यान दिनुहोस्। दीर्घकालीन योजना बनाउनुहोस्।'
    },
    'gemini': {
        'prediction': 'सञ्चार क्षेत्रमा सफलता मिल्नेछ। नयाँ सम्बन्धहरू बन्नेछन्। बौद्धिक काममा राम्रो प्रदर्शन हुनेछ। मानसिक शान्ति प्राप्त हुनेछ।',
        'love_score': 5,
        'career_score': 5,
        'health_score': 4,
        'money_score': 3,
        'lucky_color': 'Yellow',
        'lucky_number': 5,
        'advice': 'आफ्नो प्रतिभाको सही उपयोग गर्नुहोस्। सामाजिक गतिविधिमा सहभागी हुनुहोस्।'
    },
    'cancer': {
        'prediction': 'पारिवारिक सुख प्राप्त हुनेछ। भावनात्मक सन्तुलन कायम रहनेछ। घरपरिवारमा खुशी छाउनेछ। प्रेम र सहानुभूति बढ्नेछ।',
        'love_score': 5,
        'career_score': 3,
        'health_score': 3,
        'money_score': 4,
        'lucky_color': 'White',
        'lucky_number': 2,
        'advice': 'परिवारसँग समय बिताउनुहोस्। भावनाहरू नियन्त्रणमा राख्नुहोस्।'
    },
    'leo': {
        'prediction': 'आत्मविश्वास बढ्नेछ। नेतृत्व क्षमता देखाउने अवसर मिल्नेछ। सार्वजनिक मान्यता प्राप्त हुनेछ। प्रभाव बढ्नेछ।',
        'love_score': 4,
        'career_score': 5,
        'health_score': 5,
        'money_score': 4,
        'lucky_color': 'Gold',
        'lucky_number': 1,
        'advice': 'आफ्नो क्षमता देखाउनुहोस्। नेतृत्वको भूमिका लिनुहोस्।'
    },
    'virgo': {
        'prediction': 'विश्लेषणात्मक काममा सफलता मिल्नेछ। विवरणमा ध्यान दिनुहुनेछ। व्यावहारिक दृष्टिकोण रहनेछ। समस्या समाधान हुनेछ।',
        'love_score': 3,
        'career_score': 5,
        'health_score': 4,
        'money_score': 4,
        'lucky_color': 'Green',
        'lucky_number': 5,
        'advice': 'विवरणमा ध्यान दिनुहोस्। अत्यधिक आलोचनात्मक नबन्नुहोस्।'
    },
    'libra': {
        'prediction': 'सन्तुलन र सामञ्जस्य प्राप्त हुनेछ। सहकार्यमा सफलता मिल्नेछ। सौन्दर्य र कलामा रुचि बढ्नेछ। सम्बन्ध सुधार हुनेछ।',
        'love_score': 5,
        'career_score': 3,
        'health_score': 4,
        'money_score': 4,
        'lucky_color': 'Blue',
        'lucky_number': 6,
        'advice': 'सन्तुलन कायम राख्नुहोस्। सम्झौताका लागि तयार रहनुहोस्।'
    },
    'scorpio': {
        'prediction': 'गहिरो अनुभूति र शक्ति प्राप्त हुनेछ। परिवर्तन र पुनर्जन्मको समय हो। गोप्य मामलामा सफलता मिल्नेछ।',
        'love_score': 4,
        'career_score': 3,
        'health_score': 2,
        'money_score': 4,
        'lucky_color': 'Red',
        'lucky_number': 8,
        'advice': 'आत्मविश्वास कायम राख्नुहोस्। गोप्य कुराहरू सुरक्षित राख्नुहोस्।'
    },
    'sagittarius': {
        'prediction': 'नयाँ अवसर र विस्तारको समय हो। यात्रामा भाग्य साथ दिनेछ। शिक्षा र ज्ञानमा वृद्धि हुनेछ।',
        'love_score': 4,
        'career_score': 4,
        'health_score': 5,
        'money_score': 3,
        'lucky_color': 'Blue',
        'lucky_number': 3,
        'advice': 'नयाँ अवसर स्वीकार गर्नुहोस्। यात्राको योजना बनाउनुहोस्।'
    },
    'capricorn': {
        'prediction': 'कडा परिश्रमको फल प्राप्त हुनेछ। लक्ष्य प्राप्ति नजिक हुनेछ। जिम्मेवारी पूरा हुनेछ। दीर्घकालीन लाभ हुनेछ।',
        'love_score': 2,
        'career_score': 5,
        'health_score': 4,
        'money_score': 5,
        'lucky_color': 'Black',
        'lucky_number': 8,
        'advice': 'कडा मेहनत जारी राख्नुहोस्। धैर्य राख्नुहोस्।'
    },
    'aquarius': {
        'prediction': 'नवीन विचार र प्रविधिको समय हो। मित्रता र समुदायसँग सम्बन्ध बलियो हुनेछ। स्वतन्त्र सोच विकसित हुनेछ।',
        'love_score': 3,
        'career_score': 4,
        'health_score': 4,
        'money_score': 2,
        'lucky_color': 'Blue',
        'lucky_number': 7,
        'advice': 'नयाँ सोच अपनाउनुहोस्। साथीहरूसँग सम्बन्ध बलियो बनाउनुहोस्।'
    },
    'pisces': {
        'prediction': 'कल्पना र सृजनशीलता बढ्नेछ। आध्यात्मिक जागरण हुनेछ। करुणा र सहानुभूति बढ्नेछ।',
        'love_score': 5,
        'career_score': 3,
        'health_score': 2,
        'money_score': 3,
        'lucky_color': 'Sea Green',
        'lucky_number': 7,
        'advice': 'सृजनशीलता व्यक्त गर्नुहोस्। आध्यात्मिक अभ्यास गर्नुहोस्।'
    }
}


def get_daily_horoscope(rashi_name, target_date=None):
    
    if not target_date:
        target_date = str(date.today())

    rashi = rashi_name.lower()
    
    # Get mock data for this rashi
    if rashi not in HOROSCOPE_DATABASE:
        raise Exception(f"Invalid rashi: {rashi}")
    
    horoscope_data = HOROSCOPE_DATABASE[rashi]
    
    parsed = {
        "raw_response": {"source": "mock_data", "note": "Prokerala free tier limitation"},
        "prediction": horoscope_data['prediction'],
        "love_score": horoscope_data['love_score'],
        "career_score": horoscope_data['career_score'],
        "health_score": horoscope_data['health_score'],
        "money_score": horoscope_data['money_score'],
        "lucky_color": horoscope_data['lucky_color'],
        "lucky_number": horoscope_data['lucky_number'],  # Integer, not string
        "lucky_time": "",
        "advice": horoscope_data['advice'],
    }
    
    return parsed