"""
Configuration management for the Audio Transcription App
Handles environment variables and app settings
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """Configuration class to manage environment variables and app settings"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Clarifai Configuration
        self.CLARIFAI_PAT = os.getenv("CLARIFAI_PAT")
        self.CLARIFAI_API_KEY = self.CLARIFAI_PAT  # Backwards compatibility
        self.CLARIFAI_USER_ID = os.getenv("CLARIFAI_USER_ID") 
        self.CLARIFAI_APP_ID = os.getenv("CLARIFAI_APP_ID")
        self.CLARIFAI_DEPLOYMENT_ID = os.getenv("CLARIFAI_DEPLOYMENT_ID")  # For dedicated deployed models
        
        # App Configuration
        self.APP_TITLE = os.getenv("APP_TITLE", "Audio Transcription with Clarifai")
        self.APP_ICON = os.getenv("APP_ICON", "🎙️")
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
        
        # Streamlit Server Configuration
        self.STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
        self.STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
        
        # Default Model Settings
        self.DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "OpenAI Whisper Large V3")
        self.DEFAULT_VIDEO_MODEL = os.getenv("DEFAULT_VIDEO_MODEL", "MM-Poly-8B")  # Updated to valid native model
        self.DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
        self.DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
        
        # Video Processing Settings
        self.MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))  # Larger for videos
        self.VIDEO_FRAME_EXTRACTION_INTERVAL = int(os.getenv("VIDEO_FRAME_EXTRACTION_INTERVAL", "5"))  # Extract frame every N seconds
        self.VIDEO_QUALITY_OPTIMIZATION = os.getenv("VIDEO_QUALITY_OPTIMIZATION", "true").lower() == "true"
        
        # Debug Settings
        self.DEBUG_VIDEO_PROCESSING = os.getenv("DEBUG_VIDEO_PROCESSING", "false").lower() == "true"
        
        # Audio Quality Settings
        self.HIGH_QUALITY_CONVERSION = os.getenv("HIGH_QUALITY_CONVERSION", "true").lower() == "true"
        self.TARGET_SAMPLE_RATE = int(os.getenv("TARGET_SAMPLE_RATE", "16000"))  # Optimal for speech recognition
        self.NORMALIZE_AUDIO = os.getenv("NORMALIZE_AUDIO", "true").lower() == "true"
        self.TRIM_SILENCE = os.getenv("TRIM_SILENCE", "true").lower() == "true"
        
        # Model configurations
        self.AVAILABLE_MODELS = {
            "AssemblyAI Audio Transcription": {
                "model_id": "audio-transcription",
                "user_id": "assemblyai",
                "app_id": "speech-recognition",
                "description": "Human-level accuracy speech recognition (19⭐) - ✅ Now working with WAV conversion",
                "status": "working"
            },
            "OpenAI Whisper": {
                "model_id": "whisper",
                "user_id": "openai",
                "app_id": "transcription",
                "description": "Versatile pre-trained ASR model (14⭐)",
                "status": "working"
            },
            "OpenAI Whisper Large V3": {
                "model_id": "whisper-large-v3",
                "user_id": "openai",
                "app_id": "transcription",
                "description": "Latest Whisper v3: 10-20% error reduction, 5M hours training data, 128 Mel bins, multilingual with Cantonese support - ✅ Most Accurate",
                "status": "working",
                "pricing": "$0.0012/request",
                "features": ["dedicated compute","streaming","multilingual", "speech_translation", "cantonese_support", "improved_accuracy"],
                "deployment_id": "deploy-whisper-large-v3-cr4h"  # For dedicated deployed models - remove for shared model
            },
            "OpenAI Whisper Large V2": {
                "model_id": "whisper-large-v2",
                "user_id": "openai", 
                "app_id": "transcription",
                "description": "High accuracy multilingual transcription, predecessor to v3 - ✅ Working with WAV conversion",
                "status": "working"
            },
            "Deepgram Nova-2": {
                "model_id": "audio-transcription",
                "user_id": "deepgram",
                "app_id": "transcribe",
                "description": "30% lower error rates, superior speed (3⭐) - ✅ Now working with WAV conversion",
                "status": "working"
            },
            "Facebook Wav2Vec2 English": {
                "model_id": "asr-wav2vec2-base-960h-english",
                "user_id": "facebook",
                "app_id": "asr",
                "description": "English speech to text conversion (9⭐) - ✅ Fastest Processing",
                "status": "working"
            },
            "Google Chirp ASR": {
                "model_id": "chirp-asr",
                "user_id": "gcp",
                "app_id": "speech-recognition",
                "description": "Google Cloud state-of-the-art speech recognition (4⭐) - ✅ Now working with WAV conversion",
                "status": "working"
            }
        }
        
        # Video Model configurations for multimodal video transcription (Updated with valid models)
        self.AVAILABLE_VIDEO_MODELS = {
            "Qwen2.5-VL-7B-Instruct": {
                "model_id": "Qwen2_5-VL-7B-Instruct",
                "user_id": "qwen",
                "app_id": "qwen-VL",
                "description": "🌟 Advanced vision-language model with long video analysis and temporal understanding",
                "status": "working",
                "features": ["long_video_analysis", "visual_agent", "structured_extraction", "object_localization", "temporal_understanding"],
                "pricing": "$0.44472 / 1M Input Tokens, $1.32414 / 1M Output Tokens"
            },
            "MM-Poly-8B": {
                "model_id": "mm-poly-8b",
                "user_id": "clarifai",
                "app_id": "main",
                "description": "🔧 Clarifai's native multimodal AI assistant - optimized for video, image, and audio analysis",
                "status": "working",
                "features": ["multimodal_analysis", "natural_language_processing", "learning_ability", "customization", "native_clarifai"],
                "pricing": "$0.65803 / 1M Input Tokens, $1.11028 / 1M Output Tokens"
            },
            "MiniCPM-o-2.6": {
                "model_id": "MiniCPM-o-2_6-language",
                "user_id": "openbmb",
                "app_id": "miniCPM",
                "description": "Comprehensive multimedia analysis",
                "status": "working",
                "features": ["multimedia", "end_to_end", "audio_video_text"]
            }
        }
        
        # Supported file formats
        self.SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'flac', 'm4a', 'ogg']
        self.SUPPORTED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'm4v']
        
        # Parameter constraints
        self.MIN_TEMPERATURE = 0.0
        self.MAX_TEMPERATURE = 1.0
        self.MIN_MAX_TOKENS = 100
        self.MAX_MAX_TOKENS = 2000
        
    def validate_config(self) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = {}
        
        if not self.CLARIFAI_PAT:
            errors["CLARIFAI_PAT"] = "Clarifai Personal Access Token (PAT) is required"
            
        if self.MAX_FILE_SIZE_MB <= 0:
            errors["MAX_FILE_SIZE_MB"] = "Max file size must be positive"
            
        if not (self.MIN_TEMPERATURE <= self.DEFAULT_TEMPERATURE <= self.MAX_TEMPERATURE):
            errors["DEFAULT_TEMPERATURE"] = f"Temperature must be between {self.MIN_TEMPERATURE} and {self.MAX_TEMPERATURE}"
            
        if not (self.MIN_MAX_TOKENS <= self.DEFAULT_MAX_TOKENS <= self.MAX_MAX_TOKENS):
            errors["DEFAULT_MAX_TOKENS"] = f"Max tokens must be between {self.MIN_MAX_TOKENS} and {self.MAX_MAX_TOKENS}"
            
        if self.DEFAULT_MODEL not in self.AVAILABLE_MODELS:
            errors["DEFAULT_MODEL"] = (
                f"Default model '{self.DEFAULT_MODEL}' not found. "
                f"Available models: {list(self.AVAILABLE_MODELS.keys())}"
            )
            
        return errors
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model configuration by name with deployment_id override support"""
        model_info = self.AVAILABLE_MODELS.get(model_name, {}).copy()
        
        # Override deployment_id with environment variable if set
        if self.CLARIFAI_DEPLOYMENT_ID:
            model_info["deployment_id"] = self.CLARIFAI_DEPLOYMENT_ID
            
        return model_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "app_title": self.APP_TITLE,
            "app_icon": self.APP_ICON,
            "max_file_size_mb": self.MAX_FILE_SIZE_MB,
            "default_model": self.DEFAULT_MODEL,
            "default_temperature": self.DEFAULT_TEMPERATURE,
            "default_max_tokens": self.DEFAULT_MAX_TOKENS,
            "available_models": list(self.AVAILABLE_MODELS.keys()),
            "supported_formats": self.SUPPORTED_AUDIO_FORMATS,
            "clarifai_user_id": self.CLARIFAI_USER_ID,
            "clarifai_app_id": self.CLARIFAI_APP_ID,
            "pat_configured": bool(self.CLARIFAI_PAT)
        }

# Global configuration instance
config = Config()