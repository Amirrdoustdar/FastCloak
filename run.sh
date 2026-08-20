#!/bin/bash

# OAuth2 Proxy Startup Script

set -e

echo "🚀 Starting OAuth2 Proxy with Keycloak..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker container"
else
    echo "💻 Running locally"
    
    # Check Python version
    python_version=$(python3 --version | awk '{print $2}')
    echo "🐍 Python version: $python_version"
    
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run database migrations (if using SQLAlchemy)
# echo "🔄 Running database migrations..."
# alembic upgrade head

# Start application
echo "✅ Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload