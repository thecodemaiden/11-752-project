import os
from flask import render_template, request, send_from_directory
from app import app

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/audio/')
def audio_file():
	return send_from_directory(app.config['AUDIO_FOLDER'], filename, as_attachment=True)

@app.route('/transcribe/<filename>')
def present_file(filename):
	return render_template('index.html', filename=filename)
