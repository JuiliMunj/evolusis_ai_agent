import os
import json
import re
import logging
from collections import deque
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_current_weather, search_wikipedia

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

SHORT_TERM_MEMORY_SIZE = 5
short_term_memory = deque(maxlen=SHORT_TERM_MEMORY_SIZE)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def process_query_with_tools(query: str):
    short_term_memory.appendleft(query)

    system_prompt = (
        "You are an AI router. For any user query, decide whether the user is asking about weather "
        "(geographic weather info), looking for factual/world knowledge (Wikipedia-style), or something else. "
        "Return a JSON object ONLY with these keys: "
        '{"reasoning": "<string explaining why>", "action": "weather"|"wikipedia"|"llm"|"none", '
        '"city": "<city if weather>", "topic": "<topic if wikipedia>"}'
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0.0,
            max_tokens=300,
        )

        reasoning_text = resp.choices[0].message.content
        logger.info("LLM decision raw: %s", reasoning_text)

        decision = _extract_json(reasoning_text)
        if not decision:
            reasoning = "Could not parse structured decision from LLM. Falling back to direct LLM answer."
            answer = _ask_llm_for_answer(query)
            return reasoning, answer

        reasoning = decision.get("reasoning", "")
        action = decision.get("action", "none")
        city = decision.get("city", "").strip()
        topic = decision.get("topic", "").strip()

        if action == "weather" and city:
            tool_result = get_current_weather(city)
            final = _compose_final_answer_with_llm(query, "weather", tool_result, reasoning)
            return reasoning, final

        if action == "wikipedia" and topic:
            tool_result = search_wikipedia(topic)
            final = _compose_final_answer_with_llm(query, "wikipedia", tool_result, reasoning)
            return reasoning, final

        if action == "llm":
            answer = _ask_llm_for_answer(query)
            return reasoning or "LLM answered directly.", answer

        answer = _ask_llm_for_answer(query)
        return reasoning or "No specific action chosen.", answer

    except Exception as e:
        logger.exception("Error processing query: %s", e)
        if "insufficient_quota" in str(e).lower():
            return "Error: OpenAI quota exceeded.", "Please check your OpenAI billing or API usage."
        return "Error while processing the query.", str(e)


def _ask_llm_for_answer(query: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query},
            ],
            temperature=0.0,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("LLM direct answer failed")
        return f"LLM error: {e}"


def _compose_final_answer_with_llm(query: str, tool_type: str, tool_result: str, reasoning: str) -> str:
    prompt = (
        "You are a helpful assistant. The system already decided the query needs an external tool. "
        f"Tool type: {tool_type}\n"
        f"Tool result: {tool_result}\n"
        f"Router reasoning: {reasoning}\n"
        f"User query: {query}\n\n"
        "Please return a concise final answer that combines the tool result with helpful context."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Failed to compose final answer with LLM")
        return f"Tool result: {tool_result} (Could not compose with LLM: {e})"
