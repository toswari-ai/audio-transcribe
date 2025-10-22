#!/usr/bin/env python3
"""
Test the exact same flow as the video app to reproduce and fix the audio transcription issue
"""

import os
import tempfile
import shutil
from ClarifaiVideoUtil import ClarifaiVideoTranscriber, debug_print
from ClarifaiUtil import ClarifaiTranscriber

def test_video_audio_transcription():
    """Test the complete video->audio->transcription pipeline"""
    print("🎬 Testing Complete Video Audio Transcription Pipeline...")
    print("=" * 60)
    
    # Enable debug mode
    os.environ["DEBUG_VIDEO_PROCESSING"] = "true"
    
    # Step 1: Copy test video to temp location (simulate uploaded file)
    video_file = 'test_video.mp4'
    if not os.path.exists(video_file):
        print("❌ test_video.mp4 not found")
        return False
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
        shutil.copy2(video_file, temp_video.name)
        temp_video_path = temp_video.name
    
    print(f"📹 Test video copied to: {os.path.basename(temp_video_path)}")
    
    try:
        # Step 2: Initialize video transcriber (same as Streamlit app)
        video_transcriber = ClarifaiVideoTranscriber()
        
        # Step 3: Extract audio using FFmpeg (same as Streamlit app)
        print("\n🎵 Step 1: Audio Extraction")
        audio_path = video_transcriber.extract_audio_from_video(temp_video_path)
        
        if audio_path and os.path.exists(audio_path):
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"✅ Audio extraction successful: {os.path.basename(audio_path)} ({file_size_mb:.2f} MB)")
            
            # Step 4: Audio transcription (simulate exact Streamlit app flow)
            print("\n🎙️ Step 2: Audio Transcription")
            
            # Initialize audio transcriber (same as Streamlit app)
            audio_transcriber = ClarifaiTranscriber()
            
            try:
                # Read audio file into bytes for transcription (FIXED VERSION)
                debug_print(f"🎵 [DEBUG] Reading audio file for transcription: {os.path.basename(audio_path)}")
                with open(audio_path, 'rb') as f:
                    audio_bytes = f.read()
                
                debug_print(f"🎵 [DEBUG] Audio file loaded - Size: {len(audio_bytes)} bytes")
                
                # Use a good audio model for transcription
                audio_result = audio_transcriber.transcribe_audio(
                    audio_bytes,  # Pass audio bytes, not file path
                    "OpenAI Whisper Large V3",  # Use best audio model
                    temperature=0.3,  # Lower temperature for accuracy
                    max_tokens=1000
                )
                
                debug_print(f"🎵 [DEBUG] Audio transcription completed: {type(audio_result)}")
                
                if audio_result:
                    print(f"✅ Audio transcription successful!")
                    print(f"📝 Transcription: {audio_result[:100]}..." if len(str(audio_result)) > 100 else f"📝 Transcription: {audio_result}")
                else:
                    print(f"❌ Audio transcription returned None/empty result")
                    return False
                    
            except Exception as audio_error:
                print(f"❌ Audio transcription failed: {audio_error}")
                print(f"🔍 Error type: {type(audio_error).__name__}")
                return False
            
            # Step 5: Video transcription (same as Streamlit app)
            print(f"\n📹 Step 3: Video Analysis")
            try:
                video_result = video_transcriber.transcribe_video_with_modern_sdk(
                    temp_video_path,
                    "MM-Poly-8B",
                    "Describe what you see and hear in this video.",
                    max_tokens=1000
                )
                
                if video_result:
                    print(f"✅ Video transcription successful!")
                    print(f"📝 Video analysis: {video_result[:100]}..." if len(str(video_result)) > 100 else f"📝 Video analysis: {video_result}")
                else:
                    print(f"❌ Video transcription returned None/empty result")
                    
            except Exception as video_error:
                print(f"❌ Video transcription failed: {video_error}")
                
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"🧹 Cleaned up audio file")
                
        else:
            print(f"❌ Audio extraction failed")
            return False
            
    finally:
        # Cleanup temp video
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            print(f"🧹 Cleaned up temp video file")
    
    print(f"\n🎉 Complete pipeline test completed!")
    return True

if __name__ == "__main__":
    test_video_audio_transcription()