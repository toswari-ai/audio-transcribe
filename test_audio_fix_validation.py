#!/usr/bin/env python3
"""
Test to reproduce and verify the fix for the audio result handling error
"""

import os
import tempfile
from ClarifaiUtil import ClarifaiTranscriber

def test_audio_transcription_result_handling():
    """Test that we handle string results correctly from transcribe_audio"""
    print("🧪 Testing Real Audio Transcription Result Handling...")
    print("=" * 60)
    
    # Use a small audio file for testing
    test_video = 'test_video.mp4'
    if not os.path.exists(test_video):
        print("❌ test_video.mp4 not found")
        return False
    
    # Extract audio using FFmpeg
    from ffmpeg_audio_extractor import FFmpegAudioExtractor
    
    print("🎵 Step 1: Extract audio from test video")
    extractor = FFmpegAudioExtractor(debug=True)
    success, audio_path, error = extractor.extract_audio(test_video)
    
    if not success or not audio_path:
        print(f"❌ Audio extraction failed: {error}")
        return False
    
    print(f"✅ Audio extracted: {os.path.basename(audio_path)}")
    
    try:
        print("\n🎙️ Step 2: Transcribe audio and test result handling")
        
        # Read audio bytes
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        
        print(f"📊 Audio bytes loaded: {len(audio_bytes)} bytes")
        
        # Initialize transcriber
        transcriber = ClarifaiTranscriber()
        
        # Call transcribe_audio (this returns a string)
        print("🚀 Calling transcribe_audio...")
        audio_result = transcriber.transcribe_audio(
            audio_bytes,
            "OpenAI Whisper Large V3",
            temperature=0.3,
            max_tokens=1000
        )
        
        print(f"📝 Transcription result type: {type(audio_result)}")
        print(f"📏 Result length: {len(str(audio_result)) if audio_result else 0}")
        
        # Test the FIXED logic (should work now)
        print(f"\n🔧 Step 3: Test fixed result handling logic")
        try:
            if audio_result and isinstance(audio_result, str) and len(audio_result.strip()) > 0:
                audio_transcription = audio_result.strip()
                print(f"✅ SUCCESS: Audio transcription extracted ({len(audio_transcription)} characters)")
                if len(audio_transcription) > 100:
                    print(f"📝 Sample: {audio_transcription[:100]}...")
                else:
                    print(f"📝 Full text: {audio_transcription}")
            else:
                print(f"⚠️ Empty or invalid audio result")
            
            print(f"🎉 Fixed logic works correctly!")
            
        except Exception as e:
            print(f"❌ ERROR in fixed logic: {e}")
            return False
        
        # Test the OLD logic (should fail)
        print(f"\n🚫 Step 4: Test old buggy logic (for comparison)")
        try:
            # This is the OLD buggy code that caused the error
            if audio_result.get('success'):  # This should fail with AttributeError
                audio_transcription = audio_result.get('transcription', '')
            
            print(f"❌ Old logic unexpectedly worked - this shouldn't happen!")
            return False
            
        except AttributeError as e:
            print(f"✅ EXPECTED: Old logic correctly fails with: {e}")
            print(f"🎯 This confirms our fix addresses the right issue")
        
    finally:
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"\n🧹 Cleaned up temp audio file")
    
    print(f"\n🏁 Test completed successfully!")
    print(f"💡 The fix correctly handles string results from transcribe_audio")
    return True

if __name__ == "__main__":
    test_audio_transcription_result_handling()