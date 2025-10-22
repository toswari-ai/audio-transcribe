"""
Test script for video transcription functionality
"""

import os
import sys
from ClarifaiVideoUtil import ClarifaiVideoTranscriber, is_video_processing_available, get_video_info
from config import config

def test_video_dependencies():
    """Test if video processing dependencies are available"""
    print("🔧 Checking video processing dependencies...")
    
    if is_video_processing_available():
        print("✅ All video processing dependencies are available")
        return True
    else:
        print("❌ Video processing dependencies missing")
        print("Please install: pip install opencv-python moviepy numpy")
        return False

def test_video_models():
    """Test video model configuration"""
    print("🤖 Testing video model configuration...")
    
    try:
        transcriber = ClarifaiVideoTranscriber()
        models = transcriber.get_available_models()
        
        print(f"✅ Found {len(models)} video models:")
        for name, info in models.items():
            print(f"  - {name}: {info.get('description', 'No description')[:80]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error testing video models: {e}")
        return False

def test_video_info(video_path=None):
    """Test video information extraction"""
    if not video_path:
        print("⏭️ Skipping video info test (no video file provided)")
        return True
    
    print(f"📊 Testing video info extraction for: {video_path}")
    
    try:
        info = get_video_info(video_path)
        if 'error' in info:
            print(f"❌ Error getting video info: {info['error']}")
            return False
        
        print("✅ Video info extracted successfully:")
        print(f"  Duration: {info.get('duration_seconds', 0):.1f}s")
        print(f"  Resolution: {info.get('resolution', 'Unknown')}")
        print(f"  FPS: {info.get('fps', 0):.1f}")
        print(f"  File size: {info.get('file_size_mb', 0):.1f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Error testing video info: {e}")
        return False

def main():
    """Run all video tests"""
    print("🎬 Video Transcription Test Suite")
    print("=" * 40)
    
    # Check environment
    if not config.CLARIFAI_PAT:
        print("⚠️ CLARIFAI_PAT not configured. Some tests may fail.")
    else:
        print("✅ CLARIFAI_PAT is configured")
    
    print()
    
    # Test 1: Dependencies
    deps_ok = test_video_dependencies()
    print()
    
    # Test 2: Model configuration  
    models_ok = test_video_models()
    print()
    
    # Test 3: Video info (optional)
    video_path = None
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if not os.path.exists(video_path):
            print(f"⚠️ Video file not found: {video_path}")
            video_path = None
    
    info_ok = test_video_info(video_path)
    print()
    
    # Summary
    print("📋 Test Summary")
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Models: {'✅' if models_ok else '❌'}")
    print(f"Video Info: {'✅' if info_ok else '❌'}")
    
    if deps_ok and models_ok:
        print("\n🎉 Video transcription is ready to use!")
        print("Run: streamlit run app-video.py")
    else:
        print("\n⚠️ Some issues need to be resolved before using video transcription.")

if __name__ == "__main__":
    main()