#!/usr/bin/env python3
"""
test_quick_model.py - Quick test to verify system is working
"""

import os
import sys
import time

# Add current directory to path for imports
sys.path.append('.')

try:
    from ClarifaiUtil import create_transcriber
    from config import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_model(model_name):
    print(f"🎙️ Testing Model: {model_name}")
    print("="*50)
    
    # Load audio file
    audio_file_path = "sample_audio.mp3"
    try:
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
        print(f"📁 Loaded audio file: {len(audio_bytes)} bytes")
    except Exception as e:
        print(f"❌ Error loading audio file: {e}")
        return False
    
    # Create transcriber
    try:
        transcriber = create_transcriber()
        print("✅ Transcriber created")
    except Exception as e:
        print(f"❌ Failed to create transcriber: {e}")
        return False
    
    # Test transcription
    try:
        start_time = time.time()
        
        transcription = transcriber.transcribe_audio_with_quality(
            audio_bytes=audio_bytes,
            model_name=model_name,
            temperature=0.1
        )
        
        duration = time.time() - start_time
        
        if transcription:
            print(f"✅ Success! ({duration:.2f}s)")
            print(f"📝 Result: {transcription}")
            return True
        else:
            print(f"❌ Empty result")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def main():
    print("🧪 Quick Model Testing")
    print("Testing multiple models to find available ones...\n")
    
    # Test models in order of reliability
    models_to_test = [
        "AssemblyAI Audio Transcription",
        "OpenAI Whisper",
        "OpenAI Whisper Large V2", 
        "OpenAI Whisper Large V3"
    ]
    
    for model in models_to_test:
        success = test_model(model)
        print()
        
        if success and model == "OpenAI Whisper Large V3":
            print("🎉 OpenAI Whisper Large V3 is working!")
            break
        elif success:
            print(f"✅ {model} is working - now testing Whisper V3...")
            continue
        else:
            print(f"⚠️  {model} failed, trying next model...")
            
        time.sleep(2)  # Brief pause between tests


if __name__ == "__main__":
    main()