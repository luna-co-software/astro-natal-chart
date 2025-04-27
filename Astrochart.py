"""
Astrology GUI App for Natal Charts (Styled like Astro.com)
Dependencies: skyfield, pgeocode, pandas, timezonefinder, pytz, matplotlib, tkinter, pyswisseph
Install with:
    pip install skyfield pgeocode pandas timezonefinder pytz matplotlib tk pyswisseph
Also, download Swiss Ephemeris data files (e.g., seas_18.se1, semo_18.se1, sepl_18.se1) and place them in an 'ephe' directory.
"""

import datetime
import pytz
import pgeocode
import pandas as pd
from timezonefinder import TimezoneFinder
import matplotlib
matplotlib.rcParams.update({
    'axes.edgecolor': 'gray',
    'axes.linewidth': 0.5,
    'xtick.color': 'gray',
    'ytick.color': 'gray',
    'text.color': '#333333',
    'font.size': 10,
    'font.family': 'DejaVu Sans',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.edgecolor': 'white'
})
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from geopy.geocoders import Nominatim
from fuzzywuzzy import fuzz

import re
import swisseph as swe

# Set path to Swiss Ephemeris files
swe.set_ephe_path('ephe')

ELEMENT_COLORS = {
    'Fire': '#FF5733',
    'Water': '#0077B6',
    'Earth': '#4CAF50',
    'Air': '#FFC300'
}

sign_elements = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air'
}

# Interpretations for planets in signs, houses, and aspects
PLANET_IN_SIGN = {
    'Sun': {
        'Aries': 'Bold and pioneering personality.',
        'Taurus': 'Grounded and values stability.',
        'Gemini': 'Curious and communicative.',
        'Cancer': 'Nurturing and emotional.',
        'Leo': 'Confident and dramatic.',
        'Virgo': 'Analytical and detail-oriented.',
        'Libra': 'Charming and seeks balance.',
        'Scorpio': 'Intense and transformative.',
        'Sagittarius': 'Adventurous and philosophical.',
        'Capricorn': 'Ambitious and disciplined.',
        'Aquarius': 'Innovative and independent.',
        'Pisces': 'Compassionate and dreamy.'
    },
    'Moon': {
        'Aries': 'Emotionally impulsive and energetic.',
        'Taurus': 'Seeks emotional security and comfort.',
        'Gemini': 'Emotionally versatile and curious.',
        'Cancer': 'Deeply intuitive and nurturing.',
        'Leo': 'Emotionally expressive and dramatic.',
        'Virgo': 'Emotionally analytical and practical.',
        'Libra': 'Seeks emotional harmony and partnership.',
        'Scorpio': 'Intense and deeply emotional.',
        'Sagittarius': 'Emotionally adventurous and optimistic.',
        'Capricorn': 'Emotionally reserved and responsible.',
        'Aquarius': 'Emotionally detached and unique.',
        'Pisces': 'Highly empathetic and intuitive.'
    },
    'Mercury': {
        'Aries': 'Quick thinking and direct communication.',
        'Taurus': 'Practical and deliberate in thought.',
        'Gemini': 'Highly communicative and adaptable.',
        'Cancer': 'Intuitive and emotionally driven thinking.',
        'Leo': 'Expressive and dramatic in communication.',
        'Virgo': 'Analytical and precise in thought.',
        'Libra': 'Diplomatic and balanced in communication.',
        'Scorpio': 'Deep and investigative thinking.',
        'Sagittarius': 'Broad-minded and philosophical in thought.',
        'Capricorn': 'Structured and goal-oriented thinking.',
        'Aquarius': 'Innovative and unconventional in communication.',
        'Pisces': 'Imaginative and intuitive thinking.'
    },
    'Venus': {
        'Aries': 'Passionate and impulsive in love.',
        'Taurus': 'Sensual and values stability in relationships.',
        'Gemini': 'Playful and intellectually driven in love.',
        'Cancer': 'Nurturing and protective in relationships.',
        'Leo': 'Dramatic and generous in love.',
        'Virgo': 'Practical and service-oriented in relationships.',
        'Libra': 'Romantic and seeks harmony in love.',
        'Scorpio': 'Intense and deeply emotional in relationships.',
        'Sagittarius': 'Adventurous and freedom-loving in love.',
        'Capricorn': 'Serious and committed in relationships.',
        'Aquarius': 'Unconventional and independent in love.',
        'Pisces': 'Romantic and dreamy in relationships.'
    },
    'Mars': {
        'Aries': 'Assertive and competitive.',
        'Taurus': 'Steady and persistent in action.',
        'Gemini': 'Versatile and mentally driven in action.',
        'Cancer': 'Protective and emotionally driven in action.',
        'Leo': 'Bold and dramatic in action.',
        'Virgo': 'Precise and methodical in action.',
        'Libra': 'Balanced but indecisive in action.',
        'Scorpio': 'Intense and strategic in action.',
        'Sagittarius': 'Adventurous and impulsive in action.',
        'Capricorn': 'Disciplined and ambitious in action.',
        'Aquarius': 'Innovative and rebellious in action.',
        'Pisces': 'Intuitive and compassionate in action.'
    },
    'Jupiter': {
        'Aries': 'Optimistic and pioneering in growth.',
        'Taurus': 'Growth through stability and material abundance.',
        'Gemini': 'Expansive through communication and learning.',
        'Cancer': 'Growth through nurturing and family.',
        'Leo': 'Generous and dramatic in expansion.',
        'Virgo': 'Growth through precision and service.',
        'Libra': 'Expansion through partnerships and harmony.',
        'Scorpio': 'Deep and transformative growth.',
        'Sagittarius': 'Philosophical and adventurous in expansion.',
        'Capricorn': 'Growth through discipline and structure.',
        'Aquarius': 'Innovative and humanitarian in expansion.',
        'Pisces': 'Spiritual and compassionate growth.'
    },
    'Saturn': {
        'Aries': 'Challenges with impulsivity, learning discipline.',
        'Taurus': 'Focus on material security and patience.',
        'Gemini': 'Challenges with communication, seeking clarity.',
        'Cancer': 'Lessons in emotional security and family.',
        'Leo': 'Challenges with ego, learning humility.',
        'Virgo': 'Focus on precision and responsibility.',
        'Libra': 'Lessons in relationships and balance.',
        'Scorpio': 'Deep lessons in transformation and control.',
        'Sagittarius': 'Challenges with beliefs, seeking wisdom.',
        'Capricorn': 'Strong sense of responsibility and structure.',
        'Aquarius': 'Lessons in innovation and community.',
        'Pisces': 'Challenges with boundaries, seeking spirituality.'
    },
    'Uranus': {
        'Aries': 'Innovative and impulsive change.',
        'Taurus': 'Unconventional approach to stability.',
        'Gemini': 'Restless and inventive in communication.',
        'Cancer': 'Unpredictable emotional changes.',
        'Leo': 'Dramatic and unique self-expression.',
        'Virgo': 'Innovative in routines and health.',
        'Libra': 'Unconventional in relationships.',
        'Scorpio': 'Intense and transformative change.',
        'Sagittarius': 'Adventurous and freedom-seeking change.',
        'Capricorn': 'Innovative restructuring of traditions.',
        'Aquarius': 'Highly original and humanitarian.',
        'Pisces': 'Intuitive and spiritual innovation.'
    },
    'Neptune': {
        'Aries': 'Idealistic and impulsive dreams.',
        'Taurus': 'Dreamy approach to material beauty.',
        'Gemini': 'Imaginative and scattered communication.',
        'Cancer': 'Highly intuitive and nurturing dreams.',
        'Leo': 'Dramatic and idealistic self-expression.',
        'Virgo': 'Idealistic in service and health.',
        'Libra': 'Dreamy and romantic in relationships.',
        'Scorpio': 'Deep and mystical imagination.',
        'Sagittarius': 'Spiritual and philosophical dreams.',
        'Capricorn': 'Idealistic restructuring of reality.',
        'Aquarius': 'Visionary and humanitarian dreams.',
        'Pisces': 'Highly spiritual and intuitive.'
    },
    'Pluto': {
        'Aries': 'Transformative and impulsive energy.',
        'Taurus': 'Deep transformation in values and stability.',
        'Gemini': 'Transformative communication and ideas.',
        'Cancer': 'Deep emotional transformation.',
        'Leo': 'Powerful and dramatic transformation.',
        'Virgo': 'Transformative in health and service.',
        'Libra': 'Deep transformation in relationships.',
        'Scorpio': 'Intensely transformative and powerful.',
        'Sagittarius': 'Transformation through beliefs and adventure.',
        'Capricorn': 'Powerful restructuring of ambitions.',
        'Aquarius': 'Transformative in innovation and community.',
        'Pisces': 'Deep spiritual transformation.'
    },
    'True Node': {
        'Aries': 'Destiny tied to independence and courage.',
        'Taurus': 'Destiny tied to stability and values.',
        'Gemini': 'Destiny through communication and learning.',
        'Cancer': 'Destiny tied to family and nurturing.',
        'Leo': 'Destiny through self-expression and leadership.',
        'Virgo': 'Destiny through service and precision.',
        'Libra': 'Destiny tied to relationships and balance.',
        'Scorpio': 'Destiny through transformation and depth.',
        'Sagittarius': 'Destiny tied to adventure and wisdom.',
        'Capricorn': 'Destiny through ambition and structure.',
        'Aquarius': 'Destiny tied to innovation and community.',
        'Pisces': 'Destiny through spirituality and compassion.'
    },
    'Chiron': {
        'Aries': 'Wound related to identity and courage.',
        'Taurus': 'Wound related to self-worth and stability.',
        'Gemini': 'Wound related to communication and learning.',
        'Cancer': 'Wound tied to family and emotional security.',
        'Leo': 'Wound related to self-expression and recognition.',
        'Virgo': 'Wound tied to perfectionism and service.',
        'Libra': 'Wound related to relationships and balance.',
        'Scorpio': 'Wound tied to transformation and power.',
        'Sagittarius': 'Wound related to beliefs and freedom.',
        'Capricorn': 'Wound tied to authority and ambition.',
        'Aquarius': 'Wound related to individuality and community.',
        'Pisces': 'Wound tied to spirituality and boundaries.'
    },
}

