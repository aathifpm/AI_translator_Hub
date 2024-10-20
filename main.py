from flask import Flask, render_template, request, jsonify
from translator.speech_recognition import SpeechRecognizer
from translator.translation import Translator
from translator.text_to_speech import TextToSpeech
import os
from datetime import datetime
import logging

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

@app.route('/translate', methods=['POST'])
def translate():
    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')
    
    print(f"Translating from {source_lang} to {target_lang}")  
    
    try:
        
        text = speech_recognizer.listen(language=source_lang)
        print(f"Recognized text: {text}")  
        if text:
            print(f"Recognized: {text}")
           
            translated_text = translator.translate(text, src=source_lang, dest=target_lang)
            print(f"Translated text: {translated_text}") 
            if translated_text:
                print(f"Translated: {translated_text}")
                
                audio_file = f"static/audio/translation_{hash(translated_text)}.mp3"
                tts.speak(translated_text, audio_file)
                
               
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
        
        return jsonify({'success': False, 'message': 'Translation failed. Please try again.'})
    except Exception as e:
        print(f"Error in translation: {str(e)}")  
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@app.route('/translate_text', methods=['POST'])
def translate_text():
    text = request.form.get('text')
    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')
    
    try:
        translated_text = translator.translate(text, src=source_lang, dest=target_lang)
        if translated_text:
            logger.info(f"Translated: {translated_text}")
            
           
            audio_filename = f"translation_{hash(translated_text)}.mp3"
            audio_path = os.path.join('static', 'audio', audio_filename)
            
            tts_success = tts.speak(translated_text, audio_path, lang=target_lang)
            
            if tts_success:
                audio_url = f"/static/audio/{audio_filename}"
                
                
                translation_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'original_text': text,
                    'translated_text': translated_text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'audio_url': audio_url
                })
                
                return jsonify({
                    'success': True,
                    'original_text': text,
                    'translated_text': translated_text,
                    'audio_url': audio_url
                })
            else:
                logger.error("Failed to generate audio file")
                return jsonify({'success': False, 'message': 'Failed to generate audio file'})
    
        return jsonify({'success': False, 'message': 'Translation failed. Please try again.'})
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@app.route('/history')
def history():
    return jsonify(translation_history)

@app.route('/reset_history', methods=['POST'])
def reset_history():
    global translation_history
    try:
       
        translation_history = []
        
      
        audio_folder = os.path.join('static', 'audio')
        for filename in os.listdir(audio_folder):
            if filename.endswith('.mp3'):
                os.remove(os.path.join(audio_folder, filename))
        
        return jsonify({'success': True, 'message': 'History reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error resetting history: {str(e)}'})

if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    app.run(debug=True)
