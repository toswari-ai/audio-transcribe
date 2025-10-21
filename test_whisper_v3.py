#!/usr/bin/env python3
"""
test_whisper_v3.py - Test script specifically for OpenAI Whisper Large V3 model
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
    print("Make sure you're running this from the audio-transcribe directory")
    sys.exit(1)


def main():
    print("🎙️ Testing OpenAI Whisper Large V3 Model")
    print("="*50)
    
    # Check if audio file exists
    audio_file_path = "sample_audio.mp3"
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return
    
    # Load audio file
    try:
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
        
        file_size_mb = len(audio_bytes) / (1024 * 1024)
        print(f"📁 Loaded audio file: {audio_file_path}")
        print(f"📊 File size: {file_size_mb:.2f} MB")
    except Exception as e:
        print(f"❌ Error loading audio file: {e}")
        return
    
    # Create transcriber
    try:
        print("\n🏭 Creating Clarifai transcriber...")
        transcriber = create_transcriber()
        print("✅ Transcriber created successfully")
    except Exception as e:
        print(f"❌ Failed to create transcriber: {e}")
        return
    
    # Test OpenAI Whisper Large V3 model specifically
    model_name = "OpenAI Whisper Large V3"
    
    print(f"\n🎯 Testing model: {model_name}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        
        # Perform transcription with quality enhancement
        print("🔧 Performing transcription with quality enhancement...")
        transcription = transcriber.transcribe_audio_with_quality(
            audio_bytes=audio_bytes,
            model_name=model_name,
            temperature=config.DEFAULT_TEMPERATURE,
            max_tokens=config.DEFAULT_MAX_TOKENS,
            # Audio quality settings
            target_sample_rate=16000,
            normalize_audio=True,
            trim_silence=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Display results
        print(f"\n⏱️  Processing time: {duration:.2f} seconds")
        
        if transcription:
            print(f"✅ Transcription successful!")
            print(f"📝 Text length: {len(transcription)} characters")
            print(f"\n📄 Transcription Result:")
            print("=" * 50)
            print(transcription)
            print("=" * 50)
            
            # Test model configuration
            models = transcriber.get_available_models()
            if model_name in models:
                model_config = models[model_name]
                print(f"\n🔧 Model Configuration:")
                print(f"   Model ID: {model_config['model_id']}")
                print(f"   User ID: {model_config['user_id']}")
                print(f"   App ID: {model_config['app_id']}")
                print(f"   Status: {model_config['status']}")
                print(f"   Description: {model_config['description']}")
            
            print(f"\n🎉 OpenAI Whisper Large V3 test completed successfully!")
            
        else:
            print(f"❌ Transcription returned empty result")
            print("   This could indicate:")
            print("   - Audio format compatibility issues")
            print("   - Model configuration problems")
            print("   - API authentication issues")
            
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        print("   Please check:")
        print("   - CLARIFAI_PAT is set correctly")
        print("   - Model configuration in config.py")
        print("   - Network connectivity")


if __name__ == "__main__":
    main()