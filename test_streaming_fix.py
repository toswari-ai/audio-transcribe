#!/usr/bin/env python3
"""
test_streaming_fix.py - Quick test for the streaming fix
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from ClarifaiUtil import create_streaming_transcriber


def test_streaming_fix():
    """Test the streaming fix with a simple chunk"""
    print("🧪 Testing Streaming Fix")
    print("=" * 50)
    
    if not config.CLARIFAI_PAT:
        print("❌ CLARIFAI_PAT not set in config")
        return False
    
    try:
        # Create streaming transcriber
        streaming_transcriber = create_streaming_transcriber()
        print("✅ Streaming transcriber created")
        
        # Test model URL generation
        model_name = "OpenAI Whisper Large V3"
        model_url = streaming_transcriber.get_streaming_model_url(model_name)
        print(f"✅ Model URL: {model_url}")
        
        # Test with minimal audio (we'll use a tiny synthetic chunk)
        print("🔍 Testing with minimal audio chunk...")
        
        # Create minimal WAV header + silence (about 1 second)
        # This is a minimal valid WAV file
        minimal_wav = (
            b'RIFF' + (44 + 16000).to_bytes(4, 'little') + b'WAVE' +
            b'fmt ' + (16).to_bytes(4, 'little') + 
            (1).to_bytes(2, 'little') +  # PCM
            (1).to_bytes(2, 'little') +  # mono
            (16000).to_bytes(4, 'little') +  # sample rate
            (32000).to_bytes(4, 'little') +  # byte rate  
            (2).to_bytes(2, 'little') +   # block align
            (16).to_bytes(2, 'little') +  # bits per sample
            b'data' + (16000).to_bytes(4, 'little') +
            b'\x00' * 16000  # 1 second of silence
        )
        
        print(f"📊 Test audio size: {len(minimal_wav)} bytes")
        
        # Try streaming with single chunk (no real streaming, just test the API)
        results = list(streaming_transcriber.transcribe_streaming(
            minimal_wav,
            model_name=model_name,
            chunk_duration_ms=1000,  # 1 second chunks
            enable_audio_analysis=False,
            high_quality_conversion=False
        ))
        
        print(f"✅ Streaming completed with {len(results)} results")
        
        for i, result in enumerate(results):
            if result.get("is_final"):
                print(f"📝 Final result: '{result.get('text', 'No text')}'")
            else:
                text = result.get('text', 'No text')
                print(f"📝 Chunk {i}: '{text}' ({result.get('processing_time', 0):.2f}s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_streaming_fix()
    if success:
        print("\n🎉 Streaming fix test completed successfully!")
    else:
        print("\n❌ Streaming fix test failed")
    sys.exit(0 if success else 1)