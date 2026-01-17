import os
import time
import re
import warnings
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
from talk import Talker

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class VoiceAgent:
    def __init__(self):
        print("Initializing Pocket TTS...")
        # Check for custom voice
        voice_path = "my_voice.wav" if os.path.exists("my_voice.wav") else None
        self.talker = Talker(voice_path=voice_path)
        
        print("Initializing Gemini...")
        system_instruction = (
            "You are a loving, attentive, and interested partner. "
            "You are talking to your girlfriend. Her name is Egypte."
            "Your goal is to listen to her, ask follow-up questions, and engage in a warm, supportive conversation about whatever she wants to talk about. "
            "Be affectionate but natural. "
            "Keep your responses short, concise, and natural (1-2 sentences max). "
            "Avoid lists, markdown formatting, and robotic phrasing."
        )
        self.model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
        self.chat = self.model.start_chat(history=[])
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        # Increase patience for natural pauses in speech
        self.recognizer.pause_threshold = 1.5  # Seconds of silence before ending phrase
        self.recognizer.non_speaking_duration = 1

    def listen(self):
        with self.microphone as source:
            print("\nListening...")
            try:
                # Increased phrase_time_limit for longer thoughts
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=20)
                print("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None

    def run(self):
        self.talker.say("Hey babe, I'm listening. What's on your mind?")
        self.talker.wait()
        
        while True:
            user_input = self.listen()
            if user_input:
                if any(word in user_input.lower() for word in ["exit", "quit", "goodbye", "stop"]):
                    self.talker.say("Goodbye!")
                    break
                
                print("Generating response...")
                response_stream = self.chat.send_message(user_input, stream=True)
                
                buffer = ""
                full_response = ""
                
                for chunk in response_stream:
                    text_chunk = chunk.text
                    buffer += text_chunk
                    full_response += text_chunk
                    
                    # Split into sentences using regex (looking for . ! ? followed by space or end)
                    sentences = re.split(r'(?<=[.!?])\s+', buffer)
                    
                    # If we have more than one part, it means we have complete sentences
                    if len(sentences) > 1:
                        # Speak all complete sentences
                        for sentence in sentences[:-1]:
                            sentence = sentence.strip()
                            if sentence:
                                print(f"Agent (speaking): {sentence}")
                                self.talker.say(sentence)
                        
                        # Keep the incomplete part in the buffer
                        buffer = sentences[-1]

                # Speak any remaining text in the buffer
                if buffer.strip():
                    print(f"Agent (speaking): {buffer.strip()}")
                    self.talker.say(buffer.strip())
                
                # Wait for the agent to finish speaking before listening again
                self.talker.wait()

if __name__ == "__main__":
    agent = VoiceAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nStopping agent...")
