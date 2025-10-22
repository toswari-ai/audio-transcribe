# Video Transcription with Clarifai

🎬 **Advanced video transcription using multimodal AI models that analyze both visual and audio content.**

## Features

### 🤖 Multimodal AI Analysis
- **Visual Content Analysis**: Extracts key frames and analyzes visual elements
- **Audio Track Processing**: Extracts and transcribes speech from video audio
- **Combined Analysis**: Integrates visual and audio insights for comprehensive understanding
- **Text Detection**: Identifies text, signs, and written content in video frames

### 🎯 Supported Models (Modern Clarifai SDK)
- **Qwen2.5-VL-7B-Instruct**: 🌟 **DEFAULT** - Advanced vision-language model with long video analysis and temporal understanding
- **MM-Poly-8B**: 🆕 **NATIVE CLARIFAI** - Clarifai's multimodal AI assistant optimized for video, image, and audio analysis
- **GPT-4o**: Best overall multimodal performance (38⭐)
- **GPT-4o Mini**: Cost-effective video processing (6⭐)
- **Claude 3.5 Sonnet**: Superior reasoning and visual analysis (34⭐)
- **Claude 3 Opus**: Premium video analysis (77⭐)
- **Gemini 2.0 Flash**: Fast processing with good quality (4⭐)
- **Gemini 1.5 Pro**: Extended context for long videos (18⭐)
- **MiniCPM-o-2.6**: Comprehensive multimedia analysis (10⭐)
- **Florence-2 Large**: Efficient video processing by Microsoft (8⭐)

### 📊 Video Formats
Supports: MP4, AVI, MOV, MKV, WEBM, FLV, M4V

## Installation

### 1. Install Video Dependencies
```bash
pip install opencv-python moviepy numpy
```

### 2. Run Video Transcription App
```bash
streamlit run app-video.py
```

## Quick Test

Test your setup with the included test script:
```bash
python test_video_transcription.py [optional_video_file_path]
```

## 🚀 Modern Clarifai SDK Integration

Now powered by the **latest Clarifai SDK** with improved performance and reliability:

### 🔧 SDK Features
- **Direct Video Processing**: No more frame extraction - send videos directly to models
- **Automatic Fallback**: Uses modern SDK first, falls back to gRPC if needed
- **Better Error Handling**: Improved error messages and debugging
- **Faster Processing**: Optimized video upload and inference pipeline
- **Native Support**: Full compatibility with all Clarifai multimodal models

### 📊 SDK Performance
- **Processing Speed**: ~2-5 seconds for short videos
- **Memory Efficiency**: Direct video upload without intermediate processing
- **Reliability**: Automatic retry logic and fallback mechanisms

## 🌟 Advanced Video Understanding with Qwen2.5-VL

The **Qwen2.5-VL-7B-Instruct** model brings cutting-edge capabilities to video analysis:

### 🎯 Key Enhancements
- **Long Video Analysis**: Can comprehend videos over 1 hour long
- **Temporal Understanding**: Pinpoints specific moments and events in videos
- **Visual Agent Capabilities**: Reasons and dynamically analyzes visual content
- **Object Localization**: Accurately identifies and locates objects with coordinates
- **Structured Data Extraction**: Perfect for analyzing invoices, forms, tables in videos
- **Dynamic Resolution & Frame Rate**: Adapts to various video qualities and sampling rates

### 💰 Pricing
- Input: $0.44472 per 1M tokens
- Output: $1.32414 per 1M tokens
- Excellent value for advanced video analysis capabilities

## How It Works

### 1. Frame Extraction
- Extracts up to 10 key frames from the video
- Resizes frames for optimal processing
- Selects representative frames across video duration

### 2. Audio Processing (Optional)
- Extracts audio track using MoviePy
- Transcribes using specialized audio models (Whisper V3)
- Combines with visual analysis for complete context

### 3. Multimodal Analysis
- Sends frames and text prompt to AI model
- Analyzes visual content, actions, and context
- Generates comprehensive transcription and description

### 4. Results Integration
- Combines visual and audio insights
- Provides structured output with timestamps
- Includes confidence metrics and processing stats

## Configuration

### Environment Variables
```bash
# Required
CLARIFAI_PAT=your_personal_access_token

# Optional Video Settings
DEFAULT_VIDEO_MODEL=GPT-4o Mini
MAX_VIDEO_SIZE_MB=100
VIDEO_FRAME_EXTRACTION_INTERVAL=5
VIDEO_QUALITY_OPTIMIZATION=true
```

