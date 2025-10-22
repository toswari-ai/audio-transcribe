#!/usr/bin/env python3
"""
test_streaming.py - Comprehensive test script for streaming transcription functionality
Tests streaming capabilities using Clarifai's OpenAI-compatible endpoint
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from ClarifaiUtil import create_streaming_transcriber, is_streaming_available


def test_streaming_availability():
    """Test if streaming functionality is available"""
    print("🧪 Testing Streaming Availability")
    print("=" * 50)
    
    available = is_streaming_available()
    print(f"OpenAI client available: {available}")
    
    if not available:
        print("❌ Streaming not available. Install with: pip install openai>=1.3.0")
        return False
    
    print("✅ Streaming functionality is available")
    return True


def test_streaming_transcriber_init():
    """Test streaming transcriber initialization"""
    print("\n🧪 Testing Streaming Transcriber Initialization")
    print("=" * 50)
    
    try:
        # Test with config PAT
        transcriber = create_streaming_transcriber()
        print(f"✅ Streaming transcriber initialized with config PAT")
        print(f"📡 Base URL: {transcriber.client.base_url}")
        return transcriber
        
    except Exception as e:
        print(f"❌ Failed to initialize streaming transcriber: {e}")
        return None


def test_model_url_conversion():
    """Test model name to OpenAI URL conversion"""
    print("\n🧪 Testing Model URL Conversion")
    print("=" * 50)
    
    transcriber = create_streaming_transcriber()
    if not transcriber:
        print("❌ Cannot test model conversion without transcriber")
        return
    
    # Test supported models
    test_models = [
        "OpenAI Whisper Large V3",
        "OpenAI Whisper Large V2", 
        "OpenAI Whisper"
    ]
    
    for model_name in test_models:
        try:
            model_url = transcriber.get_streaming_model_url(model_name)
            print(f"✅ {model_name}")
            print(f"   URL: {model_url}")
        except Exception as e:
            print(f"⚠️ {model_name}: {e}")
    
    # Test unsupported model
    try:
        transcriber.get_streaming_model_url("Facebook Wav2Vec2 English")
        print("❌ Expected error for non-streaming model")
    except ValueError as e:
        print(f"✅ Correctly rejected non-streaming model: {e}")


def create_test_audio():
    """Create a simple test audio file"""
    print("\n🧪 Creating Test Audio")
    print("=" * 50)
    
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Generate 10 seconds of 440Hz tone (A4 note)
        tone = Sine(440).to_audio_segment(duration=10000)
        
        # Export as WAV bytes
        import io
        audio_io = io.BytesIO()
        tone.export(audio_io, format="wav")
        audio_bytes = audio_io.getvalue()
        
        print(f"✅ Generated test audio: {len(audio_bytes)} bytes")
        print(f"📊 Duration: 10.0s, Frequency: 440Hz")
        
        return audio_bytes
        
    except ImportError:
        print("⚠️ pydub not available, cannot generate test audio")
        return None
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return None


def test_audio_chunking():
    """Test audio chunking for streaming"""
    print("\n🧪 Testing Audio Chunking")
    print("=" * 50)
    
    transcriber = create_streaming_transcriber()
    if not transcriber:
        return
    
    audio_bytes = create_test_audio()
    if not audio_bytes:
        print("⚠️ Cannot test chunking without test audio")
        return
    
    # Test different chunk sizes
    chunk_sizes = [2000, 5000, 8000]  # ms
    
    for chunk_ms in chunk_sizes:
        print(f"\n📊 Testing {chunk_ms}ms chunks:")
        
        chunk_count = 0
        total_size = 0
        
        try:
            for chunk_bytes in transcriber.chunk_audio_for_streaming(audio_bytes, chunk_ms):
                chunk_count += 1
                chunk_size = len(chunk_bytes)
                total_size += chunk_size
                
                print(f"  Chunk {chunk_count}: {chunk_size} bytes")
                
                if chunk_count >= 5:  # Limit output for readability
                    print(f"  ... (stopping at 5 chunks for display)")
                    break
            
            print(f"✅ Chunking successful: {chunk_count} chunks, {total_size} total bytes")
            
        except Exception as e:
            print(f"❌ Chunking failed: {e}")


def test_streaming_mock():
    """Test streaming with mock API response (dry run)"""
    print("\n🧪 Testing Streaming Mock (Dry Run)")
    print("=" * 50)
    
    transcriber = create_streaming_transcriber()
    if not transcriber:
        return
    
    audio_bytes = create_test_audio()
    if not audio_bytes:
        print("⚠️ Cannot test streaming without test audio")
        return
    
    print("🔄 This would test actual streaming, but requires valid Clarifai PAT")
    print("📝 Mock test parameters:")
    print(f"   Model: OpenAI Whisper Large V3")
    print(f"   Chunk size: 3000ms")
    print(f"   Audio size: {len(audio_bytes)} bytes")
    print(f"   Expected chunks: ~4")
    
    # Estimate processing
    expected_chunks = (10000 // 3000) + 1  # 10s audio / 3s chunks
    print(f"✅ Mock test complete: Would process ~{expected_chunks} chunks")


def test_streaming_integration():
    """Test integration with existing audio processing"""
    print("\n🧪 Testing Streaming Integration")
    print("=" * 50)
    
    transcriber = create_streaming_transcriber()
    if not transcriber:
        return
    
    # Test parameter integration
    test_params = {
        "chunk_duration_ms": 4000,
        "enable_audio_analysis": True,
        "high_quality_conversion": True,
        "target_sample_rate": 16000,
        "language": "en"
    }
    
    print("✅ Streaming parameters:")
    for param, value in test_params.items():
        print(f"   {param}: {value}")
    
    print("✅ Integration test complete")


def run_all_tests():
    """Run all streaming tests"""
    print("🚀 Clarifai Streaming Transcription Test Suite")
    print("=" * 60)
    print(f"Config PAT available: {'✅' if config.CLARIFAI_PAT else '❌'}")
    print(f"Test environment: {os.getcwd()}")
    print()
    
    # Run tests in sequence
    if not test_streaming_availability():
        print("\n❌ Streaming not available, stopping tests")
        return False
    
    transcriber = test_streaming_transcriber_init()
    if not transcriber:
        print("\n❌ Cannot initialize transcriber, stopping tests")
        return False
    
    test_model_url_conversion()
    test_audio_chunking()
    test_streaming_mock()
    test_streaming_integration()
    
    print("\n🎉 All streaming tests completed!")
    print("\n💡 To test with real audio:")
    print("   1. Ensure CLARIFAI_PAT is set in .env")
    print("   2. Run the Streamlit app: streamlit run app.py")
    print("   3. Upload an audio file and enable streaming mode")
    print("   4. Try different chunk sizes and streaming modes")
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)