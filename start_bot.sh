#!/bin/bash

# Discord Bot 24/7 Startup Script
# This script ensures the bot runs continuously with proper process management

echo "🚀 Starting Discord Bot for 24/7 Operation"
echo "📅 Started at: $(date)"
echo "📁 Working directory: $(pwd)"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in current directory"
    exit 1
fi

if [ ! -f "config.json" ]; then
    echo "❌ config.json not found in current directory"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Make sure to create it from .env.example"
    echo "📝 Copy .env.example to .env and add your bot token"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing/updating dependencies..."
    python3 -m pip install -r requirements.txt --quiet
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to handle cleanup on script termination
cleanup() {
    echo ""
    echo "🛑 Received termination signal"
    echo "🔄 Stopping bot runner..."
    if [ ! -z "$RUNNER_PID" ]; then
        kill $RUNNER_PID 2>/dev/null
        wait $RUNNER_PID 2>/dev/null
    fi
    echo "✅ Bot stopped gracefully"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the bot runner in background and capture PID
echo "🔄 Starting bot runner with auto-restart capability..."
python3 run_bot.py &
RUNNER_PID=$!

echo "✅ Bot runner started with PID: $RUNNER_PID"
echo "📊 Monitoring bot status..."
echo "🛑 Press Ctrl+C to stop the bot"
echo ""

# Wait for the runner process
wait $RUNNER_PID

echo "🏁 Bot runner has stopped"
