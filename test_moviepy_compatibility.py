#!/usr/bin/env python3
"""
Test script to diagnose MoviePy compatibility issues
This will help identify what might be causing the error message
"""

import os
from ClarifaiVideoUtil import ClarifaiVideoTranscriber

def test_moviepy_compatibility():
    """Test various MoviePy scenarios that might trigger compatibility errors"""
    
    print("🧪 MoviePy Compatibility Diagnostic Test")
    print("=" * 50)
    
    # Enable debug mode
    os.environ['DEBUG_VIDEO_PROCESSING'] = 'true'
    
    transcriber = ClarifaiVideoTranscriber()
    
    print("\n1️⃣ Testing normal audio extraction:")
    if os.path.exists('test_video.mp4'):
        try:
            result = transcriber.extract_audio_from_video('test_video.mp4')
            if result:
                print("✅ SUCCESS: Audio extraction worked")
                os.remove(result) if os.path.exists(result) else None
            else:
                print("⚠️ WARNING: Audio extraction returned None")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
            # Check if this matches the app's error detection
            error_msg = str(e)
            if any(phrase in error_msg.lower() for phrase in [
                "expected bytes, got str", 
                "unexpected keyword argument 'verbose'",
                "got an unexpected keyword argument",
                "moviepy version compatibility"
            ]):
                print("🎯 MATCH: This error would trigger MoviePy compatibility message")
            else:
                print("🔍 INFO: This error would show as general audio failure")
    else:
        print("❌ test_video.mp4 not found")
    
    print("\n2️⃣ Testing with problematic parameters:")
    try:
        # Try to simulate old MoviePy usage that would fail
        from moviepy import VideoFileClip
        
        if os.path.exists('test_video.mp4'):
            video = VideoFileClip('test_video.mp4')
            if video.audio:
                import tempfile
                temp_audio = tempfile.mktemp(suffix='.wav')
                
                try:
                    # This should fail with MoviePy 2.1.2
                    video.audio.write_audiofile(temp_audio, verbose=False, logger=None)
                    print("❌ UNEXPECTED: verbose=False should have failed")
                except TypeError as e:
                    print("✅ EXPECTED: verbose=False parameter failed as expected")
                    print(f"   Error: {e}")
                    
                    # Test our error detection
                    error_msg = str(e)
                    if "unexpected keyword argument 'verbose'" in error_msg:
                        print("🎯 CONFIRMATION: This matches our MoviePy compatibility detection")
                        
            video.close()
                    
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    print("\n✅ Diagnostic test completed")
    print("\nIf you're seeing the MoviePy compatibility error in the app:")
    print("1. Clear browser cache and restart Streamlit")
    print("2. Try a different video file")  
    print("3. Check if the video has an audio track")
    print("4. Verify the video file is not corrupted")

if __name__ == "__main__":
    test_moviepy_compatibility()