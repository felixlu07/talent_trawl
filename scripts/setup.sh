#!/bin/bash
# Talent Trawler Setup Script for Linux/Mac
# This script sets up the virtual environment and installs dependencies

echo "🎯 Talent Trawler Setup"
echo "============================================================"

# Check Python installation
echo ""
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

# Check for .env file
echo ""
echo "🔐 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it and add your ANTHROPIC_API_KEY"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Edit .env and add your API key"
    echo "   2. Install Poppler (PDF processing):"
    echo "      - macOS: brew install poppler"
    echo "      - Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "      - Fedora: sudo dnf install poppler-utils"
else
    echo "✅ .env file exists"
fi

# Check Poppler installation
echo ""
echo "📄 Checking Poppler installation..."
if command -v pdftoppm &> /dev/null; then
    POPPLER_VERSION=$(pdftoppm -v 2>&1 | head -n 1)
    echo "✅ Poppler found: $POPPLER_VERSION"
else
    echo "⚠️  Poppler not found. PDF processing will not work."
    echo ""
    echo "Install Poppler:"
    echo "  macOS:         brew install poppler"
    echo "  Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "  Fedora:        sudo dnf install poppler-utils"
fi

echo ""
echo "============================================================"
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To create an example configuration:"
echo "  python3 talent_trawler.py --create-example pm_candidates"
echo ""
echo "To process resumes:"
echo "  python3 talent_trawler.py pm_candidates"
echo "============================================================"
