import time
import os
import sys
from pathlib import Path

# Test text to convert to speech
TEST_TEXT = """You know, you know where you are with
You know where you are with
Floor collapses, floating
Bouncing back
And one day, I am gonna grow wings"""

def main():
    """Main function to prevent script restart issues"""
    
    # Force line buffering to prevent output issues
    sys.stdout.reconfigure(line_buffering=True)
    
    print("="*90, flush=True)
    print("=== TEXT-TO-SPEECH SYSTEMS COMPARISON ===", flush=True)
    print("="*90, flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)
    print(f"Starting at: {time.strftime('%H:%M:%S')}", flush=True)
    print(f"Test text: {TEST_TEXT[:50]}...\n", flush=True)
    
    # Create output directory
    output_dir = Path("tts_output")
    output_dir.mkdir(exist_ok=True)
    
    # Storage for results
    results = []
    
    # ==========================================
    # 1. GTTS (Google Text-to-Speech)
    # ==========================================
    print("--- 1. GTTS (Google Text-to-Speech) ---", flush=True)
    try:
        from gtts import gTTS
        
        start_time = time.time()
        
        # Generate speech
        output_file = output_dir / "gtts_output.mp3"
        tts = gTTS(text=TEST_TEXT, lang='en', slow=False)
        tts.save(str(output_file))
        
        elapsed_time = time.time() - start_time
        file_size = os.path.getsize(output_file) / 1024  # KB
        
        results.append({
            'name': 'gTTS',
            'time': elapsed_time,
            'file_size': file_size,
            'file_path': str(output_file),
            'quality': 'Good',
            'online': 'Yes',
            'voices': 'Limited',
            'naturalness': 'Natural'
        })
        
        print(f"✓ Time: {elapsed_time:.3f}s", flush=True)
        print(f"✓ File size: {file_size:.2f} KB", flush=True)
        print(f"✓ Output: {output_file}", flush=True)
        print(f"✓ Requires Internet: Yes\n", flush=True)
        
    except ImportError:
        print("⚠ gTTS not installed. Install with: pip install gtts\n", flush=True)
    except Exception as e:
        print(f"✗ Error: {e}\n", flush=True)
    
    # ==========================================
    # 2. PYTTSX3 (Offline TTS)
    # ==========================================
    print("--- 2. PYTTSX3 (Offline TTS) ---", flush=True)
    try:
        import pyttsx3
        
        start_time = time.time()
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # Optional: Configure voice properties
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Get available voices
        voices = engine.getProperty('voices')
        # Use first English voice if available
        for voice in voices:
            if 'english' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Generate speech
        output_file = output_dir / "pyttsx3_output.mp3"
        engine.save_to_file(TEST_TEXT, str(output_file))
        engine.runAndWait()
        
        elapsed_time = time.time() - start_time
        
        # Check if file was created
        if output_file.exists():
            file_size = os.path.getsize(output_file) / 1024  # KB
        else:
            # Try WAV format instead
            output_file = output_dir / "pyttsx3_output.wav"
            engine.save_to_file(TEST_TEXT, str(output_file))
            engine.runAndWait()
            file_size = os.path.getsize(output_file) / 1024 if output_file.exists() else 0
        
        results.append({
            'name': 'pyttsx3',
            'time': elapsed_time,
            'file_size': file_size,
            'file_path': str(output_file),
            'quality': 'Basic',
            'online': 'No',
            'voices': f'{len(voices)} system voices',
            'naturalness': 'Robotic'
        })
        
        print(f"✓ Time: {elapsed_time:.3f}s", flush=True)
        print(f"✓ File size: {file_size:.2f} KB", flush=True)
        print(f"✓ Output: {output_file}", flush=True)
        print(f"✓ Available voices: {len(voices)}", flush=True)
        print(f"✓ Requires Internet: No\n", flush=True)
        
    except ImportError:
        print("⚠ pyttsx3 not installed. Install with: pip install pyttsx3\n", flush=True)
    except Exception as e:
        print(f"✗ Error: {e}\n", flush=True)
    
    
    # ==========================================
    # 3. EDGE-TTS (Microsoft Edge)
    # ==========================================
    print("--- 3. EDGE-TTS (Microsoft Edge) ---", flush=True)
    try:
        import edge_tts
        import asyncio
        
        async def generate_edge_tts():
            output_file = output_dir / "edge_tts_output.mp3"
            
            # Use Microsoft Edge TTS
            communicate = edge_tts.Communicate(TEST_TEXT, "en-US-AriaNeural")
            await communicate.save(str(output_file))
            
            return output_file
        
        start_time = time.time()
        
        # Run async function
        output_file = asyncio.run(generate_edge_tts())
        
        elapsed_time = time.time() - start_time
        file_size = os.path.getsize(output_file) / 1024  # KB
        
        results.append({
            'name': 'Edge-TTS',
            'time': elapsed_time,
            'file_size': file_size,
            'file_path': str(output_file),
            'quality': 'Excellent',
            'online': 'Yes',
            'voices': '200+ voices',
            'naturalness': 'Very Natural'
        })
        
        print(f"✓ Time: {elapsed_time:.3f}s", flush=True)
        print(f"✓ File size: {file_size:.2f} KB", flush=True)
        print(f"✓ Output: {output_file}", flush=True)
        print(f"✓ Requires Internet: Yes\n", flush=True)
        
    except ImportError:
        print("⚠ Edge-TTS not installed. Install with: pip install edge-tts\n", flush=True)
    except Exception as e:
        print(f"✗ Error: {e}\n", flush=True)
    
    # ==========================================
    # COMPARISON SUMMARY
    # ==========================================
    print("\n" + "="*90, flush=True)
    print("PERFORMANCE COMPARISON SUMMARY", flush=True)
    print("="*90, flush=True)
    
    if results:
        # Sort by speed (ascending)
        results_sorted = sorted(results, key=lambda x: x['time'])
        
        print(f"\n{'TTS System':<15} {'Time (s)':<12} {'Size (KB)':<12} {'Quality':<12} {'Online':<10} {'Naturalness':<15}", flush=True)
        print("-" * 90, flush=True)
        
        for result in results:
            print(f"{result['name']:<15} {result['time']:<12.3f} {result['file_size']:<12.2f} "
                  f"{result['quality']:<12} {result['online']:<10} {result['naturalness']:<15}", flush=True)
        
        print("\n" + "="*90, flush=True)
        print("RANKINGS", flush=True)
        print("="*90, flush=True)
        
        print("\n⚡ FASTEST:", flush=True)
        fastest = results_sorted[0]
        print(f"   {fastest['name']} - Time: {fastest['time']:.3f}s", flush=True)
        
        print("\n💾 SMALLEST FILE:", flush=True)
        smallest = min(results, key=lambda x: x['file_size'])
        print(f"   {smallest['name']} - Size: {smallest['file_size']:.2f} KB", flush=True)
        
        print("\n🌐 OFFLINE SYSTEMS:", flush=True)
        offline = [r for r in results if r['online'] == 'No']
        if offline:
            for r in offline:
                print(f"   • {r['name']}", flush=True)
        else:
            print("   None available", flush=True)
        
        print("\n🎤 HIGH QUALITY SYSTEMS:", flush=True)
        high_quality = [r for r in results if r['quality'] in ['Excellent', 'Good']]
        for r in high_quality:
            print(f"   • {r['name']} - {r['naturalness']}", flush=True)
        
        print("\n📊 KEY METRICS:", flush=True)
        print("   • Time: Speed to generate audio", flush=True)
        print("   • Size: Audio file size in KB", flush=True)
        print("   • Quality: Audio clarity and bitrate", flush=True)
        print("   • Online: Requires internet connection", flush=True)
        print("   • Naturalness: How human-like the voice sounds", flush=True)
        
        # Find best overall (balance of quality and speed)
        excellent = [r for r in results if r['quality'] == 'Excellent']
        if excellent:
            best_overall = min(excellent, key=lambda x: x['time'])
            print(f"   Best overall (quality + speed): Use {best_overall['name']}", flush=True)
        
    else:
        print("No TTS systems were successfully tested.", flush=True)
    
    print("="*90, flush=True)
    print(f"Completed at: {time.strftime('%H:%M:%S')}", flush=True)
    print("="*90, flush=True)


# This is critical - prevents script restart on Windows
if __name__ == '__main__':
    main()