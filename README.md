# 🎙️ Audio Transcription App with Clarifai

A powerful Streamlit application that transcribes audio files using Clarifai's speech-to-text models with advanced audio quality enhancement. Upload audio files, select from 7 top-rated models, and get high-quality transcriptions with real-time audio processing.

## ✨ Features

### � **Advanced Audio Processing**
- **Smart Format Conversion**: Automatic MP3→WAV conversion with quality optimization
- **Audio Enhancement**: 16kHz resampling, mono conversion, normalization, silence trimming
- **Real-time Playback**: Listen to converted audio files before and after processing
- **Quality Controls**: Configurable audio processing parameters in sidebar
- **Format Support**: WAV, MP3, FLAC, M4A, OGG input formats

### 🤖 **7 Premium Speech-to-Text Models**
- **OpenAI Whisper Large V3** ⭐ Most Accurate & Fast (1.6s)
- **AssemblyAI Audio Transcription** ⭐ Human-level accuracy (5.2s)
- **Deepgram Nova-2** ⚡ Speed-accuracy balance (1.3s)
- **Google Chirp ASR** 🏢 Enterprise-grade (6.2s)
- **Facebook Wav2Vec2 English** 🚀 Fastest processing (0.8s)
- **OpenAI Whisper Large V2** 🌍 Multilingual support (1.9s)
- **OpenAI Whisper Base** ⚖️ Balanced performance (2.5s)

### ⚙️ **Advanced Configuration**
- **Audio Quality Settings**: High-quality vs basic conversion modes
- **Inference Parameters**: Temperature (0.01-1.0) and max tokens (100-2000)
- **Model Selection**: Real-time model switching with descriptions
- **Dedicated Compute**: Support for deployed models with guaranteed performance
- **Environment Config**: Complete .env file configuration system
- **Validation**: Automatic configuration validation with helpful error messages

### 🎨 **Professional Interface**
- **Clean Design**: Modern Streamlit interface with organized sidebar controls
- **Real-time Feedback**: Live audio conversion progress and quality metrics
- **Export Options**: Download transcriptions as text files
- **Audio Playback**: Built-in audio player for quality verification
- **Status Indicators**: Model performance and processing information

## 🔧 Prerequisites

