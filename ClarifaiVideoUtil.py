"""
ClarifaiVideoUtil.py - Utility module for Clarifai video transcription functionality
Contains all Clarifai-specific API calls and video processing for multimodal models
"""

import base64
import io
import os
import time
from typing import Optional, Dict, Any, List, Tuple, Union
from config import config

# New Clarifai SDK imports
try:
    from clarifai.client import Model
    from clarifai.runners.utils.data_types import Video, Image
    NEW_CLARIFAI_SDK_AVAILABLE = True
except ImportError:
    NEW_CLARIFAI_SDK_AVAILABLE = False
    Model = None
    Video = None
    Image = None

# Fallback to old gRPC imports if new SDK not available
try:
    from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
    from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
    from clarifai_grpc.grpc.api.status import status_code_pb2
    GRPC_SDK_AVAILABLE = True
except ImportError:
    GRPC_SDK_AVAILABLE = False

# Video processing imports
try:
    import cv2
    import numpy as np
    VIDEO_PROCESSING_AVAILABLE = True
    # Type alias for numpy array when available
    NDArray = np.ndarray
except ImportError:
    VIDEO_PROCESSING_AVAILABLE = False
    cv2 = None
    np = None
    # Fallback type when numpy not available
    NDArray = Any

# Audio extraction from video - Using FFmpeg for better reliability
try:
    from ffmpeg_audio_extractor import FFmpegAudioExtractor
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    FFmpegAudioExtractor = None

# Keep MoviePy as fallback (but prioritize FFmpeg)
try:
    from moviepy import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None


def debug_print(message: str, force: bool = False):
    """Print debug message if debug mode is enabled"""
    if force or config.DEBUG_VIDEO_PROCESSING:
        print(message)


