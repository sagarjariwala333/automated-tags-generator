#!/bin/bash

# Multi-Agent System API Testing Script
# Make sure the server is running: uvicorn main:app --reload

BASE_URL="http://127.0.0.1:8000"

echo "=================================="
echo "Multi-Agent System API Tests"
echo "=================================="
echo ""

# 1. Health Check
echo "1. Health Check"
echo "curl -X GET \"$BASE_URL/health\""
curl -X GET "$BASE_URL/health"
echo -e "\n\n"

# 2. Root Endpoint
echo "2. Root Endpoint"
echo "curl -X GET \"$BASE_URL/\""
curl -X GET "$BASE_URL/"
echo -e "\n\n"

# 3. Execute Multi-Agent Task
echo "3. Execute Multi-Agent Task"
echo "curl -X POST \"$BASE_URL/agent/execute\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"task\": \"Research AI trends in 2024, write a summary, and review it\"}'"
curl -X POST "$BASE_URL/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Research AI trends in 2024, write a summary, and review it"}'
echo -e "\n\n"

# 4. Extract Metadata
echo "4. Extract Metadata"
echo "curl -X POST \"$BASE_URL/agent/metadata\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"content\": \"Artificial Intelligence is revolutionizing healthcare with predictive diagnostics and personalized treatment plans.\"}'"
curl -X POST "$BASE_URL/agent/metadata" \
  -H "Content-Type: application/json" \
  -d '{"content": "Artificial Intelligence is revolutionizing healthcare with predictive diagnostics and personalized treatment plans."}'
echo -e "\n\n"

# 5. Test Endpoint - Basic
echo "5. Test Endpoint - Basic"
echo "curl -X POST \"$BASE_URL/test\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"test_type\": \"basic\"}'"
curl -X POST "$BASE_URL/test" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "basic"}'
echo -e "\n\n"

# 6. Test Endpoint - Metadata Only
echo "6. Test Endpoint - Metadata Only"
echo "curl -X POST \"$BASE_URL/test\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"test_type\": \"metadata\", \"content\": \"Machine learning models are being deployed in production environments.\"}'"
curl -X POST "$BASE_URL/test" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "metadata", "content": "Machine learning models are being deployed in production environments."}'
echo -e "\n\n"

# 7. Test Endpoint - All Agents
echo "7. Test Endpoint - All Agents"
echo "curl -X POST \"$BASE_URL/test\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"test_type\": \"all\"}'"
curl -X POST "$BASE_URL/test" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "all"}'
echo -e "\n\n"

# 8. Test Endpoint - Custom
echo "8. Test Endpoint - Custom"
echo "curl -X POST \"$BASE_URL/test\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"test_type\": \"custom\", \"content\": \"Explain quantum computing in simple terms\"}'"
curl -X POST "$BASE_URL/test" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "custom", "content": "Explain quantum computing in simple terms"}'
echo -e "\n\n"

echo "=================================="
echo "All tests completed!"
echo "=================================="
