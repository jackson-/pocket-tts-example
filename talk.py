import sys
import os
import logging
import torch
import numpy as np
import sounddevice as sd
import queue
import threading
from pocket_tts.models.tts_model import TTSModel
from pocket_tts.default_parameters import (
    DEFAULT_VARIANT,
    DEFAULT_TEMPERATURE,
    DEFAULT_LSD_DECODE_STEPS,
    DEFAULT_NOISE_CLAMP,
    DEFAULT_EOS_THRESHOLD,
    DEFAULT_AUDIO_PROMPT,
    DEFAULT_FRAMES_AFTER_EOS,
)

# Disable excessive logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("pocket_tts")
logger.setLevel(logging.ERROR)

class Talker:
    def __init__(self, variant=DEFAULT_VARIANT, device="cpu", voice_path=None):
        self.device = device
        # Increase temperature slightly for more natural intonation
        self.tts_model = TTSModel.load_model(
            variant, 0.8, DEFAULT_LSD_DECODE_STEPS, DEFAULT_NOISE_CLAMP, DEFAULT_EOS_THRESHOLD
        )
        self.tts_model.to(device)
        self.sample_rate = self.tts_model.config.mimi.sample_rate
        
        voice_prompt = voice_path if voice_path and os.path.exists(voice_path) else DEFAULT_AUDIO_PROMPT
        if voice_path and not os.path.exists(voice_path):
            logger.warning(f"Voice file {voice_path} not found. Using default voice.")
            
        print(f"Using voice prompt: {voice_prompt}")
        self.model_state = self.tts_model.get_state_for_audio_prompt(voice_prompt)

        # Setup background playback
        self.audio_queue = queue.Queue()
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()

    def _playback_loop(self):
        """Continuous audio stream to avoid gaps between sentences."""
        stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        stream.start()
        
        while True:
            data = self.audio_queue.get()
            if data is None:
                self.audio_queue.task_done()
                break
            try:
                stream.write(data)
            except Exception as e:
                # Ignore errors during shutdown
                pass
            finally:
                self.audio_queue.task_done()
        
        stream.stop()
        stream.close()

    def say(self, text):
        audio_chunks = self.tts_model.generate_audio_stream(
            model_state=self.model_state,
            text_to_generate=text,
            frames_after_eos=DEFAULT_FRAMES_AFTER_EOS,
        )
        
        for chunk in audio_chunks:
            # Convert torch tensor to numpy and ensure it's float32 for sounddevice
            audio_data = chunk.cpu().numpy().flatten().astype(np.float32)
            if len(audio_data) > 0:
                self.audio_queue.put(audio_data)

    def wait(self):
        """Block until all queued audio has finished playing."""
        self.audio_queue.join()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python talk.py \"text to say\"")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    talker = Talker()
    talker.say(text)
    
    # Keep main thread alive long enough to play audio if running standalone
    import time
    time.sleep(len(text) * 0.1 + 2)