import streamlit as st
import time
import io
from config import config
from ClarifaiUtil import ClarifaiTranscriber, is_streaming_available

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)

def main():
    """Main Streamlit application"""
    
    # Clear any stale audio references on app start
    if hasattr(st.session_state, 'converted_wav'):
        # Check if audio timestamp exists and is recent
        audio_timestamp = getattr(st.session_state, 'audio_timestamp', 0)
        audio_age = time.time() - audio_timestamp
        if audio_age > 600:  # Older than 10 minutes
            # Clear stale audio references
            if hasattr(st.session_state, 'converted_wav'):
                del st.session_state.converted_wav
            if hasattr(st.session_state, 'audio_timestamp'):
                del st.session_state.audio_timestamp
            # Optionally show a brief info message (but don't persist it)
            st.toast("🧹 Cleaned up expired audio files", icon="ℹ️")
    
    # Validate configuration
    config_errors = config.validate_config()
    if config_errors and "CLARIFAI_PAT" in config_errors:
        # Skip PAT validation here since it can be entered in the UI
        config_errors.pop("CLARIFAI_PAT")
    
    if config_errors:
        st.error("Configuration errors found:")
        for key, error in config_errors.items():
            st.error(f"- {key}: {error}")
        st.stop()
    
    st.title(f"{config.APP_ICON} {config.APP_TITLE}")
    st.markdown("Upload an audio file and transcribe it using Clarifai's speech-to-text models.")
    
    # Debug: Add option to clear session state if experiencing issues
    if st.sidebar.button("🔧 Clear All Data", help="Clear all session data if experiencing audio playback issues"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Check if PAT is configured
    if not config.CLARIFAI_PAT:
        st.error("Clarifai Personal Access Token (PAT) is not configured.")
        st.info("Please set CLARIFAI_PAT in your .env file or environment variables.")
        st.info("You can get your PAT from [Clarifai Portal](https://clarifai.com/settings/security)")
        return
    
    try:
        transcriber = ClarifaiTranscriber(config.CLARIFAI_PAT)
        
        # Model selection
        available_models = transcriber.get_available_models()
        model_options = list(available_models.keys())
        default_index = model_options.index(config.DEFAULT_MODEL) if config.DEFAULT_MODEL in model_options else 0
        
        model_name = st.sidebar.selectbox(
            "Select Model",
            options=model_options,
            index=default_index,
            help="Choose the speech-to-text model for transcription"
        )
        
        # Show model status and description
        if model_name and model_name in available_models:
            model_info = available_models[model_name]
            st.sidebar.caption(model_info.get('description', 'No description available'))
        
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
        
        # Audio Enhancement Parameters
        st.sidebar.subheader("🎵 Audio Enhancement")
        
        # High Quality Conversion Toggle
        high_quality_conversion = st.sidebar.checkbox(
            "Enable High Quality Conversion",
            value=config.HIGH_QUALITY_CONVERSION,
            help="Applies advanced audio processing for better transcription accuracy"
        )
        
        # API Format Selection
        st.sidebar.subheader("📡 API Format Control")
        api_format_options = ["original", "wav", "mp3", "flac"]
        api_format = st.sidebar.selectbox(
            "Format to Send to API",
            options=api_format_options,
            index=0,  # Default to Original
            help="Choose which audio format to send to the Clarifai API. Original format preserves user's uploaded audio without conversion."
        )
        
        # Show format info
        format_descriptions = {
            "original": "📄 No conversion - Uses uploaded format directly (Recommended)",
            "wav": "🎵 Uncompressed PCM - Best quality, larger file",
            "mp3": "🎶 Compressed - Good quality, smaller file", 
            "flac": "🎼 Lossless compression - High quality, medium file"
        }
        st.sidebar.caption(format_descriptions[api_format])
        
        # Show enhancement details when enabled
        if high_quality_conversion:
            st.sidebar.markdown("**Quality Enhancements:**")
            
            # Sample Rate Selection
            sample_rate_options = [8000, 16000, 22050, 44100, 48000]
            sample_rate_index = sample_rate_options.index(config.TARGET_SAMPLE_RATE) if config.TARGET_SAMPLE_RATE in sample_rate_options else 1
            
            target_sample_rate = st.sidebar.selectbox(
                "Sample Rate (Hz)",
                options=sample_rate_options,
                index=sample_rate_index,
                help="Audio sample rate. 16kHz is optimal for speech recognition"
            )
            
            # Audio Processing Options
            normalize_audio = st.sidebar.checkbox(
                "Audio Normalization",
                value=config.NORMALIZE_AUDIO,
                help="Normalize audio levels for consistent volume"
            )
            
            trim_silence = st.sidebar.checkbox(
                "Trim Silence",
                value=config.TRIM_SILENCE,
                help="Remove silence from beginning and end of audio"
            )
            
            # Mono Conversion (always enabled for ASR)
            st.sidebar.checkbox(
                "Convert to Mono",
                value=True,
                disabled=True,
                help="Converts stereo to mono (always enabled for optimal ASR performance)"
            )
            
            # Advanced Audio Processing Options
            st.sidebar.subheader("🔧 Advanced Processing")
            
            # Audio Enhancement Options
            advanced_col1, advanced_col2 = st.sidebar.columns(2)
            
            with advanced_col1:
                noise_reduce = st.checkbox(
                    "Noise Reduction",
                    value=False,
                    help="Apply basic noise reduction (high-pass filter)"
                )
                
            with advanced_col2:
                gain_db = st.slider(
                    "Gain (dB)",
                    min_value=-20.0,
                    max_value=20.0,
                    value=0.0,
                    step=1.0,
                    help="Adjust audio volume (+/- dB)"
                )
            
            # Quality Preview
            st.sidebar.markdown("**Expected Output:**")
            st.sidebar.caption(f"📊 {target_sample_rate}Hz, Mono, 16-bit")
            
            # Processing Preview
            enhancements = []
            if normalize_audio:
                enhancements.append("Normalized")
            if trim_silence:
                enhancements.append("Silence trimmed")
            if noise_reduce:
                enhancements.append("Noise reduced")
            if gain_db != 0:
                enhancements.append(f"Gain: {gain_db:+.0f}dB")
            
            if enhancements:
                st.sidebar.caption(f"🎛️ Processing: {', '.join(enhancements)}")
            
            # File Size Estimation
            if target_sample_rate == 16000:
                size_estimate = "~39% smaller than basic conversion"
                efficiency_color = "green"
            elif target_sample_rate <= 22050:
                size_estimate = "~20-30% smaller than basic"
                efficiency_color = "blue"
            else:
                size_estimate = "Larger file size, higher quality"
                efficiency_color = "orange"
            
            st.sidebar.markdown(f"📦 Size: :{efficiency_color}[{size_estimate}]")
        else:
            # Set defaults when high quality is disabled
            target_sample_rate = config.TARGET_SAMPLE_RATE
            normalize_audio = False
            trim_silence = False
            noise_reduce = False
            gain_db = 0.0
            st.sidebar.caption("💡 Enable for better transcription accuracy")
        
        # Streaming Configuration
        st.sidebar.subheader("🌊 Streaming Mode")
        
        # Check if streaming is available
        from ClarifaiUtil import is_streaming_available
        
        if is_streaming_available():
            enable_streaming = st.sidebar.checkbox(
                "Enable Streaming Transcription",
                value=False,
                help="Process audio in real-time chunks for faster initial results"
            )
            
            if enable_streaming:
                # Streaming parameters
                st.sidebar.markdown("**Streaming Settings:**")
                
                chunk_duration = st.sidebar.selectbox(
                    "Chunk Duration",
                    options=[2000, 3000, 5000, 8000, 10000],
                    index=2,  # Default to 5000ms
                    help="Audio chunk size in milliseconds. Smaller chunks = faster response, larger chunks = better accuracy"
                )
                
                # Streaming quality info
                chunk_seconds = chunk_duration / 1000
                st.sidebar.caption(f"📊 {chunk_seconds}s chunks")
                
                # Streaming mode options
                streaming_mode = st.sidebar.selectbox(
                    "Streaming Mode",
                    options=["Real-time Display", "Progressive Chunks", "Batch Streaming"],
                    index=0,
                    help="Real-time: Live text updates, Progressive: Chunk-by-chunk results, Batch: All chunks processed"
                )
                
                # Show streaming benefits
                st.sidebar.success("✅ Faster initial results")
                st.sidebar.info("📺 Real-time text display")
                
                # Language override for streaming
                streaming_language = st.sidebar.selectbox(
                    "Language (Optional)",
                    options=[None, "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                    index=0,
                    help="Specify language for better streaming accuracy (leave as None for auto-detection)"
                )
            else:
                # Default values when streaming is disabled
                chunk_duration = 5000
                streaming_mode = "Real-time Display"
                streaming_language = None
        else:
            st.sidebar.warning("⚠️ Streaming requires OpenAI package")
            st.sidebar.caption("Install: pip install openai>=1.3.0")
            enable_streaming = False
            chunk_duration = 5000
            streaming_mode = "Real-time Display"  
            streaming_language = None
        
        # Processing mode selection
        st.subheader("🎚️ Processing Mode")
        processing_mode = st.radio(
            "Choose processing mode:",
            options=["Single File", "Batch Processing"],
            horizontal=True,
            help="Single File: Process one audio file at a time. Batch Processing: Upload and process multiple files simultaneously."
        )
        
        if processing_mode == "Single File":
            # Main interface
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.header("Upload Audio File")
            
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=config.SUPPORTED_AUDIO_FORMATS,
                help=f"Supported formats: {', '.join(config.SUPPORTED_AUDIO_FORMATS).upper()} (max {config.MAX_FILE_SIZE_MB}MB)"
            )
            
            if uploaded_file is not None:
                # Check file size
                file_size_mb = uploaded_file.size / (1024 * 1024)
                if file_size_mb > config.MAX_FILE_SIZE_MB:
                    st.error(f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({config.MAX_FILE_SIZE_MB}MB)")
                    return
                
                st.audio(uploaded_file, format='audio/wav')
                
                # File info
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File size:** {uploaded_file.size / 1024:.1f} KB ({file_size_mb:.2f} MB)")
                
                if file_size_mb > config.MAX_FILE_SIZE_MB * 0.8:  # Warning at 80% of limit
                    st.warning(f"Large file detected. Processing may take longer.")
                
                # Audio Quality Analysis
                if st.button("🔍 Analyze Audio Quality"):
                    uploaded_file.seek(0)
                    audio_bytes = uploaded_file.read()
                    
                    with st.spinner("Analyzing audio quality..."):
                        audio_analysis = transcriber.analyze_audio_quality(audio_bytes)
                        
                        if "error" not in audio_analysis:
                            st.session_state.audio_analysis = audio_analysis
                        else:
                            st.error(f"Audio analysis failed: {audio_analysis['error']}")
                
                # Show audio analysis if available
                if hasattr(st.session_state, 'audio_analysis') and st.session_state.audio_analysis:
                    analysis = st.session_state.audio_analysis
                    
                    st.subheader("📊 Audio Quality Analysis")
                    
                    # Quality metrics in columns
                    qual_col1, qual_col2, qual_col3, qual_col4 = st.columns(4)
                    
                    with qual_col1:
                        st.metric("Duration", f"{analysis['duration_seconds']:.1f}s")
                    with qual_col2:
                        st.metric("Sample Rate", f"{analysis['sample_rate']:,}Hz")
                    with qual_col3:
                        st.metric("Channels", analysis['channels'])
                    with qual_col4:
                        st.metric("Bit Depth", f"{analysis['bit_depth']}-bit")
                    
                    # Overall quality
                    quality_color = analysis['quality_color']
                    st.markdown(f"**Overall Quality:** :{quality_color}[{analysis['overall_quality']} ({analysis['quality_score']}/100)]")
                    
                    # Recommendations
                    if analysis['recommendations']:
                        with st.expander("💡 Quality Recommendations", expanded=True):
                            for rec in analysis['recommendations']:
                                st.write(f"• {rec}")
                
                # Transcribe button - change text based on streaming mode
                transcribe_button_text = "� Stream Transcription" if enable_streaming else "�🎯 Transcribe Audio"
                
                if st.button(transcribe_button_text, type="primary"):
                    # Read audio bytes
                    uploaded_file.seek(0)  # Reset file pointer to beginning
                    audio_bytes = uploaded_file.read()
                    
                    if not audio_bytes:
                        st.error("No audio data found. Please try uploading the file again.")
                        return
                    
                    # Choose transcription method based on streaming mode
                    if enable_streaming and is_streaming_available():
                        # Streaming transcription
                        try:
                            from ClarifaiUtil import create_streaming_transcriber
                            
                            streaming_transcriber = create_streaming_transcriber(config.CLARIFAI_PAT)
                            
                            # Create containers for real-time updates
                            st.info(f"🌊 Starting streaming transcription with {model_name}")
                            st.info(f"📊 Chunk size: {chunk_duration/1000:.1f}s | Mode: {streaming_mode}")
                            
                            # Real-time display containers
                            if streaming_mode == "Real-time Display":
                                current_text_container = st.empty()
                                progress_container = st.empty()
                                chunk_info_container = st.empty()
                            
                            # Start streaming transcription
                            start_time = time.time()
                            streaming_results = []
                            current_text = ""
                            
                            # Progress callback for real-time updates
                            def update_progress(result):
                                nonlocal current_text, streaming_results
                                streaming_results.append(result)
                                
                                if streaming_mode == "Real-time Display" and result.get("text"):
                                    current_text = result.get("cumulative_text", "")
                                    
                                    # Update containers
                                    current_text_container.text_area(
                                        "🌊 Live Transcription", 
                                        value=current_text,
                                        height=100,
                                        key=f"live_text_{len(streaming_results)}"
                                    )
                                    
                                    chunk_idx = result.get("chunk_index", 0)
                                    processing_time = result.get("processing_time", 0)
                                    
                                    progress_container.info(
                                        f"📊 Chunk {chunk_idx + 1} • "
                                        f"Processed: {processing_time:.2f}s • "
                                        f"Characters: {len(current_text)}"
                                    )
                            
                            # Execute streaming transcription with quality settings
                            final_result = streaming_transcriber.transcribe_streaming_realtime(
                                audio_bytes,
                                model_name=model_name,
                                progress_callback=update_progress if streaming_mode == "Real-time Display" else None,
                                chunk_duration_ms=chunk_duration,
                                language=streaming_language,
                                enable_audio_analysis=True,  # Always enable for streaming insights
                                high_quality_conversion=high_quality_conversion,
                                target_sample_rate=target_sample_rate
                            )
                            
                            total_time = time.time() - start_time
                            
                            # Store streaming results
                            if final_result and final_result.get("text"):
                                st.session_state.transcription = final_result["text"]
                                st.session_state.model_used = model_name
                                st.session_state.original_filename = uploaded_file.name
                                st.session_state.api_duration = total_time
                                st.session_state.streaming_results = streaming_results
                                st.session_state.streaming_mode = streaming_mode
                                st.session_state.chunk_duration = chunk_duration
                                st.session_state.is_streaming = True
                                st.session_state.audio_timestamp = time.time()
                                
                                # Success message with streaming stats
                                total_chunks = final_result.get("total_chunks", 0)
                                st.success(
                                    f"🌊 Streaming completed! "
                                    f"Total time: {total_time:.2f}s • "
                                    f"Chunks: {total_chunks} • "
                                    f"Avg per chunk: {total_time/max(total_chunks, 1):.2f}s"
                                )
                            else:
                                st.error("Streaming transcription returned empty result.")
                                
                        except ImportError:
                            st.error("⚠️ Streaming requires OpenAI package. Install with: pip install openai>=1.3.0")
                        except Exception as e:
                            st.error(f"Streaming transcription failed: {str(e)}")
                    
                    else:
                        # Regular transcription
                        with st.spinner(f"Transcribing audio using {model_name}..."):
                            try:
                                # Start timing the Clarifai API call
                                start_time = time.time()
                                
                                transcription, processed_audio, audio_analysis = transcriber.transcribe_with_format_control(
                                    audio_bytes, 
                                    model_name, 
                                    temperature, 
                                    max_tokens,
                                    api_format=api_format,
                                    high_quality_conversion=high_quality_conversion,
                                    target_sample_rate=target_sample_rate,
                                    normalize_audio=normalize_audio,
                                    trim_silence=trim_silence,
                                    noise_reduce=noise_reduce,
                                    gain_db=gain_db
                                )
                                
                                # Calculate API call duration
                                end_time = time.time()
                                api_duration = end_time - start_time
                                
                                # Store result in session state
                                if transcription:
                                    st.session_state.transcription = transcription
                                    st.session_state.model_used = model_name
                                    st.session_state.converted_wav = processed_audio  # Store processed audio
                                    st.session_state.original_filename = uploaded_file.name
                                    st.session_state.api_duration = api_duration  # Store API timing
                                    st.session_state.api_format = api_format  # Store API format used
                                    st.session_state.audio_analysis = audio_analysis  # Store audio analysis
                                    st.session_state.is_streaming = False
                                    st.session_state.audio_timestamp = time.time()  # Track when audio was created
                                    st.success(f"Transcription completed in {api_duration:.2f} seconds using {api_format.upper()} format!")
                                else:
                                    st.error("Transcription returned empty result.")
                                    
                            except TypeError as e:
                                st.error(f"Data type error: {str(e)}")
                            except ValueError as e:
                                st.error(f"Data validation error: {str(e)}")
                            except Exception as e:
                                st.error(f"Transcription failed: {str(e)}")
        
            with col2:
                st.header("Transcription Result")
                
                if hasattr(st.session_state, 'transcription'):
                    # Model and format info
                    is_streaming = getattr(st.session_state, 'is_streaming', False)
                    
                    if is_streaming:
                        # Streaming results header
                        model_info_col1, model_info_col2 = st.columns([2, 1])
                        with model_info_col1:
                            st.subheader(f"🌊 Streaming Model: {st.session_state.model_used}")
                        with model_info_col2:
                            streaming_mode_used = getattr(st.session_state, 'streaming_mode', 'Real-time Display')
                            st.subheader(f"Mode: {streaming_mode_used}")
                        
                        # Streaming statistics
                        if hasattr(st.session_state, 'streaming_results'):
                            streaming_results = st.session_state.streaming_results
                            chunk_duration = getattr(st.session_state, 'chunk_duration', 5000) / 1000
                            
                            stream_col1, stream_col2, stream_col3, stream_col4 = st.columns(4)
                            
                            with stream_col1:
                                total_chunks = len([r for r in streaming_results if not r.get('is_final', False)])
                                st.metric("Total Chunks", total_chunks)
                            
                            with stream_col2:
                                st.metric("Chunk Size", f"{chunk_duration:.1f}s")
                            
                            with stream_col3:
                                total_time = getattr(st.session_state, 'api_duration', 0)
                                st.metric("Total Time", f"{total_time:.2f}s")
                            
                            with stream_col4:
                                avg_time = total_time / max(total_chunks, 1)
                                st.metric("Avg/Chunk", f"{avg_time:.2f}s")
                            
                            # Streaming details expander
                            with st.expander("🌊 Streaming Details", expanded=False):
                                st.markdown("**Processing Timeline:**")
                                
                                for i, result in enumerate(streaming_results):
                                    if not result.get('is_final', False):
                                        chunk_text = result.get('text', '')
                                        processing_time = result.get('processing_time', 0)
                                        
                                        if chunk_text:
                                            st.markdown(f"**Chunk {i+1}** ({processing_time:.2f}s): {chunk_text}")
                                        else:
                                            st.markdown(f"**Chunk {i+1}** ({processing_time:.2f}s): *No text*")
                    else:
                        # Regular transcription header
                        model_info_col1, model_info_col2 = st.columns([2, 1])
                        with model_info_col1:
                            st.subheader(f"Model Used: {st.session_state.model_used}")
                        with model_info_col2:
                            api_format_used = getattr(st.session_state, 'api_format', 'original')
                            st.subheader(f"Format: {api_format_used.upper()}")
                
                    # Show audio analysis if available
                    if hasattr(st.session_state, 'audio_analysis') and st.session_state.audio_analysis and "error" not in st.session_state.audio_analysis:
                        analysis = st.session_state.audio_analysis
                        
                        with st.expander("📊 Audio Analysis Results", expanded=False):
                            analysis_col1, analysis_col2, analysis_col3, analysis_col4 = st.columns(4)
                            
                            with analysis_col1:
                                st.metric("Duration", f"{analysis['duration_seconds']:.1f}s")
                                st.metric("Sample Rate", f"{analysis['sample_rate']:,}Hz")
                            with analysis_col2:
                                st.metric("Channels", analysis['channels'])
                                st.metric("Bit Depth", f"{analysis['bit_depth']}-bit")
                            with analysis_col3:
                                st.metric("File Size", f"{analysis['file_size_kb']:.1f}KB")
                                st.metric("Bitrate", f"{analysis['bitrate']:,}bps")
                            with analysis_col4:
                                quality_color = analysis['quality_color']
                                st.markdown(f"**Quality Score:**")
                                st.markdown(f":{quality_color}[{analysis['overall_quality']} ({analysis['quality_score']}/100)]")
                
                    # Audio playback section
                    if hasattr(st.session_state, 'converted_wav') and st.session_state.converted_wav:
                        format_used = getattr(st.session_state, 'api_format', 'original').upper()
                        st.subheader(f"🎵 Processed Audio ({format_used})")
                        st.caption(f"This is the {format_used.lower()}-formatted audio that was sent to the AI model")
                    
                        # Check if audio is recent (within last 10 minutes to avoid stale references)
                        audio_age = time.time() - getattr(st.session_state, 'audio_timestamp', 0)
                        
                        if audio_age < 600:  # 10 minutes
                            # Play the converted WAV file with error handling
                            try:
                                # Create a fresh BytesIO object for audio playback
                                audio_buffer = io.BytesIO(st.session_state.converted_wav)
                                st.audio(audio_buffer, format="audio/wav")
                            except Exception as e:
                                st.warning("Audio playback temporarily unavailable. You can still download the converted WAV file below.")
                                st.caption(f"Audio playback error: {str(e)}")
                                
                                # Provide refresh option
                                if st.button("🔄 Refresh Audio", help="Reset audio player"):
                                    st.session_state.audio_timestamp = time.time()
                                    st.rerun()
                        else:
                            st.warning("Audio playback expired for performance reasons. You can still download the converted WAV file below.")
                            st.caption("Re-run transcription to enable audio playback again.")
                    
                        # Show audio info
                        original_name = getattr(st.session_state, 'original_filename', 'unknown')
                        processed_size_kb = len(st.session_state.converted_wav) / 1024
                        format_used = getattr(st.session_state, 'api_format', 'original')
                        st.caption(f"📁 Original: {original_name} → Processed {format_used.upper()}: {processed_size_kb:.1f} KB")
                        
                        # Download button for processed audio
                        processed_filename = f"processed_{original_name.rsplit('.', 1)[0] if '.' in original_name else original_name}.{format_used}"
                        
                        # Set appropriate MIME type
                        mime_types = {
                            'wav': 'audio/wav',
                            'mp3': 'audio/mpeg',
                            'flac': 'audio/flac', 
                            'ogg': 'audio/ogg'
                        }
                        mime_type = mime_types.get(format_used, 'audio/wav')
                        
                        st.download_button(
                            label=f"📥 Download Processed {format_used.upper()}",
                            data=st.session_state.converted_wav,
                            file_name=processed_filename,
                            mime=mime_type,
                            help=f"Download the processed {format_used.upper()} file used for transcription"
                        )
                        
                        st.divider()
                
                    # Display transcription in a text area for easy copying
                    st.text_area(
                        "Transcribed Text",
                        value=st.session_state.transcription,
                        height=300,
                        help="You can copy the transcribed text from here"
                    )
                    
                    # Download button and timing info in columns
                    download_col1, download_col2 = st.columns([2, 1])
                    
                    with download_col1:
                        # Download button for transcription
                        st.download_button(
                            label="📥 Download Transcription",
                            data=st.session_state.transcription,
                            file_name=f"transcription_{st.session_state.model_used.lower().replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    
                    with download_col2:
                        # Display API call timing
                        if hasattr(st.session_state, 'api_duration'):
                            st.metric(
                                label="⏱️ API Time",
                                value=f"{st.session_state.api_duration:.2f}s",
                                help="Time taken for the Clarifai API call"
                            )
                
                    # Clear button
                    if st.button("🗑️ Clear Result"):
                        # Clear all transcription-related session data
                        keys_to_clear = [
                            'transcription', 'model_used', 'converted_wav', 'original_filename',
                            'api_duration', 'audio_timestamp', 'api_format', 'audio_analysis'
                        ]
                        for key in keys_to_clear:
                            if hasattr(st.session_state, key):
                                delattr(st.session_state, key)
                        st.rerun()
                else:
                    st.info("Upload an audio file and click 'Transcribe Audio' to see results here.")
        
        if processing_mode == "Batch Processing":
            st.header("🗂️ Batch Audio Processing")
            st.markdown("Upload multiple audio files and process them all at once.")
            
            # Multiple file upload
            uploaded_files = st.file_uploader(
                "Choose multiple audio files",
                type=config.SUPPORTED_AUDIO_FORMATS,
                accept_multiple_files=True,
                help=f"Supported formats: {', '.join(config.SUPPORTED_AUDIO_FORMATS).upper()} (max {config.MAX_FILE_SIZE_MB}MB per file)"
            )
            
            if uploaded_files:
                st.write(f"📁 **{len(uploaded_files)} files selected**")
                
                # Show file list with sizes
                total_size = 0
                valid_files = []
                
                for i, file in enumerate(uploaded_files):
                    file_size_mb = file.size / (1024 * 1024)
                    total_size += file_size_mb
                    
                    batch_col1, batch_col2, batch_col3 = st.columns([3, 1, 1])
                    with batch_col1:
                        if file_size_mb <= config.MAX_FILE_SIZE_MB:
                            st.write(f"✅ {file.name}")
                            valid_files.append(file)
                        else:
                            st.write(f"❌ {file.name} (too large)")
                    with batch_col2:
                        st.write(f"{file_size_mb:.1f} MB")
                    with batch_col3:
                        if file_size_mb <= config.MAX_FILE_SIZE_MB:
                            st.write("Ready")
                        else:
                            st.write("Skip")
                
                st.write(f"📊 **Total size:** {total_size:.1f} MB | **Valid files:** {len(valid_files)}/{len(uploaded_files)}")
                
                # Batch processing controls
                if valid_files:
                    batch_ctrl_col1, batch_ctrl_col2 = st.columns([2, 1])
                    
                    with batch_ctrl_col1:
                        if st.button("🚀 Process All Files", type="primary"):
                            # Initialize batch processing
                            if 'batch_results' not in st.session_state:
                                st.session_state.batch_results = {}
                            
                            # Process each file
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, file in enumerate(valid_files):
                                status_text.text(f"Processing {file.name} ({i+1}/{len(valid_files)})...")
                                progress_bar.progress((i) / len(valid_files))
                                
                                try:
                                    # Read file
                                    file.seek(0)
                                    audio_bytes = file.read()
                                    
                                    # Perform transcription using the existing method
                                    start_time = time.time()
                                    transcription, converted_wav = transcriber.transcribe_audio_with_wav(
                                        audio_bytes, 
                                        model_name, 
                                        temperature, 
                                        max_tokens,
                                        high_quality_conversion=high_quality_conversion,
                                        target_sample_rate=target_sample_rate,
                                        normalize_audio=normalize_audio,
                                        trim_silence=trim_silence
                                    )
                                    end_time = time.time()
                                    
                                    # Store results
                                    st.session_state.batch_results[file.name] = {
                                        'transcription': transcription,
                                        'duration': end_time - start_time,
                                        'success': True,
                                        'converted_wav': converted_wav
                                    }
                                    
                                except Exception as e:
                                    st.session_state.batch_results[file.name] = {
                                        'error': str(e),
                                        'success': False
                                    }
                            
                            # Complete progress
                            progress_bar.progress(1.0)
                            status_text.text(f"Completed processing {len(valid_files)} files!")
                            
                            # Show results summary
                            successful = sum(1 for r in st.session_state.batch_results.values() if r['success'])
                            failed = len(valid_files) - successful
                            
                            st.success(f"✅ Batch processing complete: {successful} successful, {failed} failed")
                    
                    with batch_ctrl_col2:
                        if st.button("🗑️ Clear Batch"):
                            if 'batch_results' in st.session_state:
                                del st.session_state.batch_results
                            st.rerun()
                
                # Show batch results
                if 'batch_results' in st.session_state and st.session_state.batch_results:
                    st.subheader("📋 Batch Results")
                    
                    # Results summary
                    results = st.session_state.batch_results
                    successful_count = sum(1 for r in results.values() if r['success'])
                    total_time = sum(r.get('duration', 0) for r in results.values() if r['success'])
                    
                    summary_col1, summary_col2, summary_col3 = st.columns(3)
                    with summary_col1:
                        st.metric("Files Processed", len(results))
                    with summary_col2:
                        st.metric("Success Rate", f"{(successful_count/len(results)*100):.0f}%")
                    with summary_col3:
                        st.metric("Total Time", f"{total_time:.1f}s")
                    
                    # Individual results
                    for filename, result in results.items():
                        with st.expander(f"📄 {filename}", expanded=False):
                            if result['success']:
                                st.write(f"**Status:** ✅ Success ({result['duration']:.2f}s)")
                                
                                # Show transcription
                                st.text_area(
                                    "Transcription",
                                    value=result['transcription'],
                                    height=150,
                                    key=f"batch_text_{filename}"
                                )
                                
                                # Download buttons
                                result_col1, result_col2 = st.columns(2)
                                with result_col1:
                                    st.download_button(
                                        label="📥 Download Text",
                                        data=result['transcription'],
                                        file_name=f"transcription_{filename.rsplit('.', 1)[0]}.txt",
                                        mime="text/plain",
                                        key=f"batch_dl_text_{filename}"
                                    )
                                with result_col2:
                                    if result.get('converted_wav'):
                                        st.download_button(
                                            label="📥 Download WAV",
                                            data=result['converted_wav'],
                                            file_name=f"converted_{filename.rsplit('.', 1)[0]}.wav",
                                            mime="audio/wav",
                                            key=f"batch_dl_audio_{filename}"
                                        )
                            else:
                                st.write(f"**Status:** ❌ Failed")
                                st.error(f"Error: {result['error']}")
            
            else:
                st.info("📁 Select multiple audio files to start batch processing.")
    
    except Exception as e:
        st.error(f"Failed to initialize transcriber: {str(e)}")
        st.info("Please check your API key and try again.")

if __name__ == "__main__":
    main()