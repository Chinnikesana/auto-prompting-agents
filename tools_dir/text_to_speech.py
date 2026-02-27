import os
import requests
from gtts import gTTS
import tempfile

def text_to_speech(text):
    if os.environ.get('TOOL_TEST_MODE') == 'true':
        return 'Mock success: text converted to speech'

    try:
        tts = gTTS(text=text, lang='en', tld='com', slow=False)
        tmp_dir = tempfile.gettempdir()
        filename = 'speech.mp3'
        filepath = os.path.join(tmp_dir, filename)
        tts.save(filepath)
        return filepath
    except Exception as e:
        return f'Error: {str(e)}'