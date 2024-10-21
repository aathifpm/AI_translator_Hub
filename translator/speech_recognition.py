import speech_recognition as sr
from pydub import AudioSegment
import io

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_from_file(self, audio_file_path, language='en-US'):
        try:
            # Load the audio file
            audio = AudioSegment.from_file(audio_file_path)
            
            # Convert to WAV
            wav_data = io.BytesIO()
            audio.export(wav_data, format="wav")
            wav_data.seek(0)
            
            # Use speech_recognition to recognize the audio
            with sr.AudioFile(wav_data) as source:
                audio_data = self.recognizer.record(source)
            
            # Perform the recognition
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

    def convert_language_code(self, language):
        # Convert language codes to pocketsphinx format
        language_map = {
            'en-US': 'en-us',
            'es-ES': 'es-es',
            # Add more language mappings as needed
        }
        return language_map.get(language, 'en-us')  # Default to en-us if not found

    # Keep the existing recognize_speech method for compatibility
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
