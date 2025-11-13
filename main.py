import os
import uvicorn
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
        if not response:
            return {"query": request.query, "reasoning": "No processing happened.", "answer": "No answer available."}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Evolusis AI Agent is running. Use POST /ask to query the agent."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("Available at your primary URL https://evolusis-ai-agent-2.onrender.com")
    print("==> \n==> ///////////////////////////////////////////////////////////")
    uvicorn.run(app, host="0.0.0.0", port=port)
