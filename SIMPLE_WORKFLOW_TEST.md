# Simple Analysis Workflow - LangGraph Demo

## Overview
This workflow demonstrates LangGraph with 2 connected agents:

```
collector (Data Collection Agent)
    ↓
metadata (Metadata Extractor Agent)
    ↓
END
```

## cURL Examples

### GET Method (Easiest)
```bash
curl -X GET "http://127.0.0.1:8000/workflow/simple/analyze/facebook/react"
```

### POST Method
```bash
curl -X POST "http://127.0.0.1:8000/workflow/simple/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "facebook",
    "repo": "react"
  }'
```

### More Examples
```bash
# Vue.js
curl -X GET "http://127.0.0.1:8000/workflow/simple/analyze/vuejs/vue"

# Python
curl -X GET "http://127.0.0.1:8000/workflow/simple/analyze/python/cpython"

# Django
curl -X GET "http://127.0.0.1:8000/workflow/simple/analyze/django/django"

# Node.js
curl -X GET "http://127.0.0.1:8000/workflow/simple/analyze/nodejs/node"
```

## Postman Usage

**GET Method:**
- URL: `http://127.0.0.1:8000/workflow/simple/analyze/facebook/react`
- Method: GET
- Click Send

**POST Method:**
- URL: `http://127.0.0.1:8000/workflow/simple/analyze`
- Method: POST
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "owner": "facebook",
  "repo": "react"
}
```

## Response Structure

```json
{
  "success": true,
  "owner": "facebook",
  "repo": "react",
  "workflow": "simple_analysis",
  "steps_completed": ["collector", "metadata"],
  "readme_content": {
    "text": "React is a JavaScript library...",
    "length": 8500
  },
  "metadata": {
    "title": "React - A JavaScript library",
    "keywords": ["react", "javascript", "ui"],
    "category": "Technology",
    "summary": "React is...",
    "sentiment": "positive",
    "language": "English"
  },
  "summary": {
    "repository": "facebook/react",
    "title": "React - A JavaScript library",
    "category": "Technology",
    "keywords": ["react", "javascript", "ui"],
    "sentiment": "positive"
  }
}
```

## Workflow Steps

1. **collector** (Data Collection Agent)
   - Fetches README from GitHub API
   - Decodes base64 content
   - Converts HTML to plain text

2. **metadata** (Metadata Extractor Agent)
   - Analyzes plain text using Gemini AI
   - Extracts structured metadata
   - Returns title, keywords, category, etc.

## Interactive Documentation

Visit: http://127.0.0.1:8000/docs

Look for the **workflows** section to test interactively.
