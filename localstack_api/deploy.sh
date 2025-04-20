#!/bin/bash
set -e

echo "🔄 Starting LocalStack in the background..."
localstack start -d

echo "⏳ Waiting for LocalStack to start up..."
sleep 10

echo "📦 Creating S3 bucket in LocalStack (if not exists)..."
awslocal s3 mb s3://my-local-bucket || true

echo "📍 Current working directory: $(pwd)"
echo "📦 Checking ZIP path: lambda/lambda_function_payload.zip"

if [ ! -f lambda/lambda_function_payload.zip ]; then
  echo "❌ Lambda ZIP file not found!"
  exit 1
fi

echo "🚚 Uploading Lambda ZIP to S3..."
awslocal s3 cp lambda/lambda_function_payload.zip s3://my-local-bucket/

echo "📁 Switching to terraform directory..."
cd terraform

echo "🧹 Initializing OpenTofu..."
tofu init

echo "📌 Importing pre-created S3 bucket into state..."
tofu import aws_s3_bucket.demo_bucket my-local-bucket || true

echo "🚀 Applying infrastructure..."
tofu apply -auto-approve


