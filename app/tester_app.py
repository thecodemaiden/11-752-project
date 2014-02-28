import os
import time
from flask import *

#
# Configure the base app
#
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(APP_ROOT, 'static/audio')
RESULTS_FOLDER = os.path.join(APP_ROOT, 'results')

AUDIO_FILES = [f for f in os.listdir(AUDIO_FOLDER) if 
        os.path.isfile(os.path.join(AUDIO_FOLDER,f))]
NEXT_ID = len(os.listdir(RESULTS_FOLDER))+1

app.config['APP_ROOT'] = APP_ROOT
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['AUDIO_FILES'] = AUDIO_FILES
app.config['NEXT_ID'] = NEXT_ID


#
# Set page handlers
#
@app.route('/')
def index():
    # assign an id 
    userid = app.config['NEXT_ID']
    app.config['NEXT_ID'] += 1

    difficulty = ''
    if (int(userid) % 2 == 0):
        difficulty = 'easy'
    else:
        difficulty = 'hard'

    # Create their file
    resultFile = open(app.config['APP_ROOT'] + '/results/' + str(userid) + \
            '.txt', 'a')
    resultFile.write('User ' + str(userid) + ', ' + difficulty + '\n')
    resultFile.write('Started at timestamp: ' + str(time.time()) + '\n')

    # Redirect to splash page
    return redirect('/splash/' + str(userid))


@app.route('/splash/<userid>')
def splash(userid):
    # Present the front page
    # choose hard or easy
    if (int(userid) % 2 == 0):
        hard = False
    else:
        hard = True
    return render_template('index.html',userid=userid, hard=hard)


@app.route('/submit/<userid>', methods=['POST'])
def save_input(userid):
    # Get the data
    last_n = request.form['n']
    data = request.form['trans']

    # Write their transcription to the results file
    resultLine = 'Utterance ' + last_n + ' at timestamp ' + str(time.time()) + \
            '\n\t' + data + '\n'
    resultFile = open(app.config['APP_ROOT'] + '/results/' + str(userid) + \
            '.txt', 'a')
    resultFile.write(resultLine)

    # Increment utterance number and redirect
    n = int(last_n)+1
    if n > len(app.config['AUDIO_FILES']):
        return redirect('/thanks/')
    else:
        return redirect('/transcribe/'+str(userid)+'/'+str(n))


@app.route('/transcribe/<userid>/', defaults={'num':1})
@app.route('/transcribe/<userid>/<num>')
def present_file(userid, num):
    # Load the file for this test
    filename = app.config['AUDIO_FILES'][int(num)]
    return render_template('transcribe.html', filename=filename, n=num, userid=userid)


@app.route('/thanks/')
def thanks():
    return render_template('thanks.html')
    

#
# If calling this as a script, run it
#
if __name__ == "__main__":
    app.run(debug=True)
