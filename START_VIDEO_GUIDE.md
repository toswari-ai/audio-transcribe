# Video App Debug Launch Scripts

## 🎬 start-video.sh

Launch the video transcription app with comprehensive debug logging enabled.

### Usage:
```bash
# Make executable (first time only)
chmod +x start-video.sh

# Launch with debug mode
./start-video.sh
```

### Features:
- ✅ Debug video processing enabled (`DEBUG_VIDEO_PROCESSING=true`)
- ✅ Real-time output (`PYTHONUNBUFFERED=1`) 
- ✅ Runs on port 8502
- ✅ Clears Streamlit cache to prevent media file errors
- ✅ Reduced log verbosity for cleaner output

### Debug Output Includes:
- 📹 **Video Transmission Method**: Shows whether sending WHOLE VIDEO or KEY FRAMES
- 🔧 **SDK Details**: Modern Clarifai SDK vs gRPC fallback information
- 🎵 **Audio Extraction**: MoviePy compatibility and audio processing workflow
- 🎬 **Model Selection**: Which video model is selected and why
- ⏱️ **Performance Metrics**: Processing times and file sizes
- 🔄 **API Calls**: Detailed request/response information

### Access:
- **Web Interface**: http://localhost:8502
- **Debug Output**: Terminal window where script is running

### Stopping:
- Press `Ctrl+C` in the terminal running the script

### Available Video Models:
1. **MM-Poly-8B** - Clarifai's native multimodal model
2. **Qwen2.5-VL-7B-Instruct** - Advanced vision-language model (default)
3. **MiniCPM-o-2.6 Language** - Multimedia MLLM model

### Troubleshooting:
- **Media file errors**: These can be ignored - they're from previous Streamlit sessions
- **Port in use**: Stop any existing Streamlit processes: `pkill -f "streamlit run"`
- **Dependencies**: Ensure all packages from `requirements.txt` are installed