import streamlit as st
import time
import io
from config import config
from ClarifaiUtil import ClarifaiTranscriber

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
        api_format_options = ["wav", "mp3", "flac", "original"]
        api_format = st.sidebar.selectbox(
            "Format to Send to API",
            options=api_format_options,
            index=0,  # Default to WAV
            help="Choose which audio format to send to the Clarifai API. WAV is recommended for best results."
        )
        
        # Show format info
        format_descriptions = {
            "wav": "🎵 Uncompressed PCM - Best quality, larger file",
            "mp3": "🎶 Compressed - Good quality, smaller file", 
            "flac": "🎼 Lossless compression - High quality, medium file",
            "original": "📄 No conversion - Uses uploaded format directly"
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
                
                # Transcribe button
                if st.button("🎯 Transcribe Audio", type="primary"):
                    with st.spinner(f"Transcribing audio using {model_name}..."):
                        # Read audio bytes
                        uploaded_file.seek(0)  # Reset file pointer to beginning
                        audio_bytes = uploaded_file.read()
                        
                        if not audio_bytes:
                            st.error("No audio data found. Please try uploading the file again.")
                            return
                        
                        # Perform transcription with advanced format control
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
                    model_info_col1, model_info_col2 = st.columns([2, 1])
                    with model_info_col1:
                        st.subheader(f"Model Used: {st.session_state.model_used}")
                    with model_info_col2:
                        api_format_used = getattr(st.session_state, 'api_format', 'wav')
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
                        format_used = getattr(st.session_state, 'api_format', 'wav').upper()
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
                        format_used = getattr(st.session_state, 'api_format', 'wav')
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