PLANET_IN_HOUSE = {
    'Sun': {
        1: 'Strong focus on self-identity and personal expression.',
        2: 'Focus on personal values and financial security.',
        3: 'Emphasis on communication and learning.',
        4: 'Strong connection to home and family.',
        5: 'Focus on creativity and self-expression.',
        6: 'Emphasis on health and daily routines.',
        7: 'Focus on partnerships and relationships.',
        8: 'Interest in transformation and shared resources.',
        9: 'Focus on philosophy, travel, and higher learning.',
        10: 'Strong drive for career and public recognition.',
        11: 'Focus on friendships and community.',
        12: 'Emphasis on spirituality and the subconscious.'
    },
    'Moon': {
        1: 'Emotionally expressive and self-focused.',
        2: 'Emotional security tied to finances and possessions.',
        3: 'Emotionally curious and communicative.',
        4: 'Deep emotional connection to home and family.',
        5: 'Emotionally tied to creativity and romance.',
        6: 'Emotional focus on health and service.',
        7: 'Emotional fulfillment through relationships.',
        8: 'Deep emotional transformations and intensity.',
        9: 'Emotional need for adventure and learning.',
        10: 'Emotional investment in career and public life.',
        11: 'Emotional connection to friends and groups.',
        12: 'Highly intuitive and spiritually focused.'
    },
    'Mercury': {
        1: 'Communicative and intellectual identity.',
        2: 'Focus on financial communication and thinking.',
        3: 'Strong emphasis on learning and communication.',
        4: 'Intellectual connection to home and family.',
        5: 'Creative and playful communication.',
        6: 'Focus on health and analytical routines.',
        7: 'Communication-centered relationships.',
        8: 'Deep and investigative thinking.',
        9: 'Focus on philosophy and intellectual expansion.',
        10: 'Career driven by communication and ideas.',
        11: 'Intellectual focus on friendships and groups.',
        12: 'Intuitive and subconscious communication.'
    },
    'Venus': {
        1: 'Charming and relationship-focused identity.',
        2: 'Focus on financial beauty and values.',
        3: 'Love for learning and communication.',
        4: 'Harmonious and beautiful home life.',
        5: 'Romantic and creative expression.',
        6: 'Love expressed through service and health.',
        7: 'Strong focus on partnerships and harmony.',
        8: 'Deep and transformative relationships.',
        9: 'Love for travel and philosophical beauty.',
        10: 'Career tied to beauty and relationships.',
        11: 'Harmonious friendships and social connections.',
        12: 'Romantic and spiritual connections.'
    },
    'Mars': {
        1: 'Assertive and action-oriented identity.',
        2: 'Driven to achieve financial security.',
        3: 'Energetic communication and learning.',
        4: 'Protective and active home life.',
        5: 'Passionate and creative expression.',
        6: 'Driven in health and daily routines.',
        7: 'Assertive in relationships.',
        8: 'Intense and transformative energy.',
        9: 'Adventurous and action-oriented learning.',
        10: 'Ambitious and driven career.',
        11: 'Energetic focus on friendships and groups.',
        12: 'Subconscious drive and spiritual action.'
    },
    'Jupiter': {
        1: 'Optimistic and expansive identity.',
        2: 'Growth through financial abundance.',
        3: 'Expansive communication and learning.',
        4: 'Growth through family and home.',
        5: 'Joyful and expansive creativity.',
        6: 'Growth through health and service.',
        7: 'Expansion through partnerships.',
        8: 'Deep and transformative growth.',
        9: 'Strong focus on philosophy and travel.',
        10: 'Expansive and fortunate career.',
        11: 'Growth through friendships and community.',
        12: 'Spiritual and philosophical expansion.'
    },
    'Saturn': {
        1: 'Lessons in self-identity and discipline.',
        2: 'Focus on financial responsibility.',
        3: 'Challenges in communication and learning.',
        4: 'Lessons in family and home structure.',
        5: 'Discipline in creativity and romance.',
        6: 'Focus on health and routine responsibility.',
        7: 'Challenges in relationships and commitment.',
        8: 'Lessons in transformation and control.',
        9: 'Discipline in philosophy and travel.',
        10: 'Strong focus on career and responsibility.',
        11: 'Lessons in friendships and community.',
        12: 'Challenges in spirituality and boundaries.'
    },
    'Uranus': {
        1: 'Unconventional and unique identity.',
        2: 'Innovative approach to finances.',
        3: 'Restless and inventive communication.',
        4: 'Unpredictable home and family life.',
        5: 'Unique and rebellious creativity.',
        6: 'Innovative in health and routines.',
        7: 'Unconventional relationships.',
        8: 'Sudden and transformative changes.',
        9: 'Unique approach to philosophy and travel.',
        10: 'Innovative and rebellious career.',
        11: 'Strong focus on unique friendships.',
        12: 'Unconventional spirituality.'
    },
    'Neptune': {
        'Aries': 'Idealistic and impulsive dreams.',
        'Taurus': 'Dreamy approach to material beauty.',
        'Gemini': 'Imaginative and scattered communication.',
        'Cancer': 'Highly intuitive and nurturing dreams.',
        'Leo': 'Dramatic and idealistic self-expression.',
        'Virgo': 'Idealistic in service and health.',
        'Libra': 'Dreamy and romantic in relationships.',
        'Scorpio': 'Deep and mystical imagination.',
        'Sagittarius': 'Spiritual and philosophical dreams.',
        'Capricorn': 'Idealistic restructuring of reality.',
        'Aquarius': 'Visionary and humanitarian dreams.',
        'Pisces': 'Highly spiritual and intuitive.'
    },
    'Pluto': {
        'Aries': 'Transformative and impulsive energy.',
        'Taurus': 'Deep transformation in values and stability.',
        'Gemini': 'Transformative communication and ideas.',
        'Cancer': 'Deep emotional transformation.',
        'Leo': 'Powerful and dramatic transformation.',
        'Virgo': 'Transformative in health and service.',
        'Libra': 'Deep transformation in relationships.',
        'Scorpio': 'Intensely transformative and powerful.',
        'Sagittarius': 'Transformation through beliefs and adventure.',
        'Capricorn': 'Powerful restructuring of ambitions.',
        'Aquarius': 'Transformative in innovation and community.',
        'Pisces': 'Deep spiritual transformation.'
    },
    'True Node': {
        'Aries': 'Destiny tied to independence and courage.',
        'Taurus': 'Destiny tied to stability and values.',
        'Gemini': 'Destiny through communication and learning.',
        'Cancer': 'Destiny tied to family and nurturing.',
        'Leo': 'Destiny through self-expression and leadership.',
        'Virgo': 'Destiny through service and precision.',
        'Libra': 'Destiny tied to relationships and balance.',
        'Scorpio': 'Destiny through transformation and depth.',
        'Sagittarius': 'Destiny tied to adventure and wisdom.',
        'Capricorn': 'Destiny through ambition and structure.',
        'Aquarius': 'Destiny tied to innovation and community.',
        'Pisces': 'Destiny through spirituality and compassion.'
    },
    'Chiron': {
        'Aries': 'Wound related to identity and courage.',
        'Taurus': 'Wound related to self-worth and stability.',
        'Gemini': 'Wound related to communication and learning.',
        'Cancer': 'Wound tied to family and emotional security.',
        'Leo': 'Wound related to self-expression and recognition.',
        'Virgo': 'Wound tied to perfectionism and service.',
        'Libra': 'Wound related to relationships and balance.',
        'Scorpio': 'Wound tied to transformation and power.',
        'Sagittarius': 'Wound related to beliefs and freedom.',
        'Capricorn': 'Wound tied to authority and ambition.',
        'Aquarius': 'Wound related to individuality and community.',
        'Pisces': 'Wound tied to spirituality and boundaries.'
    },
}

ASPECT_INTERPRETATIONS = {
    'Conjunction': 'Intense blending of energies, amplifying both planets’ traits.',
    'Sextile': 'Harmonious opportunity for growth and collaboration.',
    'Square': 'Tension and challenges that drive growth through conflict.',
    'Trine': 'Natural flow and ease, bringing talent and harmony.',
    'Opposition': 'Polarity and tension, requiring balance and compromise.'
}

def validate_inputs(date_str, time_str, location_input, country_code):
    date_pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    if not re.match(date_pattern, date_str):
        raise ValueError("Date must be in YYYY-MM-DD format (e.g., 1979-11-09)")

    time_pattern = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
    if not re.match(time_pattern, time_str):
        raise ValueError("Time must be in HH:MM 24-hour format (e.g., 03:38)")

    if not location_input:
        raise ValueError("Location cannot be empty")

    if country_code and not re.match(r"^[A-Za-z]{2,3}$", country_code):
        raise ValueError("Country code must be 2-3 alphabetic characters (e.g., US)")

def get_coordinates(location_input, country_code="US"):
    geolocator = Nominatim(user_agent="astrochart_app")

    try:
        location = geolocator.geocode(location_input + ("," + country_code if country_code else ""))
        if location:
            print(f"Coordinates for {location_input}: Lat {location.latitude}, Lon {location.longitude}")
            return location.latitude, location.longitude
    except Exception as e:
        raise ValueError(f"Error finding coordinates: {str(e)}")

    try:
        search_terms = [
            f"{location_input}, {country_code}",
            f"{location_input.split(',')[0]}, {country_code}" if ',' in location_input else location_input,
        ]
        best_guess = None
        best_score = 0

        for term in search_terms:
            results = geolocator.geocode(term, exactly_one=False, limit=5)
            if results:
                for result in results:
                    score = fuzz.partial_ratio(location_input.lower(), result.address.lower())
                    if score > best_score:
                        best_score = score
                        best_guess = result

        if best_guess and best_score >= 70:
            print(f"Did you mean: {best_guess.address}?")
            return best_guess.latitude, best_guess.longitude
        else:
            raise ValueError(f"No close matches found for location: {location_input}")
    except Exception as e:
        raise ValueError(f"Error with fuzzy location search: {str(e)}")

def get_timezone(lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if not tz_name:
        raise ValueError("Could not determine the timezone for the coordinates.")
    return pytz.timezone(tz_name)

def compute_house_cusps_and_points(date_str, time_str, lat, lon, timezone):
    dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
    local_dt = timezone.localize(dt)
    utc_dt = local_dt.astimezone(pytz.UTC)

    utc_year, utc_month, utc_day = utc_dt.year, utc_dt.month, utc_dt.day
    utc_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_year, utc_month, utc_day, utc_hour)
    print(f"Julian Day: {jd}")

    house_cusps, ascmc = swe.houses(jd, lat, lon, b'P')  # 'P' for Placidus
    ascendant = ascmc[0]
    midheaven = ascmc[1]
    print(f"House Cusps: {house_cusps}")
    print(f"Ascendant: {ascendant}, Midheaven: {midheaven}")

    return house_cusps, ascendant, midheaven

def compute_planetary_longitudes(date_str, time_str, location_input, country_code='US'):
    lat, lon = get_coordinates(location_input, country_code)
    timezone = get_timezone(lat, lon)
    dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
    local_dt = timezone.localize(dt)
    utc_dt = local_dt.astimezone(pytz.UTC)

    utc_year, utc_month, utc_day = utc_dt.year, utc_dt.month, utc_dt.day
    utc_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_year, utc_month, utc_day, utc_hour)

    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO,
        'True Node': swe.TRUE_NODE,
        'Chiron': swe.CHIRON,
    }

    planet_colors = {
        'Sun': 'gold',
        'Moon': 'silver',
        'Mercury': 'grey',
        'Venus': 'pink',
        'Mars': 'red',
        'Jupiter': 'orange',
        'Saturn': 'brown',
        'Uranus': 'cyan',
        'Neptune': 'blue',
        'Pluto': 'darkred',
        'True Node': 'black',
        'Chiron': 'green',
    }

    planet_glyphs = {
        'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
        'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆',
        'Pluto': '♇', 'True Node': '☊', 'Chiron': '⚷'
    }

    longitudes = {}
    retrogrades = {}

    swe.set_topo(lat, lon, 0)
    for name, planet_id in planets.items():
        pos, ret = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
        longitude = pos[0]
        longitudes[name] = longitude
        retrogrades[name] = pos[3] < 0

    house_cusps, ascendant, midheaven = compute_house_cusps_and_points(date_str, time_str, lat, lon, timezone)
    return longitudes, retrogrades, planet_colors, house_cusps, ascendant, midheaven, local_dt, planet_glyphs

