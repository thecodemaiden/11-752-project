import os
from flask import render_template, request, send_from_directory, Flask

#
# Configure the base app
#
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(APP_ROOT, 'static/audio')
AUDIO_FILES = [f for f in os.listdir(AUDIO_FOLDER) if os.path.isfile(os.path.join(AUDIO_FOLDER,f))]

app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['AUDIO_FILES'] = AUDIO_FILES


#
# Set page handlers
#
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


#
# If calling this as a script, run it
#
if __name__ == "__main__":
    app.run(debug=True)
