#!/usr/bin/env python3
"""
test_clarifai_audio.py - Test script for ClarifaiUtil functionality
Tests audio transcription using sample_audio.mp3 file
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')

try:
    from ClarifaiUtil import ClarifaiTranscriber, create_transcriber, get_available_models, validate_model
    from config import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the audio-transcribe directory")
    sys.exit(1)


def load_audio_file(file_path: str) -> bytes:
    """
    Load audio file and return as bytes
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Audio data as bytes
    """
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading audio file: {e}")


def print_separator(title: str = ""):
    """Print a decorative separator"""
    print("\n" + "="*60)
    if title:
        print(f" {title} ".center(60))
        print("="*60)


def test_configuration():
    """Test configuration validation"""
    print_separator("CONFIGURATION TEST")
    
    # Test PAT configuration
    print(f"📋 Clarifai PAT configured: {'✅ Yes' if config.CLARIFAI_PAT else '❌ No'}")
    print(f"📋 User ID: {config.CLARIFAI_USER_ID or 'Not set'}")
    print(f"📋 App ID: {config.CLARIFAI_APP_ID or 'Not set'}")
    print(f"📋 Default model: {config.DEFAULT_MODEL}")
    print(f"📋 Default temperature: {config.DEFAULT_TEMPERATURE}")
    print(f"📋 Default max tokens: {config.DEFAULT_MAX_TOKENS}")
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print(f"\n❌ Configuration errors found:")
        for key, error in errors.items():
            print(f"   - {key}: {error}")
        return False
    else:
        print(f"\n✅ Configuration is valid!")
        return True


def test_available_models():
    """Test model availability and validation"""
    print_separator("MODEL AVAILABILITY TEST")
    
    # Get available models
    models = get_available_models()
    print(f"📦 Available models ({len(models)}):")
    
    for i, (name, info) in enumerate(models.items(), 1):
        print(f"   {i}. {name}")
        print(f"      - Model ID: {info['model_id']}")
        print(f"      - User: {info['user_id']}")
        print(f"      - App: {info['app_id']}")
        print(f"      - Description: {info['description']}")
        print()
    
    # Test model validation
    print(f"🔍 Model validation tests:")
    test_models = [config.DEFAULT_MODEL, "NonExistentModel", "OpenAI Whisper"]
    
    for model in test_models:
        is_valid = validate_model(model)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   - '{model}': {status}")


def test_transcriber_creation():
    """Test ClarifaiTranscriber instantiation"""
    print_separator("TRANSCRIBER CREATION TEST")
    
    try:
        # Test with factory function
        print("🏭 Creating transcriber with factory function...")
        transcriber1 = create_transcriber()
        print("✅ Factory function successful")
        
        # Test with direct instantiation
        print("🔧 Creating transcriber with direct instantiation...")
        transcriber2 = ClarifaiTranscriber(config.CLARIFAI_PAT)
        print("✅ Direct instantiation successful")
        
        # Test model access
        models = transcriber1.get_available_models()
        print(f"🎯 Transcriber has access to {len(models)} models")
        
        return transcriber1
        
    except Exception as e:
        print(f"❌ Transcriber creation failed: {e}")
        return None


def test_audio_file_loading():
    """Test loading the sample audio file"""
    print_separator("AUDIO FILE LOADING TEST")
    
    audio_file_path = "sample_audio.mp3"
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return None
    
    try:
        # Get file info
        file_size = os.path.getsize(audio_file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📁 Audio file: {audio_file_path}")
        print(f"📊 File size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
        
        # Check against max file size
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            print(f"⚠️  File exceeds max size limit ({config.MAX_FILE_SIZE_MB}MB)")
        else:
            print(f"✅ File size within limits")
        
        # Load audio data
        print("📖 Loading audio data...")
        audio_bytes = load_audio_file(audio_file_path)
        print(f"✅ Audio loaded successfully: {len(audio_bytes):,} bytes")
        
        return audio_bytes
        
    except Exception as e:
        print(f"❌ Audio loading failed: {e}")
        return None


def test_single_transcription(transcriber: ClarifaiTranscriber, audio_bytes: bytes, model_name: str):
    """Test transcription with a specific model"""
    print(f"\n🎙️ Testing transcription with: {model_name}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        
        # Perform transcription
        transcription = transcriber.transcribe_audio(
            audio_bytes=audio_bytes,
            model_name=model_name,
            temperature=config.DEFAULT_TEMPERATURE,
            max_tokens=config.DEFAULT_MAX_TOKENS
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Display results
        print(f"⏱️  Processing time: {duration:.2f} seconds")
        
        if transcription:
            print(f"✅ Transcription successful!")
            print(f"📝 Text length: {len(transcription)} characters")
            print(f"📄 Transcription:")
            print("-" * 30)
            print(transcription)
            print("-" * 30)
            return True, transcription, duration
        else:
            print(f"❌ Transcription returned empty result")
            return False, None, duration
            
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return False, None, 0


def test_all_models(transcriber: ClarifaiTranscriber, audio_bytes: bytes):
    """Test transcription with all available models"""
    print_separator("FULL MODEL TESTING")
    
    models = transcriber.get_available_models()
    results = {}
    
    print(f"🧪 Testing transcription with all {len(models)} models...")
    print("This may take a few minutes...\n")
    
    for i, model_name in enumerate(models.keys(), 1):
        print(f"[{i}/{len(models)}]", end=" ")
        success, transcription, duration = test_single_transcription(
            transcriber, audio_bytes, model_name
        )
        
        results[model_name] = {
            'success': success,
            'transcription': transcription,
            'duration': duration
        }
        
        # Brief pause between requests
        if i < len(models):
            time.sleep(1)
    
    return results


def print_summary(results: dict):
    """Print summary of all transcription tests"""
    print_separator("TEST SUMMARY")
    
    successful = [name for name, result in results.items() if result['success']]
    failed = [name for name, result in results.items() if not result['success']]
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Successful: {len(successful)}/{len(results)} models")
    print(f"   ❌ Failed: {len(failed)}/{len(results)} models")
    
    if successful:
        print(f"\n🏆 Successful Models:")
        for model in successful:
            duration = results[model]['duration']
            text_len = len(results[model]['transcription']) if results[model]['transcription'] else 0
            print(f"   - {model}: {duration:.2f}s, {text_len} chars")
    
    if failed:
        print(f"\n💥 Failed Models:")
        for model in failed:
            print(f"   - {model}")
    
    # Find fastest model
    if successful:
        fastest = min(successful, key=lambda m: results[m]['duration'])
        fastest_time = results[fastest]['duration']
        print(f"\n🚀 Fastest Model: {fastest} ({fastest_time:.2f}s)")


def main():
    """Main test function"""
    print("🎙️ ClarifaiUtil Audio Transcription Test")
    print("=" * 60)
    
    # Test 1: Configuration
    if not test_configuration():
        print("\n❌ Configuration test failed. Please fix configuration issues.")
        return
    
    # Test 2: Model availability
    test_available_models()
    
    # Test 3: Transcriber creation
    transcriber = test_transcriber_creation()
    if not transcriber:
        print("\n❌ Transcriber creation failed. Cannot continue.")
        return
    
    # Test 4: Audio file loading
    audio_bytes = test_audio_file_loading()
    if not audio_bytes:
        print("\n❌ Audio file loading failed. Cannot continue.")
        return
    
    # Test 5: Single model test (default model)
    print_separator("SINGLE MODEL TEST")
    print(f"🎯 Testing default model: {config.DEFAULT_MODEL}")
    
    success, transcription, duration = test_single_transcription(
        transcriber, audio_bytes, config.DEFAULT_MODEL
    )
    
    if not success:
        print(f"\n❌ Default model test failed. Check your configuration.")
        return
    
    # Ask user if they want to test all models
    print(f"\n🤔 Would you like to test all available models?")
    print(f"   This will test {len(transcriber.get_available_models())} models and may take several minutes.")
    
    response = input("Continue with full testing? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        # Test 6: All models
        results = test_all_models(transcriber, audio_bytes)
        print_summary(results)
    else:
        print("\n✅ Single model test completed successfully!")
    
    print(f"\n🎉 All tests completed!")


if __name__ == "__main__":
    main()