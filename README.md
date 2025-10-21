# Audio Transcription App with Clarifai

A Streamlit application that transcribes audio files using Clarifai's speech-to-text models. Users can upload audio files, select different transcription models, and adjust inference parameters for optimal results.

## Features

- 🎙️ **Audio File Upload**: Support for multiple audio formats (WAV, MP3, FLAC, M4A, OGG)
- 🤖 **Multiple Models**: Choose from 7 top-rated Clarifai speech-to-text models:
  - AssemblyAI Audio Transcription (human-level accuracy)
  - OpenAI Whisper V3 (latest with improved accuracy) 
  - OpenAI Whisper V2 & Base (multilingual support)
  - Deepgram Nova-2 (30% lower error rates)
  - Facebook Wav2Vec2 (English optimized)
  - Google Chirp ASR (enterprise-grade)
- ⚙️ **Configurable Parameters**: Adjust temperature and max tokens for transcription
- 📥 **Export Results**: Download transcriptions as text files
- 🎨 **User-Friendly Interface**: Clean, intuitive Streamlit interface

## Prerequisites

- Python 3.8 or higher
- Clarifai API key (get one from [Clarifai Portal](https://clarifai.com/settings/security))

## Installation

1. **Clone or download this repository**
   ```bash
   cd audio-transcribe
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy the example environment file and edit it:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your settings:
   ```bash
   # Required
   CLARIFAI_PAT=your_actual_pat_here
   CLARIFAI_USER_ID=your_user_id_here
   CLARIFAI_APP_ID=your_app_id_here
   
   # Optional (defaults shown)
   STREAMLIT_SERVER_PORT=8501
   STREAMLIT_SERVER_ADDRESS=localhost
   MAX_FILE_SIZE_MB=25
   DEFAULT_MODEL=AssemblyAI Audio Transcription
   DEFAULT_TEMPERATURE=0.7
   DEFAULT_MAX_TOKENS=1000
   APP_TITLE=Audio Transcription with Clarifai
   APP_ICON=🎙️
   ```
   
   Alternative options:
   - Set environment variables manually: `export CLARIFAI_PAT=your_pat`
   - Enter the PAT directly in the app interface (sidebar)

## Usage

### Option A: Quick Start (Recommended)
```bash
./start.sh
```
This script will automatically load environment variables and start the app.

### Option B: Manual Start
```bash
streamlit run app.py
```

### Accessing the App
- The app will open in your default browser at `http://localhost:8501`
- If not, navigate to the URL shown in the terminal
- Port and address can be configured via environment variables

3. **Using the app**
   - Enter your Clarifai API key in the sidebar (if not set via environment)
   - Select a speech-to-text model from the dropdown
   - Adjust inference parameters if needed:
     - **Temperature**: Controls randomness (0.0 = deterministic, 1.0 = creative)
     - **Max Tokens**: Maximum length of transcription output
   - Upload an audio file using the file uploader
   - Click "Transcribe Audio" to start transcription
   - View results and optionally download as a text file

## Supported Audio Formats

- WAV (`.wav`)
- MP3 (`.mp3`) 
- FLAC (`.flac`)
- M4A (`.m4a`)
- OGG (`.ogg`)

## Available Models

The app now includes the top-rated audio-to-text models from Clarifai's marketplace:

### AssemblyAI Audio Transcription (⭐ 19 stars)
- **Provider**: AssemblyAI
- **Description**: Achieves human-level accuracy in just seconds
- **Best for**: High accuracy general transcription

### OpenAI Whisper Large V3 (⭐ 6 stars) 
- **Provider**: OpenAI
- **Description**: Latest Whisper with 10-20% error reduction compared to V2
- **Best for**: Latest improvements, multilingual support

### OpenAI Whisper Large V2 (⭐ 13 stars)
- **Provider**: OpenAI  
- **Description**: High accuracy multilingual transcription model
- **Best for**: Multilingual content, detailed transcription

### OpenAI Whisper (⭐ 14 stars)
- **Provider**: OpenAI
- **Description**: Versatile pre-trained ASR and speech translation model
- **Best for**: General purpose, fast processing

### Deepgram Nova-2 (⭐ 3 stars)
- **Provider**: Deepgram
- **Description**: 30% lower error rates with unmatched speed
- **Best for**: Speed and accuracy balance

### Facebook Wav2Vec2 English (⭐ 9 stars)
- **Provider**: Facebook
- **Description**: Optimized for English speech recognition
- **Best for**: English-only content

### Google Chirp ASR (⭐ 4 stars)
- **Provider**: Google Cloud
- **Description**: State-of-the-art speech recognition from GCP
- **Best for**: Enterprise-grade accuracy

## Environment Variables

All configuration can be managed through environment variables in the `.env` file:

### Required Variables
- **`CLARIFAI_PAT`**: Your Clarifai Personal Access Token (get from [Clarifai Portal](https://clarifai.com/settings/security))
- **`CLARIFAI_USER_ID`**: Your Clarifai user ID
- **`CLARIFAI_APP_ID`**: Your Clarifai application ID

### Optional Variables
- **`STREAMLIT_SERVER_PORT`**: Port for the Streamlit server (default: 8501)
- **`STREAMLIT_SERVER_ADDRESS`**: Address for the Streamlit server (default: localhost)
- **`MAX_FILE_SIZE_MB`**: Maximum allowed file size in MB (default: 25)
- **`DEFAULT_MODEL`**: Default transcription model (default: "AssemblyAI Audio Transcription")
- **`DEFAULT_TEMPERATURE`**: Default temperature value (default: 0.7)
- **`DEFAULT_MAX_TOKENS`**: Default max tokens value (default: 1000)
- **`APP_TITLE`**: Application title (default: "Audio Transcription with Clarifai")
- **`APP_ICON`**: Application icon emoji (default: "🎙️")

### Configuration Validation
The app automatically validates all environment variables on startup and shows helpful error messages if any values are invalid.

## Configuration Parameters

### Temperature
- **Range**: 0.0 - 1.0
- **Default**: 0.7
- **Description**: Controls the randomness of the model's output. Lower values (closer to 0) make the output more deterministic and focused, while higher values increase creativity and variation.

### Max Tokens
- **Range**: 100 - 2000
- **Default**: 1000
- **Description**: Sets the maximum number of tokens (roughly words) in the transcription output. Adjust based on expected audio length.

## Troubleshooting

### Common Issues

1. **"Import could not be resolved" errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using the correct Python environment

2. **"Clarifai API key is required" error**
   - Verify your API key is correct
   - Check that the environment variable is set or enter it in the sidebar

3. **"Transcription failed" error**
   - Check your internet connection
   - Verify the audio file format is supported
   - Ensure your Clarifai API key has sufficient credits
   - Try a smaller audio file or different model

4. **Slow transcription**
   - Large audio files take longer to process
   - Try using Whisper Base for faster (but potentially less accurate) results
   - Consider breaking long audio files into smaller segments

### Getting Help

- Check the [Clarifai Documentation](https://docs.clarifai.com/)
- Verify your API key at [Clarifai Portal](https://clarifai.com/settings/security)
- Ensure your audio file is under the size limits (typically 25MB for most services)

## Project Structure

```
audio-transcribe/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── start.sh                  # Startup script (executable)
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Environment variables template
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── README.md                # This documentation
└── SoftwareSpec.md          # Original specification
```

## Dependencies

- **streamlit**: Web app framework
- **clarifai**: Clarifai Python SDK
- **clarifai-grpc**: Clarifai gRPC client
- **python-dotenv**: Environment variable management

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.