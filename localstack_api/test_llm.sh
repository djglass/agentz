#!/bin/bash

PROMPT=${1:-"Explain large language models in one sentence."}

# Corrected API ID extraction
API_ID=$(awslocal apigateway get-rest-apis \
  | jq -r '.items | sort_by(.createdDate) | .[-1].id')

if [ -z "$API_ID" ] || [ "$API_ID" == "null" ]; then
  echo "❌ No API Gateway found. Is LocalStack running?"
  exit 1
fi

URL="http://localhost:4566/restapis/$API_ID/v1/_user_request_/hello"

echo "🧠 Prompt: $PROMPT"
echo "🌐 URL: $URL"

curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$PROMPT\"}" \
  | jq .
