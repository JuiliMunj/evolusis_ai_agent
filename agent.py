from tools import get_weather, get_wikipedia_summary, call_openai_with_prompt

def hybrid_agent(query: str):
    lower_query = query.lower()

    # Weather queries
    if "weather" in lower_query:
        city = lower_query.replace("what is the weather in", "").replace("today", "").strip(" ?.")
        reasoning = f"The user asked about weather, so I fetched data from OpenWeather API for {city}."
        answer = get_weather(city)
        return {"query": query, "reasoning": reasoning, "answer": answer}

    # Wikipedia queries
    elif "who is" in lower_query or "what is" in lower_query or "tell me about" in lower_query:
        topic = lower_query.replace("who is", "").replace("what is", "").replace("tell me about", "").strip(" ?.")
        reasoning = f"The user asked for factual information, so I fetched details from Wikipedia about {topic}."
        answer = get_wikipedia_summary(topic)
        return {"query": query, "reasoning": reasoning, "answer": answer}

    # General/OpenAI queries
    else:
        reasoning = "The user asked a general or reasoning-based question, so I used OpenAI to answer."
        answer = call_openai_with_prompt(query)
        return {"query": query, "reasoning": reasoning, "answer": answer}
