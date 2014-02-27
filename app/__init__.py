import os
from flask import Flask

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

AUDIO_FOLDER = os.path.join(APP_ROOT, 'static/audio')

AUDIO_FILES = [f for f in os.listdir(AUDIO_FOLDER) if os.path.isfile(os.path.join(AUDIO_FOLDER,f))]



app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['AUDIO_FILES'] = AUDIO_FILES

from app import views
