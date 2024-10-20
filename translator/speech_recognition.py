import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self, language='en-US'):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Adjusted for ambient noise")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Audio captured successfully.")
                return self.recognize_speech(audio, language)
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
        except Exception as e:
            print(f"Error during listening: {str(e)}")
        return None

    def recognize_speech(self, audio, language):
        if audio is None:
            return None
        try:
            text = self.recognizer.recognize_google(audio, language=language)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
        except sr.RequestError as e:
            print(f"Sorry, there was an error connecting to the speech recognition service: {str(e)}")
        return None
