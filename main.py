from flask import Flask, render_template, request, jsonify
from translator.speech_recognition import SpeechRecognizer
from translator.translation import Translator
from translator.text_to_speech import TextToSpeech
import os
from datetime import datetime
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

speech_recognizer = SpeechRecognizer()
translator = Translator()
tts = TextToSpeech()

translation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize_and_translate', methods=['POST'])
def recognize_and_translate():
    logger.info("Received request for speech recognition and translation")
    if 'audio' not in request.files:
        logger.error("No audio file provided in the request")
        return jsonify({'success': False, 'message': 'No audio file provided'})
    
    audio_file = request.files['audio']
    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')
    
    logger.info(f"Source language: {source_lang}, Target language: {target_lang}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
        audio_file.save(temp_file.name)
        temp_filepath = temp_file.name
        logger.debug(f"Temporary audio file saved: {temp_filepath}")

    try:
        # Recognize speech
        logger.info("Starting speech recognition")
        original_text = speech_recognizer.recognize_speech(temp_filepath, language=source_lang)
        
        if not original_text:
            logger.warning("No speech recognized")
            return jsonify({'success': False, 'message': 'No speech recognized'})
        
        logger.info(f"Speech recognized: {original_text}")
        
        # Translate text
        logger.info("Starting translation")
        translated_text = translator.translate(original_text, src=source_lang, dest=target_lang)
        
        if not translated_text:
            logger.error("Translation failed")
            return jsonify({'success': False, 'message': 'Translation failed'})
        
        logger.info(f"Translation successful: {translated_text}")
        
        # Generate audio file for translated text
        audio_file = f"static/audio/translation_{hash(translated_text)}.mp3"
        tts.speak(translated_text, audio_file, lang=target_lang)
        
        # Add to history
        translation_history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'original_text': original_text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'audio_url': audio_file
        })
        
        return jsonify({
            'success': True,
            'original_text': original_text,
            'translated_text': translated_text,
            'audio_url': audio_file
        })
    
    except Exception as e:
        logger.error(f"Error in recognition or translation: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    finally:
        os.unlink(temp_filepath)
        logger.debug(f"Temporary file removed: {temp_filepath}")

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(translation_history)

@app.route('/reset_history', methods=['POST'])
def reset_history():
    global translation_history
    translation_history = []
    return jsonify({'success': True, 'message': 'History reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
