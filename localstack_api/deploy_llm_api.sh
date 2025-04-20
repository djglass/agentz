#!/bin/bash

set -e

echo "🚀 Deploying Local LLM API via LocalStack..."

# Step 1: Check if LocalStack is running
if curl -s http://localhost:4566/_localstack/health | jq -r '.services.apigateway' | grep -q 'running'; then
  echo "✅ LocalStack is already running and healthy."
else
  echo "🔄 Starting LocalStack..."
  localstack start -d
  echo "⏳ Waiting for LocalStack to become healthy..."
  until curl -s http://localhost:4566/_localstack/health | jq -r '.services.apigateway' | grep -q 'running'; do
    sleep 2
  done
fi

# Step 2: 📦 Package the Lambda function if needed
LAMBDA_DIR="$(dirname "$0")/lambda"
PAYLOAD_ZIP="$LAMBDA_DIR/lambda_function_payload.zip"

if [ ! -f "$PAYLOAD_ZIP" ]; then
  echo "📦 Packaging Lambda function code into $PAYLOAD_ZIP..."
  (
    cd "$LAMBDA_DIR" || exit 1
    zip -r lambda_function_payload.zip lambda_function.py > /dev/null
  )
else
  echo "📦 Lambda payload already packaged."
fi

# Step 3: Deploy with OpenTofu
echo "🛠️ Deploying with OpenTofu..."
cd localstack_api/terraform
tofu init -input=false
tofu apply -auto-approve
cd ../..

# Step 4: Output API Gateway URL
API_ID=$(awslocal apigateway get-rest-apis | jq -r '.items[-1].id')
if [ "$API_ID" == "null" ] || [ -z "$API_ID" ]; then
  echo "❌ Failed to retrieve API Gateway ID"
  exit 1
fi

echo "🌐 Local API Gateway URL: http://localhost:4566/restapis/$API_ID/v1/_user_request_/hello"
