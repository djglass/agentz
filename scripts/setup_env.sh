#!/bin/bash

# setup_env.sh — loads environment variables from .env
# Usage: source setup_env.sh

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "✅ Environment variables loaded from .env"
else
  echo "⚠️  No .env file found. Please create one with NVD_API_KEY"
fi

