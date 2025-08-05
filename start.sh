#!/bin/bash

# Agentic Chat Assistant - Startup Script
# This script helps you quickly start the entire system

set -e

echo "🚀 Starting Agentic Chat Assistant..."
echo "=================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Environment file not found. Creating from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    read -p "Press Enter after you've added your OpenAI API key to continue..."
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" backend/.env 2>/dev/null; then
    echo "⚠️  OpenAI API key not found in backend/.env"
    echo "📝 Please add your OpenAI API key to backend/.env:"
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    read -p "Press Enter after you've added your OpenAI API key to continue..."
fi

echo "🔧 Building and starting services..."
docker-compose up --build -d

echo ""
echo "✅ System is starting up!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop the system:"
echo "   docker-compose down"
echo ""
echo "🎉 Happy chatting with your agentic assistant!"
