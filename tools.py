# tools.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_current_weather(city: str) -> str:
    """
    Fetch current weather from OpenWeatherMap.
    Returns a human-readable string or an error string.
    """
    if not OPENWEATHER_API_KEY:
        return "Error: Missing OpenWeather API key."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code == 404:
            return f"City '{city}' not found."
        resp.raise_for_status()
        data = resp.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        country = data["sys"].get("country", "")
        return f"{temp}°C, {desc} ({country})"
    except requests.exceptions.RequestException as e:
        return f"Could not fetch weather data for {city}. Error: {e}"


def search_wikipedia(topic: str) -> str:
    """
    Return a short extract from Wikipedia for the topic.
    """
    try:
        params = {
            "action": "query",
            "format": "json",
            "titles": topic,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "redirects": 1,
        }
        resp = requests.get("https://en.wikipedia.org/w/api.php", params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return "No information found on Wikipedia."
        page_id = next(iter(pages))
        extract = pages[page_id].get("extract", "")
        return extract or "No extract available on Wikipedia."
    except requests.exceptions.RequestException as e:
        return f"Could not search Wikipedia for {topic}. Error: {e}"
