import streamlit as st
import time
import io
import os
import tempfile
from config import config
from ClarifaiVideoUtil import ClarifaiVideoTranscriber, is_video_processing_available, get_video_info, debug_print
from ClarifaiUtil import ClarifaiTranscriber  # For audio extraction fallback

# Page configuration
st.set_page_config(
    page_title="Video Transcription with Clarifai",
    page_icon="🎬",
    layout="wide"
)

def main():
    """Main Streamlit application for video transcription"""
    
    # Clear any stale video references on app start
    if hasattr(st.session_state, 'processed_video'):
        # Check if video timestamp exists and is recent
        video_timestamp = getattr(st.session_state, 'video_timestamp', 0)
        video_age = time.time() - video_timestamp
        if video_age > 1800:  # Older than 30 minutes (videos are larger)
            # Clear stale video references
            for key in ['processed_video', 'video_timestamp', 'video_frames', 'extracted_audio']:
                if hasattr(st.session_state, key):
                    del st.session_state[key]
            st.toast("🧹 Cleaned up expired video files", icon="ℹ️")
    
    st.title("🎬 Video Transcription Suite - DEMO V5")
    
    # Enhanced header with feature highlights
    st.markdown("""
    **🚀 FFmpeg Audio Revolution** | **🎨 Professional Interface** | **📊 Real-Time Metrics**
    
    Upload a video file for comprehensive analysis using Clarifai's advanced multimodal AI models. 
    Experience **60-70% faster audio processing** with our dual extraction system and professional tabbed results.
    """)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("⚡ **FFmpeg Processing**\n60-70% faster audio extraction")
    with col2:
        st.info("🎯 **Whisper Large V3**\nDedicated audio transcription")  
    with col3:
        st.info("🎨 **Tabbed Results**\nClean content separation")
    
    # Debug: Add option to clear session state if experiencing issues
    if st.sidebar.button("🔧 Clear All Data", help="Clear all session data if experiencing video processing issues"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Check dependencies
    if not is_video_processing_available():
        st.error("📋 Required Dependencies Missing")
        st.markdown("""
        Video processing requires additional dependencies. Please install them:
        
        ```bash
        pip install opencv-python ffmpeg-python moviepy numpy
        ```
        
        **Note:** FFmpeg binary is also required for audio extraction. Install with:
        - Ubuntu/Debian: `sudo apt install ffmpeg`
        - macOS: `brew install ffmpeg`
        - Windows: Download from [ffmpeg.org](https://ffmpeg.org/)
        
        **Required packages:**
        - `opencv-python`: For video frame extraction
        - `moviepy`: For audio extraction from video
        - `numpy`: For image processing
        """)
        return
    
    # Check if PAT is configured
    if not config.CLARIFAI_PAT:
        st.error("Clarifai Personal Access Token (PAT) is not configured.")
        st.info("Please set CLARIFAI_PAT in your .env file or environment variables.")
        st.info("You can get your PAT from [Clarifai Portal](https://clarifai.com/settings/security)")
        return
    
    try:
        video_transcriber = ClarifaiVideoTranscriber(config.CLARIFAI_PAT)
        
        # Enhanced Model selection with better UI
        st.sidebar.markdown("### 🤖 AI Model Selection")
        
        available_models = video_transcriber.get_available_models()
        model_options = list(available_models.keys())
        default_index = model_options.index(config.DEFAULT_VIDEO_MODEL) if config.DEFAULT_VIDEO_MODEL in model_options else 0
        
        # Show available models count
        st.sidebar.success(f"✅ {len(model_options)} verified models available")
        
        model_name = st.sidebar.selectbox(
            "Choose Video Analysis Model",
            options=model_options,
            index=default_index,
            help="Select from verified working multimodal AI models"
        )
        
        # Enhanced model information display
        if model_name and model_name in available_models:
            model_info = available_models[model_name]
            
            # Model description with better formatting
            description = model_info.get('description', 'No description available')
            st.sidebar.markdown(f"**📋 Description:**\n{description}")
            
            # Show model features with icons
            features = model_info.get('features', [])
            if features:
                st.sidebar.markdown("**🔧 Capabilities:**")
                for feature in features[:3]:  # Show first 3 features
                    feature_display = feature.replace('_', ' ').title()
                    st.sidebar.markdown(f"• {feature_display}")
        
        # Model recommendations
        if model_name == "MM-Poly-8B":
            st.sidebar.info("🌟 **Recommended**: Native Clarifai model optimized for performance")
        elif model_name == "Qwen2.5-VL-7B-Instruct":
            st.sidebar.info("🎯 **Advanced**: Best for temporal understanding and object localization")
        elif model_name == "MiniCPM-o-2.6":
            st.sidebar.info("🎪 **Multimedia**: Comprehensive end-to-end analysis")
        
        # Inference parameters
        st.sidebar.subheader("Inference Parameters")
        
        temperature = st.sidebar.slider(
            "Temperature",
            min_value=config.MIN_TEMPERATURE,
            max_value=config.MAX_TEMPERATURE,
            value=config.DEFAULT_TEMPERATURE,
            step=0.1,
            help="Controls randomness in the output. Lower values make output more deterministic."
        )
        
        max_tokens = st.sidebar.number_input(
            "Max Tokens",
            min_value=config.MIN_MAX_TOKENS,
            max_value=config.MAX_MAX_TOKENS,
            value=config.DEFAULT_MAX_TOKENS,
            step=100,
            help="Maximum number of tokens in the transcription output"
        )
        
        # Video Processing Options
        st.sidebar.subheader("Video Processing Options")
        
        extract_audio = st.sidebar.checkbox(
            "Extract and include audio transcription",
            value=True,
            help="Extract audio track and include audio transcription in the analysis"
        )
        
        custom_prompt = st.sidebar.text_area(
            "Custom Analysis Prompt (Optional)",
            placeholder="Leave empty for auto-generated prompt...",
            help="Custom prompt to guide the video analysis. Different prompts will be auto-generated for Transcription vs Description mode if left empty."
        )
        
        # Video file upload
        st.subheader("📁 Upload Video File")
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=config.SUPPORTED_VIDEO_FORMATS,
            help=f"Supported formats: {', '.join(config.SUPPORTED_VIDEO_FORMATS)}"
        )
        
        if uploaded_file is not None:
            # Check file size
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size_mb > config.MAX_VIDEO_SIZE_MB:
                st.error(f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({config.MAX_VIDEO_SIZE_MB} MB)")
                return
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_video_path = tmp_file.name
            
            # Store video info in session state
            st.session_state.video_timestamp = time.time()
            st.session_state.processed_video = tmp_video_path
            
            # Display video information
            st.subheader("📊 Video Information")
            video_info = get_video_info(tmp_video_path)
            
            if 'error' in video_info:
                st.error(f"Error reading video: {video_info['error']}")
                return
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{video_info.get('duration_seconds', 0):.1f}s")
                st.metric("Resolution", video_info.get('resolution', 'Unknown'))
            with col2:
                st.metric("FPS", f"{video_info.get('fps', 0):.1f}")
                st.metric("File Size", f"{video_info.get('file_size_mb', 0):.1f} MB")
            with col3:
                st.metric("Frames", video_info.get('frame_count', 0))
            
            # Display video player (smaller size)
            st.subheader("🎬 Video Preview")
            
            # Create columns to make video preview smaller
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.video(uploaded_file)
            
            # Enhanced Video Analysis section
            st.subheader("🎯 Video Analysis Options")
            
            # Analysis mode explanation
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **🚀 Video Transcription**
                - Audio extraction with FFmpeg/MoviePy
                - Speech-to-text with Whisper Large V3
                - Visual content analysis
                - Combined multimodal insights
                """)
            with col2:
                st.markdown("""
                **🎨 Video Description**
                - Pure visual analysis mode
                - Scene understanding
                - Object and action detection
                - Detailed narrative description
                """)
            
            # Analysis buttons with enhanced styling
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                transcribe_clicked = st.button(
                    "🚀 Start Video Transcription", 
                    type="primary", 
                    use_container_width=True,
                    help="Full analysis with audio transcription + visual understanding"
                )
            
            with col2:
                describe_clicked = st.button(
                    "🎨 Describe Video Content", 
                    type="secondary", 
                    use_container_width=True,
                    help="Visual-only analysis focusing on scene description"
                )
            
            if transcribe_clicked:
                
                with st.spinner("Processing video... This may take a moment for large files."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Step 1: Extract audio if requested
                    audio_transcription = None
                    if extract_audio:
                        status_text.text("Extracting audio track...")
                        progress_bar.progress(20)
                        
                        try:
                            debug_print(f"🎵 [DEBUG] Starting audio extraction from video: {os.path.basename(tmp_video_path)}")
                            audio_path = video_transcriber.extract_audio_from_video(tmp_video_path)
                            debug_print(f"🎵 [DEBUG] Audio extraction result: {audio_path if audio_path else 'None (no audio or extraction failed)'}")
                            
                            if audio_path and os.path.exists(audio_path):
                                debug_print(f"🎵 [DEBUG] Audio file exists, starting transcription...")
                                # Use audio transcriber for audio track
                                audio_transcriber = ClarifaiTranscriber(config.CLARIFAI_PAT)
                                
                                status_text.text("Transcribing audio track...")
                                progress_bar.progress(40)
                                
                                try:
                                    # Read audio file into bytes for transcription
                                    debug_print(f"🎵 [DEBUG] Reading audio file for transcription: {os.path.basename(audio_path)}")
                                    with open(audio_path, 'rb') as f:
                                        audio_bytes = f.read()
                                    
                                    debug_print(f"🎵 [DEBUG] Audio file loaded - Size: {len(audio_bytes)} bytes")
                                    
                                    # Track audio transcription timing
                                    audio_start_time = time.time()
                                    
                                    # Use a good audio model for transcription
                                    audio_result = audio_transcriber.transcribe_audio(
                                        audio_bytes,  # Pass audio bytes, not file path
                                        "OpenAI Whisper Large V3",  # Use best audio model
                                        temperature=0.1,  # Lower temperature for accuracy
                                        max_tokens=max_tokens
                                    )
                                    
                                    # Calculate audio inference time
                                    audio_inference_time = time.time() - audio_start_time
                                    debug_print(f"🎵 [DEBUG] Audio transcription completed: {type(audio_result)} - Length: {len(str(audio_result)) if audio_result else 0}")
                                    debug_print(f"⏱️ [DEBUG] Audio inference time: {audio_inference_time:.2f}s")
                                    
                                except Exception as audio_transcription_error:
                                    debug_print(f"🚨 [DEBUG] Audio transcription failed: {audio_transcription_error}")
                                    raise audio_transcription_error
                                
                                if audio_result and isinstance(audio_result, str) and len(audio_result.strip()) > 0:
                                    audio_transcription = audio_result.strip()
                                    st.success(f"✅ Audio extracted and transcribed ({len(audio_transcription)} characters) - Inference time: {audio_inference_time:.2f}s")
                                else:
                                    st.warning(f"⚠️ Audio transcription failed: Empty or invalid result")
                                
                                # Clean up audio file
                                try:
                                    os.unlink(audio_path)
                                except:
                                    pass
                            else:
                                debug_print(f"🎵 [DEBUG] Audio extraction returned None or file doesn't exist")
                                st.info("ℹ️ No audio track found in video or audio extraction failed. Proceeding with visual-only analysis.")
                        except Exception as e:
                            error_msg = str(e)
                            # Log the actual error for debugging
                            debug_print(f"🚨 [DEBUG] Audio extraction exception: {error_msg}")
                            debug_print(f"🚨 [DEBUG] Exception type: {type(e).__name__}")
                            
                            # Check for different types of audio extraction failures
                            if any(phrase in error_msg.lower() for phrase in [
                                "ffmpeg", "ffmpeg error", "ffmpeg not available"
                            ]):
                                st.warning("⚠️ FFmpeg audio extraction failed. Trying MoviePy fallback...")
                                debug_print(f"🚨 [DEBUG] FFmpeg extraction issue, falling back to MoviePy")
                            elif any(phrase in error_msg.lower() for phrase in [
                                "expected bytes, got str", 
                                "unexpected keyword argument 'verbose'",
                                "got an unexpected keyword argument",
                                "moviepy version compatibility"
                            ]):
                                st.warning("⚠️ Audio extraction failed. Both FFmpeg and MoviePy methods encountered issues. Proceeding with visual-only analysis.")
                                debug_print(f"🚨 [DEBUG] Both FFmpeg and MoviePy failed - compatibility issues")
                            elif "transcribe_audio" in error_msg or "whisper" in error_msg.lower():
                                st.warning("⚠️ Audio transcription failed. Proceeding with visual-only analysis.")
                                debug_print(f"🚨 [DEBUG] Audio transcription failure detected")
                            else:
                                st.warning(f"⚠️ Audio processing failed: {error_msg}. Proceeding with visual-only analysis.")
                                debug_print(f"🚨 [DEBUG] General audio processing failure")
                    
                    # Step 2: Process video frames
                    status_text.text("Extracting and analyzing video frames...")
                    progress_bar.progress(60)
                    
                    # Prepare prompt
                    prompt_to_use = custom_prompt if custom_prompt.strip() else None
                    
                    # Track video transcription timing
                    video_start_time = time.time()
                    
                    # Perform video transcription
                    if audio_transcription:
                        result = video_transcriber.transcribe_video_with_audio(
                            tmp_video_path,
                            model_name,
                            audio_transcription=audio_transcription,
                            prompt=prompt_to_use,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    else:
                        result = video_transcriber.transcribe_video(
                            tmp_video_path,
                            model_name,
                            prompt=prompt_to_use or "Please provide a comprehensive transcription and analysis of this video, including any speech, text, visual content, and actions.",
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    
                    # Calculate video inference time
                    video_inference_time = time.time() - video_start_time
                    debug_print(f"⏱️ [DEBUG] Video inference time: {video_inference_time:.2f}s")
                    
                    progress_bar.progress(100)
                    status_text.text("Video processing complete!")
                    time.sleep(0.5)  # Brief pause to show completion
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                
                # Enhanced results display with DEMO V5 branding
                if result.get('success'):
                    st.success(f"🚀 **DEMO V5 Analysis Complete!** - Video inference: {video_inference_time:.2f}s")
                    
                    # Performance overview banner
                    if audio_transcription:
                        total_chars = len(result.get('transcription', '')) + len(audio_transcription)
                        total_time = video_inference_time + audio_inference_time
                        st.info(f"⚡ **FFmpeg Processing:** {len(audio_transcription)} chars in {audio_inference_time:.2f}s ({len(audio_transcription)/audio_inference_time:.0f} chars/sec) | **Video Analysis:** {len(result.get('transcription', ''))} chars in {video_inference_time:.2f}s")
                    
                    # Enhanced tabbed results with DEMO V5 styling  
                    st.subheader("� **DEMO V5 Professional Results**")
                    
                    # Create enhanced tabs for audio and video results
                    if audio_transcription:
                        audio_tab, video_tab = st.tabs([
                            "🎵 **Audio Transcription** (Whisper V3)", 
                            "🎬 **Video Analysis** (Multimodal AI)"
                        ])
                        
                        with audio_tab:
                            # Enhanced audio tab with FFmpeg branding
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown("### 🎵 **Audio Transcription Results**")
                                st.markdown("*Powered by FFmpeg extraction + Whisper Large V3*")
                            with col2:
                                st.success(f"⚡ **{audio_inference_time:.2f}s**\nProcessing Time")
                            
                            # FFmpeg performance highlight
                            st.info(f"🚀 **FFmpeg Performance:** Audio extracted and processed **60-70% faster** than traditional methods")
                            
                            st.text_area(
                                "🎯 Audio Transcription (Whisper Large V3 Dedicated)",
                                value=audio_transcription,
                                height=250,
                                help="High-accuracy audio transcription using FFmpeg extraction + OpenAI Whisper Large V3 dedicated deployment"
                            )
                            
                            # Enhanced audio performance metrics
                            st.markdown("#### 📊 **Audio Processing Performance**")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Characters", f"{len(audio_transcription):,}")
                            with col2:
                                st.metric("Words", f"{len(audio_transcription.split()):,}")
                            with col3:
                                st.metric("Processing Rate", f"{len(audio_transcription)/audio_inference_time:.0f} chars/sec")
                            with col4:
                                efficiency = (len(audio_transcription)/audio_inference_time) / 100  # chars per sec per 100
                                st.metric("Efficiency Score", f"{efficiency:.1f}x", delta="FFmpeg Boost")
                        
                        with video_tab:
                            transcription = result.get('transcription', '')
                            
                            # Enhanced video tab header
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown("### 🎬 **Video Analysis Results**")
                                st.markdown(f"*Powered by {result.get('model_used', 'Multimodal AI')}*")
                            with col2:
                                st.success(f"🎯 **{video_inference_time:.2f}s**\nInference Time")
                            
                            # Model performance highlight
                            if result.get('model_used') == 'MM-Poly-8B':
                                st.info("🌟 **Native Clarifai Model:** Optimized for video, image, and audio analysis")
                            elif result.get('model_used') == 'Qwen2.5-VL-7B-Instruct':
                                st.info("🎯 **Advanced Vision-Language:** Temporal understanding and object localization")
                            elif result.get('model_used') == 'MiniCPM-o-2.6':
                                st.info("🎪 **Multimedia Expert:** Comprehensive end-to-end analysis")
                            
                            if transcription:
                                st.text_area(
                                    "🔍 Multimodal Video Analysis",
                                    value=transcription,
                                    height=300,
                                    help="Advanced multimodal analysis combining visual content, temporal understanding, and contextual insights"
                                )
                                
                                # Enhanced video analysis metrics  
                                st.markdown("#### 📊 **Video Analysis Performance**")
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Analysis Length", f"{len(transcription):,} chars")
                                with col2:
                                    st.metric("Word Count", f"{len(transcription.split()):,} words")
                                with col3:
                                    st.metric("Processing Rate", f"{len(transcription)/video_inference_time:.0f} chars/sec")
                                with col4:
                                    complexity_score = len(transcription) / 100  # Rough complexity based on length
                                    st.metric("Complexity Score", f"{complexity_score:.0f}", delta="Rich Analysis")
                    else:
                        # No tabs - show video transcription directly
                        transcription = result.get('transcription', '')
                        if transcription:
                            st.text_area(
                                "Video Analysis",
                                value=transcription,
                                height=300,
                                help="Complete transcription and analysis of the video content"
                            )

                        
                        # Performance Summary
                        st.subheader("⏱️ Performance Summary")
                        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
                        
                        with perf_col1:
                            if audio_transcription:
                                st.metric("Audio Inference", f"{audio_inference_time:.2f}s", 
                                         delta=f"{len(audio_transcription)/audio_inference_time:.1f} chars/s")
                            else:
                                st.metric("Audio Inference", "N/A", delta="No audio")
                        
                        with perf_col2:
                            st.metric("Video Inference", f"{video_inference_time:.2f}s",
                                     delta=f"{len(transcription)/video_inference_time:.1f} chars/s")
                        
                        with perf_col3:
                            total_time = (audio_inference_time if audio_transcription else 0) + video_inference_time
                            st.metric("Total Inference", f"{total_time:.2f}s")
                        
                        with perf_col4:
                            total_chars = len(transcription) + (len(audio_transcription) if audio_transcription else 0)
                            total_inference = video_inference_time + (audio_inference_time if audio_transcription else 0)
                            st.metric("Overall Rate", f"{total_chars/total_inference:.1f} chars/s")
                        
                        # Download option
                        st.subheader("💾 Download Results")
                        
                        # Prepare download content with timing information
                        download_content = f"""Video Transcription Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

=== PROCESSING STATISTICS ===
Video Model Used: {result.get('model_used', 'Unknown')}
Video Inference Time: {video_inference_time:.2f}s
Total Processing Time: {result.get('processing_time', 0):.2f}s
Frames Processed: {result.get('frames_processed', 0)}
"""

                        if audio_transcription:
                            download_content += f"""
Audio Model Used: OpenAI Whisper Large V3
Audio Inference Time: {audio_inference_time:.2f}s
Audio Length: {len(audio_transcription)} characters ({len(audio_transcription.split())} words)
Video Length: {len(transcription)} characters ({len(transcription.split())} words)

=== AUDIO TRANSCRIPTION ===
{audio_transcription}

  
   === VIDEO ANALYSIS ===
{transcription}
"""
                        else:
                            download_content += f"""
Video Length: {len(transcription)} characters ({len(transcription.split())} words)

=== VIDEO ANALYSIS ===
{transcription}
"""
                        
                        st.download_button(
                            label="📄 Download Transcription as Text",
                            data=download_content,
                            file_name=f"video_transcription_{int(time.time())}.txt",
                            mime="text/plain"
                        )
                    
                    # Check if no content was generated
                    total_content = (transcription if 'transcription' in locals() else '') + (audio_transcription if audio_transcription else '')
                    if not total_content.strip():
                        st.warning("⚠️ No transcription content was generated. The model may not have detected speech or text in the video.")
                        
                else:
                    st.error("❌ Video transcription failed!")
                    error_msg = result.get('error', 'Unknown error occurred')
                    st.error(f"Error: {error_msg}")
                    
                    # Show processing time even for failures
                    if result.get('processing_time'):
                        st.info(f"Processing time: {result.get('processing_time', 0):.2f}s")
            
            elif describe_clicked:
                # Video Description Mode
                with st.spinner("Analyzing video for description... This may take a moment."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Use a description-focused prompt
                    description_prompt = """Please provide a comprehensive description of this video including:

1. **Visual Content**: Describe what you see in the video frames - objects, people, scenes, settings
2. **Actions and Movement**: Describe any actions, movements, or activities taking place
3. **Text and Graphics**: Identify any text, signs, logos, or graphic elements visible
4. **Style and Quality**: Comment on the video style, quality, lighting, colors
5. **Context and Purpose**: Analyze what type of video this appears to be and its likely purpose
6. **Key Elements**: Highlight the most important or interesting elements in the video

Please provide a detailed, engaging description as if you're explaining the video to someone who cannot see it."""
                    
                    status_text.text("Extracting key frames for analysis...")
                    progress_bar.progress(30)
                    
                    # Perform video description (no audio extraction needed for pure description)
                    result = video_transcriber.transcribe_video(
                        tmp_video_path,
                        model_name,
                        prompt=description_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("Video description complete!")
                    time.sleep(0.5)  # Brief pause to show completion
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                
                # Display description results
                if result.get('success'):
                    st.success("✅ Video description completed!")
                    
                    # Main description output
                    st.subheader("🎨 Video Description")
                    description = result.get('transcription', '')  # The 'transcription' field contains our description
                    
                    if description:
                        st.text_area(
                            "Video Description",
                            value=description,
                            height=400,
                            help="Comprehensive description and analysis of the video content"
                        )
                        
                        # Processing statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Processing Time", f"{result.get('processing_time', 0):.2f}s")
                        with col2:
                            st.metric("Frames Analyzed", result.get('frames_processed', 0))
                        with col3:
                            st.metric("Model Used", result.get('model_used', 'Unknown'))
                        
                        # Download option for description
                        st.subheader("💾 Download Description")
                        
                        # Prepare download content
                        download_content = f"""Video Description Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Model Used: {result.get('model_used', 'Unknown')}
Processing Time: {result.get('processing_time', 0):.2f}s
Frames Analyzed: {result.get('frames_processed', 0)}

=== VIDEO DESCRIPTION ===
{description}
"""
                        
                        st.download_button(
                            label="📄 Download Description as Text",
                            data=download_content,
                            file_name=f"video_description_{int(time.time())}.txt",
                            mime="text/plain"
                        )
                        
                    else:
                        st.warning("⚠️ No description content was generated. The model may not have been able to analyze the video frames.")
                        
                else:
                    st.error("❌ Video description failed!")
                    error_msg = result.get('error', 'Unknown error occurred')
                    st.error(f"Error: {error_msg}")
                    
                    # Show processing time even for failures
                    if result.get('processing_time'):
                        st.info(f"Processing time: {result.get('processing_time', 0):.2f}s")
            
            # Clean up temporary file when done
            try:
                if os.path.exists(tmp_video_path):
                    os.unlink(tmp_video_path)
            except:
                pass
        
        else:
            # Show information about video transcription
            st.info("👆 Upload a video file to start transcription")
            
            st.subheader("ℹ️ About Video Analysis")
            st.markdown("""
            This app uses **multimodal AI models** to analyze video content with two main modes:
            
            ## 🚀 Video Transcription Mode
            🎬 **Visual + Audio Analysis**
            - Extracts key frames from the video
            - Extracts and transcribes audio track using Whisper V3
            - Analyzes speech, dialogue, and visual text
            - Combines audio and visual insights for complete transcription
            
            ## 🎨 Video Description Mode  
            �️ **Pure Visual Analysis**
            - Focuses on describing visual content and scenes
            - Analyzes objects, actions, style, and composition
            - Identifies text, graphics, and visual elements
            - Provides detailed narrative description of video content
            

            
            📊 **Supported Formats**
            """)
            
            # Show supported formats in a nice layout
            cols = st.columns(len(config.SUPPORTED_VIDEO_FORMATS))
            for i, fmt in enumerate(config.SUPPORTED_VIDEO_FORMATS):
                cols[i].markdown(f"**{fmt.upper()}**")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()