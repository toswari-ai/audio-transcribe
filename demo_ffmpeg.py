#!/usr/bin/env python3
"""
Simple test to demonstrate FFmpeg audio extraction working with sample video
"""

import os
import tempfile
from ffmpeg_audio_extractor import FFmpegAudioExtractor

def demo_ffmpeg_extraction():
    """Demonstrate FFmpeg audio extraction capabilities"""
    print("🎵 FFmpeg Audio Extraction Demo")
    print("=" * 50)
    
    # Initialize extractor with debug enabled
    extractor = FFmpegAudioExtractor(debug=True)
    
    # Check FFmpeg availability
    if not extractor.check_ffmpeg_available():
        print("❌ FFmpeg is not available. Please install FFmpeg:")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: Download from https://ffmpeg.org/")
        return False
    
    # Test with existing video file
    if os.path.exists('test_video.mp4'):
        video_file = 'test_video.mp4'
        print(f"📹 Testing with: {video_file}")
        
        # Get video information
        video_info = extractor.get_video_info(video_file)
        if video_info:
            print(f"📊 Video Info:")
            print(f"   Duration: {video_info['duration']:.2f} seconds")
            print(f"   Has Audio: {video_info['has_audio']}")
            print(f"   Has Video: {video_info['has_video']}")
        
        # Extract full audio
        print("\n🎵 Extracting Full Audio...")
        success, audio_path, error = extractor.extract_audio(video_file)
        
        if success and audio_path:
            file_size = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"✅ Full audio extraction successful!")
            print(f"   Audio file: {os.path.basename(audio_path)}")
            print(f"   Size: {file_size:.2f} MB")
            
            # Test audio segment extraction (first 5 seconds)
            print(f"\n✂️ Extracting Audio Segment (0-5 seconds)...")
            segment_success, segment_path, segment_error = extractor.extract_audio_segment(
                video_file, 0, 5
            )
            
            if segment_success and segment_path:
                segment_size = os.path.getsize(segment_path) / (1024 * 1024)
                print(f"✅ Segment extraction successful!")
                print(f"   Segment file: {os.path.basename(segment_path)}")
                print(f"   Size: {segment_size:.2f} MB")
                
                # Clean up
                extractor.cleanup_temp_files([audio_path, segment_path])
            else:
                print(f"❌ Segment extraction failed: {segment_error}")
        else:
            print(f"❌ Full audio extraction failed: {error}")
            return False
    else:
        print("⚠️ No test video file found (test_video.mp4)")
        print("📝 Creating a simple test...")
        
        # Create a simple test video with FFmpeg if available
        try:
            import subprocess
            test_cmd = [
                'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=1',
                '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5',
                '-c:v', 'libx264', '-c:a', 'aac', '-shortest', 'demo_test.mp4', '-y'
            ]
            
            print("🎬 Creating test video with FFmpeg...")
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists('demo_test.mp4'):
                print("✅ Test video created: demo_test.mp4")
                
                # Test extraction
                success, audio_path, error = extractor.extract_audio('demo_test.mp4')
                if success:
                    file_size = os.path.getsize(audio_path) / (1024 * 1024)
                    print(f"✅ Audio extraction from generated video successful!")
                    print(f"   Size: {file_size:.2f} MB")
                    
                    # Clean up
                    extractor.cleanup_temp_files([audio_path])
                    os.remove('demo_test.mp4')
                else:
                    print(f"❌ Extraction from generated video failed: {error}")
                    
            else:
                print("❌ Could not create test video")
                return False
                
        except Exception as e:
            print(f"❌ Test video creation failed: {e}")
            return False
    
    print("\n🎉 FFmpeg Audio Extraction Demo Complete!")
    return True

if __name__ == "__main__":
    demo_ffmpeg_extraction()