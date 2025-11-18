# Multi-Agent System with Langflow & FastAPI

A multi-agent system built with Langflow, LangChain, Google Gemini, and FastAPI featuring coordinated agents for research, writing, and review tasks.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (Get it from https://makersuite.google.com/app/apikey)
```

## Run

### Option 1: FastAPI Server with Multi-Agent System
```bash
uvicorn langflow_integration:app --reload
```

### Option 2: Original Hello World API
```bash
uvicorn main:app --reload
```

### Option 3: Standalone Multi-Agent Script
```bash
python multi_agent_system.py
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `GET /` - Returns Hello World message
- `POST /agent/execute` - Execute a task using the multi-agent system
- `GET /health` - Check system health and configuration

## Multi-Agent System Architecture

The system consists of:
1. **Research Agent** - Gathers and analyzes information
2. **Writer Agent** - Creates and formats content
3. **Reviewer Agent** - Reviews and provides feedback
4. **Coordinator Agent** - Orchestrates the other agents

## Example Usage

```bash
curl -X POST "http://localhost:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Research AI trends, write a summary, and review it"}'
```

## Installing Langflow UI (Optional)

To use Langflow's visual interface:
```bash
pip install langflow
langflow run
```

Then access the UI at http://localhost:7860
# automated-tags-generator
