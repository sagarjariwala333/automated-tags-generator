from fastapi import FastAPI
from endpoints import agent_router, test_router, health_router, data_router, workflow_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Multi-Agent System with Langflow",
    description="AI-powered multi-agent system using Google Gemini with data collection capabilities and workflows",
    version="1.0.0"
)

# Include routers
app.include_router(health_router)
app.include_router(agent_router)
app.include_router(data_router)
app.include_router(workflow_router)
app.include_router(test_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