def compute_aspects(longitudes):
    aspects = []
    major_aspects = {
        'Conjunction': (0, 6),
        'Sextile': (60, 4),
        'Square': (90, 7),
        'Trine': (120, 6),
        'Opposition': (180, 8),
    }

    filtered_longitudes = {k: v for k, v in longitudes.items() if v is not None}
    planet_names = list(filtered_longitudes.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            # Skip if either planet is Chiron
            if 'Chiron' in (p1, p2):
                continue
            lon1, lon2 = filtered_longitudes[p1], filtered_longitudes[p2]
            diff = min((lon1 - lon2) % 360, (lon2 - lon1) % 360)
            for aspect_name, (angle, orb) in major_aspects.items():
                if ('Mars' in (p1, p2) or 'Jupiter' in (p1, p2) or 'Saturn' in (p1, p2) or
                    'Uranus' in (p1, p2) or 'Neptune' in (p1, p2) or 'Pluto' in (p1, p2)) and aspect_name == 'Conjunction':
                    orb = 5
                if ('Mercury' in (p1, p2) and 'Uranus' in (p1, p2)) and aspect_name == 'Sextile':
                    continue
                if ('True Node' in (p1, p2) and ('Mercury' in (p1, p2) or 'Venus' in (p1, p2) or 'Sun' in (p1, p2))) and aspect_name in ['Square']:
                    continue
                if abs(diff - angle) <= orb:
                    aspects.append((p1, p2, aspect_name, diff))
                    break

    aspects.sort(key=lambda x: x[3])
    return aspects

    filtered_longitudes = {k: v for k, v in longitudes.items() if v is not None}
    planet_names = list(filtered_longitudes.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            lon1, lon2 = filtered_longitudes[p1], filtered_longitudes[p2]
            diff = min((lon1 - lon2) % 360, (lon2 - lon1) % 360)
            for aspect_name, (angle, orb) in major_aspects.items():
                if ('Mars' in (p1, p2) or 'Jupiter' in (p1, p2) or 'Saturn' in (p1, p2) or
                    'Uranus' in (p1, p2) or 'Neptune' in (p1, p2) or 'Pluto' in (p1, p2)) and aspect_name == 'Conjunction':
                    orb = 5
                if 'Chiron' in (p1, p2):
                    orb = 8
                if 'Chiron' in (p1, p2) and aspect_name == 'Square':
                    orb = 5
                if (p1 == 'Venus' and p2 == 'Chiron') or (p1 == 'Chiron' and p2 == 'Venus') and aspect_name == 'Square':
                    continue
                if ('Mercury' in (p1, p2) and 'Uranus' in (p1, p2)) and aspect_name == 'Sextile':
                    continue
                if ('True Node' in (p1, p2) and ('Mercury' in (p1, p2) or 'Venus' in (p1, p2) or 'Sun' in (p1, p2))) and aspect_name in ['Square']:
                    continue
                if abs(diff - angle) <= orb:
                    aspects.append((p1, p2, aspect_name, diff))
                    break

    aspects.sort(key=lambda x: x[3])
    return aspects

def get_sign_and_house(longitude, house_cusps):
    if longitude is None:
        return None, None

    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_idx = int(longitude // 30)
    sign = signs[sign_idx]

    lon = longitude % 360
    house = 1
    for i in range(len(house_cusps)):
        cusp = house_cusps[i] % 360
        next_cusp = house_cusps[(i + 1) % 12] % 360
        if next_cusp < cusp:  # Crossing 0°
            if lon >= cusp or lon < next_cusp:
                house = (i + 1) % 12 if i + 1 != 12 else 12
                break
        else:
            if cusp <= lon < next_cusp:
                house = (i + 1) % 12 if i + 1 != 12 else 12
                break

    return sign, house

def draw_chart(longitudes, retrogrades, planet_colors, house_cusps, ascendant, midheaven, aspects, canvas_widget, fig, ax, planet_glyphs, ax_aspect=None):
    # Clear the axes and reset all properties
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()

    # Ensure the axes is set up as a polar plot with no grid lines
    ax.set_facecolor('white')
    ax.set_theta_direction(1)  # Counter-clockwise
    theta_offset = np.radians(180 - ascendant)  # Rotate so AC lands at 9 o'clock
    ax.set_theta_offset(theta_offset)

    # Explicitly disable all grid lines and ticks
    ax.set_xticks([])  # No radial ticks
    ax.set_yticks([])  # No radial distance ticks
    ax.set_xticklabels([])  # No tick labels
    ax.set_yticklabels([])  # No tick labels
    ax.grid(False)  # Disable all grid lines
    ax.spines['polar'].set_visible(False)  # Hide the polar spine
    ax.set_rgrids([])  # Disable radial grid lines
    ax.set_thetagrids([])  # Disable angular grid lines

    signs = [
        ('♈', 'Aries'), ('♉', 'Taurus'), ('♊', 'Gemini'), ('♋', 'Cancer'),
        ('♌', 'Leo'), ('♍', 'Virgo'), ('♎', 'Libra'), ('♏', 'Scorpio'),
        ('♐', 'Sagittarius'), ('♑', 'Capricorn'), ('♒', 'Aquarius'), ('♓', 'Pisces')
    ]

    # Draw concentric circles
    for r in [0.4, 0.7, 1.0]:
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, color='lightgrey', linestyle='-', linewidth=0.5)
        ax.add_artist(circle)

    outer_circle = plt.Circle((0, 0), 1.05, transform=ax.transData._b, fill=False, color='lightblue', linewidth=2)
    ax.add_artist(outer_circle)

    # Zodiac signs and degree labels
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    for i in range(12):
        theta = theta_ticks[i]
        degree = i * 30
        # Zodiac sign symbols (e.g., ♈ for Aries)
        ax.text(theta, 1.03, signs[i][0], ha='center', va='center', fontsize=16, color='orange', fontfamily='DejaVu Sans')
        # Degree labels (e.g., 0°, 30°)
        ax.text(theta, 0.97, f"{degree}°", ha='center', va='center', fontsize=6, color='black', fontfamily='DejaVu Sans')

    # House cusps
    for i, cusp in enumerate(house_cusps):
        theta = np.radians(cusp)
        ax.plot([theta, theta], [0.4, 1.0], color='black', linewidth=0.7)
        degree = int(cusp % 30)
        minutes = int((cusp % 1) * 60)
        ax.text(theta, 0.88, f"{degree}° {minutes}'", ha='center', va='center', fontsize=8, color='black', fontfamily='DejaVu Sans')
        house_number = (i + 1) % 12 if (i + 1) % 12 != 0 else 12
        ax.text(theta, 0.35, str(house_number), ha='center', va='center', fontsize=10, color='black', fontfamily='DejaVu Sans')

    # Draw the Ascendant at chart's 0° (maps to 180° on screen after offset)
    asc_theta = np.radians(ascendant)
    ax.plot([asc_theta, asc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(asc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(asc_theta, 1.13, 'AC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    # Draw the Midheaven
    mc_theta = np.radians(midheaven)
    ax.plot([mc_theta, mc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(mc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(mc_theta, 1.13, 'MC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    ax.set_ylim(0, 1.1)

    # Planets
    planet_radii = {}
    planet_positions = {}  # To store final (theta, radius) for each planet
    base_radius = 0.75
    radius_step = 0.15
    angular_offset = 3.5  # Degrees to offset planets angularly when too close

    # Group planets by clusters (within 5 degrees)
    clusters = []
    sorted_planets = sorted(longitudes.items(), key=lambda x: x[1])
    for planet, lon in sorted_planets:
        if lon is None:
            continue
        # Find or create a cluster
        found_cluster = False
        for cluster in clusters:
            cluster_lons = [longitudes[p] for p in cluster]
            if any(abs((lon - l) % 360) < 5 for l in cluster_lons):
                cluster.append(planet)
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([planet])

    # Position planets within each cluster
    for cluster in clusters:
        cluster_lons = [longitudes[p] for p in cluster]
        avg_lon = sum(cluster_lons) / len(cluster_lons)  # Center of the cluster
        num_planets = len(cluster)

        # Adjust radius based on cluster size
        radius = base_radius + (num_planets - 1) * radius_step / 2  # Center the cluster radially

        # Calculate angular offsets to spread planets side by side
        if num_planets == 1:
            planet = cluster[0]
            planet_radii[planet] = radius
            planet_positions[planet] = (np.radians(longitudes[planet]), radius)
        else:
            # Spread planets angularly around the average longitude
            offsets = np.linspace(-(num_planets-1)*angular_offset/2, (num_planets-1)*angular_offset/2, num_planets)
            for i, planet in enumerate(cluster):
                adjusted_lon = (avg_lon + offsets[i]) % 360
                planet_radii[planet] = radius
                planet_positions[planet] = (np.radians(adjusted_lon), radius)

    # Draw the planets with their adjusted positions
    for planet in longitudes.keys():
        if planet not in planet_positions:
            continue
        theta, radius = planet_positions[planet]
        sign, _ = get_sign_and_house(longitudes[planet], house_cusps)
        ax.text(theta, radius, planet_glyphs[planet], ha='center', va='center',
                fontsize=20, color="black", fontfamily='DejaVu Sans', weight='bold')

    # Aspect grid
    if ax_aspect:
        ax_aspect.set_xticks([])
        ax_aspect.set_yticks([])
        ax_aspect.set_xlim(0, 12)
        ax_aspect.set_ylim(0, 12)
        ax_aspect.set_facecolor('white')

        for i in range(13):
            ax_aspect.plot([i, i], [0, 12], color='black', linewidth=0.5)
            ax_aspect.plot([0, 12], [i, i], color='black', linewidth=0.5)

        planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron']
        for i, planet in enumerate(planet_list):
            ax_aspect.text(i + 0.5, 12.2, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')
            ax_aspect.text(-0.5, 11.5 - i, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')

        aspect_symbols = {
            'Conjunction': ('red', 'C'),
            'Sextile': ('green', 'S'),
            'Square': ('red', 'Q'),
            'Trine': ('blue', 'T'),
            'Opposition': ('red', 'O')
        }
        for p1, p2, aspect_name, _ in aspects:
            idx1 = planet_list.index(p1)
            idx2 = planet_list.index(p2)
            x, y = min(idx1, idx2), 11 - max(idx1, idx2)
            color, symbol = aspect_symbols.get(aspect_name, ('black', ''))
            ax_aspect.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=10, color=color, fontfamily='DejaVu Sans')

        # Add legend for aspect symbols below the grid
        aspect_legend = [
            'C = Conjunction', 'S = Sextile', 'Q = Square', 'T = Trine', 'O = Opposition'
        ]
        ax_aspect.text(6, -2, '\n'.join(aspect_legend), ha='left', va='top', fontsize=10, fontfamily='DejaVu Sans', color='black')

    # Add legend for planets and signs in the figure (upper-left corner)
    planet_legend = [f"{glyph} = {planet}" for planet, glyph in planet_glyphs.items()]
    sign_legend = [f"{symbol} = {name}" for symbol, name in signs]
    combined_legend = planet_legend + [''] + sign_legend
    fig.text(0.01, 1, '\n'.join(combined_legend), ha='left', va='top', fontsize=8, fontfamily='DejaVu Sans', color='black')

    canvas_widget.draw()
    # Clear the axes once
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()

    signs = [
        ('♈', 'Aries'), ('♉', 'Taurus'), ('♊', 'Gemini'), ('♋', 'Cancer'),
        ('♌', 'Leo'), ('♍', 'Virgo'), ('♎', 'Libra'), ('♏', 'Scorpio'),
        ('♐', 'Sagittarius'), ('♑', 'Capricorn'), ('♒', 'Aquarius'), ('♓', 'Pisces')
    ]

    ax.set_facecolor('white')

    # Correct orientation: Ascendant at 9 o'clock
    ax.set_theta_direction(1)  # Counter-clockwise
    theta_offset = np.radians(180 - ascendant)  # Rotate so AC lands at 9 o'clock
    ax.set_theta_offset(theta_offset)

    # Draw concentric circles
    for r in [0.4, 0.7, 1.0]:
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, color='lightgrey', linestyle='-', linewidth=0.5)
        ax.add_artist(circle)

    outer_circle = plt.Circle((0, 0), 1.05, transform=ax.transData._b, fill=False, color='lightblue', linewidth=2)
    ax.add_artist(outer_circle)

    # Zodiac signs and degree labels
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ax.set_xticks([])  # Explicitly set no ticks to avoid radial lines
    ax.set_xticklabels([])  # Clear any existing tick labels
    ax.grid(False)  # Disable the grid (both radial and angular)
    ax.spines['polar'].set_visible(False)  # Hide the polar spine (removes lines connecting opposite sides)

    for i in range(12):
        theta = theta_ticks[i]
        degree = i * 30
        # Zodiac sign symbols (e.g., ♈ for Aries)
        ax.text(theta, 1.03, signs[i][0], ha='center', va='center', fontsize=16, color='orange', fontfamily='DejaVu Sans')
        # Degree labels (e.g., 0°, 30°)
        ax.text(theta, 0.97, f"{degree}°", ha='center', va='center', fontsize=6, color='black', fontfamily='DejaVu Sans')

    # House cusps
    for i, cusp in enumerate(house_cusps):
        theta = np.radians(cusp)
        ax.plot([theta, theta], [0.4, 1.0], color='black', linewidth=0.7)
        degree = int(cusp % 30)
        minutes = int((cusp % 1) * 60)
        ax.text(theta, 0.88, f"{degree}° {minutes}'", ha='center', va='center', fontsize=8, color='black', fontfamily='DejaVu Sans')
        house_number = (i + 1) % 12 if (i + 1) % 12 != 0 else 12
        ax.text(theta, 0.25, str(house_number), ha='center', va='center', fontsize=10, color='black', fontfamily='DejaVu Sans')

    # Draw the Ascendant at chart's 0° (maps to 180° on screen after offset)
    asc_theta = np.radians(ascendant)
    ax.plot([asc_theta, asc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(asc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(asc_theta, 1.13, 'AC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    # Draw the Midheaven
    mc_theta = np.radians(midheaven)
    ax.plot([mc_theta, mc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(mc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(mc_theta, 1.13, 'MC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)

    # Planets
    planet_radii = {}
    planet_positions = {}  # To store final (theta, radius) for each planet
    base_radius = 0.75
    radius_step = 0.15
    angular_offset = 3.5  # Degrees to offset planets angularly when too close

    # Group planets by clusters (within 5 degrees)
    clusters = []
    sorted_planets = sorted(longitudes.items(), key=lambda x: x[1])
    for planet, lon in sorted_planets:
        if lon is None:
            continue
        # Find or create a cluster
        found_cluster = False
        for cluster in clusters:
            cluster_lons = [longitudes[p] for p in cluster]
            if any(abs((lon - l) % 360) < 5 for l in cluster_lons):
                cluster.append(planet)
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([planet])

    # Position planets within each cluster
    for cluster in clusters:
        cluster_lons = [longitudes[p] for p in cluster]
        avg_lon = sum(cluster_lons) / len(cluster_lons)  # Center of the cluster
        num_planets = len(cluster)

        # Adjust radius based on cluster size
        radius = base_radius + (num_planets - 1) * radius_step / 2  # Center the cluster radially

        # Calculate angular offsets to spread planets side by side
        if num_planets == 1:
            planet = cluster[0]
            planet_radii[planet] = radius
            planet_positions[planet] = (np.radians(longitudes[planet]), radius)
        else:
            # Spread planets angularly around the average longitude
            offsets = np.linspace(-(num_planets-1)*angular_offset/2, (num_planets-1)*angular_offset/2, num_planets)
            for i, planet in enumerate(cluster):
                adjusted_lon = (avg_lon + offsets[i]) % 360
                planet_radii[planet] = radius
                planet_positions[planet] = (np.radians(adjusted_lon), radius)

    # Draw the planets with their adjusted positions
    for planet in longitudes.keys():
        if planet not in planet_positions:
            continue
        theta, radius = planet_positions[planet]
        sign, _ = get_sign_and_house(longitudes[planet], house_cusps)
        ax.text(theta, radius, planet_glyphs[planet], ha='center', va='center',
                fontsize=20, color="black", fontfamily='DejaVu Sans', weight='bold')

    # Aspect grid
    if ax_aspect:
        ax_aspect.set_xticks([])
        ax_aspect.set_yticks([])
        ax_aspect.set_xlim(0, 12)
        ax_aspect.set_ylim(0, 12)
        ax_aspect.set_facecolor('white')

        for i in range(13):
            ax_aspect.plot([i, i], [0, 12], color='black', linewidth=0.5)
            ax_aspect.plot([0, 12], [i, i], color='black', linewidth=0.5)

        planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron']
        for i, planet in enumerate(planet_list):
            ax_aspect.text(i + 0.5, 12.2, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')
            ax_aspect.text(-0.5, 11.5 - i, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')

        aspect_symbols = {
            'Conjunction': ('red', 'C'),
            'Sextile': ('green', 'S'),
            'Square': ('red', 'Q'),
            'Trine': ('blue', 'T'),
            'Opposition': ('red', 'O')
        }
        for p1, p2, aspect_name, _ in aspects:
            idx1 = planet_list.index(p1)
            idx2 = planet_list.index(p2)
            x, y = min(idx1, idx2), 11 - max(idx1, idx2)
            color, symbol = aspect_symbols.get(aspect_name, ('black', ''))
            ax_aspect.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=10, color=color, fontfamily='DejaVu Sans')

        # Add legend for aspect symbols below the grid
        aspect_legend = [
            'C = Conjunction', 'S = Sextile', 'Q = Square', 'T = Trine', 'O = Opposition'
        ]
        ax_aspect.text(6, -2, '\n'.join(aspect_legend), ha='left', va='top', fontsize=10, fontfamily='DejaVu Sans', color='black')

    # Add legend for planets and signs in the figure (upper-left corner)
    planet_legend = [f"{glyph} = {planet}" for planet, glyph in planet_glyphs.items()]
    sign_legend = [f"{symbol} = {name}" for symbol, name in signs]
    combined_legend = planet_legend + [''] + sign_legend
    fig.text(0.01, 1, '\n'.join(combined_legend), ha='left', va='top', fontsize=8, fontfamily='DejaVu Sans', color='black')

    canvas_widget.draw()
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()

    signs = [
        ('♈', 'Aries'), ('♉', 'Taurus'), ('♊', 'Gemini'), ('♋', 'Cancer'),
        ('♌', 'Leo'), ('♍', 'Virgo'), ('♎', 'Libra'), ('♏', 'Scorpio'),
        ('♐', 'Sagittarius'), ('♑', 'Capricorn'), ('♒', 'Aquarius'), ('♓', 'Pisces')
    ]

    ax.set_facecolor('white')

    # Correct orientation: Ascendant at 9 o'clock
    ax.set_theta_direction(1)  # Counter-clockwise
    theta_offset = np.radians(180 - ascendant)  # Rotate so AC lands at 9 o'clock
    ax.set_theta_offset(theta_offset)

    for r in [0.4, 0.7, 1.0]:
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, color='lightgrey', linestyle='-', linewidth=0.5)
        ax.add_artist(circle)

    outer_circle = plt.Circle((0, 0), 1.05, transform=ax.transData._b, fill=False, color='lightblue', linewidth=2)
    ax.add_artist(outer_circle)

    # Zodiac signs and degree labels
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ax.set_xticks([])  # Explicitly set no ticks to avoid radial lines
    ax.set_xticklabels([])  # Clear any existing tick labels
    ax.grid(False)  # Disable the grid (both radial and angular)
    ax.spines['polar'].set_visible(False)  # Hide the polar spine (removes lines connecting opposite sides)

    for i in range(12):
        theta = theta_ticks[i]
        degree = i * 30
        # Zodiac sign symbols (e.g., ♈ for Aries)
        ax.text(theta, 1.03, signs[i][0], ha='center', va='center', fontsize=16, color='orange', fontfamily='DejaVu Sans')
        # Degree labels (e.g., 0°, 30°)
        ax.text(theta, 0.97, f"{degree}°", ha='center', va='center', fontsize=6, color='black', fontfamily='DejaVu Sans')

    # House cusps
    for i, cusp in enumerate(house_cusps):
        theta = np.radians(cusp)
        ax.plot([theta, theta], [0.4, 1.0], color='black', linewidth=0.7)
        degree = int(cusp % 30)
        minutes = int((cusp % 1) * 60)
        ax.text(theta, 0.88, f"{degree}° {minutes}'", ha='center', va='center', fontsize=8, color='black', fontfamily='DejaVu Sans')
        house_number = (i + 1) % 12 if (i + 1) % 12 != 0 else 12
        ax.text(theta, 0.25, str(house_number), ha='center', va='center', fontsize=10, color='black', fontfamily='DejaVu Sans')

    # Draw the Ascendant at chart's 0° (maps to 180° on screen after offset)
    asc_theta = np.radians(ascendant)
    ax.plot([asc_theta, asc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(asc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(asc_theta, 1.13, 'AC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    # Draw the Midheaven
    mc_theta = np.radians(midheaven)
    ax.plot([mc_theta, mc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(mc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(mc_theta, 1.13, 'MC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)

    # Planets
    planet_radii = {}
    planet_positions = {}  # To store final (theta, radius) for each planet
    base_radius = 0.75
    radius_step = 0.15
    angular_offset = 3.5  # Degrees to offset planets angularly when too close

    # Group planets by clusters (within 5 degrees)
    clusters = []
    sorted_planets = sorted(longitudes.items(), key=lambda x: x[1])
    for planet, lon in sorted_planets:
        if lon is None:
            continue
        # Find or create a cluster
        found_cluster = False
        for cluster in clusters:
            cluster_lons = [longitudes[p] for p in cluster]
            if any(abs((lon - l) % 360) < 5 for l in cluster_lons):
                cluster.append(planet)
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([planet])

    # Position planets within each cluster
    for cluster in clusters:
        cluster_lons = [longitudes[p] for p in cluster]
        avg_lon = sum(cluster_lons) / len(cluster_lons)  # Center of the cluster
        num_planets = len(cluster)

        # Adjust radius based on cluster size
        radius = base_radius + (num_planets - 1) * radius_step / 2  # Center the cluster radially

        # Calculate angular offsets to spread planets side by side
        if num_planets == 1:
            planet = cluster[0]
            planet_radii[planet] = radius
            planet_positions[planet] = (np.radians(longitudes[planet]), radius)
        else:
            # Spread planets angularly around the average longitude
            offsets = np.linspace(-(num_planets-1)*angular_offset/2, (num_planets-1)*angular_offset/2, num_planets)
            for i, planet in enumerate(cluster):
                adjusted_lon = (avg_lon + offsets[i]) % 360
                planet_radii[planet] = radius
                planet_positions[planet] = (np.radians(adjusted_lon), radius)

    # Draw the planets with their adjusted positions
    for planet in longitudes.keys():
        if planet not in planet_positions:
            continue
        theta, radius = planet_positions[planet]
        sign, _ = get_sign_and_house(longitudes[planet], house_cusps)
        ax.text(theta, radius, planet_glyphs[planet], ha='center', va='center',
                fontsize=20, color="black", fontfamily='DejaVu Sans', weight='bold')

    # Aspect grid
    if ax_aspect:
        ax_aspect.set_xticks([])
        ax_aspect.set_yticks([])
        ax_aspect.set_xlim(0, 12)
        ax_aspect.set_ylim(0, 12)
        ax_aspect.set_facecolor('white')

        for i in range(13):
            ax_aspect.plot([i, i], [0, 12], color='black', linewidth=0.5)
            ax_aspect.plot([0, 12], [i, i], color='black', linewidth=0.5)

        planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron']
        for i, planet in enumerate(planet_list):
            ax_aspect.text(i + 0.5, 12.2, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')
            ax_aspect.text(-0.5, 11.5 - i, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')

        aspect_symbols = {
            'Conjunction': ('red', 'C'),
            'Sextile': ('green', 'S'),
            'Square': ('red', 'Q'),
            'Trine': ('blue', 'T'),
            'Opposition': ('red', 'O')
        }
        for p1, p2, aspect_name, _ in aspects:
            idx1 = planet_list.index(p1)
            idx2 = planet_list.index(p2)
            x, y = min(idx1, idx2), 11 - max(idx1, idx2)
            color, symbol = aspect_symbols.get(aspect_name, ('black', ''))
            ax_aspect.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=10, color=color, fontfamily='DejaVu Sans')

        # Add legend for aspect symbols below the grid
        aspect_legend = [
            'C = Conjunction', 'S = Sextile', 'Q = Square', 'T = Trine', 'O = Opposition'
        ]
        ax_aspect.text(6, -2, '\n'.join(aspect_legend), ha='left', va='top', fontsize=10, fontfamily='DejaVu Sans', color='black')

    # Add legend for planets and signs in the figure (upper-left corner)
    planet_legend = [f"{glyph} = {planet}" for planet, glyph in planet_glyphs.items()]
    sign_legend = [f"{symbol} = {name}" for symbol, name in signs]
    combined_legend = planet_legend + [''] + sign_legend
    fig.text(0.01, 1, '\n'.join(combined_legend), ha='left', va='top', fontsize=8, fontfamily='DejaVu Sans', color='black')

    canvas_widget.draw()
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()

    signs = [
        ('♈', 'Aries'), ('♉', 'Taurus'), ('♊', 'Gemini'), ('♋', 'Cancer'),
        ('♌', 'Leo'), ('♍', 'Virgo'), ('♎', 'Libra'), ('♏', 'Scorpio'),
        ('♐', 'Sagittarius'), ('♑', 'Capricorn'), ('♒', 'Aquarius'), ('♓', 'Pisces')
    ]

    ax.set_facecolor('white')

    # Correct orientation: Ascendant at 9 o'clock
    ax.set_theta_direction(1)  # Counter-clockwise
    theta_offset = np.radians(180 - ascendant)  # Rotate so AC lands at 9 o'clock
    ax.set_theta_offset(theta_offset)

    for r in [0.4, 0.7, 1.0]:
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, color='lightgrey', linestyle='-', linewidth=0.5)
        ax.add_artist(circle)

    outer_circle = plt.Circle((0, 0), 1.05, transform=ax.transData._b, fill=False, color='lightblue', linewidth=2)
    ax.add_artist(outer_circle)

    # Zodiac signs and degree labels
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    # Remove ax.set_xticks() to prevent radial grid lines
    ax.set_xticklabels([])  # Clear any existing tick labels
    ax.grid(False)  # Disable the grid to ensure no lines are drawn

    for i in range(12):
        theta = theta_ticks[i]
        degree = i * 30
        # Zodiac sign symbols (e.g., ♈ for Aries)
        ax.text(theta, 1.03, signs[i][0], ha='center', va='center', fontsize=16, color='orange', fontfamily='DejaVu Sans')
        # Degree labels (e.g., 0°, 30°)
        ax.text(theta, 0.97, f"{degree}°", ha='center', va='center', fontsize=6, color='black', fontfamily='DejaVu Sans')

    # House cusps
    for i, cusp in enumerate(house_cusps):
        theta = np.radians(cusp)
        ax.plot([theta, theta], [0.4, 1.0], color='black', linewidth=0.7)
        degree = int(cusp % 30)
        minutes = int((cusp % 1) * 60)
        ax.text(theta, 0.88, f"{degree}° {minutes}'", ha='center', va='center', fontsize=8, color='black', fontfamily='DejaVu Sans')
        house_number = (i + 1) % 12 if (i + 1) % 12 != 0 else 12
        ax.text(theta, 0.25, str(house_number), ha='center', va='center', fontsize=10, color='black', fontfamily='DejaVu Sans')

    # Draw the Ascendant at chart's 0° (maps to 180° on screen after offset)
    asc_theta = np.radians(ascendant)
    ax.plot([asc_theta, asc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(asc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(asc_theta, 1.13, 'AC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    # Draw the Midheaven
    mc_theta = np.radians(midheaven)
    ax.plot([mc_theta, mc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(mc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(mc_theta, 1.13, 'MC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)

    # Planets
    planet_radii = {}
    planet_positions = {}  # To store final (theta, radius) for each planet
    base_radius = 0.75
    radius_step = 0.15
    angular_offset = 3.5  # Degrees to offset planets angularly when too close

    # Group planets by clusters (within 5 degrees)
    clusters = []
    sorted_planets = sorted(longitudes.items(), key=lambda x: x[1])
    for planet, lon in sorted_planets:
        if lon is None:
            continue
        # Find or create a cluster
        found_cluster = False
        for cluster in clusters:
            cluster_lons = [longitudes[p] for p in cluster]
            if any(abs((lon - l) % 360) < 5 for l in cluster_lons):
                cluster.append(planet)
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([planet])

    # Position planets within each cluster
    for cluster in clusters:
        cluster_lons = [longitudes[p] for p in cluster]
        avg_lon = sum(cluster_lons) / len(cluster_lons)  # Center of the cluster
        num_planets = len(cluster)

        # Adjust radius based on cluster size
        radius = base_radius + (num_planets - 1) * radius_step / 2  # Center the cluster radially

        # Calculate angular offsets to spread planets side by side
        if num_planets == 1:
            planet = cluster[0]
            planet_radii[planet] = radius
            planet_positions[planet] = (np.radians(longitudes[planet]), radius)
        else:
            # Spread planets angularly around the average longitude
            offsets = np.linspace(-(num_planets-1)*angular_offset/2, (num_planets-1)*angular_offset/2, num_planets)
            for i, planet in enumerate(cluster):
                adjusted_lon = (avg_lon + offsets[i]) % 360
                planet_radii[planet] = radius
                planet_positions[planet] = (np.radians(adjusted_lon), radius)

    # Draw the planets with their adjusted positions
    for planet in longitudes.keys():
        if planet not in planet_positions:
            continue
        theta, radius = planet_positions[planet]
        sign, _ = get_sign_and_house(longitudes[planet], house_cusps)
        ax.text(theta, radius, planet_glyphs[planet], ha='center', va='center',
                fontsize=20, color="black", fontfamily='DejaVu Sans', weight='bold')

    # Aspect grid
    if ax_aspect:
        ax_aspect.set_xticks([])
        ax_aspect.set_yticks([])
        ax_aspect.set_xlim(0, 12)
        ax_aspect.set_ylim(0, 12)
        ax_aspect.set_facecolor('white')

        for i in range(13):
            ax_aspect.plot([i, i], [0, 12], color='black', linewidth=0.5)
            ax_aspect.plot([0, 12], [i, i], color='black', linewidth=0.5)

        planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron']
        for i, planet in enumerate(planet_list):
            ax_aspect.text(i + 0.5, 12.2, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')
            ax_aspect.text(-0.5, 11.5 - i, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')

        aspect_symbols = {
            'Conjunction': ('red', 'C'),
            'Sextile': ('green', 'S'),
            'Square': ('red', 'Q'),
            'Trine': ('blue', 'T'),
            'Opposition': ('red', 'O')
        }
        for p1, p2, aspect_name, _ in aspects:
            idx1 = planet_list.index(p1)
            idx2 = planet_list.index(p2)
            x, y = min(idx1, idx2), 11 - max(idx1, idx2)
            color, symbol = aspect_symbols.get(aspect_name, ('black', ''))
            ax_aspect.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=10, color=color, fontfamily='DejaVu Sans')

        # Add legend for aspect symbols below the grid
        aspect_legend = [
            'C = Conjunction', 'S = Sextile', 'Q = Square', 'T = Trine', 'O = Opposition'
        ]
        ax_aspect.text(6, -2, '\n'.join(aspect_legend), ha='left', va='top', fontsize=10, fontfamily='DejaVu Sans', color='black')

    # Add legend for planets and signs in the figure (upper-left corner)
    planet_legend = [f"{glyph} = {planet}" for planet, glyph in planet_glyphs.items()]
    sign_legend = [f"{symbol} = {name}" for symbol, name in signs]
    combined_legend = planet_legend + [''] + sign_legend
    fig.text(0.01, 1, '\n'.join(combined_legend), ha='left', va='top', fontsize=8, fontfamily='DejaVu Sans', color='black')

    canvas_widget.draw()
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()

    signs = [
        ('♈', 'Aries'), ('♉', 'Taurus'), ('♊', 'Gemini'), ('♋', 'Cancer'),
        ('♌', 'Leo'), ('♍', 'Virgo'), ('♎', 'Libra'), ('♏', 'Scorpio'),
        ('♐', 'Sagittarius'), ('♑', 'Capricorn'), ('♒', 'Aquarius'), ('♓', 'Pisces')
    ]

    ax.set_facecolor('white')

    # Correct orientation: Ascendant at 9 o'clock
    ax.set_theta_direction(1)  # Counter-clockwise
    theta_offset = np.radians(180 - ascendant)  # Rotate so AC lands at 9 o'clock
    ax.set_theta_offset(theta_offset)

    for r in [0.4, 0.7, 1.0]:
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, color='lightgrey', linestyle='-', linewidth=0.5)
        ax.add_artist(circle)

    outer_circle = plt.Circle((0, 0), 1.05, transform=ax.transData._b, fill=False, color='lightblue', linewidth=2)
    ax.add_artist(outer_circle)

    # Zodiac signs and degree labels
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    #ax.set_xticks(theta_ticks)
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ax.set_xticks(theta_ticks)                      # Needed for label placement
    ax.set_xticklabels([])                          # Hides default tick labels
    ax.grid(False)                                  # Disables grid lines
    ax.spines['polar'].set_visible(False)           # Removes circle around chart

    ax.set_xticklabels([symbol for symbol, name in signs], fontsize=16, color='orange', fontfamily='DejaVu Sans')

    for i in range(12):
        theta = theta_ticks[i]
        degree = i * 30
        ax.text(theta, 0.97, f"{degree}°", ha='center', va='center', fontsize=6, color='black', fontfamily='DejaVu Sans')

    # House cusps
    for i, cusp in enumerate(house_cusps):
        theta = np.radians(cusp)
        ax.plot([theta, theta], [0.4, 1.0], color='black', linewidth=0.7)
        degree = int(cusp % 30)
        minutes = int((cusp % 1) * 60)
        ax.text(theta, 0.88, f"{degree}° {minutes}'", ha='center', va='center', fontsize=8, color='black', fontfamily='DejaVu Sans')
        house_number = (i + 1) % 12 if (i + 1) % 12 != 0 else 12
        ax.text(theta, 0.25, str(house_number), ha='center', va='center', fontsize=10, color='black', fontfamily='DejaVu Sans')

    # Draw the Ascendant at chart's 0° (maps to 180° on screen after offset)
    asc_theta = np.radians(ascendant)
    ax.plot([asc_theta, asc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(asc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(asc_theta, 1.13, 'AC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    # Draw the Midheaven
    mc_theta = np.radians(midheaven)
    ax.plot([mc_theta, mc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(mc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(mc_theta, 1.13, 'MC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)

    # Planets
    planet_radii = {}
    planet_positions = {}  # To store final (theta, radius) for each planet
    base_radius = 0.75
    radius_step = 0.15
    angular_offset = 3  # Degrees to offset planets angularly when too close (updated as per your preference)

    # Group planets by clusters (within 5 degrees)
    clusters = []
    sorted_planets = sorted(longitudes.items(), key=lambda x: x[1])
    for planet, lon in sorted_planets:
        if lon is None:
            continue
        # Find or create a cluster
        found_cluster = False
        for cluster in clusters:
            cluster_lons = [longitudes[p] for p in cluster]
            if any(abs((lon - l) % 360) < 5 for l in cluster_lons):
                cluster.append(planet)
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([planet])

    # Position planets within each cluster
    for cluster in clusters:
        cluster_lons = [longitudes[p] for p in cluster]
        avg_lon = sum(cluster_lons) / len(cluster_lons)  # Center of the cluster
        num_planets = len(cluster)

        # Adjust radius based on cluster size
        radius = base_radius + (num_planets - 1) * radius_step / 2  # Center the cluster radially

        # Calculate angular offsets to spread planets side by side
        if num_planets == 1:
            planet = cluster[0]
            planet_radii[planet] = radius
            planet_positions[planet] = (np.radians(longitudes[planet]), radius)
        else:
            # Spread planets angularly around the average longitude
            offsets = np.linspace(-(num_planets-1)*angular_offset/2, (num_planets-1)*angular_offset/2, num_planets)
            for i, planet in enumerate(cluster):
                adjusted_lon = (avg_lon + offsets[i]) % 360
                planet_radii[planet] = radius
                planet_positions[planet] = (np.radians(adjusted_lon), radius)

    # Draw the planets with their adjusted positions
    for planet in longitudes.keys():
        if planet not in planet_positions:
            continue
        theta, radius = planet_positions[planet]
        sign, _ = get_sign_and_house(longitudes[planet], house_cusps)
        ax.text(theta, radius, planet_glyphs[planet], ha='center', va='center',
                fontsize=20, color="black", fontfamily='DejaVu Sans', weight='bold')

    # Aspect grid (unchanged, as this is where aspects are now solely represented)
    if ax_aspect:
        ax_aspect.set_xticks([])
        ax_aspect.set_yticks([])
        ax_aspect.set_xlim(0, 12)
        ax_aspect.set_ylim(0, 12)
        ax_aspect.set_facecolor('white')

        for i in range(13):
            ax_aspect.plot([i, i], [0, 12], color='black', linewidth=0.5)
            ax_aspect.plot([0, 12], [i, i], color='black', linewidth=0.5)

        planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron']
        for i, planet in enumerate(planet_list):
            ax_aspect.text(i + 0.5, 12.2, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')
            ax_aspect.text(-0.5, 11.5 - i, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')

        aspect_symbols = {
            'Conjunction': ('red', 'C'),
            'Sextile': ('green', 'S'),
            'Square': ('red', 'Q'),
            'Trine': ('blue', 'T'),
            'Opposition': ('red', 'O')
        }
        for p1, p2, aspect_name, _ in aspects:
            idx1 = planet_list.index(p1)
            idx2 = planet_list.index(p2)
            x, y = min(idx1, idx2), 11 - max(idx1, idx2)
            color, symbol = aspect_symbols.get(aspect_name, ('black', ''))
            ax_aspect.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=10, color=color, fontfamily='DejaVu Sans')

        # Add legend for aspect symbols below the grid
        aspect_legend = [
            'C = Conjunction', 'S = Sextile', 'Q = Square', 'T = Trine', 'O = Opposition'
        ]
        ax_aspect.text(6, -2, '\n'.join(aspect_legend), ha='left', va='top', fontsize=10, fontfamily='DejaVu Sans', color='black')

    # Add legend for planets and signs in the figure (upper-left corner)
    planet_legend = [f"{glyph} = {planet}" for planet, glyph in planet_glyphs.items()]
    sign_legend = [f"{symbol} = {name}" for symbol, name in signs]
    combined_legend = planet_legend + [''] + sign_legend
    fig.text(0.01, 1, '\n'.join(combined_legend), ha='left', va='top', fontsize=8, fontfamily='DejaVu Sans', color='black')

    canvas_widget.draw()
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()

    signs = [
        ('♈', 'Aries'), ('♉', 'Taurus'), ('♊', 'Gemini'), ('♋', 'Cancer'),
        ('♌', 'Leo'), ('♍', 'Virgo'), ('♎', 'Libra'), ('♏', 'Scorpio'),
        ('♐', 'Sagittarius'), ('♑', 'Capricorn'), ('♒', 'Aquarius'), ('♓', 'Pisces')
    ]

    ax.set_facecolor('white')

    # Correct orientation: Ascendant at 9 o'clock
    ax.set_theta_direction(1)  # Counter-clockwise
    theta_offset = np.radians(180 - ascendant)  # Rotate so AC lands at 9 o'clock
    ax.set_theta_offset(theta_offset)

    for r in [0.4, 0.7, 1.0]:
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, color='lightgrey', linestyle='-', linewidth=0.5)
        ax.add_artist(circle)

    outer_circle = plt.Circle((0, 0), 1.05, transform=ax.transData._b, fill=False, color='lightblue', linewidth=2)
    ax.add_artist(outer_circle)

    # Zodiac signs and degree labels
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    #ax.set_xticks(theta_ticks)
    theta_ticks = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ax.set_xticks(theta_ticks)
    ax.set_xticklabels([symbol for symbol, name in signs], fontsize=16, color='orange', fontfamily='DejaVu Sans')


    for i in range(12):
        theta = theta_ticks[i]
        degree = i * 30
        ax.text(theta, 0.97, f"{degree}°", ha='center', va='center', fontsize=6, color='black', fontfamily='DejaVu Sans')

    # House cusps
    for i, cusp in enumerate(house_cusps):
        theta = np.radians(cusp)
        ax.plot([theta, theta], [0.4, 1.0], color='black', linewidth=0.7)
        degree = int(cusp % 30)
        minutes = int((cusp % 1) * 60)
        ax.text(theta, 0.88, f"{degree}° {minutes}'", ha='center', va='center', fontsize=8, color='black', fontfamily='DejaVu Sans')
        house_number = (i + 1) % 12 if (i + 1) % 12 != 0 else 12
        ax.text(theta, 0.25, str(house_number), ha='center', va='center', fontsize=10, color='black', fontfamily='DejaVu Sans')

    # Draw the Ascendant at chart's 0° (maps to 180° on screen after offset)
    asc_theta = np.radians(ascendant)
    ax.plot([asc_theta, asc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(asc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(asc_theta, 1.13, 'AC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    # Draw the Midheaven
    mc_theta = np.radians(midheaven)
    ax.plot([mc_theta, mc_theta], [0.85, 1.0], color='blue', linewidth=2)
    ax.arrow(mc_theta, 1.0, 0, 0.05, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    ax.text(mc_theta, 1.13, 'MC', ha='center', va='center', fontsize=8, color='blue', fontfamily='DejaVu Sans')

    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)

    # Planets
    planet_radii = {}
    planet_positions = {}  # To store final (theta, radius) for each planet
    base_radius = 0.75
    radius_step = 0.15
    angular_offset = 3.5  # Degrees to offset planets angularly when too close

    # Group planets by clusters (within 5 degrees)
    clusters = []
    sorted_planets = sorted(longitudes.items(), key=lambda x: x[1])
    for planet, lon in sorted_planets:
        if lon is None:
            continue
        # Find or create a cluster
        found_cluster = False
        for cluster in clusters:
            cluster_lons = [longitudes[p] for p in cluster]
            if any(abs((lon - l) % 360) < 5 for l in cluster_lons):
                cluster.append(planet)
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([planet])

    # Position planets within each cluster
    for cluster in clusters:
        cluster_lons = [longitudes[p] for p in cluster]
        avg_lon = sum(cluster_lons) / len(cluster_lons)  # Center of the cluster
        num_planets = len(cluster)

        # Adjust radius based on cluster size
        radius = base_radius + (num_planets - 1) * radius_step / 2  # Center the cluster radially

        # Calculate angular offsets to spread planets side by side
        if num_planets == 1:
            planet = cluster[0]
            planet_radii[planet] = radius
            planet_positions[planet] = (np.radians(longitudes[planet]), radius)
        else:
            # Spread planets angularly around the average longitude
            offsets = np.linspace(-(num_planets-1)*angular_offset/2, (num_planets-1)*angular_offset/2, num_planets)
            for i, planet in enumerate(cluster):
                adjusted_lon = (avg_lon + offsets[i]) % 360
                planet_radii[planet] = radius
                planet_positions[planet] = (np.radians(adjusted_lon), radius)

    # Draw the planets with their adjusted positions
    for planet in longitudes.keys():
        if planet not in planet_positions:
            continue
        theta, radius = planet_positions[planet]
        sign, _ = get_sign_and_house(longitudes[planet], house_cusps)
        ax.text(theta, radius, planet_glyphs[planet], ha='center', va='center',
                fontsize=20, color="black", fontfamily='DejaVu Sans', weight='bold')

    # Aspects
    aspect_colors = {
        'Conjunction': ('red', '-'),
        'Sextile': ('green', '-'),
        'Square': ('red', '-'),
        'Trine': ('blue', '-'),
        'Opposition': ('red', '-')
    }
    for p1, p2, aspect_name, _ in aspects:
        lon1 = longitudes[p1]
        lon2 = longitudes[p2]
        if lon1 is None or lon2 is None:
            continue
        theta1 = np.radians(lon1)
        theta2 = np.radians(lon2)
        radius1 = planet_radii.get(p1, 0.75)
        radius2 = planet_radii.get(p2, 0.75)
        color, linestyle = aspect_colors.get(aspect_name, ('black', '-'))
        ax.plot([theta1, theta2], [radius1, radius2],
            color=color, alpha=0.5, linewidth=1, linestyle=linestyle)

    # Aspect grid
    if ax_aspect:
        ax_aspect.set_xticks([])
        ax_aspect.set_yticks([])
        ax_aspect.set_xlim(0, 12)
        ax_aspect.set_ylim(0, 12)
        ax_aspect.set_facecolor('white')

        for i in range(13):
            ax_aspect.plot([i, i], [0, 12], color='black', linewidth=0.5)
            ax_aspect.plot([0, 12], [i, i], color='black', linewidth=0.5)

        planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron']
        for i, planet in enumerate(planet_list):
            ax_aspect.text(i + 0.5, 12.2, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')  # Increased fontsize
            ax_aspect.text(-0.5, 11.5 - i, planet_glyphs[planet], ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')  # Increased fontsize

        aspect_symbols = {
            'Conjunction': ('red', 'C'),
            'Sextile': ('green', 'S'),
            'Square': ('red', 'Q'),
            'Trine': ('blue', 'T'),
            'Opposition': ('red', 'O')
        }
        for p1, p2, aspect_name, _ in aspects:
            idx1 = planet_list.index(p1)
            idx2 = planet_list.index(p2)
            x, y = min(idx1, idx2), 11 - max(idx1, idx2)
            color, symbol = aspect_symbols.get(aspect_name, ('black', ''))
            ax_aspect.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=10, color=color, fontfamily='DejaVu Sans')  # Increased fontsize

        # Add legend for aspect symbols below the grid
        aspect_legend = [
            'C = Conjunction', 'S = Sextile', 'Q = Square', 'T = Trine', 'O = Opposition'
        ]
        ax_aspect.text(6, -2, '\n'.join(aspect_legend), ha='left', va='top', fontsize=10, fontfamily='DejaVu Sans', color='black')  # Increased fontsize

    # Add legend for planets and signs in the figure (upper-left corner)
    planet_legend = [f"{glyph} = {planet}" for planet, glyph in planet_glyphs.items()]
    sign_legend = [f"{symbol} = {name}" for symbol, name in signs]
    combined_legend = planet_legend + [''] + sign_legend
    fig.text(0.01, 1, '\n'.join(combined_legend), ha='left', va='top', fontsize=8, fontfamily='DejaVu Sans', color='black')

    canvas_widget.draw()

def display_positions(longitudes, retrogrades, house_cusps, aspects, text_widget):
    text_widget.delete("1.0", tk.END)

    text_widget.insert(tk.END, "Planetary Longitudes (°):\n\n")
    for planet, lon in longitudes.items():
        if lon is None:
            text_widget.insert(tk.END, f"{planet}: Not available\n")
            continue
        sign, house = get_sign_and_house(lon, house_cusps)
        retrograde = " (R)" if retrogrades[planet] else ""
        text_widget.insert(tk.END, f"{planet}{retrograde}: {lon:.2f}° - {sign}, House {house}\n")

    if aspects:
        text_widget.insert(tk.END, "\nMajor Aspects:\n\n")
        for p1, p2, aspect_name, diff in aspects:
            text_widget.insert(tk.END, f"{p1} {aspect_name} {p2} (Diff: {diff:.2f}°)\n")

    text_widget.insert(tk.END, "\nInterpretations:\n\n")
    for planet, lon in longitudes.items():
        if lon is None:
            continue
        sign, house = get_sign_and_house(lon, house_cusps)
        if planet in PLANET_IN_SIGN and sign in PLANET_IN_SIGN[planet]:
            text_widget.insert(tk.END, f"{planet} in {sign}: {PLANET_IN_SIGN[planet][sign]}\n")
        if planet in PLANET_IN_HOUSE and house in PLANET_IN_HOUSE[planet]:
            text_widget.insert(tk.END, f"{planet} in {house}: {PLANET_IN_HOUSE[planet][house]}\n")

def clear_chart(canvas_widget, fig, ax, ax_aspect, text_widget):
    ax.clear()
    if ax_aspect:
        ax_aspect.clear()
    ax.set_ylim(0, 1)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_title("")
    canvas_widget.draw()
    text_widget.delete("1.0", tk.END)

# Create main window
root = tk.Tk()
root.title("Astrology Desktop App - Natal Chart")
root.configure(bg='#f5f7fa')

try:
    root.wm_attributes('-zoomed', True)
except tk.TclError:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.wm_attributes('-topmost', 1)
    root.wm_attributes('-topmost', 0)

# Main frame setup
main_frame = tk.Frame(root, bg='#f5f7fa')
main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Split the main frame into left sidebar and right content area
main_frame.grid_columnconfigure(0, weight=0)  # Left sidebar (fixed width)
main_frame.grid_columnconfigure(1, weight=1)  # Right content area (expands)
main_frame.grid_rowconfigure(0, weight=1)

# Left Frame (Sidebar + Interpretations)
left_frame = tk.Frame(main_frame, bg='#f5f7fa', width=500)
left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
left_frame.grid_rowconfigure(0, weight=0)  # Sidebar
left_frame.grid_rowconfigure(1, weight=1)  # Interpretations
left_frame.grid_columnconfigure(0, weight=1)

left_frame.grid_propagate(False)


# Sidebar (Inputs and Buttons)
sidebar_frame = tk.Frame(left_frame, width=220, bg='#e8eff5', padx=10, pady=10, relief="flat", borderwidth=1)

sidebar_frame.grid(row=0, column=0, sticky='new', pady=(0, 10))

# Input fields
tk.Label(sidebar_frame, text="Person's Data", font=('DejaVu Sans', 12, 'bold'), bg='#e8eff5', fg='#2c3e50').pack(anchor='w', pady=(0, 10))
labels = ["Date (YYYY-MM-DD)", "Time (HH:MM 24h)", "Location (ZIP or City, ST)", "Country Code (e.g., US)"]
entries = []
for label in labels:
    tk.Label(sidebar_frame, text=label, font=('DejaVu Sans', 10), bg='#e8eff5', fg='#34495e').pack(anchor='w')
    entry = tk.Entry(sidebar_frame, font=('DejaVu Sans', 10), bg='white', fg='black', borderwidth=1, relief="solid")
    entry.pack(anchor='w', fill=tk.X, pady=5)
    entries.append(entry)

entries[0].insert(0, "1979-11-09")
entries[1].insert(0, "03:38")
entries[2].insert(0, "05478")
entries[3].insert(0, "US")

# Interpretations Area (Below Sidebar)
text_frame = tk.Frame(left_frame, bg='#ffffff', relief="flat", borderwidth=1)
text_frame.grid(row=1, column=0, sticky='nsew')
text_frame.grid_rowconfigure(1, weight=1)
text_frame.grid_columnconfigure(0, weight=1)

tk.Label(text_frame, text="Interpretations & Positions", font=("DejaVu Sans", 12, "bold"),
         bg='#ffffff', fg='#2c3e50').grid(row=0, column=0, sticky='w', padx=10, pady=(10, 5))

# Text output with scrollbar
text_output = tk.Text(text_frame, wrap=tk.WORD, font=('DejaVu Sans', 10), bg='#ffffff', fg='#34495e', height=20)
text_output.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_output.yview)
scrollbar.grid(row=1, column=1, sticky='ns', pady=(0, 10))
text_output.config(yscrollcommand=scrollbar.set)

# Right Content Area (Chart)
chart_frame = tk.Frame(main_frame, bg='#f5f7fa')
chart_frame.grid(row=0, column=1, sticky='nsew')
chart_frame.grid_rowconfigure(1, weight=1)
chart_frame.grid_columnconfigure(0, weight=1)

# Initialize Matplotlib figure and axes
fig = plt.figure(figsize=(6, 6), dpi=100)
ax = fig.add_subplot(111, polar=True)
ax_aspect = fig.add_axes([0.75, 0.70, 0.22, 0.22])

# Create canvas and pack into chart_frame
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")


tk.Label(chart_frame, text="Astrological Chart", font=("DejaVu Sans", 12, "bold"),
         bg='#f5f7fa', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=(0, 5))

# Store chart data for redrawing
chart_data = {}

def resize_chart(event):
    if not chart_data:
        return  # No chart to resize yet

    # Get the size of the chart frame
    width = chart_frame.winfo_width()
    height = chart_frame.winfo_height()

    # Convert pixels to inches
    dpi = root.winfo_fpixels('1i')
    width_inches = width / dpi
    height_inches = height / dpi

    # Maintain a square aspect ratio
    size = min(width_inches, height_inches) * 0.9  # You can adjust the 0.9 to fit tighter or looser

    # Only resize the figure
    fig.set_size_inches(size, size, forward=True)

    # DO NOT replot or call draw_chart here!

    # Just redraw the existing figure
    canvas.draw()

from matplotlib.backends.backend_pdf import PdfPages

def save_chart():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Document", "*.pdf"), ("PNG Image", "*.png")]
    )
    if not file_path:
        return

    if file_path.endswith(".pdf"):
        with PdfPages(file_path) as pdf:
            # --- Page 1: Cover Page ---
            cover_fig = plt.figure(figsize=(8.5, 11))
            cover_ax = cover_fig.add_subplot(111)
            cover_ax.axis('off')  # No axes

            # Extract person info from the entries if you want
            person_name = entries[2].get().strip() or "Astrological Chart"  # Default to location if no name field yet
            date_of_chart = datetime.datetime.now().strftime("%B %d, %Y")

            # Add title text
            cover_ax.text(
                0.5, 0.7, person_name,
                fontsize=24, ha='center', va='center', family='DejaVu Sans', weight='bold'
            )
            cover_ax.text(
                0.5, 0.6, "Astrological Natal Chart",
                fontsize=16, ha='center', va='center', family='DejaVu Sans'
            )
            cover_ax.text(
                0.5, 0.4, f"Generated on {date_of_chart}",
                fontsize=12, ha='center', va='center', family='DejaVu Sans', color='gray'
            )

            pdf.savefig(cover_fig, bbox_inches='tight')
            plt.close(cover_fig)

            # --- Page 2: The Chart Image ---
            fig.savefig(pdf, format='pdf', bbox_inches='tight')

            # --- Page 3: The Interpretations Text ---
            text_fig = plt.figure(figsize=(8.5, 11))
            text_ax = text_fig.add_subplot(111)
            text_ax.axis('off')

            text_content = text_output.get("1.0", tk.END)

            text_ax.text(
                0.05, 0.95, text_content,
                fontsize=10, ha='left', va='top', wrap=True,
                family='DejaVu Sans'
            )

            pdf.savefig(text_fig, bbox_inches='tight')
            plt.close(text_fig)

        messagebox.showinfo("Saved", f"Chart saved to {file_path}")

    elif file_path.endswith(".png"):
        # PNG mode: Only chart
        fig.savefig(file_path, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Saved", f"Chart image saved to {file_path}")

def on_submit():
    try:
        date, time, loc, country = [e.get().strip() for e in entries]
        validate_inputs(date, time, loc, country or 'US')
        result = compute_planetary_longitudes(date, time, loc, country or 'US')
        longitudes, retrogrades, planet_colors, house_cusps, ascendant, midheaven, _, planet_glyphs = result
        aspects = compute_aspects(longitudes)

        # Store chart data for resizing
        chart_data['longitudes'] = longitudes
        chart_data['retrogrades'] = retrogrades
        chart_data['planet_colors'] = planet_colors
        chart_data['house_cusps'] = house_cusps
        chart_data['ascendant'] = ascendant
        chart_data['midheaven'] = midheaven
        chart_data['aspects'] = aspects
        chart_data['planet_glyphs'] = planet_glyphs

        # Draw the chart
        draw_chart(longitudes, retrogrades, planet_colors, house_cusps, ascendant, midheaven, aspects, canvas, fig, ax, planet_glyphs, ax_aspect)
        display_positions(longitudes, retrogrades, house_cusps, aspects, text_output)

        # Force a resize to ensure the chart fits the current window size
        if canvas:
            canvas.draw()
            chart_frame.update_idletasks()
            resize_chart(None)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_clear():
    clear_chart(canvas, fig, ax, ax_aspect, text_output)
    chart_data.clear()

# Initial chart display
try:
    default_date, default_time, default_loc, default_country = [e.get().strip() for e in entries]
    validate_inputs(default_date, default_time, default_loc, default_country or 'US')
    default_result = compute_planetary_longitudes(default_date, default_time, default_loc, default_country or 'US')
    default_longitudes, default_retrogrades, default_planet_colors, default_house_cusps, default_ascendant, default_midheaven, _, default_planet_glyphs = default_result
    default_aspects = compute_aspects(default_longitudes)

    # Store chart data for resizing
    chart_data['longitudes'] = default_longitudes
    chart_data['retrogrades'] = default_retrogrades
    chart_data['planet_colors'] = default_planet_colors
    chart_data['house_cusps'] = default_house_cusps
    chart_data['ascendant'] = default_ascendant
    chart_data['midheaven'] = default_midheaven
    chart_data['aspects'] = default_aspects
    chart_data['planet_glyphs'] = default_planet_glyphs

    # Draw the chart
    draw_chart(default_longitudes, default_retrogrades, default_planet_colors, default_house_cusps, default_ascendant, default_midheaven, default_aspects, canvas, fig, ax, default_planet_glyphs, ax_aspect)
    display_positions(default_longitudes, default_retrogrades, default_house_cusps, default_aspects, text_output)

    # Force a resize to ensure the chart fits the current window size
    if canvas:
        canvas.draw()

except Exception as e:
    messagebox.showerror("Error on Startup", str(e))

# Buttons
button_frame = tk.Frame(sidebar_frame, bg='#e8eff5')
button_frame.pack(fill=tk.X, pady=10)

submit_btn = tk.Button(button_frame, text="Generate Chart", command=on_submit, font=('DejaVu Sans', 10), bg='#3498db', fg='white', activebackground='#2980b9', relief="flat", padx=10, pady=5)
submit_btn.pack(side=tk.LEFT, padx=5)

save_btn = tk.Button(button_frame, text="Save Chart", command=save_chart, font=('DejaVu Sans', 10), bg='#2ecc71', fg='white', activebackground='#27ae60', relief="flat", padx=10, pady=5)
save_btn.pack(side=tk.LEFT, padx=5)

clear_btn = tk.Button(button_frame, text="Clear Chart", command=on_clear, font=('DejaVu Sans', 10), bg='#e74c3c', fg='white', activebackground='#c0392b', relief="flat", padx=10, pady=5)
clear_btn.pack(side=tk.LEFT, padx=5)

def on_closing():
    plt.close(fig)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.update_idletasks()

root.mainloop()
