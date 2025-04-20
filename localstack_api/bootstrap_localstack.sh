#!/bin/bash
set -e

echo "🧰 Starting system bootstrap for LocalStack + OpenTofu dev environment..."

# Install Homebrew if missing
if ! command -v brew &>/dev/null; then
  echo "🍺 Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "🍺 Installing required packages via Homebrew..."
brew install awscli opentofu python3

# Use pip from Homebrew's Python
PYTHON_BIN=$(which python3)
PIP_BIN=$(which pip3)

echo "🐍 Using Python from: $PYTHON_BIN"

# Install awscli-local and localstack using pip
echo "📦 Installing Python packages: awscli-local, localstack..."
$PIP_BIN install --upgrade awscli-local localstack

# Show installed versions
echo
echo "✅ Installed versions:"
aws --version
awslocal --version || echo "awslocal installed (wrapper script)"
tofu --version
localstack --version
$PYTHON_BIN --version

echo
echo "🎉 Bootstrap complete. You can now run ./deploy.sh in your project."
