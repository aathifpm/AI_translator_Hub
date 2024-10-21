from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
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
socketio = SocketIO(app)

speech_recognizer = SpeechRecognizer()
translator = Translator()
tts = TextToSpeech()

# In-memory storage for translation history
translation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('stream-audio')
def handle_stream_audio(audio_blob):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(audio_blob)
        temp_filepath = temp_file.name

    try:
        text = speech_recognizer.recognize_speech(temp_filepath)
        is_final = speech_recognizer.is_final_result(text)
        socketio.emit('transcription', {'text': text, 'isFinal': is_final})
    except Exception as e:
        logger.error(f"Error in speech recognition: {str(e)}")
        socketio.emit('transcription', {'text': 'Error in speech recognition', 'isFinal': True})
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

if __name__ == '__main__':
    socketio.run(app, debug=True)
