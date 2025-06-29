#!/bin/bash

# AI Personal Assistant API - Local Development Startup Script

echo "🚀 Starting AI Personal Assistant API..."

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
    echo "   Required: OPENAI_API_KEY, GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID"
    exit 1
fi

# Load environment variables
source .env

# Check if Google credentials file exists
if [ -z "$GOOGLE_CREDENTIALS_PATH" ]; then
    echo "⚠️  GOOGLE_CREDENTIALS_PATH not set in .env file!"
    echo "📋 Please set GOOGLE_CREDENTIALS_PATH in your .env file"
    exit 1
fi

if [ ! -f "$GOOGLE_CREDENTIALS_PATH" ]; then
    echo "⚠️  Google credentials file not found at: $GOOGLE_CREDENTIALS_PATH"
    echo "📋 Please download your Google credentials from:"
    echo "   https://console.cloud.google.com/apis/credentials"
    echo "   and update GOOGLE_CREDENTIALS_PATH in your .env file"
    exit 1
fi

# Start the application
echo "🌟 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload 