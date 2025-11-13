from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import hybrid_agent

app = FastAPI(title="Evolusis AI Agent")

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    try:
        response = hybrid_agent(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Evolusis AI Agent is running. Use POST /ask to query the agent."}
