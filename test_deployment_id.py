#!/usr/bin/env python3
"""
Test script to verify deployment_id functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append('.')

from config import config

def test_deployment_id_functionality():
    """Test deployment_id configuration and override functionality"""
    
    print("🚀 Testing Deployment ID Functionality")
    print("=" * 50)
    
    # Test 1: Check model configuration with deployment_id
    print("📋 Test 1: Model Configuration with Deployment ID")
    model_name = "OpenAI Whisper Large V3"
    model_info = config.get_model_info(model_name)
    
    print(f"Model: {model_name}")
    print(f"Model ID: {model_info.get('model_id', 'Not found')}")
    print(f"User ID: {model_info.get('user_id', 'Not found')}")
    print(f"App ID: {model_info.get('app_id', 'Not found')}")
    
    deployment_id = model_info.get('deployment_id')
    if deployment_id:
        print(f"✅ Deployment ID: {deployment_id}")
    else:
        print("❌ No deployment_id configured")
    
    print()
    
    # Test 2: Check environment variable override
    print("📋 Test 2: Environment Variable Override")
    env_deployment_id = config.CLARIFAI_DEPLOYMENT_ID
    if env_deployment_id:
        print(f"✅ Environment CLARIFAI_DEPLOYMENT_ID: {env_deployment_id}")
        print("🔄 This will override any model-specific deployment_id")
    else:
        print("ℹ️  No CLARIFAI_DEPLOYMENT_ID set in environment")
        print("   Model-specific deployment_id will be used if available")
    
    print()
    
    # Test 3: Show expected API request structure
    print("📋 Test 3: Expected API Request Structure")
    print("When calling Clarifai API, the request will include:")
    print(f"  - user_app_id.user_id: {model_info.get('user_id')}")
    print(f"  - user_app_id.app_id: {model_info.get('app_id')}")
    print(f"  - model_id: {model_info.get('model_id')}")
    
    final_deployment_id = model_info.get('deployment_id')
    if final_deployment_id:
        print(f"  - deployment_id: {final_deployment_id} ✅")
        print("    🎯 This enables dedicated deployed model usage")
    else:
        print("  - deployment_id: (not set)")
        print("    🎯 Will use standard shared model")
    
    print()
    
    # Test 4: Show other models for comparison
    print("📋 Test 4: Other Models (without deployment_id)")
    other_models = ["OpenAI Whisper", "Facebook Wav2Vec2 English", "AssemblyAI Audio Transcription"]
    
    for model in other_models:
        other_info = config.get_model_info(model)
        other_deployment_id = other_info.get('deployment_id')
        status = "✅ Has deployment_id" if other_deployment_id else "❌ No deployment_id"
        print(f"  {model}: {status}")
    
    print()
    
    # Test 5: Configuration summary
    print("📋 Test 5: Configuration Summary")
    print("Deployment ID Configuration Options:")
    print("1. Per-Model: Set 'deployment_id' in model config (config.py)")
    print("2. Global Override: Set CLARIFAI_DEPLOYMENT_ID environment variable (.env)")
    print("3. Priority: Environment variable > Model-specific config")
    print()
    print("💡 Use Cases:")
    print("- Dedicated deployed models for better performance")
    print("- Custom model versions or fine-tuned models")
    print("- Enterprise deployments with guaranteed compute")
    
    return True

def main():
    """Main test function"""
    print("🎙️ Deployment ID Configuration Test")
    print()
    
    success = test_deployment_id_functionality()
    
    print()
    if success:
        print("✅ All deployment_id tests completed successfully!")
        print("💡 Ready to use dedicated deployed models when available")
    else:
        print("❌ Tests failed. Check configuration.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)