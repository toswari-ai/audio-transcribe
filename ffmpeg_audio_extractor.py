"""
FFmpeg-based Audio Extractor
A robust audio extraction utility using FFmpeg-python for video processing.
Replaces MoviePy with better performance and compatibility.
"""

import os
import tempfile
import ffmpeg
from typing import Optional, Tuple
import subprocess
import logging

class FFmpegAudioExtractor:
    """
    High-performance audio extraction using FFmpeg-python.
    Provides better compatibility and performance than MoviePy.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize FFmpeg audio extractor.
        
        Args:
            debug (bool): Enable debug logging
        """
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
    
    def debug_print(self, message: str, prefix: str = "🎵") -> None:
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"{prefix} [DEBUG] {message}")
    
    def check_ffmpeg_available(self) -> bool:
        """
        Check if FFmpeg is available on the system.
        
        Returns:
            bool: True if FFmpeg is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            available = result.returncode == 0
            if available:
                version_line = result.stdout.split('\n')[0]
                self.debug_print(f"FFmpeg available: {version_line}")
            else:
                self.debug_print("FFmpeg binary not working")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.debug_print(f"FFmpeg check failed: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get video information using FFmpeg probe.
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            dict: Video information or None if failed
        """
        try:
            self.debug_print(f"Probing video: {video_path}")
            probe = ffmpeg.probe(video_path)
            
            # Find video and audio streams
            video_stream = None
            audio_stream = None
            
            for stream in probe.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            duration = float(probe.get('format', {}).get('duration', 0))
            
            info = {
                'duration': duration,
                'has_audio': audio_stream is not None,
                'has_video': video_stream is not None,
                'format': probe.get('format', {}),
                'video_stream': video_stream,
                'audio_stream': audio_stream
            }
            
            self.debug_print(f"Video info - Duration: {duration:.2f}s, Audio: {info['has_audio']}, Video: {info['has_video']}")
            return info
            
        except Exception as e:
            self.debug_print(f"Failed to probe video: {e}", "❌")
            return None
    
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract audio from video using FFmpeg.
        
        Args:
            video_path (str): Path to input video file
            output_path (str, optional): Path for output audio file. Auto-generated if None.
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (Success, audio_path, error_message)
        """
        try:
            # Check if FFmpeg is available
            if not self.check_ffmpeg_available():
                return False, None, "FFmpeg is not available on this system"
            
            self.debug_print(f"Starting audio extraction from: {os.path.basename(video_path)}")
            
            # Get video information
            video_info = self.get_video_info(video_path)
            if not video_info:
                return False, None, "Failed to analyze video file"
            
            if not video_info['has_audio']:
                return False, None, "Video file contains no audio track"
            
            # Generate output path if not provided
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(
                    tempfile.gettempdir(), 
                    f"{base_name}_extracted_audio.wav"
                )
            
            self.debug_print(f"Target audio path: {os.path.basename(output_path)}")
            
            # Extract audio using FFmpeg
            self.debug_print("Extracting audio with FFmpeg...")
            
            # Build FFmpeg command
            stream = ffmpeg.input(video_path)
            audio = stream.audio
            
            # Configure output with high quality settings
            output = ffmpeg.output(
                audio, 
                output_path,
                acodec='pcm_s16le',  # 16-bit PCM WAV
                ar=44100,            # 44.1 kHz sample rate
                ac=2,                # Stereo
                loglevel='error'     # Reduce verbose output
            )
            
            # Overwrite output file if it exists
            output = ffmpeg.overwrite_output(output)
            
            # Run the extraction
            self.debug_print("Running FFmpeg extraction...")
            ffmpeg.run(output, quiet=not self.debug)
            
            # Verify the output file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                self.debug_print(f"Audio extraction successful - Size: {file_size:.2f} MB", "✅")
                return True, output_path, None
            else:
                return False, None, "Audio file was not created or is empty"
                
        except ffmpeg.Error as e:
            error_msg = f"FFmpeg error during audio extraction: {e}"
            self.debug_print(error_msg, "❌")
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error during audio extraction: {e}"
            self.debug_print(error_msg, "❌")
            return False, None, error_msg
    
    def extract_audio_segment(self, video_path: str, start_time: float, end_time: float, output_path: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract a specific time segment of audio from video.
        
        Args:
            video_path (str): Path to input video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            output_path (str, optional): Path for output audio file
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (Success, audio_path, error_message)
        """
        try:
            if not self.check_ffmpeg_available():
                return False, None, "FFmpeg is not available on this system"
            
            # Validate time segment
            if start_time >= end_time:
                return False, None, "Start time must be less than end time"
            
            duration = end_time - start_time
            self.debug_print(f"Extracting audio segment: {start_time:.2f}s to {end_time:.2f}s ({duration:.2f}s)")
            
            # Generate output path if not provided
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(
                    tempfile.gettempdir(), 
                    f"{base_name}_segment_{start_time:.0f}_{end_time:.0f}.wav"
                )
            
            # Extract segment using FFmpeg
            stream = ffmpeg.input(video_path, ss=start_time, t=duration)
            audio = stream.audio
            
            output = ffmpeg.output(
                audio, 
                output_path,
                acodec='pcm_s16le',
                ar=44100,
                ac=2,
                loglevel='error'
            )
            
            output = ffmpeg.overwrite_output(output)
            ffmpeg.run(output, quiet=not self.debug)
            
            # Verify output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                self.debug_print(f"Audio segment extraction successful - Size: {file_size:.2f} MB", "✅")
                return True, output_path, None
            else:
                return False, None, "Audio segment file was not created or is empty"
                
        except Exception as e:
            error_msg = f"Error extracting audio segment: {e}"
            self.debug_print(error_msg, "❌")
            return False, None, error_msg
    
    def cleanup_temp_files(self, file_paths: list) -> None:
        """
        Clean up temporary audio files.
        
        Args:
            file_paths (list): List of file paths to clean up
        """
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    self.debug_print(f"Cleaned up temp file: {os.path.basename(file_path)}")
            except Exception as e:
                self.debug_print(f"Failed to cleanup {file_path}: {e}", "⚠️")


def test_ffmpeg_extractor():
    """Test the FFmpeg audio extractor."""
    print("🧪 Testing FFmpeg Audio Extractor...")
    
    extractor = FFmpegAudioExtractor(debug=True)
    
    # Test with a sample video file
    if os.path.exists('test_video.mp4'):
        success, audio_path, error = extractor.extract_audio('test_video.mp4')
        
        if success:
            print(f"✅ Test successful! Audio extracted to: {audio_path}")
            # Clean up
            if audio_path:
                extractor.cleanup_temp_files([audio_path])
        else:
            print(f"❌ Test failed: {error}")
    else:
        print("⚠️ No test video file found (test_video.mp4)")


if __name__ == "__main__":
    test_ffmpeg_extractor()