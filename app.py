import streamlit as st
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
            
            # Quality Preview
            st.sidebar.markdown("**Expected Output:**")
            st.sidebar.caption(f"📊 {target_sample_rate}Hz, Mono, 16-bit PCM WAV")
            
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
            st.sidebar.caption("💡 Enable for better transcription accuracy")
        
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
                
                # Transcribe button
                if st.button("🎯 Transcribe Audio", type="primary"):
                    with st.spinner(f"Transcribing audio using {model_name}..."):
                        # Read audio bytes
                        uploaded_file.seek(0)  # Reset file pointer to beginning
                        audio_bytes = uploaded_file.read()
                        
                        if not audio_bytes:
                            st.error("No audio data found. Please try uploading the file again.")
                            return
                        
                        # Perform transcription with enhanced quality settings
                        try:
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
                            
                            # Store result in session state
                            if transcription:
                                st.session_state.transcription = transcription
                                st.session_state.model_used = model_name
                                st.session_state.converted_wav = converted_wav  # Store converted WAV
                                st.session_state.original_filename = uploaded_file.name
                                st.success("Transcription completed!")
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
                st.subheader(f"Model Used: {st.session_state.model_used}")
                
                # Audio playback section
                if hasattr(st.session_state, 'converted_wav') and st.session_state.converted_wav:
                    st.subheader("🎵 Converted Audio (WAV)")
                    st.caption("This is the processed audio that was sent to the AI model")
                    
                    # Play the converted WAV file
                    st.audio(st.session_state.converted_wav, format="audio/wav")
                    
                    # Show audio info
                    original_name = getattr(st.session_state, 'original_filename', 'unknown')
                    wav_size_kb = len(st.session_state.converted_wav) / 1024
                    st.caption(f"📁 Original: {original_name} → Converted WAV: {wav_size_kb:.1f} KB")
                    
                    # Download button for converted WAV
                    wav_filename = f"converted_{original_name.rsplit('.', 1)[0] if '.' in original_name else original_name}.wav"
                    st.download_button(
                        label="📥 Download Converted WAV",
                        data=st.session_state.converted_wav,
                        file_name=wav_filename,
                        mime="audio/wav",
                        help="Download the high-quality WAV file used for transcription"
                    )
                    
                    st.divider()
                
                # Display transcription in a text area for easy copying
                st.text_area(
                    "Transcribed Text",
                    value=st.session_state.transcription,
                    height=300,
                    help="You can copy the transcribed text from here"
                )
                
                # Download button for transcription
                st.download_button(
                    label="📥 Download Transcription",
                    data=st.session_state.transcription,
                    file_name=f"transcription_{st.session_state.model_used.lower().replace(' ', '_')}.txt",
                    mime="text/plain"
                )
                
                # Clear button
                if st.button("🗑️ Clear Result"):
                    del st.session_state.transcription
                    del st.session_state.model_used
                    if hasattr(st.session_state, 'converted_wav'):
                        del st.session_state.converted_wav
                    if hasattr(st.session_state, 'original_filename'):
                        del st.session_state.original_filename
                    st.rerun()
            else:
                st.info("Upload an audio file and click 'Transcribe Audio' to see results here.")
    
    except Exception as e:
        st.error(f"Failed to initialize transcriber: {str(e)}")
        st.info("Please check your API key and try again.")

if __name__ == "__main__":
    main()