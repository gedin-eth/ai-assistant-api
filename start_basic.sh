#!/bin/bash

# AI Personal Assistant API - Basic Startup (No Google Credentials Required)

echo "🚀 Starting AI Personal Assistant API (Basic Mode)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Copying env.example to .env..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual credentials before starting!"
    exit 1
fi

# Start the application (will work without Google credentials for basic endpoints)
echo "🌟 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Health check: http://localhost:8000/health"
echo ""
echo "⚠️  Note: Google integration features will not work without credentials.json"
echo "   You can still test:"
echo "   - Task management (local database)"
echo "   - AI task processing (if OpenAI key is set)"
echo "   - Basic API endpoints"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload 