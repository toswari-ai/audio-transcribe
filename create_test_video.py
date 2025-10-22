"""
Create a simple test video for video transcription testing
This creates a basic video with text overlay for testing purposes
"""

import cv2
import numpy as np
import os

def create_test_video(output_path="test_video.mp4", duration_seconds=10, fps=30, with_audio=True):
    """
    Create a simple test video with text overlay and optional audio
    
    Args:
        output_path: Path where to save the video
        duration_seconds: Duration of the video in seconds
        fps: Frames per second
        with_audio: Whether to add a simple audio track
    """
    # Video properties
    width, height = 640, 480
    total_frames = duration_seconds * fps
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    try:
        for frame_num in range(total_frames):
            # Create a frame with changing background color
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradient background based on frame number
            color_intensity = int(255 * (frame_num / total_frames))
            frame[:, :] = [color_intensity // 3, color_intensity // 2, color_intensity]
            
            # Add text overlay
            current_second = frame_num // fps
            text = f"Test Video - Second {current_second + 1}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            color = (255, 255, 255)
            thickness = 2
            
            # Get text size for centering
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2
            
            cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)
            
            # Add additional test text
            instruction = "This is a test video for Clarifai transcription"
            instruction_size = cv2.getTextSize(instruction, font, 0.5, 1)[0]
            instruction_x = (width - instruction_size[0]) // 2
            instruction_y = text_y + 50
            
            cv2.putText(frame, instruction, (instruction_x, instruction_y), 
                       font, 0.5, (200, 200, 200), 1)
            
            # Add frame counter
            counter_text = f"Frame: {frame_num + 1}/{total_frames}"
            cv2.putText(frame, counter_text, (10, 30), font, 0.4, (255, 255, 0), 1)
            
            # Write frame to video
            out.write(frame)
        
        # Add audio track if requested
        if with_audio:
            try:
                # Create a simple audio track using moviepy
                from moviepy import AudioClip, VideoFileClip, CompositeAudioClip
                import numpy as np
                
                # Generate a simple tone (440 Hz - A note)
                def make_frame_audio(t):
                    return np.array([np.sin(440 * 2 * np.pi * t) * 0.1]).T  # Quiet tone
                
                # Create audio clip
                audio_clip = AudioClip(make_frame_audio, duration=duration_seconds)
                
                # Load the video and add audio
                video_clip = VideoFileClip(output_path)
                final_clip = video_clip.set_audio(audio_clip)
                
                # Write final video with audio
                temp_path = output_path.replace('.mp4', '_temp.mp4')
                final_clip.write_videofile(temp_path, codec='libx264', audio_codec='aac', logger=None)
                
                # Replace original with audio version
                video_clip.close()
                final_clip.close()
                audio_clip.close()
                
                os.replace(temp_path, output_path)
                print(f"✅ Added audio track to video")
                
            except Exception as e:
                print(f"⚠️ Could not add audio track: {e}. Video created without audio.")
        
        print(f"✅ Test video created successfully: {output_path}")
        print(f"Duration: {duration_seconds}s, Resolution: {width}x{height}, FPS: {fps}")
        print(f"Audio: {'Yes' if with_audio else 'No'}")
        
        # Get file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return False
        
    finally:
        out.release()

def main():
    """Create test video and provide usage instructions"""
    print("🎬 Creating Test Video for Video Transcription")
    print("=" * 50)
    
    # Create test video with audio
    success = create_test_video("test_video.mp4", duration_seconds=5, fps=30, with_audio=True)
    
    if success:
        print("\n📋 How to test video transcription:")
        print("1. Run: streamlit run app-video.py")
        print("2. Upload the generated 'test_video.mp4' file")
        print("3. Select a model (GPT-4o Mini recommended)")
        print("4. Click 'Start Video Transcription'")
        print("\n🎯 Expected results:")
        print("- Should detect text: 'Test Video - Second X'")
        print("- Should see: 'This is a test video for Clarifai transcription'")
        print("- Should describe changing background colors")
        print("- Should mention frame counter in corner")
    
    print(f"\n🔧 Test completed: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    main()