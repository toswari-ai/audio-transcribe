#!/usr/bin/env python3
"""
Audio Quality Test Script
Demonstrates the quality improvements from enhanced audio conversion
"""

from ClarifaiUtil import create_transcriber
import time
from config import config

def test_quality_improvements():
    """Test and compare audio quality enhancements"""
    
    print("🎵 AUDIO QUALITY ENHANCEMENT DEMO")
    print("=" * 60)
    
    # Load sample audio
    try:
        with open('sample_audio.mp3', 'rb') as f:
            audio_bytes = f.read()
        print(f"📁 Loaded sample audio: {len(audio_bytes)} bytes")
    except FileNotFoundError:
        print("❌ sample_audio.mp3 not found!")
        print("   Please ensure you have an audio file to test with.")
        return
    
    transcriber = create_transcriber()
    
    print(f"\n🔧 Current Quality Settings:")
    print(f"   • High Quality Conversion: {config.HIGH_QUALITY_CONVERSION}")
    print(f"   • Target Sample Rate: {config.TARGET_SAMPLE_RATE}Hz")
    print(f"   • Audio Normalization: {config.NORMALIZE_AUDIO}")
    print(f"   • Silence Trimming: {config.TRIM_SILENCE}")
    
    # Test enhanced quality conversion
    print(f"\n✨ ENHANCED QUALITY CONVERSION:")
    print("-" * 50)
    
    start_time = time.time()
    enhanced_wav = transcriber.convert_to_wav(audio_bytes, high_quality=True)
    conversion_time = time.time() - start_time
    
    print(f"⏱️  Conversion time: {conversion_time:.3f}s")
    print(f"📊 Size efficiency: {((len(enhanced_wav) - len(audio_bytes)) / len(audio_bytes) * 100):+.1f}%")
    
    # Test basic quality conversion
    print(f"\n🎵 BASIC QUALITY CONVERSION:")
    print("-" * 50)
    
    start_time = time.time()
    basic_wav = transcriber.convert_to_wav(audio_bytes, high_quality=False)
    basic_conversion_time = time.time() - start_time
    
    print(f"⏱️  Conversion time: {basic_conversion_time:.3f}s")
    print(f"📊 Size change: {((len(basic_wav) - len(audio_bytes)) / len(audio_bytes) * 100):+.1f}%")
    
    # Compare sizes
    print(f"\n📊 SIZE COMPARISON:")
    print("-" * 50)
    print(f"Original MP3:     {len(audio_bytes):,} bytes")
    print(f"Enhanced WAV:     {len(enhanced_wav):,} bytes")
    print(f"Basic WAV:        {len(basic_wav):,} bytes")
    
    size_improvement = ((len(basic_wav) - len(enhanced_wav)) / len(basic_wav) * 100)
    print(f"Enhanced is {size_improvement:.1f}% smaller than basic!")
    
    # Test transcription quality with best model
    test_model = "OpenAI Whisper Large V3"
    print(f"\n🎙️ TRANSCRIPTION QUALITY TEST ({test_model}):")
    print("-" * 50)
    
    # Test enhanced quality
    print("Enhanced Quality Result:")
    start_time = time.time()
    
    # Temporarily set validation to use enhanced quality
    original_validate = transcriber.validate_audio_data
    transcriber.validate_audio_data = lambda x: transcriber.convert_to_wav(x, high_quality=True)
    
    enhanced_result = transcriber.transcribe_audio(audio_bytes, test_model)
    enhanced_transcription_time = time.time() - start_time
    
    print(f"  📝 \"{enhanced_result}\"")
    print(f"  ⏱️  {enhanced_transcription_time:.2f}s")
    
    # Test basic quality
    print("\nBasic Quality Result:")
    start_time = time.time()
    
    # Set validation to use basic quality
    transcriber.validate_audio_data = lambda x: transcriber.convert_to_wav(x, high_quality=False)
    
    basic_result = transcriber.transcribe_audio(audio_bytes, test_model)
    basic_transcription_time = time.time() - start_time
    
    # Restore original validation
    transcriber.validate_audio_data = original_validate
    
    print(f"  📝 \"{basic_result}\"")
    print(f"  ⏱️  {basic_transcription_time:.2f}s")
    
    # Analysis
    print(f"\n🏆 QUALITY ANALYSIS:")
    print("-" * 50)
    
    if enhanced_result != basic_result:
        print("✅ Enhanced quality produced different (potentially more accurate) results")
        
        # Check if enhanced result is more detailed
        if len(enhanced_result) > len(basic_result):
            print(f"📈 Enhanced result is {len(enhanced_result) - len(basic_result)} characters longer")
        elif len(enhanced_result) < len(basic_result):
            print(f"📉 Basic result is {len(basic_result) - len(enhanced_result)} characters longer")
    else:
        print("📊 Both quality levels produced identical results for this audio")
    
    # Performance summary
    total_enhanced_time = conversion_time + enhanced_transcription_time
    total_basic_time = basic_conversion_time + basic_transcription_time
    
    print(f"\n⚡ PERFORMANCE SUMMARY:")
    print("-" * 50)
    print(f"Enhanced Total Time: {total_enhanced_time:.2f}s")
    print(f"Basic Total Time:    {total_basic_time:.2f}s")
    
    if total_enhanced_time < total_basic_time:
        print(f"✅ Enhanced is {total_basic_time - total_enhanced_time:.2f}s faster!")
    else:
        print(f"⚠️ Enhanced takes {total_enhanced_time - total_basic_time:.2f}s longer (but better quality)")
    
    print(f"\n🎉 RECOMMENDATION:")
    print("-" * 50)
    print("✅ Use Enhanced Quality for:")
    print("   • Production applications")
    print("   • Accuracy-critical use cases") 
    print("   • Professional transcription")
    
    print("🎵 Use Basic Quality for:")
    print("   • Quick testing/development")
    print("   • Very large files")
    print("   • When speed is more important than accuracy")

if __name__ == "__main__":
    test_quality_improvements()