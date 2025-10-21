#!/bin/bash

# Audio Transcription App Startup Script
# This script loads environment variables and starts the Streamlit app

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎙️ Starting Audio Transcription App${NC}"

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}Loading environment variables from .env file...${NC}"
    set -a
    source .env
    set +a
else
    echo -e "${YELLOW}Warning: .env file not found. Using default values.${NC}"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo -e "${YELLOW}Streamlit not found. Installing requirements...${NC}"
    pip install -r requirements.txt
fi

# Validate PAT
if [ -z "$CLARIFAI_PAT" ] || [ "$CLARIFAI_PAT" = "your_clarifai_pat_here" ]; then
    echo -e "${YELLOW}Warning: CLARIFAI_PAT not set or using placeholder value${NC}"
    echo -e "${YELLOW}You can set it in the .env file or enter it in the app sidebar${NC}"
fi

# Set default values if not provided
export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
export STREAMLIT_SERVER_ADDRESS=${STREAMLIT_SERVER_ADDRESS:-localhost}

echo -e "${GREEN}Configuration:${NC}"
echo -e "  Server: http://$STREAMLIT_SERVER_ADDRESS:$STREAMLIT_SERVER_PORT"
echo -e "  Max file size: ${MAX_FILE_SIZE_MB:-25}MB"
echo -e "  Default model: ${DEFAULT_MODEL:-Whisper Base}"

# Start the Streamlit app
echo -e "${GREEN}Starting Streamlit server...${NC}"
streamlit run app.py --server.port=$STREAMLIT_SERVER_PORT --server.address=$STREAMLIT_SERVER_ADDRESS