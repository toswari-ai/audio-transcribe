#!/bin/bash

# start-video.sh - Launch Video Transcription App with Debug Mode
# This script starts the Streamlit video app with comprehensive debug logging enabled

# Handle help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "🎬 Video Transcription App Debug Launcher"
    echo "============================================================"
    echo ""
    echo "Usage: ./start-video.sh"
    echo ""
    echo "This script launches the video transcription app with debug mode enabled."
    echo ""
    echo "Features:"
    echo "  📹 Video transmission method indicators (WHOLE VIDEO vs KEY FRAMES)"
    echo "  🔧 SDK initialization and configuration details" 
    echo "  🎵 Audio extraction workflow with MoviePy compatibility"
    echo "  🎬 Model selection and API call tracking"
    echo "  ⏱️  Processing time and performance metrics"
    echo ""
    echo "Access: http://localhost:8502"
    echo "Stop: Press Ctrl+C"
    echo ""
    echo "Available Models: MM-Poly-8B, Qwen2.5-VL-7B-Instruct, MiniCPM-o-2.6"
    exit 0
fi

echo "🎬 Starting Video Transcription App with Debug Mode..."
echo "============================================================"

# Set debug environment variables
export DEBUG_VIDEO_PROCESSING=true
export PYTHONUNBUFFERED=1  # Ensure real-time output

# Display configuration
echo "🔧 Configuration:"
echo "   Debug Video Processing: ${DEBUG_VIDEO_PROCESSING}"
echo "   Python Unbuffered: ${PYTHONUNBUFFERED}"
echo "   Port: 8502"
echo "   App: app-video.py"
echo ""

echo "🎯 Debug Features Enabled:"
echo "   📹 Video transmission method indicators (WHOLE VIDEO vs KEY FRAMES)"
echo "   🔧 SDK initialization and configuration details"
echo "   🎵 Audio extraction workflow with MoviePy compatibility"
echo "   🎬 Model selection and API call tracking"
echo "   ⏱️  Processing time and performance metrics"
echo ""

echo "🌐 Access the app at: http://localhost:8502"
echo "📝 Debug output will appear in this terminal"
echo ""

# Change to the correct directory
cd "$(dirname "$0")"

# Check if required files exist
if [ ! -f "app-video.py" ]; then
    echo "❌ Error: app-video.py not found in current directory"
    echo "   Please run this script from the audio-transcribe directory"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Make sure CLARIFAI_PAT is set in environment"
fi

echo "🚀 Launching Streamlit app..."
echo "   Use Ctrl+C to stop the server"
echo "   Streamlit errors about missing media files can be ignored"
echo ""

# Clear any previous Streamlit cache to avoid media file errors
echo "🧹 Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache 2>/dev/null || true

# Start the Streamlit app with debug enabled
streamlit run app-video.py \
    --server.port 8502 \
    --server.address localhost \
    --server.headless true \
    --browser.serverAddress localhost \
    --browser.serverPort 8502 \
    --logger.level warning