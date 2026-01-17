import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time

def record_voice(filename="my_voice.wav", duration=10, fs=44100):
    print(f"Recording for {duration} seconds...")
    print("Please speak clearly. You can read this text: 'The quick brown fox jumps over the lazy dog. I am creating a custom voice for my AI assistant.'")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    print("GO!")
    
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    
    print("Recording finished.")
    
    # Save as WAV file
    # Ensure it is int16 for compatibility
    recording_int16 = (recording * 32767).astype(np.int16)
    wav.write(filename, fs, recording_int16)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    record_voice()
