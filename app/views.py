import os
from flask import render_template, request, send_from_directory
from app import app

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/submit/', methods=['POST'])
def save_input():
	last_n = request.form['n']
	data = request.form['trans']
	print data, last_n
	n = int(last_n)+1
	return present_file(str(n))

@app.route('/transcribe/', defaults={'num':1})
@app.route('/transcribe/<num>')
def present_file(num):
	filename = app.config['AUDIO_FILES'][int(num)]
	return render_template('index.html', filename=filename, n=num)
