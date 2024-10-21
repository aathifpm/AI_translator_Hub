from flask import Flask, render_template, request, jsonify
from translator.speech_recognition import SpeechRecognizer
from translator.translation import Translator
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

speech_recognizer = SpeechRecognizer()
translator = Translator()

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
    logger.info(f"Received audio file of size: {audio_file.content_length} bytes")
    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')
    
    logger.info(f"Source language: {source_lang}, Target language: {target_lang}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
        audio_file.save(temp_file.name)
        temp_filepath = temp_file.name

    try:
        # Recognize speech
        original_text = speech_recognizer.recognize_speech(temp_filepath, language=source_lang)
        
        if not original_text:
            logger.info("No speech recognized in this chunk")
            return jsonify({'success': True, 'message': 'No speech recognized in this chunk'})
        
        logger.info(f"Speech recognized: {original_text}")
        
        # Translate text
        translated_text = translator.translate(original_text, src=source_lang, dest=target_lang)
        
        if not translated_text:
            logger.error("Translation failed")
            return jsonify({'success': False, 'message': 'Translation failed'})
        
        logger.info(f"Translation successful: {translated_text}")
        
        return jsonify({
            'success': True,
            'original_text': original_text,
            'translated_text': translated_text
        })
    
    except Exception as e:
        logger.error(f"Error in recognition or translation: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    finally:
        os.unlink(temp_filepath)

if __name__ == '__main__':
    app.run(debug=True)
