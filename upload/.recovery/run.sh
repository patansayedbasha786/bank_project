#!/bin/bash

# Royal Bank of India - Development Server Script
# This script sets up and runs the banking application locally

echo "🏦 Royal Bank of India - Starting Development Server"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "server/venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   cd server && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
cd server
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using default configuration."
    echo "   For production, please configure your database credentials in .env"
fi

# Start the server
echo "🚀 Starting Flask development server..."
echo "📱 Frontend will be available at: http://localhost:5000"
echo "🔌 API endpoints available at: http://localhost:5000/api/"
echo ""
echo "Default login credentials:"
echo "   Username: sk"
echo "   Password: 00"
echo "   Table Name: bank_transactions"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Run the Flask application
python src/main.py

