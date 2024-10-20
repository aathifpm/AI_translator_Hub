from gtts import gTTS
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self):
        pass

    def speak(self, text, filename, lang='en'):
        try:
            logger.info(f"Generating speech for text: '{text}' in language: {lang}")
            tts = gTTS(text=text, lang=lang, slow=False)
            
  
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            tts.save(filename)
            logger.info(f"Audio file saved successfully: {filename}")
            

            if os.path.exists(filename):
                logger.info(f"File exists: {filename}")
                return True
            else:
                logger.error(f"File was not created: {filename}")
                return False
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return False
