"""
ClarifaiUtil.py - Utility module for Clarifai audio transcription functionality
Contains all Clarifai-specific API calls and data handling
"""

import base64
import io
from typing import Optional, Dict, Any
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from config import config

# Audio processing imports
try:
    from pydub import AudioSegment
    AUDIO_CONVERSION_AVAILABLE = True
except ImportError:
    AUDIO_CONVERSION_AVAILABLE = False
    AudioSegment = None


class ClarifaiTranscriber:
    """Handler for Clarifai audio transcription"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Clarifai transcriber
        
        Args:
            api_key: Clarifai API key/PAT. If None, uses config.CLARIFAI_API_KEY
        """
        self.api_key = api_key or config.CLARIFAI_API_KEY
        if not self.api_key:
            raise ValueError("Clarifai API key is required")
        
        # Initialize Clarifai channel and stub
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)
        
        # Use models from config
        self.models = config.AVAILABLE_MODELS
    
    def convert_to_wav(self, audio_bytes: bytes, high_quality: bool = None) -> bytes:
        """
        Convert audio data to high-quality WAV format optimized for speech recognition
        
        Args:
            audio_bytes: Raw audio data as bytes
            high_quality: Enable high-quality conversion settings (uses config default if None)
            
        Returns:
            Audio data converted to high-quality WAV format as bytes
            
        Raises:
            ImportError: If pydub is not available
            Exception: If audio conversion fails
        """
        if not AUDIO_CONVERSION_AVAILABLE:
            # If pydub is not available, return original bytes
            print("⚠️ pydub not available - using original audio format")
            return audio_bytes
        
        # Use config default if not specified
        if high_quality is None:
            high_quality = config.HIGH_QUALITY_CONVERSION
        
        try:
            # Create audio segment from bytes
            audio_io = io.BytesIO(audio_bytes)
            
            # Try to detect format and load audio
            # pydub can auto-detect most common formats
            try:
                # Try common formats
                audio_segment = AudioSegment.from_file(audio_io)
                print(f"🎵 Original audio: {len(audio_segment)}ms, {audio_segment.frame_rate}Hz, {audio_segment.channels}ch, {audio_segment.sample_width * 8}bit")
            except Exception as e:
                # If auto-detection fails, try specific formats
                audio_io.seek(0)
                try:
                    audio_segment = AudioSegment.from_mp3(audio_io)
                    print("🎵 Loaded as MP3, converting to high-quality WAV")
                except:
                    audio_io.seek(0)
                    audio_segment = AudioSegment.from_file(audio_io, format="mp3")
                    print("🎵 Forced MP3 format, converting to high-quality WAV")
            
            # Apply quality enhancements if enabled
            if high_quality:
                # Convert to mono if stereo (most ASR models prefer mono)
                if audio_segment.channels > 1:
                    audio_segment = audio_segment.set_channels(1)
                    print("🔊 Converted to mono audio for better ASR performance")
                
                # Standardize sample rate (configurable, default 16kHz)
                target_sample_rate = config.TARGET_SAMPLE_RATE
                if audio_segment.frame_rate != target_sample_rate:
                    audio_segment = audio_segment.set_frame_rate(target_sample_rate)
                    print(f"📊 Resampled to {target_sample_rate}Hz (optimal for speech recognition)")
                
                # Ensure 16-bit sample width (standard for speech recognition)
                if audio_segment.sample_width != 2:  # 2 bytes = 16 bits
                    audio_segment = audio_segment.set_sample_width(2)
                    print("🎛️ Set to 16-bit sample width for optimal quality")
                
                # Apply normalization if enabled
                if config.NORMALIZE_AUDIO:
                    audio_segment = audio_segment.normalize()
                    print("🔧 Applied audio normalization for consistent levels")
                
                # Apply silence trimming if enabled
                if config.TRIM_SILENCE and len(audio_segment) > 1000:  # Only for audio longer than 1 second
                    # Remove silence at beginning and end
                    audio_segment = audio_segment.strip_silence(silence_thresh=-40, silence_len=300, padding=200)
                    print("🤫 Trimmed silence for cleaner audio")
            
            # Convert to high-quality WAV format
            wav_io = io.BytesIO()
            
            # Export with optimal parameters for speech recognition
            export_params = [
                "-ac", "1",  # Force mono
                "-ar", str(config.TARGET_SAMPLE_RATE),  # Configurable sample rate
                "-sample_fmt", "s16",  # 16-bit signed integer
                "-acodec", "pcm_s16le"  # PCM 16-bit little-endian
            ]
            
            audio_segment.export(wav_io, format="wav", parameters=export_params)
            
            wav_bytes = wav_io.getvalue()
            
            quality_mode = "High-quality" if high_quality else "Basic"
            print(f"✅ {quality_mode} WAV: {len(wav_bytes)} bytes (was {len(audio_bytes)} bytes)")
            print(f"📈 Final format: {config.TARGET_SAMPLE_RATE}Hz, mono, 16-bit PCM WAV")
            return wav_bytes
            
        except Exception as e:
            print(f"⚠️ High-quality conversion failed: {str(e)}")
            print("📝 Falling back to basic conversion...")
            
            # Fallback to basic conversion
            try:
                audio_io = io.BytesIO(audio_bytes)
                audio_segment = AudioSegment.from_file(audio_io)
                wav_io = io.BytesIO()
                audio_segment.export(wav_io, format="wav")
                wav_bytes = wav_io.getvalue()
                print(f"✅ Basic WAV conversion: {len(wav_bytes)} bytes")
                return wav_bytes
            except Exception as fallback_error:
                print(f"⚠️ Basic conversion also failed: {str(fallback_error)}")
                print("📝 Using original audio format")
                return audio_bytes
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Get available transcription models
        
        Returns:
            Dictionary of available models with their configuration
        """
        return self.models
    
    def get_model_info(self, model_name: str) -> Dict[str, str]:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model configuration dictionary
        """
        return self.models.get(model_name, {})
    
    def validate_audio_data(self, audio_bytes: Any) -> bytes:
        """
        Validate and convert audio data to bytes, converting to WAV format for better compatibility
        
        Args:
            audio_bytes: Audio data to validate
            
        Returns:
            Validated audio data as bytes in WAV format
            
        Raises:
            TypeError: If data type is invalid
            ValueError: If data is empty
        """
        if not isinstance(audio_bytes, bytes):
            raise TypeError(f"Expected bytes, got {type(audio_bytes).__name__}")
        
        if len(audio_bytes) == 0:
            raise ValueError("Audio data is empty")
        
        # Convert to WAV format for better model compatibility
        wav_bytes = self.convert_to_wav(audio_bytes)
        return wav_bytes
    
    def create_transcription_request(
        self, 
        audio_bytes: bytes, 
        model_info: Dict[str, str], 
        temperature: float = 0.01, 
        max_tokens: int = 1000
    ):
        """
        Create a Clarifai transcription request
        
        Args:
            audio_bytes: Raw audio data as bytes
            model_info: Model configuration
            temperature: Temperature parameter for inference
            max_tokens: Maximum tokens for output
            
        Returns:
            Configured Clarifai PostModelOutputsRequest object
        """
        user_app_id = resources_pb2.UserAppIDSet(
            user_id=model_info["user_id"],
            app_id=model_info["app_id"]
        )
        
        # Create audio object with raw bytes
        audio_obj = resources_pb2.Audio(base64=audio_bytes)
        
        # Build the request structure
        data_obj = resources_pb2.Data(audio=audio_obj)
        input_obj = resources_pb2.Input(data=data_obj)
        
        # Create and return the request
        return service_pb2.PostModelOutputsRequest(
            user_app_id=user_app_id,
            model_id=model_info["model_id"],
            inputs=[input_obj]
        )
    
    def extract_transcription_text(self, response) -> str:
        """
        Extract transcription text from Clarifai response
        
        Args:
            response: Clarifai PostModelOutputsResponse object
            
        Returns:
            Extracted transcription text
        """
        transcription = ""
        
        if response.outputs:
            output = response.outputs[0]
            
            # Try to get text from concepts first
            if output.data.concepts:
                for concept in output.data.concepts:
                    transcription += concept.name + " "
            
            # If no concepts, try text data
            if not transcription and output.data.text and output.data.text.raw:
                transcription = output.data.text.raw
            
            # If still no transcription, check if response indicates model issues
            if not transcription:
                # Check if the model returned a successful status but no content
                # This often indicates model deployment or compatibility issues
                if hasattr(output.data, 'text') and output.data.text:
                    if not output.data.text.raw:
                        return "Model returned empty response - may not be deployed or compatible with audio format"
                else:
                    return "Model did not return text data - may not support this audio format"
        
        return transcription.strip() if transcription else "No transcription available"
    
    def transcribe_audio(
        self, 
        audio_bytes: bytes, 
        model_name: str, 
        temperature: float = 0.01, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Transcribe audio using selected Clarifai model
        
        Args:
            audio_bytes: Raw audio data as bytes
            model_name: Name of the model to use
            temperature: Temperature parameter for inference (default: 0.01)
            max_tokens: Maximum tokens for output (default: 1000)
            
        Returns:
            Transcription text or None if failed
            
        Raises:
            ValueError: If model is unknown or audio data is invalid
            TypeError: If audio_bytes is not bytes
            Exception: For API errors
        """
        try:
            # Validate model
            model_info = self.models.get(model_name)
            if not model_info:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Validate audio data
            validated_audio = self.validate_audio_data(audio_bytes)
            
            # Create the request with raw audio bytes
            request = self.create_transcription_request(
                validated_audio, model_info, temperature, max_tokens
            )
            
            # Add authentication
            metadata = (('authorization', 'Key ' + self.api_key),)
            
            # Make the request
            response = self.stub.PostModelOutputs(request, metadata=metadata)
            
            # Check response status
            if response.status.code != status_code_pb2.SUCCESS:
                raise Exception(f"Clarifai API error: {response.status.description}")
            
            # Extract transcription text
            transcription_result = self.extract_transcription_text(response)
            
            # Print the transcription result
            print(f"🎙️ Transcription Result from {model_name}:")
            print(f"📝 Text: '{transcription_result}'")
            print(f"📊 Length: {len(transcription_result)} characters")
            
            return transcription_result
            
        except (TypeError, ValueError) as e:
            # Re-raise validation errors to be handled by caller
            raise e
        except Exception as e:
            # Re-raise API errors to be handled by caller
            raise Exception(f"Transcription failed: {str(e)}")
    
    def transcribe_audio_with_quality(
        self,
        audio_bytes: bytes,
        model_name: str,
        temperature: float = 0.01,
        max_tokens: int = 1000,
        high_quality_conversion: bool = None,
        target_sample_rate: int = None,
        normalize_audio: bool = None,
        trim_silence: bool = None
    ) -> Optional[str]:
        """
        Transcribe audio using selected Clarifai model with custom quality settings
        
        Args:
            audio_bytes: Raw audio data as bytes
            model_name: Name of the model to use
            temperature: Temperature parameter for inference (default: 0.01)
            max_tokens: Maximum tokens for output (default: 1000)
            high_quality_conversion: Enable high-quality conversion (uses config default if None)
            target_sample_rate: Target sample rate in Hz (uses config default if None)
            normalize_audio: Enable audio normalization (uses config default if None)
            trim_silence: Enable silence trimming (uses config default if None)
            
        Returns:
            Transcription text or None if failed
            
        Raises:
            ValueError: If model is unknown or audio data is invalid
            TypeError: If audio_bytes is not bytes
            Exception: For API errors
        """
        try:
            # Validate model
            model_info = self.models.get(model_name)
            if not model_info:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Apply custom quality settings temporarily
            original_hq = config.HIGH_QUALITY_CONVERSION
            original_sample_rate = config.TARGET_SAMPLE_RATE
            original_normalize = config.NORMALIZE_AUDIO
            original_trim = config.TRIM_SILENCE
            
            # Override config with user settings
            if high_quality_conversion is not None:
                config.HIGH_QUALITY_CONVERSION = high_quality_conversion
            if target_sample_rate is not None:
                config.TARGET_SAMPLE_RATE = target_sample_rate
            if normalize_audio is not None:
                config.NORMALIZE_AUDIO = normalize_audio
            if trim_silence is not None:
                config.TRIM_SILENCE = trim_silence
            
            try:
                # Validate audio data with custom settings
                validated_audio = self.validate_audio_data(audio_bytes)
                
                # Create the request with processed audio bytes
                request = self.create_transcription_request(
                    validated_audio, model_info, temperature, max_tokens
                )
                
                # Add authentication
                metadata = (('authorization', 'Key ' + self.api_key),)
                
                # Make the request
                response = self.stub.PostModelOutputs(request, metadata=metadata)
                
                # Check response status
                if response.status.code != status_code_pb2.SUCCESS:
                    raise Exception(f"Clarifai API error: {response.status.description}")
                
                # Extract transcription text
                transcription_result = self.extract_transcription_text(response)
                
                # Print the transcription result with quality info
                quality_info = "Enhanced" if config.HIGH_QUALITY_CONVERSION else "Basic"
                print(f"🎙️ Transcription Result from {model_name} ({quality_info} Quality):")
                print(f"📝 Text: '{transcription_result}'")
                print(f"📊 Length: {len(transcription_result)} characters")
                print(f"🎛️ Settings: {config.TARGET_SAMPLE_RATE}Hz, Normalize: {config.NORMALIZE_AUDIO}, Trim: {config.TRIM_SILENCE}")
                
                return transcription_result
                
            finally:
                # Restore original config settings
                config.HIGH_QUALITY_CONVERSION = original_hq
                config.TARGET_SAMPLE_RATE = original_sample_rate
                config.NORMALIZE_AUDIO = original_normalize
                config.TRIM_SILENCE = original_trim
            
        except (TypeError, ValueError) as e:
            # Re-raise validation errors to be handled by caller
            raise e
        except Exception as e:
            # Re-raise API errors to be handled by caller
            raise Exception(f"Transcription failed: {str(e)}")

    def transcribe_audio_with_wav(
        self,
        audio_bytes: bytes,
        model_name: str,
        temperature: float = 0.01,
        max_tokens: int = 1000,
        high_quality_conversion: bool = None,
        target_sample_rate: int = None,
        normalize_audio: bool = None,
        trim_silence: bool = None
    ) -> tuple[Optional[str], Optional[bytes]]:
        """
        Transcribe audio and return both transcription and converted WAV file
        
        Args:
            audio_bytes: Raw audio data as bytes
            model_name: Name of the model to use
            temperature: Temperature parameter for inference (default: 0.01)
            max_tokens: Maximum tokens for output (default: 1000)
            high_quality_conversion: Enable high-quality conversion (uses config default if None)
            target_sample_rate: Target sample rate in Hz (uses config default if None)
            normalize_audio: Enable audio normalization (uses config default if None)
            trim_silence: Enable silence trimming (uses config default if None)
            
        Returns:
            Tuple of (transcription_text, converted_wav_bytes) or (None, None) if failed
            
        Raises:
            ValueError: If model is unknown or audio data is invalid
            TypeError: If audio_bytes is not bytes
            Exception: For API errors
        """
        try:
            # Validate model
            model_info = self.models.get(model_name)
            if not model_info:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Apply custom quality settings temporarily
            original_hq = config.HIGH_QUALITY_CONVERSION
            original_sample_rate = config.TARGET_SAMPLE_RATE
            original_normalize = config.NORMALIZE_AUDIO
            original_trim = config.TRIM_SILENCE
            
            # Override config with user settings
            if high_quality_conversion is not None:
                config.HIGH_QUALITY_CONVERSION = high_quality_conversion
            if target_sample_rate is not None:
                config.TARGET_SAMPLE_RATE = target_sample_rate
            if normalize_audio is not None:
                config.NORMALIZE_AUDIO = normalize_audio
            if trim_silence is not None:
                config.TRIM_SILENCE = trim_silence
            
            try:
                # Convert to WAV with custom settings
                converted_wav = self.convert_to_wav(audio_bytes)
                
                # Validate audio data (which also converts if needed)
                validated_audio = self.validate_audio_data(audio_bytes)
                
                # Create the request with processed audio bytes
                request = self.create_transcription_request(
                    validated_audio, model_info, temperature, max_tokens
                )
                
                # Add authentication
                metadata = (('authorization', 'Key ' + self.api_key),)
                
                # Make the request
                response = self.stub.PostModelOutputs(request, metadata=metadata)
                
                # Check response status
                if response.status.code != status_code_pb2.SUCCESS:
                    raise Exception(f"Clarifai API error: {response.status.description}")
                
                # Extract transcription text
                transcription_result = self.extract_transcription_text(response)
                
                # Print the transcription result with quality info
                quality_info = "Enhanced" if config.HIGH_QUALITY_CONVERSION else "Basic"
                print(f"🎙️ Transcription Result from {model_name} ({quality_info} Quality):")
                print(f"📝 Text: '{transcription_result}'")
                print(f"📊 Length: {len(transcription_result)} characters")
                print(f"🎛️ Settings: {config.TARGET_SAMPLE_RATE}Hz, Normalize: {config.NORMALIZE_AUDIO}, Trim: {config.TRIM_SILENCE}")
                
                return transcription_result, converted_wav
                
            finally:
                # Restore original config settings
                config.HIGH_QUALITY_CONVERSION = original_hq
                config.TARGET_SAMPLE_RATE = original_sample_rate
                config.NORMALIZE_AUDIO = original_normalize
                config.TRIM_SILENCE = original_trim
            
        except (TypeError, ValueError) as e:
            # Re-raise validation errors to be handled by caller
            raise e
        except Exception as e:
            # Re-raise API errors to be handled by caller
            raise Exception(f"Transcription failed: {str(e)}")


def create_transcriber(api_key: Optional[str] = None) -> ClarifaiTranscriber:
    """
    Factory function to create a ClarifaiTranscriber instance
    
    Args:
        api_key: Optional API key. If None, uses config value
        
    Returns:
        Configured ClarifaiTranscriber instance
    """
    return ClarifaiTranscriber(api_key)


def get_available_models() -> Dict[str, Dict[str, str]]:
    """
    Get available transcription models without creating a transcriber instance
    
    Returns:
        Dictionary of available models
    """
    return config.AVAILABLE_MODELS


def validate_model(model_name: str) -> bool:
    """
    Validate if a model name is available
    
    Args:
        model_name: Name of the model to validate
        
    Returns:
        True if model exists, False otherwise
    """
    return model_name in config.AVAILABLE_MODELS
