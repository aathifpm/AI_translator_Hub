from flask import Flask, render_template, request, jsonify, send_from_directory
from translator.speech_recognition import SpeechRecognizer
from translator.translation import Translator
from translator.text_to_speech import TextToSpeech
import tempfile
import os
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

speech_recognizer = SpeechRecognizer()
translator = Translator()
tts = TextToSpeech()

# Add this global variable to store chat history
chat_history = []

# Ensure the 'static/audio' directory exists
AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

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
        
        # Generate TTS audio for translated text
        unique_id = uuid.uuid4().hex
        audio_filename = f"translated_{unique_id}.mp3"
        audio_filepath = os.path.join(AUDIO_FOLDER, audio_filename)
        tts_success = tts.speak(translated_text, audio_filepath, lang=target_lang)
        
        if not tts_success:
            logger.error("Text-to-Speech conversion failed")
            return jsonify({'success': False, 'message': 'Text-to-Speech conversion failed'})
        
        audio_url = f"/static/audio/{audio_filename}"
        
        # Append to chat history before returning
        chat_history.append({
            'original_text': original_text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'audio_url': audio_url
        })
        
        return jsonify({
            'success': True,
            'original_text': original_text,
            'translated_text': translated_text,
            'audio_url': audio_url
        })
    
    except Exception as e:
        logger.error(f"Error in recognition or translation: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    finally:
        os.unlink(temp_filepath)

@app.route('/translate_text', methods=['POST'])
def translate_text():
    text = request.form.get('text')
    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')

    translated_text = translator.translate(text, src=source_lang, dest=target_lang)

    if translated_text:
        # Generate TTS audio for translated text
        unique_id = uuid.uuid4().hex
        audio_filename = f"translated_text_{unique_id}.mp3"
        audio_filepath = os.path.join(AUDIO_FOLDER, audio_filename)
        tts_success = tts.speak(translated_text, audio_filepath, lang=target_lang)
        
        if not tts_success:
            logger.error("Text-to-Speech conversion failed for text translation")
            return jsonify({'success': False, 'message': 'Text-to-Speech conversion failed'})
        
        audio_url = f"/static/audio/{audio_filename}"
        
        chat_history.append({
            'original_text': text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'audio_url': audio_url
        })
        return jsonify({'success': True, 'translated_text': translated_text, 'audio_url': audio_url})
    else:
        return jsonify({'success': False, 'message': 'Translation failed'})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(chat_history)

@app.route('/reset_history', methods=['POST'])
def reset_history():
    global chat_history
    chat_history = []
    return jsonify({'success': True, 'message': 'History reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
