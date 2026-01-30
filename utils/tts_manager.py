"""
AURA TTS Manager v2 - Uses Windows SAPI directly for reliable TTS
Avoids pyttsx3's threading issues
"""

import queue
import threading
import time
import os

# Try Windows SAPI directly
try:
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False
    print("[TTS] win32com not available")

# Fallback to pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

TTS_AVAILABLE = SAPI_AVAILABLE or PYTTSX3_AVAILABLE


class TTSManager:
    """
    Thread-safe TTS manager using Windows SAPI or pyttsx3.
    Uses a dedicated thread with proper COM initialization.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._queue = queue.Queue()
        self._running = True
        self._thread = None
        self._ready = threading.Event()
        self._current_speaker = None  # Track current speaker for interruption
        self._should_stop = False  # Flag to stop current speech
        
        if TTS_AVAILABLE:
            self._start_engine_thread()
            # Wait for engine to be ready
            self._ready.wait(timeout=5.0)
    
    def _start_engine_thread(self):
        """Start the TTS engine in a separate thread"""
        self._thread = threading.Thread(target=self._engine_loop, daemon=True)
        self._thread.start()
    
    def _engine_loop(self):
        """Main loop for TTS engine - runs in dedicated thread"""
        
        speaker = None
        use_sapi = False
        
        # Try SAPI first (more reliable)
        if SAPI_AVAILABLE:
            try:
                import pythoncom
                pythoncom.CoInitialize()  # Initialize COM for this thread
                
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Set voice (female preferred)
                voices = speaker.GetVoices()
                voice_pref = os.environ.get('AURA_VOICE', 'female').lower()
                
                for i in range(voices.Count):
                    voice_name = voices.Item(i).GetDescription().lower()
                    if voice_pref == 'female':
                        if any(x in voice_name for x in ['zira', 'helena', 'eva', 'female']):
                            speaker.Voice = voices.Item(i)
                            break
                    else:
                        if any(x in voice_name for x in ['david', 'mark', 'male']):
                            speaker.Voice = voices.Item(i)
                            break
                
                speaker.Rate = 1  # -10 to 10
                speaker.Volume = 100  # 0 to 100
                
                use_sapi = True
                print("[TTS] SAPI engine initialized")
            except Exception as e:
                print(f"[TTS] SAPI failed: {e}")
                speaker = None
        
        # Fallback to pyttsx3
        if speaker is None and PYTTSX3_AVAILABLE:
            try:
                speaker = pyttsx3.init()
                speaker.setProperty('rate', 175)
                speaker.setProperty('volume', 0.9)
                print("[TTS] pyttsx3 engine initialized")
            except Exception as e:
                print(f"[TTS] pyttsx3 failed: {e}")
                speaker = None
        
        if speaker is None:
            print("[TTS] No TTS engine available!")
            self._ready.set()
            return
        
        print("[TTS] Engine ready")
        self._ready.set()
        
        while self._running:
            try:
                text = self._queue.get(timeout=1.0)
                
                if text is None:
                    break
                
                # Check if we should stop before speaking
                if self._should_stop:
                    self._should_stop = False
                    # Clear queue of pending messages
                    try:
                        while True:
                            self._queue.get_nowait()
                    except queue.Empty:
                        pass
                    continue
                
                if text and text.strip():
                    print(f"[TTS] Speaking: {text[:40]}...")
                    self._current_speaker = speaker  # Track for interruption
                    try:
                        if use_sapi:
                            # SAPI supports interruption via Skip() method
                            speaker.Speak(text, 1)  # 1 = async flag for SAPI
                            # Wait for completion or stop signal
                            while speaker.Status.RunningState != 1:  # 1 = done
                                if self._should_stop:
                                    speaker.Skip("Sentence", 999)  # Skip remaining
                                    break
                                time.sleep(0.1)
                        else:
                            # For pyttsx3, we can't easily interrupt, but we can stop the engine
                            if not self._should_stop:
                                speaker.say(text)
                                speaker.runAndWait()
                    except Exception as e:
                        print(f"[TTS] Speak error: {e}")
                    finally:
                        self._current_speaker = None
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS] Loop error: {e}")
                time.sleep(0.5)
        
        # Cleanup
        if use_sapi:
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except:
                pass
        elif speaker and hasattr(speaker, 'stop'):
            speaker.stop()
        
        print("[TTS] Engine stopped")
    
    def speak(self, text: str):
        """Queue text to be spoken"""
        if TTS_AVAILABLE and text and text.strip():
            self._queue.put(text)
    
    def stop_speaking(self):
        """Stop current speech immediately"""
        self._should_stop = True
        if self._current_speaker:
            try:
                # Try to interrupt SAPI
                if hasattr(self._current_speaker, 'Skip'):
                    self._current_speaker.Skip("Sentence", 999)
            except:
                pass
    
    def stop(self):
        """Stop the TTS engine"""
        self._running = False
        self._should_stop = True
        self._queue.put(None)
        if self._thread:
            self._thread.join(timeout=2.0)


# Global singleton instance
_tts_manager = None

def get_tts_manager() -> TTSManager:
    """Get the global TTS manager"""
    global _tts_manager
    if _tts_manager is None:
        print("[TTS] Creating TTS Manager...")
        _tts_manager = TTSManager()
    return _tts_manager

def speak(text: str):
    """Speak text using the TTS manager"""
    if text:
        print(f"[TTS] speak() called: {text[:30]}...")
    get_tts_manager().speak(text)

def stop_speaking():
    """Stop current TTS playback immediately"""
    get_tts_manager().stop_speaking()


def speak_chunked(text: str, max_chunk_words: int = 50):
    """
    Speak text in manageable chunks for interruptibility.
    Splits by sentences, then by word count if sentences are too long.
    
    Args:
        text: The text to speak
        max_chunk_words: Maximum words per chunk (default 50 ~15-20 seconds)
    """
    if not text:
        return
    
    import re
    tts = get_tts_manager()
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        words = sentence.split()
        
        # If single sentence is too long, split it
        if len(words) > max_chunk_words:
            # Speak current chunk first
            if current_chunk:
                tts.speak(' '.join(current_chunk))
                current_chunk = []
                current_word_count = 0
            
            # Split long sentence into smaller parts
            for i in range(0, len(words), max_chunk_words):
                chunk_words = words[i:i + max_chunk_words]
                tts.speak(' '.join(chunk_words))
        else:
            # Add sentence to current chunk
            if current_word_count + len(words) > max_chunk_words:
                # Speak current chunk and start new one
                if current_chunk:
                    tts.speak(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = len(words)
            else:
                current_chunk.append(sentence)
                current_word_count += len(words)
    
    # Speak remaining chunk
    if current_chunk:
        tts.speak(' '.join(current_chunk))


# Auto-initialize on import
if TTS_AVAILABLE:
    print("[TTS] Auto-initializing...")
    get_tts_manager()


if __name__ == "__main__":
    print("Testing TTS Manager v2...")
    
    speak("Hello, I am Aura.")
    time.sleep(3)
    speak("This is a test of the text to speech system.")
    time.sleep(4)
    speak("Goodbye!")
    time.sleep(2)
    
    get_tts_manager().stop()
    print("Test complete!")
