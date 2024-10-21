from flask import Flask, render_template, request, jsonify
from translator.speech_recognition import SpeechRecognizer
from translator.translation import Translator
from translator.text_to_speech import TextToSpeech
import os
from datetime import datetime
import logging
import tempfile
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

speech_recognizer = SpeechRecognizer()
translator = Translator()
tts = TextToSpeech()

# In-memory storage for translation history
translation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file provided'})
    
    audio_file = request.files['audio']
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        audio_file.save(temp_file.name)
        temp_filepath = temp_file.name

    try:
        text = speech_recognizer.recognize_speech(temp_filepath)
        if text:
            return jsonify({'success': True, 'text': text})
        else:
            return jsonify({'success': False, 'message': 'No speech recognized'})
    except Exception as e:
        logger.error(f"Error in speech recognition: {str(e)}")
        return jsonify({'success': False, 'message': f'Error in speech recognition: {str(e)}'})
    finally:
        os.unlink(temp_filepath)

@app.route('/translate', methods=['POST'])
def translate():
    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')
    text = request.form.get('text', '')
    
    logger.info(f"Translating from {source_lang} to {target_lang}")
    
    try:
        if not text:
            return jsonify({'success': False, 'message': 'No text provided for translation'})
        
        # Translate
        translated_text = translator.translate(text, src=source_lang, dest=target_lang)
        logger.info(f"Translated text: {translated_text}")
        
        if translated_text:
            # Generate audio file
            audio_file = f"static/audio/translation_{hash(translated_text)}.mp3"
            tts.speak(translated_text, audio_file, lang=target_lang)
            
            # Add to history
            translation_history.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'original_text': text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'audio_url': audio_file
            })
            
            return jsonify({
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'audio_url': audio_file
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to translate text'})
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(translation_history)

# Add this new route for resetting history
@app.route('/reset_history', methods=['POST'])
def reset_history():
    global translation_history
    translation_history = []
    return jsonify({'success': True, 'message': 'History reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
