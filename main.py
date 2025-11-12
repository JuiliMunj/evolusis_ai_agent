import uvicorn
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from agent import process_query_with_tools
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Evolusis AI Agent Backend",
    description="AI agent that decides between LLM and external tools (weather/wikipedia).",
)


class QueryRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    reasoning: str
    answer: str


@app.post("/ask", response_model=AgentResponse)
async def ask_agent(request: QueryRequest):
    reasoning, answer = process_query_with_tools(request.query)
    return AgentResponse(reasoning=str(reasoning), answer=str(answer))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
