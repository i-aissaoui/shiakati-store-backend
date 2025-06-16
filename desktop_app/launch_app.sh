#!/bin/bash
# filepath: /home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/launch_app.sh

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Display header
echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}      Shiakati Store Application Launcher    ${NC}"
echo -e "${BLUE}==============================================${NC}"

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON="python3"
    echo -e "${GREEN}Python 3 found!${NC}"
elif command -v python &> /dev/null; then
    PYTHON="python"
    echo -e "${GREEN}Python found!${NC}"
else
    echo -e "${RED}Python is not installed. Please install Python 3.${NC}"
    exit 1
fi

# Check PyQt5
echo -e "${YELLOW}Checking PyQt5 installation...${NC}"
if $PYTHON -c "import PyQt5" &> /dev/null; then
    echo -e "${GREEN}PyQt5 found!${NC}"
else
    echo -e "${RED}PyQt5 is not installed.${NC}"
    echo -e "${YELLOW}Would you like to install it now? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Installing PyQt5...${NC}"
        pip install PyQt5
    else
        echo -e "${RED}PyQt5 is required to run the application.${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}Choose how to start the application:${NC}"
echo -e "${GREEN}1)${NC} Auto (try all fix methods - recommended)"
echo -e "${GREEN}2)${NC} Standalone fixed client"
echo -e "${GREEN}3)${NC} Patched original client"
echo -e "${GREEN}4)${NC} Fixed original client (syntax fix only)"
echo -e "${GREEN}5)${NC} Original (without fixes)"
echo -e "${GREEN}0)${NC} Exit"

read -r choice

case $choice in
    1)
        echo -e "${YELLOW}Starting with auto fix mode...${NC}"
        $PYTHON run_app.py --mode auto
        ;;
    2)
        echo -e "${YELLOW}Starting with standalone fixed client...${NC}"
        $PYTHON run_app.py --mode standalone
        ;;
    3)
        echo -e "${YELLOW}Starting with patched original client...${NC}"
        $PYTHON run_app.py --mode patched
        ;;
    4)
        echo -e "${YELLOW}Starting with fixed original client...${NC}"
        $PYTHON run_app.py --mode fixed-original
        ;;
    5)
        echo -e "${YELLOW}Starting with original client (no fixes)...${NC}"
        $PYTHON run_app.py --mode original
        ;;
    0)
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice.${NC}"
        exit 1
        ;;
esac