- **Python 3.8+** (Python 3.12 recommended)
- **Clarifai Account**: Get your API key from [Clarifai Portal](https://clarifai.com/settings/security)
- **Audio Files**: Supported formats (MP3, WAV, FLAC, M4A, OGG)
- **Internet Connection**: Required for Clarifai API calls

## 📦 Quick Installation

### Option A: One-Command Setup (Recommended)
```bash
git clone <your-repo-url>
cd audio-transcribe
cp .env.example .env
# Edit .env with your Clarifai credentials
pip install -r requirements.txt
./start.sh
```

### Option B: Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd audio-transcribe
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (see Configuration section below)
   ```
   
## ⚙️ Configuration

### Step 1: Get Your Clarifai Credentials

1. **Create a Clarifai Account**: Visit [Clarifai.com](https://clarifai.com) and sign up
2. **Get Personal Access Token (PAT)**:
   - Go to [Clarifai Portal → Security](https://clarifai.com/settings/security)
   - Create a new Personal Access Token
   - Copy the token (starts with your username)
3. **Find Your User ID**: Usually your username or displayed in portal
4. **Get App ID**: Use existing app or create new one for transcription

### Step 2: Configure Environment Variables

Edit the `.env` file with your Clarifai credentials:

```bash
# ===== REQUIRED CONFIGURATION =====
CLARIFAI_PAT=your_personal_access_token_here
CLARIFAI_USER_ID=your_username_here
CLARIFAI_APP_ID=your_app_id_here

# ===== DEDICATED COMPUTE (OPTIONAL) =====
# For dedicated deployed models - better performance & custom models
# CLARIFAI_DEPLOYMENT_ID=deploy-whisper-large-v3-cr4h

# ===== MODEL SETTINGS =====
DEFAULT_MODEL=OpenAI Whisper Large V3
DEFAULT_TEMPERATURE=0.01
DEFAULT_MAX_TOKENS=1000

# ===== AUDIO QUALITY ENHANCEMENT =====
HIGH_QUALITY_CONVERSION=true
TARGET_SAMPLE_RATE=16000
NORMALIZE_AUDIO=true
TRIM_SILENCE=true

# ===== APP CONFIGURATION =====
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
MAX_FILE_SIZE_MB=25
APP_TITLE=Audio Transcription with Clarifai
APP_ICON=🎙️
```

### Configuration Options Explained

#### 🔑 **Required Settings**
| Variable | Description | Example |
|----------|-------------|---------|
| `CLARIFAI_PAT` | Your Personal Access Token from Clarifai Portal | `username_1a2b3c4d...` |
| `CLARIFAI_USER_ID` | Your Clarifai username/user ID | `your-username` |
| `CLARIFAI_APP_ID` | Clarifai application ID to use | `audio-transcription` |

#### 🚀 **Dedicated Compute (Optional)**
| Variable | Description | Example | Benefits |
|----------|-------------|---------|----------|
| `CLARIFAI_DEPLOYMENT_ID` | Deployment ID for dedicated models | `deploy-whisper-large-v3-cr4h` | Better performance, custom models, guaranteed compute |

**Dedicated Compute Features:**
- **🎯 Better Performance**: Dedicated compute resources with guaranteed availability
- **⚡ Faster Processing**: No shared resource contention, reduced latency  
- **🔧 Custom Models**: Access to fine-tuned or specialized model versions
- **📊 Enhanced Reliability**: SLA guarantees and isolated infrastructure
- **💰 Enterprise Features**: Priority support and advanced monitoring

**Configuration Options:**
1. **Global Override** (Environment Variable): Set `CLARIFAI_DEPLOYMENT_ID` to apply to ALL models
2. **Per-Model Config** (config.py): Set `deployment_id` for specific models only
3. **Priority Order**: Environment variable overrides model-specific settings

#### 🎯 **Model Settings**
| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `DEFAULT_MODEL` | `OpenAI Whisper Large V3` | See models list | Default selected model |
| `DEFAULT_TEMPERATURE` | `0.01` | `0.0-1.0` | Transcription randomness (0=deterministic, 1=creative) |
| `DEFAULT_MAX_TOKENS` | `1000` | `100-2000` | Maximum transcription length |

#### 🎵 **Audio Quality Settings**
| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `HIGH_QUALITY_CONVERSION` | `true` | `true/false` | Enable enhanced audio processing |
| `TARGET_SAMPLE_RATE` | `16000` | `8000,16000,22050,44100` | Sample rate for conversion (16kHz recommended) |
| `NORMALIZE_AUDIO` | `true` | `true/false` | Normalize audio levels for consistency |
| `TRIM_SILENCE` | `true` | `true/false` | Remove silence from beginning/end |

#### 🖥️ **Server Settings**
| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMLIT_SERVER_PORT` | `8501` | Port for web interface |
| `STREAMLIT_SERVER_ADDRESS` | `localhost` | Server address (use `0.0.0.0` for external access) |
| `MAX_FILE_SIZE_MB` | `25` | Maximum audio file size in MB |

### Alternative Configuration Methods

1. **Direct Environment Variables** (Linux/Mac):
   ```bash
   export CLARIFAI_PAT="your_token_here"
   export CLARIFAI_USER_ID="your_username"
   export CLARIFAI_APP_ID="your_app_id"
   streamlit run app.py
   ```

2. **Windows PowerShell**:
   ```powershell
   $env:CLARIFAI_PAT="your_token_here"
   $env:CLARIFAI_USER_ID="your_username"  
   $env:CLARIFAI_APP_ID="your_app_id"
   streamlit run app.py
   ```

3. **Runtime Configuration**: Leave .env empty and enter credentials in the app sidebar

### 🚀 Dedicated Compute Configuration

The application now supports dedicated compute deployments for better performance and custom models. Here's how to configure deployment IDs:

#### Option 1: Environment Variable (Global Override)

Set `CLARIFAI_DEPLOYMENT_ID` in your `.env` file to apply to **ALL models**:

```bash
# .env file
CLARIFAI_DEPLOYMENT_ID=deploy-whisper-large-v3-cr4h
```

This will override any model-specific deployment IDs and apply the same deployment to all transcriptions.

#### Option 2: Per-Model Configuration (config.py)

Configure deployment IDs for specific models by editing `config.py`:

```python
# config.py - Add deployment_id to specific models
"OpenAI Whisper Large V3": {
    "model_id": "whisper-large-v3",
    "user_id": "openai",
    "app_id": "transcription",
    "description": "Latest Whisper v3: 10-20% error reduction...",
    "status": "working",
    "deployment_id": "deploy-whisper-large-v3-cr4h"  # Add this line
},

"Custom Fine-tuned Model": {
    "model_id": "my-custom-model",
    "user_id": "my-username",
    "app_id": "my-app",
    "description": "My custom fine-tuned model",
    "status": "working",
    "deployment_id": "deploy-custom-model-xyz123"     # Custom deployment
}
```

#### Getting Deployment IDs

1. **Visit Clarifai Dashboard**: Go to [clarifai.com/apps](https://clarifai.com/apps)
2. **Select Your App**: Navigate to your application
3. **Go to Models**: Choose the model you want to deploy
4. **Create/View Deployments**: In the "Deployments" section
5. **Copy Deployment ID**: Format is usually `deploy-model-name-xxxx`

#### Configuration Priority

The deployment ID resolution follows this priority order:

1. **🌍 Environment Variable** (`CLARIFAI_DEPLOYMENT_ID`) - **Highest Priority**
2. **📝 Model-Specific Config** (`config.py` deployment_id) - **Fallback**
3. **🌐 Standard Shared Models** (no deployment_id) - **Default**

#### Debug Messages

When deployment IDs are configured, you'll see debug messages indicating which compute type is being used:

```bash
# Dedicated compute messages
🎯 Initializing dedicated compute for: OpenAI Whisper Large V3
📋 Deployment ID: deploy-whisper-large-v3-cr4h
🚀 Using dedicated compute deployment: deploy-whisper-large-v3-cr4h

# Shared compute messages  
🌐 Using shared compute for: Facebook Wav2Vec2 English
🌐 Using shared model: asr-wav2vec2-base-960h-english (standard)
```

#### Testing Deployment Configuration

Use the provided test scripts to verify your deployment setup:

```bash
# Test deployment ID configuration
python3 test_deployment_id.py

# Test debug messages with different deployments
python3 test_debug_messages.py

# Test with environment override
CLARIFAI_DEPLOYMENT_ID=your-deployment-id python3 test_debug_messages.py
```

---

## 🚀 Running the Application

### Option A: Quick Start (Recommended)
```bash
# Make startup script executable and run
chmod +x start.sh
./start.sh
```
✅ **Benefits**: Automatic environment loading, error checking, and optimized startup

### Option B: Direct Streamlit Launch
```bash
streamlit run app.py --server.port 8501 --server.address localhost
```

### Option C: Python Module Launch  
```bash
python -m streamlit run app.py
```

### Option D: Development Mode
```bash
# For development with auto-reload
streamlit run app.py --server.runOnSave true
```

---

## 🖥️ Using the Application

### 1. **Access the Web Interface**
- **URL**: http://localhost:8501 (opens automatically)
- **Alternative**: Check terminal for exact URL if different port
- **External Access**: Set `STREAMLIT_SERVER_ADDRESS=0.0.0.0` in .env for network access

### 2. **Sidebar Configuration Panel**

#### **🤖 Model Selection**
- Choose from 7 premium speech-to-text models
- Real-time model descriptions and performance indicators
- Default: OpenAI Whisper Large V3 (best balance of speed/accuracy)

#### **🎛️ Inference Parameters**
- **Temperature** (0.01-1.0): Controls transcription creativity
  - `0.01`: Most deterministic, consistent results
  - `0.5`: Balanced approach  
  - `1.0`: Most creative, varied results
- **Max Tokens** (100-2000): Maximum transcription length
  - `500`: Short audio clips
  - `1000`: Standard recordings (default)
  - `2000`: Long-form content

#### **🎵 Audio Enhancement Controls**
- **Enable High Quality**: Toggle advanced audio processing
- **Sample Rate**: Choose optimal frequency (8kHz-48kHz)
- **Audio Normalization**: Standardize volume levels
- **Silence Trimming**: Remove quiet segments
- **Quality Preview**: Real-time processing information

### 3. **Audio Processing Workflow**

#### **📁 Step 1: Upload Audio File**
```
Supported Formats: MP3, WAV, FLAC, M4A, OGG
Maximum Size: 25MB (configurable)
Quality: Any bitrate, sample rate, mono/stereo
```

#### **🔄 Step 2: Automatic Enhancement**
- **Format Detection**: Automatic audio format recognition
- **Quality Conversion**: MP3→WAV with optimization
- **Processing Pipeline**: 
  1. Mono conversion (stereo→mono)
  2. Sample rate optimization (→16kHz)  
  3. Bit depth standardization (→16-bit)
  4. Audio normalization (volume leveling)
  5. Silence trimming (noise reduction)

#### **▶️ Step 3: Audio Playback**
- **Original Audio**: Play uploaded file
- **Converted Audio**: Play processed WAV file  
- **Quality Comparison**: A/B testing capability
- **Download Option**: Save converted WAV file

#### **🎯 Step 4: Transcription**
- **Model Processing**: Real-time transcription with selected model
- **Progress Indicators**: Processing status and timing
- **Quality Metrics**: Conversion details and performance stats

#### **📄 Step 5: Results & Export**
- **Text Display**: Formatted transcription results
- **Copy to Clipboard**: Quick text copying
- **Download**: Export as .txt file
- **Processing Stats**: Speed, accuracy, and quality information

### 4. **🔍 Debug Messages & Compute Monitoring**

The application provides real-time debug messages to help you monitor which compute type is being used for each transcription:

#### **🚀 Dedicated Compute Indicators**
When using deployed models with dedicated compute, you'll see:
```bash
🎯 Initializing dedicated compute for: OpenAI Whisper Large V3
📋 Deployment ID: deploy-whisper-large-v3-cr4h
🚀 Using dedicated compute deployment: deploy-whisper-large-v3-cr4h
💻 Model: whisper-large-v3 (dedicated deployment)
```

#### **🌐 Shared Compute Indicators**
For standard shared models, you'll see:
```bash
🌐 Using shared compute for: Facebook Wav2Vec2 English  
🌐 Using shared model: asr-wav2vec2-base-960h-english (standard)
```

#### **📊 Benefits of Debug Messages**
- **💰 Cost Tracking**: Know when you're using dedicated (paid) vs shared compute
- **🐛 Configuration Debugging**: Verify deployment_id settings are working
- **📈 Performance Monitoring**: Track which deployments are being used
- **⚠️ Issue Detection**: Get notified about configuration problems

### 5. **Advanced Usage Patterns**

#### **🔄 Batch Processing Workflow**
1. Configure optimal settings for your audio type
2. Process multiple files with same settings
3. Compare model performance for your content
4. Export all results for analysis

#### **🧪 Quality Testing Workflow**  
1. Upload sample audio file
2. Test with different quality settings
3. Compare transcription accuracy
4. Optimize settings for your use case

#### **⚡ Speed Optimization Workflow**
1. Use Facebook Wav2Vec2 for fastest processing
2. Disable quality enhancements for speed
3. Lower sample rate (8kHz) for very fast results
4. Reduce max tokens for shorter content

## Supported Audio Formats

- WAV (`.wav`)
- MP3 (`.mp3`) 
- FLAC (`.flac`)
- M4A (`.m4a`)
- OGG (`.ogg`)

## 🤖 Available Speech-to-Text Models

All 7 premium models now work with 100% reliability thanks to advanced WAV conversion!

### 🏆 **Recommended Models**

#### **OpenAI Whisper Large V3** ⭐ **BEST OVERALL**
- **Speed**: 1.6 seconds (Very Fast)
- **Accuracy**: Excellent (Most accurate results)
- **Provider**: OpenAI  
- **Features**: Latest Whisper with 10-20% error reduction
- **Best For**: Production use, high accuracy + speed balance
- **Sample Result**: `"Hello. Hello. Huh? Hi, how you doing? I'm good. How's your new single?"`

#### **AssemblyAI Audio Transcription** 🎯 **MOST ACCURATE**  
- **Speed**: 5.2 seconds (Thorough processing)
- **Accuracy**: Excellent (Human-level accuracy)
- **Provider**: AssemblyAI (19⭐)
- **Features**: Achieves professional-grade transcription quality
- **Best For**: Critical accuracy applications, professional transcription
- **Sample Result**: `"Hello. Hello. Huh? Hi. How you doing? I'm good. How's university going?"`

#### **Facebook Wav2Vec2 English** ⚡ **FASTEST**
- **Speed**: 0.8 seconds (Ultra-fast)
- **Accuracy**: Good (Optimized for speed)
- **Provider**: Facebook (9⭐)
- **Features**: Lightning-fast English speech recognition
- **Best For**: Real-time applications, quick transcription needs
- **Sample Result**: `"WHO YONDER HER AT BABA NA A MAN HAN YOU O AN"`

### 🚀 **High-Performance Models**

#### **Deepgram Nova-2** 🏃 **SPEED + ACCURACY**
- **Speed**: 1.3 seconds (Very fast)
- **Accuracy**: Very Good
- **Provider**: Deepgram (3⭐)
- **Features**: 30% lower error rates with superior speed
- **Best For**: High-throughput applications, speed-critical use cases
- **Sample Result**: `"Hello? Hi. How are you doing? I'm good. How's University of"`

#### **OpenAI Whisper Large V2** 🌍 **MULTILINGUAL**
- **Speed**: 1.9 seconds (Fast)
- **Accuracy**: Very Good  
- **Provider**: OpenAI (13⭐)
- **Features**: Excellent multilingual support
- **Best For**: International content, multiple languages
- **Sample Result**: `"Hello, I'm... Wylo. Tosh. And I'm doing... I'm doing... How's it going?"`

### 📊 **Standard Models**

#### **OpenAI Whisper Base** ⚖️ **BALANCED**
- **Speed**: 2.5 seconds (Moderate)
- **Accuracy**: Good
- **Provider**: OpenAI (14⭐) 
- **Features**: Versatile general-purpose ASR model
- **Best For**: General transcription, development testing
- **Sample Result**: `"Hello. Why, love? Huh? Hi, how you doing? I'm good. How's your disabled?"`

#### **Google Chirp ASR** 🏢 **ENTERPRISE**
- **Speed**: 6.2 seconds (Thorough)
- **Accuracy**: Good
- **Provider**: Google Cloud (4⭐)
- **Features**: Enterprise-grade cloud-based recognition  
- **Best For**: Enterprise integration, Google Cloud workflows
- **Sample Result**: `"hello hello huh hi how you doing i'm good how's university"`

### 📈 **Performance Comparison**

| Model | Speed | Accuracy | Best Use Case | Output Style |
|-------|-------|----------|---------------|-------------|
| **Whisper Large V3** | ⚡⚡⚡⚡ | 🎯🎯🎯🎯🎯 | **Production** | Natural, punctuated |
| **AssemblyAI** | ⚡⚡⚡ | 🎯🎯🎯🎯🎯 | **Professional** | Formal, detailed |  
| **Wav2Vec2 English** | ⚡⚡⚡⚡⚡ | 🎯🎯🎯 | **Real-time** | Uppercase, phonetic |
| **Deepgram Nova-2** | ⚡⚡⚡⚡ | 🎯🎯🎯🎯 | **High-volume** | Clean, natural |
| **Whisper Large V2** | ⚡⚡⚡⚡ | 🎯🎯🎯🎯 | **Multilingual** | Detailed, hesitations |
| **Whisper Base** | ⚡⚡⚡ | 🎯🎯🎯 | **General** | Simple, direct |
| **Google Chirp** | ⚡⚡ | 🎯🎯🎯 | **Enterprise** | Lowercase, basic |

### 🎯 **Model Selection Guide**

- **For Maximum Accuracy**: AssemblyAI Audio Transcription  
- **For Best Balance**: OpenAI Whisper Large V3 ⭐ **DEFAULT**
- **For Speed**: Facebook Wav2Vec2 English
- **For Multilingual**: OpenAI Whisper Large V2
- **For Enterprise**: Google Chirp ASR
- **For Development**: OpenAI Whisper Base

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

## 🔧 Troubleshooting & FAQ

### 🚨 **Common Issues & Solutions**

#### **Configuration Errors**

**❌ "Clarifai API key is required"**
```bash
# Solution 1: Check .env file
cat .env | grep CLARIFAI_PAT

# Solution 2: Set environment variable  
export CLARIFAI_PAT="your_actual_token_here"

# Solution 3: Enter in app sidebar
# Open app and enter PAT in "Clarifai Configuration" section
```

**❌ "Import could not be resolved"** 
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt

# For conda users:
conda install --file requirements.txt
```

**❌ "Configuration validation failed"**
```bash
# Check your .env file format:
# - No spaces around = signs
# - No quotes unless needed  
# - Check for typos in variable names
```

#### **Audio Processing Issues**

**❌ "Audio conversion failed"**
```bash  
# Solution 1: Install pydub properly
pip install pydub

# Solution 2: For MP3 support (Linux/Mac)
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS

# Solution 3: Try different audio file
# Some corrupted files may fail conversion
```

**❌ "File size exceeds maximum"**
```bash
# Solution 1: Increase limit in .env
MAX_FILE_SIZE_MB=50

# Solution 2: Compress audio file
ffmpeg -i large_file.mp3 -b:a 128k compressed.mp3

# Solution 3: Split long audio
ffmpeg -i long.mp3 -f segment -segment_time 300 -c copy output%d.mp3
```

#### **Performance Issues**

**🐌 "Transcription is slow"**
- **Quick Fix**: Use Facebook Wav2Vec2 English (0.8s processing)
- **Quality Fix**: Reduce audio file size or duration  
- **Settings Fix**: Disable quality enhancements for speed
```bash
# In .env file:
HIGH_QUALITY_CONVERSION=false
TARGET_SAMPLE_RATE=8000
```

**💾 "High memory usage"**
- **Solution**: Process shorter audio segments
- **Alternative**: Use basic quality conversion mode
- **Optimization**: Close other applications during processing

#### **Dedicated Compute Issues**

**❌ "Deployment not found"**
```bash
# Error: Deployment not found: deploy-invalid-xxxx
# Solution 1: Verify deployment ID exists and is active
# - Check Clarifai dashboard under Deployments
# - Ensure deployment is running (not stopped/paused)

# Solution 2: Check deployment ID format
# - Should look like: deploy-model-name-xxxx
# - Copy exact ID from Clarifai portal

# Solution 3: Test with debug messages
python3 test_deployment_id.py
```

**❌ "Deployment is starting up"**
```bash
# Error: Deployment is starting up, please retry in a few seconds
# Solution: Wait 30-60 seconds and retry
# - Deployments take time to initialize
# - This is normal for dedicated compute

# Alternative: Use shared model temporarily
# Comment out deployment_id in config.py
```

**❌ "Access denied to deployment"**
```bash
# Solution 1: Verify PAT permissions
# - Ensure your PAT has access to deployments
# - Check if deployment belongs to your account

# Solution 2: Check organization access
# - Verify you're in the right Clarifai organization
# - Ask admin to grant deployment access
```

**🔍 "Debug messages show wrong deployment ID"**
```bash
# Check environment variable override
echo $CLARIFAI_DEPLOYMENT_ID

# If set, it overrides all model-specific deployment IDs
# To use per-model settings:
unset CLARIFAI_DEPLOYMENT_ID

# Or comment out in .env:
# CLARIFAI_DEPLOYMENT_ID=deploy-whisper-large-v3-cr4h
```

### ❓ **Frequently Asked Questions**

#### **Q: Which model should I use?**
- **General Use**: OpenAI Whisper Large V3 (default)
- **Speed Critical**: Facebook Wav2Vec2 English  
- **Maximum Accuracy**: AssemblyAI Audio Transcription
- **Multilingual**: OpenAI Whisper Large V2
- **Long Audio**: Deepgram Nova-2 (good speed/accuracy balance)

#### **Q: How can I improve transcription accuracy?**
1. **Use high-quality audio**: Clear recording, minimal background noise
2. **Enable quality enhancement**: `HIGH_QUALITY_CONVERSION=true`
3. **Choose optimal model**: AssemblyAI for best accuracy
4. **Adjust temperature**: Lower values (0.01) for consistency
5. **Proper audio format**: WAV files often work better than MP3

#### **Q: What audio formats work best?**
- **Best**: WAV files (16kHz, mono, 16-bit)
- **Good**: MP3 files (any quality - will be converted)
- **Supported**: FLAC, M4A, OGG
- **Recommended**: < 10MB file size for best performance

#### **Q: Can I use this for real-time transcription?**
- **Current**: No, this is designed for file-based transcription
- **Fastest**: Facebook Wav2Vec2 English processes in 0.8 seconds
- **Alternative**: Use for near-real-time by processing short segments

#### **Q: Is my audio data secure?**
- **Processing**: Audio is sent to Clarifai's secure servers
- **Storage**: No audio is stored locally after processing  
- **Privacy**: Check [Clarifai's Privacy Policy](https://clarifai.com/privacy)
- **Security**: All API calls use HTTPS encryption

#### **Q: Should I use dedicated compute or shared models?**
- **Shared Models (Free/Cheaper)**: Perfect for testing, development, and low-volume use
- **Dedicated Compute (Premium)**: Better for production, guaranteed performance, custom models
- **When to Upgrade**: High-volume usage, need guaranteed availability, custom fine-tuned models
- **Cost Difference**: Dedicated compute costs more but provides better SLA and performance
- **Testing**: Start with shared models, upgrade when you need reliability/performance guarantees

#### **Q: How much does it cost?**
- **Clarifai**: Check current pricing at [Clarifai Pricing](https://clarifai.com/pricing)
- **This App**: Free and open source
- **Credits**: Most models use Clarifai credits per API call

### 🆘 **Getting Additional Help**

#### **Documentation & Resources**
- 📚 [Clarifai Official Documentation](https://docs.clarifai.com/)
- 🔑 [API Key Management](https://clarifai.com/settings/security)  
- 💰 [Pricing Information](https://clarifai.com/pricing)
- 🌐 [Clarifai Community](https://community.clarifai.com/)

#### **Technical Support**
- 🐛 **App Issues**: Check GitHub issues or create new issue
- 🔧 **Clarifai API**: Contact Clarifai support
- 📖 **Audio Processing**: See [AUDIO_QUALITY_GUIDE.md](AUDIO_QUALITY_GUIDE.md)

#### **Performance Optimization**
- 📊 **Model Comparison**: See [MODEL_STATUS_REPORT.md](MODEL_STATUS_REPORT.md)
- ⚡ **Speed Testing**: Run `python test_audio_quality.py`
- 🎵 **Quality Testing**: Use the audio playback features in the app

## 📁 Project Structure

```
audio-transcribe/
├── 🎯 Core Application
│   ├── app.py                          # Main Streamlit web interface
│   ├── ClarifaiUtil.py                # Clarifai API integration & audio processing
│   └── config.py                      # Configuration management & validation
│
├── ⚙️ Configuration Files  
│   ├── .env                           # Your environment variables (create from example)
│   ├── .env.example                   # Environment template with all options
│   ├── requirements.txt               # Python dependencies
│   └── .streamlit/config.toml         # Streamlit app configuration
│
├── 🚀 Startup & Testing
│   ├── start.sh                       # Quick startup script (recommended)
│   ├── test_audio_quality.py          # Audio quality testing & comparison
│   └── test_clarifai_audio.py         # Model performance testing
│
├── 📚 Documentation
│   ├── README.md                      # This comprehensive guide
│   ├── AUDIO_QUALITY_GUIDE.md        # Audio enhancement documentation  
│   ├── MODEL_STATUS_REPORT.md        # Model performance analysis
│   └── UPDATED_MODEL_STATUS_REPORT.md # Latest model test results
│
├── 📋 Project Info
│   ├── SoftwareSpec.md               # Original project specification
│   └── .gitignore                    # Git ignore rules (excludes .env, cache, etc.)
│
└── 🔧 Development Files (excluded from git)
    ├── __pycache__/                  # Python cache (auto-generated)
    ├── *.wav, *.mp3                 # Audio test files  
    └── debug_*.py                   # Debug scripts
```

### 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────┐
│                 🖥️ Web Interface                │
│              (Streamlit app.py)                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            ⚙️ Configuration Layer              │
│              (config.py + .env)               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│         🎵 Audio Processing Engine             │
│            (ClarifaiUtil.py)                   │
│  ┌─────────────────────────────────────────────┐│
│  │ MP3→WAV Conversion │ Quality Enhancement  ││
│  │ Normalization      │ Silence Trimming    ││  
│  │ Sample Rate Opt.   │ Format Standardization││
│  └─────────────────────────────────────────────┘│
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          🤖 Clarifai API Integration           │
│        (7 Speech-to-Text Models)               │
│                                                 │
│  OpenAI Whisper V3  │  AssemblyAI  │ Wav2Vec2 │
│  Deepgram Nova-2    │  Google Chirp │ Whisper V2│  
│  OpenAI Whisper Base                            │
└─────────────────────────────────────────────────┘
```

## 📦 Dependencies

### **Core Dependencies**
```python
streamlit>=1.28.0          # Modern web app framework
clarifai>=10.0.0           # Clarifai Python SDK  
clarifai-grpc>=10.0.0      # Clarifai gRPC client for API calls
python-dotenv>=1.0.0       # Environment variable management
pydub>=0.25.0              # Audio processing and format conversion
```

### **System Requirements**
- **Python**: 3.8+ (3.12 recommended for best performance)
- **Memory**: 2GB RAM minimum (4GB recommended for large files)
- **Storage**: 100MB for app + space for audio files
- **Network**: Internet connection for Clarifai API calls
- **Audio Codecs**: FFmpeg (auto-installed with pydub for most formats)

### **Optional Dependencies**
```bash
# For enhanced MP3 support (Linux/Mac)  
sudo apt install ffmpeg     # Ubuntu/Debian
brew install ffmpeg         # macOS Homebrew

# For development
pytest>=7.0.0              # Testing framework
black>=22.0.0               # Code formatting
flake8>=4.0.0               # Linting
```

## 🏷️ Version Information

- **App Version**: 1.0.0  
- **API Compatibility**: Clarifai v10+
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Last Updated**: October 21, 2025

## 📄 License & Usage

### **Open Source License**
This project is released under the **MIT License**:
- ✅ Commercial use allowed
- ✅ Modification allowed  
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ License and copyright notice required

### **Third-Party Services**
- **Clarifai API**: Subject to [Clarifai Terms of Service](https://clarifai.com/terms)
- **Audio Processing**: Uses open-source pydub library
- **Web Interface**: Built on open-source Streamlit framework

## 🤝 Contributing & Support

### **How to Contribute**
1. **Fork the Repository**: Create your own copy
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your improvements
4. **Test Thoroughly**: Ensure everything works  
5. **Submit Pull Request**: Describe your changes

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/your-username/audio-transcribe.git
cd audio-transcribe

# Create development environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Install development tools
pip install pytest black flake8

# Run tests
python test_audio_quality.py
python test_clarifai_audio.py
```

### **Reporting Issues**
- 🐛 **Bug Reports**: Include error messages, steps to reproduce
- 💡 **Feature Requests**: Describe the use case and expected behavior  
- 📚 **Documentation**: Help improve this README or other docs
- 🎵 **Audio Issues**: Include audio file format and size information

### **Community**
- **GitHub**: Issues, discussions, and pull requests
- **Documentation**: Keep README and guides updated
- **Testing**: Help test new models and features
- **Feedback**: Share your use cases and experiences

---

**🎉 Ready to transcribe audio with AI? Start with `./start.sh` and upload your first file!**