import pyttsx3
import threading

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        self.is_speaking = False
        self.stop_speaking_flag = False
    
    def speak(self, text):
        self.stop_speaking_flag = False
        self.is_speaking = True
        
        def _speak():
            self.engine.say(text)
            try:
                self.engine.runAndWait()
            except RuntimeError:
                pass
            self.is_speaking = False
        
        thread = threading.Thread(target=_speak)
        thread.start()
    
    def stop_speaking(self):
        if self.is_speaking:
            self.stop_speaking_flag = True
            self.engine.stop()
            self.is_speaking = False
    
    def is_speaking(self):
        return self.is_speaking