class ClarifaiVideoTranscriber:
    """Handler for Clarifai video transcription using multimodal models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Clarifai video transcriber
        
        Args:
            api_key: Clarifai API key/PAT. If None, uses config.CLARIFAI_API_KEY
        """
        debug_print(f"🔧 [DEBUG] Initializing ClarifaiVideoTranscriber...")
        
        self.api_key = api_key or config.CLARIFAI_API_KEY
        if not self.api_key:
            raise ValueError("Clarifai API key is required")
        
        debug_print(f"🔧 [DEBUG] API key configured: {self.api_key[:8]}...{self.api_key[-4:] if len(self.api_key) > 12 else 'short'}")
        
        # Set API key in environment for new SDK
        os.environ["CLARIFAI_PAT"] = self.api_key
        
        # Check which SDK is available
        self.use_new_sdk = NEW_CLARIFAI_SDK_AVAILABLE
        debug_print(f"🔧 [DEBUG] SDK availability - Modern: {NEW_CLARIFAI_SDK_AVAILABLE}, gRPC: {GRPC_SDK_AVAILABLE if 'GRPC_SDK_AVAILABLE' in globals() else 'Unknown'}")
        
        if not self.use_new_sdk and not GRPC_SDK_AVAILABLE:
            raise ImportError("Neither new Clarifai SDK nor gRPC SDK is available. Please install: pip install clarifai")
        
        # Initialize gRPC fallback if new SDK not available
        if not self.use_new_sdk:
            debug_print(f"🔧 [DEBUG] Initializing gRPC fallback...")
            self.channel = ClarifaiChannel.get_grpc_channel()
            self.stub = service_pb2_grpc.V2Stub(self.channel)
            self.metadata = (("authorization", f"Key {self.api_key}"),)
            debug_print(f"🔧 [DEBUG] gRPC client initialized")
        
        # Video processing settings
        self.max_video_size_mb = config.MAX_VIDEO_SIZE_MB
        self.frame_interval = config.VIDEO_FRAME_EXTRACTION_INTERVAL
        debug_print(f"🔧 [DEBUG] Video settings - Max size: {self.max_video_size_mb}MB, Frame interval: {self.frame_interval}s")
        
        # Initialize audio extractor (prefer FFmpeg over MoviePy)
        self.audio_extractor = None
        if FFMPEG_AVAILABLE:
            self.audio_extractor = FFmpegAudioExtractor(debug=config.DEBUG_VIDEO_PROCESSING)
            debug_print(f"🎵 [DEBUG] Audio extractor: FFmpeg (preferred)")
        elif MOVIEPY_AVAILABLE:
            debug_print(f"🎵 [DEBUG] Audio extractor: MoviePy (fallback)")
        else:
            debug_print(f"⚠️ [DEBUG] No audio extraction available (install ffmpeg-python or moviepy)")
            
        debug_print(f"🔧 [DEBUG] ClarifaiVideoTranscriber initialization complete")
        
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get available video models from config"""
        return config.AVAILABLE_VIDEO_MODELS
    
    def transcribe_video_modern_sdk(self, 
                                  video_path: str, 
                                  model_name: str,
                                  prompt: str = "Describe in detail what is in the video.",
                                  max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Transcribe video using the modern Clarifai SDK
        
        Args:
            video_path: Path to video file
            model_name: Name of the model to use
            prompt: Prompt for analysis
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with transcription results
        """
        debug_print(f"🔧 [DEBUG] Starting modern SDK video transcription")
        debug_print(f"🔧 [DEBUG] Video path: {video_path}")
        debug_print(f"🔧 [DEBUG] Model: {model_name}")
        debug_print(f"🔧 [DEBUG] Prompt length: {len(prompt)} characters")
        debug_print(f"🔧 [DEBUG] Max tokens: {max_tokens}")
        
        if not self.use_new_sdk:
            raise ImportError("New Clarifai SDK not available. Install with: pip install clarifai")
        
        start_time = time.time()
        
        try:
            # Get model info
            debug_print(f"🔧 [DEBUG] Looking up model configuration...")
            available_models = self.get_available_models()
            if model_name not in available_models:
                debug_print(f"🔧 [DEBUG] Available models: {list(available_models.keys())}")
                raise ValueError(f"Model '{model_name}' not available")
            
            model_info = available_models[model_name]
            debug_print(f"🔧 [DEBUG] Model info: {model_info}")
            
            # Construct model URL
            model_url = f"https://clarifai.com/{model_info['user_id']}/{model_info['app_id']}/models/{model_info['model_id']}"
            debug_print(f"🔧 [DEBUG] Model URL: {model_url}")
            
            # Initialize model
            debug_print(f"🔧 [DEBUG] Initializing Clarifai model...")
            model = Model(url=model_url)
            debug_print(f"🔧 [DEBUG] Model initialized successfully")
            
            # Create video object from file bytes
            debug_print(f"🔧 [DEBUG] Reading video file...")
            debug_print(f"📹 [DEBUG] METHOD: Sending WHOLE VIDEO (complete file) to API")
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
            video_size_mb = len(video_bytes) / (1024 * 1024)
            debug_print(f"🔧 [DEBUG] Video file read: {video_size_mb:.2f} MB")
            debug_print(f"📹 [DEBUG] PAYLOAD: Complete video file ({len(video_bytes):,} bytes)")
            
            debug_print(f"🔧 [DEBUG] Creating Video object...")
            video_obj = Video(bytes=video_bytes)
            debug_print(f"🔧 [DEBUG] Video object created successfully")
            debug_print(f"📹 [DEBUG] ADVANTAGE: Full temporal context, motion analysis, complete audio-visual correlation")
            
            # Make prediction
            debug_print(f"🔧 [DEBUG] Making API prediction request...")
            result = model.predict(
                prompt=prompt,
                video=video_obj,
                max_tokens=max_tokens,
            )
            debug_print(f"🔧 [DEBUG] API prediction completed")
            debug_print(f"🔧 [DEBUG] Result type: {type(result)}")
            debug_print(f"🔧 [DEBUG] Result attributes: {dir(result) if result else 'None'}")
            
            # Extract text from result
            transcription_text = ""
            debug_print(f"🔧 [DEBUG] Extracting text from result...")
            
            if hasattr(result, 'text') and result.text:
                transcription_text = result.text
                debug_print(f"🔧 [DEBUG] Extracted text from result.text")
            elif hasattr(result, 'outputs') and result.outputs:
                # Handle different result formats
                output = result.outputs[0] if result.outputs else None
                debug_print(f"🔧 [DEBUG] Found outputs, processing first output...")
                if output and hasattr(output, 'data') and hasattr(output.data, 'text'):
                    transcription_text = output.data.text.raw
                    debug_print(f"🔧 [DEBUG] Extracted text from output.data.text.raw")
            else:
                # Try to extract as string
                transcription_text = str(result) if result else ""
                debug_print(f"🔧 [DEBUG] Extracted text as string representation")
            
            debug_print(f"🔧 [DEBUG] Transcription text length: {len(transcription_text)} characters")
            processing_time = time.time() - start_time
            debug_print(f"🔧 [DEBUG] Processing completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "transcription": transcription_text,
                "model_used": model_name,
                "model_url": model_url,
                "processing_time": processing_time,
                "video_info": {
                    "path": video_path,
                    "size_mb": os.path.getsize(video_path) / (1024 * 1024)
                },
                "sdk_used": "modern"
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            debug_print(f"🔧 [DEBUG] Modern SDK transcription failed after {processing_time:.2f}s")
            debug_print(f"🔧 [DEBUG] Error type: {type(e).__name__}")
            debug_print(f"🔧 [DEBUG] Error message: {str(e)}")
            import traceback
            debug_print(f"🔧 [DEBUG] Full traceback:")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "sdk_used": "modern"
            }
    
    def extract_frames_from_video(self, video_path: str, max_frames: int = 10) -> List[Any]:
        """
        Extract key frames from video for analysis
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of frame arrays
        """
        if not VIDEO_PROCESSING_AVAILABLE:
            raise ImportError("OpenCV is required for video processing. Install with: pip install opencv-python")
        
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        try:
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            debug_print(f"🖼️ [DEBUG] FRAME EXTRACTION: Video has {total_frames} total frames")
            debug_print(f"🖼️ [DEBUG] FRAME EXTRACTION: Duration {duration:.1f}s at {fps:.1f} FPS")
            
            # Calculate frame extraction interval
            if duration > 0:
                interval = max(1, int(total_frames / max_frames))
            else:
                interval = 1
            
            debug_print(f"🖼️ [DEBUG] FRAME EXTRACTION: Taking every {interval} frame(s) to get max {max_frames} frames")
            
            frame_count = 0
            while len(frames) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % interval == 0:
                    # Resize frame if too large
                    height, width = frame.shape[:2]
                    if width > 1280 or height > 720:
                        scale = min(1280/width, 720/height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    frames.append(frame)
                
                frame_count += 1
                
        finally:
            cap.release()
        
        debug_print(f"🖼️ [DEBUG] FRAME EXTRACTION: Successfully extracted {len(frames)} key frames")
        debug_print(f"🖼️ [DEBUG] FRAME EXTRACTION: Each frame converted to base64 for API transmission")
        return frames
    
    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """
        Extract audio track from video file using FFmpeg (preferred) or MoviePy (fallback)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file or None if extraction fails
        """
        debug_print(f"🎵 [DEBUG] Starting audio extraction from video: {os.path.basename(video_path)}")
        
        # Try FFmpeg first (more reliable and performant)
        if self.audio_extractor and FFMPEG_AVAILABLE:
            debug_print(f"🎵 [DEBUG] Using FFmpeg audio extractor (preferred method)")
            
            success, audio_path, error_message = self.audio_extractor.extract_audio(video_path)
            
            if success and audio_path:
                debug_print(f"🎵 [DEBUG] FFmpeg extraction successful: {os.path.basename(audio_path)}")
                return audio_path
            else:
                debug_print(f"🎵 [DEBUG] FFmpeg extraction failed: {error_message}")
                debug_print(f"🎵 [DEBUG] Falling back to MoviePy...")
        
        # Fallback to MoviePy if FFmpeg fails or not available
        if not MOVIEPY_AVAILABLE:
            debug_print("🎵 [DEBUG] MoviePy not available. Audio extraction disabled.")
            return None
            
        debug_print(f"🎵 [DEBUG] Using MoviePy audio extractor (fallback method)")
        
        # Log MoviePy version for debugging
        try:
            import moviepy
            debug_print(f"🎵 [DEBUG] MoviePy version: {moviepy.__version__}")
        except:
            debug_print("🎵 [DEBUG] MoviePy version detection failed")
        
        try:
            # Create temporary audio file
            audio_path = video_path.rsplit('.', 1)[0] + '_extracted_audio.wav'
            debug_print(f"🎵 [DEBUG] Target audio path: {os.path.basename(audio_path)}")
            
            # Extract audio using moviepy
            debug_print(f"🎵 [DEBUG] Loading video file with MoviePy...")
            video_clip = VideoFileClip(video_path)
            debug_print(f"🎵 [DEBUG] Video loaded - Duration: {video_clip.duration:.2f}s")
            
            # Check if video has audio
            debug_print(f"🎵 [DEBUG] Checking for audio track...")
            if video_clip.audio is None:
                debug_print("🎵 [DEBUG] Video has no audio track")
                video_clip.close()
                return None
            
            debug_print(f"🎵 [DEBUG] Audio track found - Duration: {video_clip.audio.duration:.2f}s")
            audio_clip = video_clip.audio
            
            # Write audio file with proper error handling and MoviePy version compatibility
            try:
                debug_print(f"🎵 [DEBUG] Writing audio file...")
                debug_print(f"🎵 [DEBUG] MoviePy compatibility: Using logger=None for version 2.1.2+")
                
                # Use compatible parameters for MoviePy 2.1.2+
                audio_clip.write_audiofile(
                    audio_path, 
                    logger=None  # Compatible with MoviePy 2.1.2+
                )
                debug_print(f"🎵 [DEBUG] Audio file written successfully")
                audio_clip.close()
            except TypeError as type_error:
                # Handle parameter compatibility issues
                debug_print(f"🎵 [DEBUG] Parameter error with logger=None: {str(type_error)}")
                debug_print(f"🎵 [DEBUG] Trying minimal parameters for MoviePy compatibility...")
                try:
                    audio_clip.write_audiofile(audio_path)  # Minimal parameters
                    debug_print(f"🎵 [DEBUG] Audio file written with minimal parameters")
                    audio_clip.close()
                except Exception as fallback_error:
                    debug_print(f"🎵 [DEBUG] Fallback also failed: {str(fallback_error)}")
                    debug_print(f"🎵 [DEBUG] MoviePy version compatibility issue")
                    audio_clip.close()
                    video_clip.close()
                    return None
            except Exception as write_error:
                debug_print(f"🎵 [DEBUG] Failed to write audio file: {str(write_error)}")
                debug_print(f"🎵 [DEBUG] Write error type: {type(write_error).__name__}")
                audio_clip.close()
                video_clip.close()
                return None
            
            video_clip.close()
            debug_print(f"🎵 [DEBUG] Video resources cleaned up")
            
            # Verify the file was created and has content
            debug_print(f"🎵 [DEBUG] Verifying audio file...")
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                debug_print(f"🎵 [DEBUG] Audio extraction successful - Size: {file_size_mb:.2f} MB")
                return audio_path
            else:
                debug_print("🎵 [DEBUG] Audio file was not created or is empty")
                return None
            
        except Exception as e:
            debug_print(f"🎵 [DEBUG] Audio extraction failed with exception:")
            debug_print(f"🎵 [DEBUG] Error type: {type(e).__name__}")
            debug_print(f"🎵 [DEBUG] Error message: {str(e)}")
            import traceback
            debug_print(f"🎵 [DEBUG] Full traceback:")
            traceback.print_exc()
            return None
    
    def encode_frame_to_base64(self, frame: Any) -> str:
        """
        Encode frame to base64 string for API transmission
        
        Args:
            frame: OpenCV frame array
            
        Returns:
            Base64 encoded string
        """
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        # Convert to base64
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return frame_base64
    
    def create_multimodal_input(self, frames: List[Any], prompt: str) -> List[resources_pb2.Input]:
        """
        Create multimodal inputs for video transcription
        
        Args:
            frames: List of video frames
            prompt: Text prompt for transcription context
            
        Returns:
            List of Clarifai Input objects
        """
        inputs = []
        
        # Add text prompt as first input
        text_input = resources_pb2.Input(
            data=resources_pb2.Data(
                text=resources_pb2.Text(raw=prompt)
            )
        )
        inputs.append(text_input)
        
        # Add frames as image inputs
        for i, frame in enumerate(frames):
            frame_base64 = self.encode_frame_to_base64(frame)
            
            image_input = resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(base64=frame_base64)
                )
            )
            inputs.append(image_input)
        
        return inputs
    
    def transcribe_video(self, 
                        video_path: str, 
                        model_name: str,
                        prompt: str = "Please transcribe any speech, dialogue, or text visible in this video. Describe what is happening and provide a detailed transcription.",
                        temperature: float = 0.7,
                        max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Transcribe video using multimodal Clarifai model
        
        Args:
            video_path: Path to video file
            model_name: Name of the model to use
            prompt: Transcription prompt
            temperature: Model temperature (only used with gRPC fallback)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with transcription results
        """
        debug_print(f"🎬 [DEBUG] Video transcription request started")
        debug_print(f"🎬 [DEBUG] Video: {os.path.basename(video_path)}")
        debug_print(f"🎬 [DEBUG] SDK available - Modern: {self.use_new_sdk}, gRPC: {GRPC_SDK_AVAILABLE if 'GRPC_SDK_AVAILABLE' in globals() else 'Unknown'}")
        debug_print(f"🔄 [DEBUG] TRANSMISSION OPTIONS:")
        debug_print(f"   📹 Modern SDK: WHOLE VIDEO (complete file, temporal context, motion analysis)")
        debug_print(f"   🖼️ gRPC Fallback: KEY FRAMES (8 static images, no temporal context)")
        
        # Try modern SDK first
        if self.use_new_sdk:
            try:
                debug_print(f"🎬 [DEBUG] Attempting modern SDK approach...")
                debug_print(f"📹 [DEBUG] SELECTED METHOD: Modern SDK → WHOLE VIDEO transmission")
                return self.transcribe_video_modern_sdk(video_path, model_name, prompt, max_tokens)
            except Exception as e:
                debug_print(f"🎬 [DEBUG] Modern SDK failed, falling back to gRPC: {e}")
        
        # Fallback to old gRPC method
        debug_print(f"🎬 [DEBUG] Using gRPC fallback method...")
        debug_print(f"🖼️ [DEBUG] SELECTED METHOD: gRPC SDK → KEY FRAMES extraction")
        return self.transcribe_video_grpc(video_path, model_name, prompt, temperature, max_tokens)
    
    def transcribe_video_grpc(self, 
                             video_path: str, 
                             model_name: str,
                             prompt: str,
                             temperature: float = 0.7,
                             max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Transcribe video using gRPC API (fallback method)
        """
        start_time = time.time()
        
        try:
            # Get model info
            available_models = self.get_available_models()
            if model_name not in available_models:
                raise ValueError(f"Model '{model_name}' not available")
            
            model_info = available_models[model_name]
            
            # Extract frames from video
            debug_print(f"🖼️ [DEBUG] METHOD: Extracting KEY FRAMES (gRPC fallback method)")
            frames = self.extract_frames_from_video(video_path, max_frames=8)
            if not frames:
                raise ValueError("Could not extract frames from video")
            debug_print(f"🖼️ [DEBUG] PAYLOAD: {len(frames)} extracted frames (static images)")
            debug_print(f"🖼️ [DEBUG] LIMITATION: No temporal context, motion analysis limited")
            
            # Create multimodal inputs
            inputs = self.create_multimodal_input(frames, prompt)
            
            # Prepare model version
            model_version = resources_pb2.ModelVersion(
                id=model_info['model_id'],
                app_id=model_info['app_id'],
                user_id=model_info['user_id']
            )
            
            # Create predict request
            request = service_pb2.PostModelOutputsRequest(
                model_id=model_info['model_id'],
                version_id="",  # Use latest version
                inputs=inputs,
                model=resources_pb2.Model(
                    model_version=model_version,
                    output_info=resources_pb2.OutputInfo(
                        params=resources_pb2.Struct(
                            fields={
                                "temperature": resources_pb2.Value(number_value=temperature),
                                "max_tokens": resources_pb2.Value(number_value=max_tokens)
                            }
                        )
                    )
                )
            )
            
            # Make API call
            response = self.stub.PostModelOutputs(request, metadata=self.metadata)
            
            # Process response
            if response.status.code != status_code_pb2.SUCCESS:
                error_msg = f"API Error: {response.status.description}"
                return {
                    "success": False,
                    "error": error_msg,
                    "processing_time": time.time() - start_time
                }
            
            # Extract transcription from response
            transcription_text = ""
            if response.outputs:
                output = response.outputs[0]
                if output.data.text.raw:
                    transcription_text = output.data.text.raw
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "transcription": transcription_text,
                "model_used": model_name,
                "frames_processed": len(frames),
                "processing_time": processing_time,
                "video_info": {
                    "path": video_path,
                    "size_mb": os.path.getsize(video_path) / (1024 * 1024)
                },
                "sdk_used": "grpc"
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "sdk_used": "grpc"
            }
    
    def transcribe_video_with_audio(self,
                                  video_path: str,
                                  model_name: str,
                                  audio_transcription: Optional[str] = None,
                                  prompt: str = None,
                                  temperature: float = 0.7,
                                  max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Enhanced video transcription that combines visual and audio analysis
        
        Args:
            video_path: Path to video file
            model_name: Name of the model to use
            audio_transcription: Pre-extracted audio transcription
            prompt: Custom prompt (auto-generated if None)
            temperature: Model temperature (only used with gRPC fallback)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with comprehensive transcription results
        """
        debug_print(f"🎯 [DEBUG] Enhanced video transcription started")
        debug_print(f"🎯 [DEBUG] Audio transcription provided: {bool(audio_transcription)}")
        if audio_transcription:
            debug_print(f"🎯 [DEBUG] Audio transcription length: {len(audio_transcription)} chars")
        debug_print(f"🎯 [DEBUG] Custom prompt provided: {bool(prompt)}")
        
        # Auto-generate prompt if audio transcription is available
        if prompt is None:
            if audio_transcription:
                debug_print(f"🎯 [DEBUG] Generating audio-enhanced prompt...")
                prompt = f"""Please analyze this video and provide a comprehensive transcription. 

Audio transcription (already extracted): "{audio_transcription}"

Please:
1. Describe what is happening visually in the video
2. Identify any text, signs, or written content visible in the frames
3. Correlate the visual content with the audio transcription provided
4. Provide timestamps or sequence information if possible
5. Note any important visual context that complements the audio

Provide a detailed, structured response combining both visual and audio information."""
            else:
                debug_print(f"🎯 [DEBUG] Generating visual-only prompt...")
                prompt = """Please analyze this video and provide a comprehensive transcription including:
1. Any speech or dialogue you can detect
2. Visual text, signs, or written content
3. Description of key visual events and actions
4. Context and setting information
5. Any other relevant audio-visual information

Provide a detailed, structured transcription."""
        
        debug_print(f"🎯 [DEBUG] Final prompt length: {len(prompt)} characters")
        debug_print(f"🎯 [DEBUG] Calling main transcribe_video method...")
        return self.transcribe_video(video_path, model_name, prompt, temperature, max_tokens)


def is_video_processing_available() -> bool:
    """Check if video processing dependencies are available"""
    return VIDEO_PROCESSING_AVAILABLE and MOVIEPY_AVAILABLE


def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get basic information about a video file
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    if not VIDEO_PROCESSING_AVAILABLE:
        return {"error": "Video processing not available"}
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # Get file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        return {
            "duration_seconds": duration,
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}",
            "file_size_mb": round(file_size_mb, 2)
        }
        
    except Exception as e:
        return {"error": str(e)}