# API Testing with cURL

## Base URL
```bash
BASE_URL="http://127.0.0.1:8000"
```

## 1. Health Check
Check if the API is running and Gemini is configured.

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "available_endpoints": [
    "GET /",
    "POST /agent/execute",
    "POST /agent/metadata",
    "POST /test",
    "GET /health"
  ]
}
```

---

## 2. Root Endpoint
Simple hello world endpoint.

```bash
curl -X GET "http://127.0.0.1:8000/"
```

**Expected Response:**
```json
{
  "message": "Hello World - Multi-Agent System"
}
```

---

## 3. Execute Multi-Agent Task
Run a task through Research, Writer, and Reviewer agents.

```bash
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research AI trends in 2024, write a summary, and review it"
  }'
```

**More Examples:**
```bash
# Healthcare AI
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research the impact of AI in healthcare, write a report, and review it"
  }'

# Climate Change
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze climate change solutions, write a summary, and provide feedback"
  }'

# Technology Trends
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research blockchain technology trends, create content, and review"
  }'
```

---

## 4. Extract Metadata
Extract structured metadata from any content.

```bash
curl -X POST "http://127.0.0.1:8000/agent/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Artificial Intelligence is revolutionizing healthcare with predictive diagnostics and personalized treatment plans."
  }'
```

**More Examples:**
```bash
# News Article
curl -X POST "http://127.0.0.1:8000/agent/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Tesla announced a breakthrough in battery technology that could extend electric vehicle range by 50%. CEO Elon Musk revealed the innovation at the company headquarters in Austin, Texas."
  }'

# Technical Content
curl -X POST "http://127.0.0.1:8000/agent/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Python 3.12 introduces significant performance improvements with a new bytecode compiler and optimized memory management. Developers can expect up to 20% faster execution times."
  }'

# Business Content
curl -X POST "http://127.0.0.1:8000/agent/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The global e-commerce market is projected to reach $8 trillion by 2025, driven by mobile shopping and AI-powered personalization."
  }'
```

---

## 5. Test Endpoint - Basic
Test the multi-agent system with a predefined task.

```bash
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "basic"
  }'
```

---

## 6. Test Endpoint - Metadata Only
Test only the metadata extractor agent.

```bash
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "metadata",
    "content": "Machine learning models are being deployed in production environments across various industries."
  }'
```

---

## 7. Test Endpoint - All Agents
Test both multi-agent system and metadata extractor.

```bash
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "all"
  }'
```

---

## 8. Test Endpoint - Custom
Test with your own custom content.

```bash
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "custom",
    "content": "Explain quantum computing in simple terms"
  }'
```

**More Custom Examples:**
```bash
# Custom - Space Exploration
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "custom",
    "content": "Research Mars colonization plans, write a feasibility report, and review"
  }'

# Custom - Renewable Energy
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "custom",
    "content": "Analyze solar energy adoption trends, create a summary, and provide insights"
  }'
```

---

## Pretty Print JSON (Optional)
Add `| jq` to format JSON output nicely:

```bash
curl -X GET "http://127.0.0.1:8000/health" | jq
```

---

## Save Response to File
```bash
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Research AI trends"}' \
  -o response.json
```

---

## Verbose Mode (See Headers)
```bash
curl -v -X GET "http://127.0.0.1:8000/health"
```

---

## Test All Endpoints (Bash Script)
Run all tests at once:

```bash
chmod +x test_curls.sh
./test_curls.sh
```

---

## Interactive API Documentation
Visit these URLs in your browser:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## Error Handling Examples

### Missing API Key
```bash
# This will return an error if GOOGLE_API_KEY is not set
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "test"}'
```

### Invalid Request (Empty Task)
```bash
curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": ""}'
```

### Invalid Test Type
```bash
curl -X POST "http://127.0.0.1:8000/test" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "invalid"}'
```

---

## Performance Testing

### Measure Response Time
```bash
time curl -X POST "http://127.0.0.1:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Quick test"}'
```

### Multiple Concurrent Requests
```bash
for i in {1..5}; do
  curl -X POST "http://127.0.0.1:8000/agent/metadata" \
    -H "Content-Type: application/json" \
    -d '{"content": "Test content '$i'"}' &
done
wait
```
