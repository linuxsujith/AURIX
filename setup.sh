#!/bin/bash
# ============================================
# AURIX AI Assistant — Setup Script
# ============================================

set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║           AURIX SETUP & INSTALLATION             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python
echo -e "${CYAN}[1/5]${NC} Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
    echo -e "  ${GREEN}✓${NC} Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON=python
    echo -e "  ${GREEN}✓${NC} Python found: $(python --version)"
else
    echo -e "  ${RED}✗${NC} Python not found! Install Python 3.9+"
    exit 1
fi

# Create virtual environment
echo ""
echo -e "${CYAN}[2/5]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
else
    echo -e "  ${YELLOW}⚠${NC} Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo ""
echo -e "${CYAN}[3/5]${NC} Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q 2>&1 | tail -5
echo -e "  ${GREEN}✓${NC} Dependencies installed"

# Create data directories
echo ""
echo -e "${CYAN}[4/5]${NC} Creating data directories..."
mkdir -p data/chromadb
mkdir -p data/faces
mkdir -p data/logs
mkdir -p data/generated_images
echo -e "  ${GREEN}✓${NC} Data directories ready"

# System dependencies info
echo ""
echo -e "${CYAN}[5/5]${NC} System dependencies check..."
echo -e "  ${YELLOW}NOTE:${NC} Some features require system packages:"
echo -e "  - Voice (STT): ${CYAN}sudo apt install ffmpeg${NC}"
echo -e "  - Voice (TTS): ${CYAN}sudo apt install espeak-ng${NC}"
echo -e "  - Face Recognition: ${CYAN}sudo apt install cmake libdlib-dev${NC}"
echo -e "  - Audio Playback: ${CYAN}sudo apt install portaudio19-dev${NC}"
echo -e "  - Screenshots: ${CYAN}sudo apt install scrot${NC}"
echo ""

# Optional: install system deps
read -p "  Install system dependencies now? (y/n): " INSTALL_SYS
if [[ "$INSTALL_SYS" == "y" || "$INSTALL_SYS" == "Y" ]]; then
    echo -e "  Installing system dependencies..."
    sudo apt update -qq
    sudo apt install -y -qq ffmpeg espeak-ng portaudio19-dev scrot cmake 2>&1 | tail -3
    echo -e "  ${GREEN}✓${NC} System dependencies installed"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║              SETUP COMPLETE! ✓                   ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║                                                  ║"
echo "║  To start AURIX:                                 ║"
echo "║                                                  ║"
echo "║    source venv/bin/activate                      ║"
echo "║    python run.py                                 ║"
echo "║                                                  ║"
echo "║  Then open: http://localhost:8000                 ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
