import speech_recognition as sr
from pydub import AudioSegment
import io

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_speech(self, audio_file_path, language='en-US'):
        try:
            # Convert WebM to WAV
            audio = AudioSegment.from_file(audio_file_path, format="webm")
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Perform the recognition
            with sr.AudioFile(wav_io) as source:
                audio_data = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio_data, language=language)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"Error during speech recognition: {str(e)}")
        return None

    def is_final_result(self, text):
        # For this implementation, we'll consider all results as final
        return True
