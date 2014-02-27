import os
from flask import render_template, request, send_from_directory
from app import app

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/transcribe/<num>')
def present_file(num):
	filename = app.config['AUDIO_FILES'][int(num)]
	return render_template('index.html', filename=filename)
