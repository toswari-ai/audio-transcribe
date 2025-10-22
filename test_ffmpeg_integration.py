#!/usr/bin/env python3
"""
Test the updated ClarifaiVideoUtil with FFmpeg audio extraction
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ClarifaiVideoUtil import ClarifaiVideoTranscriber, debug_print

def test_ffmpeg_integration():
    """Test FFmpeg integration in ClarifaiVideoUtil"""
    print("🧪 Testing FFmpeg Integration with ClarifaiVideoUtil...")
    
    # Initialize transcriber (will use FFmpeg if available)
    transcriber = ClarifaiVideoTranscriber()
    
    # Test audio extraction with test video
    if os.path.exists('test_video.mp4'):
        print("📹 Testing audio extraction from test_video.mp4...")
        
        audio_path = transcriber.extract_audio_from_video('test_video.mp4')
        
        if audio_path and os.path.exists(audio_path):
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"✅ Audio extraction successful!")
            print(f"   Audio file: {os.path.basename(audio_path)}")
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Clean up
            try:
                os.remove(audio_path)
                print(f"🧹 Cleaned up temp audio file")
            except:
                pass
                
        else:
            print(f"❌ Audio extraction failed")
            return False
    else:
        print("⚠️ No test video file found (test_video.mp4)")
        return False
    
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    # Enable debug for testing
    os.environ["DEBUG_VIDEO_PROCESSING"] = "true"
    
    test_ffmpeg_integration()