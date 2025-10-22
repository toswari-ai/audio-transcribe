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
    
    def analyze_audio_quality(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze audio file quality and provide recommendations
        
        Args:
            audio_bytes: Raw audio data as bytes
            
        Returns:
            Dictionary with audio analysis and quality recommendations
        """
        if not AUDIO_CONVERSION_AVAILABLE:
            return {"error": "pydub not available for audio analysis"}
        
        try:
            audio_io = io.BytesIO(audio_bytes)
            audio_segment = AudioSegment.from_file(audio_io)
            
            # Basic audio properties
            duration_ms = len(audio_segment)
            sample_rate = audio_segment.frame_rate
            channels = audio_segment.channels
            sample_width = audio_segment.sample_width
            bitrate = (sample_rate * sample_width * 8 * channels)
            file_size_kb = len(audio_bytes) / 1024
            
            # Quality analysis
            quality_score = 0
            recommendations = []
            
            # Sample rate assessment
            if sample_rate >= 44100:
                quality_score += 30
                recommendations.append("✅ Excellent sample rate for high-quality transcription")
            elif sample_rate >= 16000:
                quality_score += 25
                recommendations.append("✅ Good sample rate for speech recognition")
            elif sample_rate >= 8000:
                quality_score += 15
                recommendations.append("⚠️ Low sample rate - may affect transcription accuracy")
            else:
                quality_score += 5
                recommendations.append("❌ Very low sample rate - transcription quality may be poor")
            
            # Channel assessment
            if channels == 1:
                quality_score += 20
                recommendations.append("✅ Mono audio - optimal for speech recognition")
            else:
                quality_score += 10
                recommendations.append("💡 Stereo audio - will convert to mono for better ASR")
            
            # Bit depth assessment
            bit_depth = sample_width * 8
            if bit_depth >= 16:
                quality_score += 20
                recommendations.append("✅ Good bit depth for clear audio")
            else:
                quality_score += 10
                recommendations.append("⚠️ Low bit depth - may introduce artifacts")
            
            # Duration assessment
            duration_seconds = duration_ms / 1000
            if duration_seconds < 1:
                quality_score += 5
                recommendations.append("⚠️ Very short audio - transcription may be limited")
            elif duration_seconds > 300:  # 5 minutes
                quality_score += 15
                recommendations.append("💡 Long audio - processing may take time")
            else:
                quality_score += 20
                recommendations.append("✅ Good audio duration for transcription")
            
            # File size efficiency
            expected_size = (sample_rate * sample_width * channels * duration_seconds) / 1024
            compression_ratio = file_size_kb / expected_size if expected_size > 0 else 1
            
            if compression_ratio < 0.1:
                recommendations.append("📦 Highly compressed - quality may be affected")
            elif compression_ratio > 0.8:
                recommendations.append("📦 Minimal compression - excellent quality retention")
            
            # Overall quality assessment
            if quality_score >= 80:
                overall_quality = "Excellent"
                color = "green"
            elif quality_score >= 60:
                overall_quality = "Good"
                color = "blue"
            elif quality_score >= 40:
                overall_quality = "Fair"
                color = "orange"
            else:
                overall_quality = "Poor"
                color = "red"
            
            return {
                "duration_seconds": duration_seconds,
                "sample_rate": sample_rate,
                "channels": channels,
                "bit_depth": bit_depth,
                "bitrate": bitrate,
                "file_size_kb": file_size_kb,
                "quality_score": quality_score,
                "overall_quality": overall_quality,
                "quality_color": color,
                "recommendations": recommendations,
                "compression_ratio": compression_ratio
            }
            
        except Exception as e:
            return {"error": f"Audio analysis failed: {str(e)}"}

    def convert_to_format(self, audio_bytes: bytes, target_format: str = "wav",
                         high_quality: bool = None, target_sample_rate: int = None,
                         normalize_audio: bool = None, trim_silence: bool = None,
                         noise_reduce: bool = False, gain_db: float = 0.0) -> bytes:
        """
        Convert audio to specified format with quality enhancements
        
        Args:
            audio_bytes: Raw audio data as bytes
            target_format: Target format ("wav", "mp3", "flac", "ogg")
            high_quality: Enable high-quality conversion settings
            target_sample_rate: Target sample rate
            normalize_audio: Enable audio normalization
            trim_silence: Enable silence trimming
            noise_reduce: Enable basic noise reduction
            gain_db: Audio gain adjustment in dB
            
        Returns:
            Audio data converted to target format as bytes
        """
        if not AUDIO_CONVERSION_AVAILABLE:
            print(f"⚠️ pydub not available - cannot convert to {target_format.upper()}")
            return audio_bytes
        
        # Use config defaults if not specified
        if high_quality is None:
            high_quality = config.HIGH_QUALITY_CONVERSION
        if target_sample_rate is None:
            target_sample_rate = config.TARGET_SAMPLE_RATE
        if normalize_audio is None:
            normalize_audio = config.NORMALIZE_AUDIO
        if trim_silence is None:
            trim_silence = config.TRIM_SILENCE
        
        try:
            # Create audio segment from bytes
            audio_io = io.BytesIO(audio_bytes)
            
            try:
                audio_segment = AudioSegment.from_file(audio_io)
                print(f"🎵 Original audio: {len(audio_segment)}ms, {audio_segment.frame_rate}Hz, {audio_segment.channels}ch, {audio_segment.sample_width * 8}bit")
            except Exception as e:
                # Fallback format detection
                audio_io.seek(0)
                audio_segment = AudioSegment.from_file(audio_io, format="mp3")
                print("🎵 Loaded with fallback format detection")
            
            # Apply the same processing as convert_to_wav
            if gain_db != 0.0:
                audio_segment = audio_segment + gain_db
                print(f"🔊 Applied {gain_db:+.1f}dB gain adjustment")
            
            if high_quality:
                if audio_segment.channels > 1:
                    audio_segment = audio_segment.set_channels(1)
                    print("🔊 Converted to mono audio")
                
                if audio_segment.frame_rate != target_sample_rate:
                    audio_segment = audio_segment.set_frame_rate(target_sample_rate)
                    print(f"📊 Resampled to {target_sample_rate}Hz")
                
                if audio_segment.sample_width != 2:
                    audio_segment = audio_segment.set_sample_width(2)
                    print("🎛️ Set to 16-bit sample width")
                
                if normalize_audio:
                    audio_segment = audio_segment.normalize()
                    print("🔧 Applied audio normalization")
                
                if noise_reduce:
                    try:
                        audio_segment = audio_segment.high_pass_filter(80)
                        print("🎛️ Applied basic noise reduction")
                    except:
                        pass
                
                if trim_silence and len(audio_segment) > 1000:
                    original_length = len(audio_segment)
                    audio_segment = audio_segment.strip_silence(silence_thresh=-40, silence_len=300, padding=200)
                    trimmed_amount = original_length - len(audio_segment)
                    if trimmed_amount > 0:
                        print(f"🤫 Trimmed {trimmed_amount}ms of silence")
            
            # Export to specified format
            output_io = io.BytesIO()
            
            if target_format.lower() == "wav":
                export_params = [
                    "-ac", "1",
                    "-ar", str(target_sample_rate),
                    "-sample_fmt", "s16",
                    "-acodec", "pcm_s16le"
                ]
                audio_segment.export(output_io, format="wav", parameters=export_params)
            elif target_format.lower() == "mp3":
                # High-quality MP3 settings
                audio_segment.export(output_io, format="mp3", bitrate="192k", parameters=["-ac", "1"])
            elif target_format.lower() == "flac":
                # Lossless compression
                audio_segment.export(output_io, format="flac", parameters=["-ac", "1", "-compression_level", "8"])
            elif target_format.lower() == "ogg":
                # High-quality OGG
                audio_segment.export(output_io, format="ogg", parameters=["-ac", "1", "-q:a", "6"])
            else:
                # Default to WAV
                audio_segment.export(output_io, format="wav")
            
            converted_bytes = output_io.getvalue()
            
            print(f"✅ Converted to {target_format.upper()}: {len(converted_bytes)} bytes (was {len(audio_bytes)} bytes)")
            return converted_bytes
            
        except Exception as e:
            print(f"⚠️ Conversion to {target_format.upper()} failed: {str(e)}")
            print("📝 Using original audio format")
            return audio_bytes

    def convert_to_wav(self, audio_bytes: bytes, high_quality: bool = None, 
                      target_sample_rate: int = None, normalize_audio: bool = None,
                      trim_silence: bool = None, noise_reduce: bool = False,
                      gain_db: float = 0.0) -> bytes:
        """
        Convert audio data to high-quality WAV format optimized for speech recognition
        
        Args:
            audio_bytes: Raw audio data as bytes
            high_quality: Enable high-quality conversion settings (uses config default if None)
            target_sample_rate: Target sample rate (uses config default if None)
            normalize_audio: Enable audio normalization (uses config default if None) 
            trim_silence: Enable silence trimming (uses config default if None)
            noise_reduce: Enable basic noise reduction (default: False)
            gain_db: Audio gain adjustment in dB (default: 0.0)
            
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
        
        # Use config defaults if not specified
        if high_quality is None:
            high_quality = config.HIGH_QUALITY_CONVERSION
        if target_sample_rate is None:
            target_sample_rate = config.TARGET_SAMPLE_RATE
        if normalize_audio is None:
            normalize_audio = config.NORMALIZE_AUDIO
        if trim_silence is None:
            trim_silence = config.TRIM_SILENCE
        
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
            
            # Apply gain adjustment if specified
            if gain_db != 0.0:
                audio_segment = audio_segment + gain_db
                print(f"🔊 Applied {gain_db:+.1f}dB gain adjustment")
            
            # Apply quality enhancements if enabled
            if high_quality:
                # Convert to mono if stereo (most ASR models prefer mono)
                if audio_segment.channels > 1:
                    audio_segment = audio_segment.set_channels(1)
                    print("🔊 Converted to mono audio for better ASR performance")
                
                # Standardize sample rate
                if audio_segment.frame_rate != target_sample_rate:
                    audio_segment = audio_segment.set_frame_rate(target_sample_rate)
                    print(f"📊 Resampled to {target_sample_rate}Hz (optimal for speech recognition)")
                
                # Ensure 16-bit sample width (standard for speech recognition)
                if audio_segment.sample_width != 2:  # 2 bytes = 16 bits
                    audio_segment = audio_segment.set_sample_width(2)
                    print("🎛️ Set to 16-bit sample width for optimal quality")
                
                # Apply normalization if enabled
                if normalize_audio:
                    audio_segment = audio_segment.normalize()
                    print("🔧 Applied audio normalization for consistent levels")
                
                # Apply basic noise reduction if enabled
                if noise_reduce:
                    # Simple high-pass filter to reduce low-frequency noise
                    # This is a basic approach - more advanced noise reduction would require additional libraries
                    try:
                        audio_segment = audio_segment.high_pass_filter(80)  # Remove frequencies below 80Hz
                        print("🎛️ Applied basic noise reduction (high-pass filter)")
                    except:
                        print("⚠️ Basic noise reduction not available in this pydub version")
                
                # Apply silence trimming if enabled
                if trim_silence and len(audio_segment) > 1000:  # Only for audio longer than 1 second
                    # Remove silence at beginning and end
                    original_length = len(audio_segment)
                    audio_segment = audio_segment.strip_silence(silence_thresh=-40, silence_len=300, padding=200)
                    trimmed_amount = original_length - len(audio_segment)
                    if trimmed_amount > 0:
                        print(f"🤫 Trimmed {trimmed_amount}ms of silence for cleaner audio")
            
            # Convert to high-quality WAV format
            wav_io = io.BytesIO()
            
            # Export with optimal parameters for speech recognition
            export_params = [
                "-ac", "1",  # Force mono
                "-ar", str(target_sample_rate),  # Use specified sample rate
                "-sample_fmt", "s16",  # 16-bit signed integer
                "-acodec", "pcm_s16le"  # PCM 16-bit little-endian
            ]
            
            audio_segment.export(wav_io, format="wav", parameters=export_params)
            
            wav_bytes = wav_io.getvalue()
            
            quality_mode = "High-quality" if high_quality else "Basic"
            enhancement_info = []
            if gain_db != 0.0:
                enhancement_info.append(f"Gain: {gain_db:+.1f}dB")
            if normalize_audio:
                enhancement_info.append("Normalized")
            if trim_silence:
                enhancement_info.append("Silence trimmed")
            if noise_reduce:
                enhancement_info.append("Noise reduced")
            
            enhancement_text = f" ({', '.join(enhancement_info)})" if enhancement_info else ""
            print(f"✅ {quality_mode} WAV: {len(wav_bytes)} bytes (was {len(audio_bytes)} bytes){enhancement_text}")
            print(f"📈 Final format: {target_sample_rate}Hz, mono, 16-bit PCM WAV")
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
        
        # Build request parameters
        request_params = {
            "user_app_id": user_app_id,
            "model_id": model_info["model_id"],
            "inputs": [input_obj]
        }
        
        # Add deployment_id if available for dedicated deployed models
        if "deployment_id" in model_info and model_info["deployment_id"]:
            deployment_id = model_info["deployment_id"]
            # TODO: deployment_id needs to be passed when creating the Model connection, not in PostModelOutputsRequest
            # request_params["deployment_id"] = deployment_id  # Not supported in current gRPC version
            print(f"🚀 Using dedicated compute deployment: {deployment_id}")
            print(f"💻 Model: {model_info['model_id']} (dedicated deployment)")
            print(f"⚠️  Note: deployment_id requires newer Clarifai SDK with Model() class")
        else:
            print(f"🌐 Using shared model: {model_info['model_id']} (standard)")
        
        # Create and return the request
        return service_pb2.PostModelOutputsRequest(**request_params)
    
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
            model_info = config.get_model_info(model_name)
            if not model_info:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Debug: Show deployment configuration
            deployment_id = model_info.get("deployment_id")
            if deployment_id:
                print(f"🎯 Using dedicated compute: {model_name}")
                print(f"📋 Deployment ID: {deployment_id}")
            else:
                print(f"🌐 Using shared compute: {model_name}")
            
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
            model_info = config.get_model_info(model_name)
            if not model_info:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Debug: Show deployment configuration
            deployment_id = model_info.get("deployment_id")
            if deployment_id:
                print(f"🎯 Initializing dedicated compute for: {model_name}")
                print(f"📋 Deployment ID: {deployment_id}")
            else:
                print(f"🌐 Using shared compute for: {model_name}")
            
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

    def transcribe_with_format_control(
        self,
        audio_bytes: bytes,
        model_name: str,
        temperature: float = 0.01,
        max_tokens: int = 1000,
        api_format: str = "wav",
        high_quality_conversion: bool = None,
        target_sample_rate: int = None,
        normalize_audio: bool = None,
        trim_silence: bool = None,
        noise_reduce: bool = False,
        gain_db: float = 0.0
    ) -> tuple[Optional[str], Optional[bytes], Optional[Dict[str, Any]]]:
        """
        Advanced transcription with format control and audio analysis
        
        Args:
            audio_bytes: Raw audio data as bytes
            model_name: Name of the model to use
            temperature: Temperature parameter for inference
            max_tokens: Maximum tokens for output
            api_format: Format to send to API ("wav", "mp3", "flac", "original")
            high_quality_conversion: Enable high-quality conversion
            target_sample_rate: Target sample rate
            normalize_audio: Enable audio normalization
            trim_silence: Enable silence trimming
            noise_reduce: Enable basic noise reduction
            gain_db: Audio gain adjustment in dB
            
        Returns:
            Tuple of (transcription_text, processed_audio_bytes, audio_analysis)
        """
        try:
            # First, analyze the original audio
            print("🔍 Analyzing original audio quality...")
            audio_analysis = self.analyze_audio_quality(audio_bytes)
            
            # Validate model
            model_info = config.get_model_info(model_name)
            if not model_info:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Debug: Show deployment configuration
            deployment_id = model_info.get("deployment_id")
            if deployment_id:
                print(f"🎯 Using dedicated compute: {model_name}")
                print(f"📋 Deployment ID: {deployment_id}")
            else:
                print(f"🌐 Using shared compute: {model_name}")
            
            # Process audio based on format selection
            if api_format.lower() == "original":
                print("📄 Using original audio format for API call")
                processed_audio = audio_bytes
            else:
                print(f"🔄 Converting audio to {api_format.upper()} for API call")
                processed_audio = self.convert_to_format(
                    audio_bytes, 
                    api_format,
                    high_quality_conversion,
                    target_sample_rate,
                    normalize_audio,
                    trim_silence,
                    noise_reduce,
                    gain_db
                )
            
            # Create the request
            request = self.create_transcription_request(
                processed_audio, model_info, temperature, max_tokens
            )
            
            # Add authentication
            metadata = (('authorization', 'Key ' + self.api_key),)
            
            # Make the request
            print(f"📡 Sending {api_format.upper()} audio to Clarifai API...")
            response = self.stub.PostModelOutputs(request, metadata=metadata)
            
            # Check response status
            if response.status.code != status_code_pb2.SUCCESS:
                raise Exception(f"Clarifai API error: {response.status.description}")
            
            # Extract transcription text
            transcription_result = self.extract_transcription_text(response)
            
            # Print results with format info
            format_info = f" ({api_format.upper()} format)" if api_format != "original" else " (original format)"
            print(f"🎙️ Transcription Result from {model_name}{format_info}:")
            print(f"📝 Text: '{transcription_result}'")
            print(f"📊 Length: {len(transcription_result)} characters")
            
            return transcription_result, processed_audio, audio_analysis
            
        except (TypeError, ValueError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Advanced transcription failed: {str(e)}")


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
