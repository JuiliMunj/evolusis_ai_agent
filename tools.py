import requests
import wikipedia
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_weather(city: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"It's {temp}°C with {description} in {city.capitalize()}."
        else:
            return f"Could not fetch weather for {city}. Error: {data.get('message', 'unknown error')}"
    except Exception as e:
        return f"Error fetching weather: {e}"

def get_wikipedia_summary(topic: str) -> str:
    try:
        return wikipedia.summary(topic, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found for '{topic}'. Try being more specific: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return f"No page found for '{topic}'."
    except Exception as e:
        return f"Error fetching Wikipedia data: {e}"

def call_openai_with_prompt(prompt: str) -> str:
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI: {e}"
