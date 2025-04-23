#!/bin/bash

set -euo pipefail

echo "🚀 Deploying Local LLM API via LocalStack..."

LAMBDA_DIR="$(dirname "$0")/lambda"
PAYLOAD_ZIP="$LAMBDA_DIR/lambda_function_payload.zip"
TERRAFORM_DIR="$(dirname "$0")/terraform"

# Step 1: Start or wait for LocalStack container
CONTAINER_NAME="localstack-main"

if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  echo "🔍 LocalStack container is already running."
else
  echo "🔄 Starting LocalStack..."
  localstack start -d
fi

# Wait for Docker container to report healthy
echo "⏳ Waiting for LocalStack to become healthy (via Docker)..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null)" == "healthy" ]; do
  sleep 2
done

echo "✅ LocalStack is healthy."

# Step 2: Package Lambda function
if [ ! -f "$PAYLOAD_ZIP" ]; then
  echo "📦 Packaging Lambda function into $PAYLOAD_ZIP..."
  (
    cd "$LAMBDA_DIR" || exit 1
    zip -r "lambda_function_payload.zip" "lambda_function.py" > /dev/null
  )
else
  echo "📦 Lambda payload already packaged."
fi

# Step 3: Deploy with OpenTofu
echo "🛠️ Deploying infrastructure with OpenTofu..."
(
  cd "$TERRAFORM_DIR"
  tofu init -input=false
  tofu apply -auto-approve
)

# Step 4: Output API Gateway URL
API_ID=$(awslocal apigateway get-rest-apis | jq -r '.items[-1].id')
if [[ -z "$API_ID" || "$API_ID" == "null" ]]; then
  echo "❌ Failed to retrieve API Gateway ID"
  exit 1
fi

echo "🌐 Local API Gateway URL: http://localhost:4566/restapis/$API_ID/v1/_user_request_/hello"