### Model Configuration
Video models are configured in `config.py` under `AVAILABLE_VIDEO_MODELS`. Each model includes:
- Model ID and provider information
- Description and star rating
- Supported features (multimodal, video_analysis, etc.)
- Processing capabilities

## Usage Examples

### Basic Video Transcription
1. Upload video file (MP4, AVI, MOV, etc.)
2. Select AI model (GPT-4o Mini recommended for cost-effectiveness)
3. Enable audio extraction for complete analysis
4. Click "Start Video Transcription"

### Custom Analysis Prompts
```
Please analyze this video and provide:
1. Complete dialogue transcription
2. Visual scene descriptions
3. Any text or signs visible
4. Key actions and events
5. Emotional context and tone
```

### Processing Large Videos
- Videos up to 100MB supported by default
- Automatic frame sampling for efficiency
- Audio extraction happens separately for accuracy
- Progress tracking during processing

## API Integration

### Direct API Usage
```python
from ClarifaiVideoUtil import ClarifaiVideoTranscriber

transcriber = ClarifaiVideoTranscriber("your_api_key")

# Basic video transcription
result = transcriber.transcribe_video(
    video_path="path/to/video.mp4",
    model_name="GPT-4o Mini",
    temperature=0.7,
    max_tokens=1000
)

# Enhanced transcription with audio
result = transcriber.transcribe_video_with_audio(
    video_path="path/to/video.mp4",
    model_name="Claude 3.5 Sonnet",
    audio_transcription="Previously extracted audio text...",
    temperature=0.5,
    max_tokens=1500
)
```

### Response Format
```python
{
    "success": True,
    "transcription": "Complete video analysis text...",
    "model_used": "GPT-4o Mini",
    "frames_processed": 8,
    "processing_time": 12.34,
    "video_info": {
        "path": "/path/to/video.mp4",
        "size_mb": 25.6
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Dependencies Missing
```
Error: OpenCV is required for video processing
Solution: pip install opencv-python moviepy numpy
```

#### 2. Large Video Files
```
Error: File size exceeds maximum allowed size
Solution: Compress video or increase MAX_VIDEO_SIZE_MB
```

#### 3. Audio Extraction Fails
```
Warning: Could not extract audio from video
Solution: Check video has audio track, or disable audio processing
```

#### 4. No Frames Extracted
```
Error: Could not extract frames from video
Solution: Check video format compatibility, try converting to MP4
```

### Performance Optimization

#### For Best Results:
- **Video Quality**: 720p-1080p resolution recommended
- **Duration**: Under 5 minutes for fastest processing
- **Format**: MP4 with H.264 encoding works best
- **Audio**: Clear speech for better audio transcription

#### Model Selection:
- **Qwen2.5-VL-7B-Instruct**: 🌟 **RECOMMENDED** - Advanced video understanding with temporal reasoning, long video analysis (1+ hours), object localization, and structured data extraction
- **GPT-4o Mini**: Best balance of speed and cost
- **Claude 3.5 Sonnet**: Best for complex analysis
- **Gemini 2.0 Flash**: Fastest processing
- **GPT-4o**: Best overall quality (higher cost)

## Technical Details

### Frame Processing
- Extracts frames at regular intervals
- Resizes to max 1280x720 for efficiency
- Converts to JPEG with 85% quality
- Base64 encoding for API transmission

### Audio Integration
- Uses MoviePy for audio extraction
- Leverages Whisper V3 for audio transcription
- Combines audio and visual context intelligently
- Automatic cleanup of temporary files

### API Communication
- Uses Clarifai gRPC API for reliability
- Supports all major multimodal models
- Handles authentication and error responses
- Provides detailed processing metrics

## Comparison with Audio-Only

| Feature | Audio App | Video App |
|---------|-----------|-----------|
| Input Types | Audio files | Video files + extracted audio |
| AI Models | Speech-to-text | Multimodal (vision + text) |
| Analysis | Audio transcription | Visual + audio analysis |
| Use Cases | Podcasts, calls, music | Movies, presentations, tutorials |
| Processing | Fast audio-only | Comprehensive multimodal |
| Output | Text transcription | Rich content description |

## Next Steps

1. **Install Dependencies**: `pip install opencv-python moviepy numpy`
2. **Test Setup**: `python test_video_transcription.py`
3. **Run App**: `streamlit run app-video.py`
4. **Upload Video**: Try with a short test video first
5. **Experiment**: Test different models and prompts for your use case

---

*Built with ❤️ using Clarifai's multimodal AI models*