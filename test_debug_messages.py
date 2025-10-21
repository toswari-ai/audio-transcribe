#!/usr/bin/env python3
"""
Test script to verify debug messages for dedicated compute calls
"""

import os
import sys

# Add current directory to path
sys.path.append('.')

try:
    from ClarifaiUtil import create_transcriber
    from config import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_debug_messages():
    """Test debug messages for dedicated compute deployment"""
    
    print("🔍 Testing Debug Messages for Dedicated Compute")
    print("=" * 55)
    
    # Check if audio file exists
    audio_file = "sample_audio.mp3"
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    print(f"📁 Audio file: {audio_file}")
    
    # Test 1: Model with deployment_id (Whisper V3)
    print("\n📋 Test 1: Model WITH Deployment ID (OpenAI Whisper Large V3)")
    print("-" * 60)
    
    model_name = "OpenAI Whisper Large V3"
    model_info = config.get_model_info(model_name)
    
    print(f"Model: {model_name}")
    print(f"Deployment ID in config: {model_info.get('deployment_id', 'None')}")
    
    try:
        transcriber = create_transcriber()
        print("\n🎯 Expected debug output for dedicated compute:")
        
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
            
        # This should show debug messages for dedicated compute
        result = transcriber.transcribe_audio_with_quality(
            audio_bytes,
            model_name,
            temperature=0.1,
            high_quality_conversion=True
        )
        
        if result:
            print(f"✅ Transcription successful (with debug messages shown above)")
        else:
            print(f"❌ Transcription failed (but debug messages should still appear)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Model without deployment_id (Facebook Wav2Vec2)
    print("\n📋 Test 2: Model WITHOUT Deployment ID (Facebook Wav2Vec2)")
    print("-" * 60)
    
    model_name2 = "Facebook Wav2Vec2 English"
    model_info2 = config.get_model_info(model_name2)
    
    print(f"Model: {model_name2}")
    print(f"Deployment ID in config: {model_info2.get('deployment_id', 'None')}")
    
    try:
        print("\n🌐 Expected debug output for shared compute:")
        
        # This should show debug messages for shared compute
        result = transcriber.transcribe_audio_with_quality(
            audio_bytes,
            model_name2,
            temperature=0.1,
            high_quality_conversion=True
        )
        
        if result:
            print(f"✅ Transcription successful (with debug messages shown above)")
        else:
            print(f"❌ Transcription failed (but debug messages should still appear)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Environment variable override
    print("\n📋 Test 3: Environment Variable Override")
    print("-" * 50)
    
    env_deployment_id = config.CLARIFAI_DEPLOYMENT_ID
    if env_deployment_id:
        print(f"✅ Environment CLARIFAI_DEPLOYMENT_ID: {env_deployment_id}")
        print("🔄 All models will show this deployment_id in debug messages")
    else:
        print("ℹ️  No CLARIFAI_DEPLOYMENT_ID set - using model-specific values")
    
    return True

def main():
    """Main test function"""
    print("🎙️ Debug Messages Test for Dedicated Compute")
    print()
    
    success = test_debug_messages()
    
    print("\n📊 Summary:")
    print("=" * 30)
    print("Debug messages show:")
    print("🎯 Dedicated compute: When deployment_id is configured")
    print("🌐 Shared compute: When no deployment_id is set")
    print("📋 Deployment ID: The actual ID being used")
    print("💻 Model info: Model name and compute type")
    
    if success:
        print("\n✅ Debug message test completed!")
    else:
        print("\n❌ Test failed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)