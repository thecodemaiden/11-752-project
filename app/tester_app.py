import os
import time
from flask import *

#
# Configure the base app
#
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TRAIN_FOLDER = os.path.join(APP_ROOT, 'static/training')
AUDIO_FOLDER = os.path.join(APP_ROOT, 'static/audio')
RESULTS_FOLDER = os.path.join(APP_ROOT, 'results')

TRAIN_FILES = [f for f in os.listdir(TRAIN_FOLDER) if 
        os.path.isfile(os.path.join(TRAIN_FOLDER,f)) and
        f.endswith('.wav')]
AUDIO_FILES = [f for f in os.listdir(AUDIO_FOLDER) if 
        os.path.isfile(os.path.join(AUDIO_FOLDER,f)) and
        f.endswith('.wav')]
RESULTS_FILES = [f for f in os.listdir(RESULTS_FOLDER) if 
        os.path.isfile(os.path.join(RESULTS_FOLDER,f)) and
        f.endswith('.txt')]
NEXT_ID = len(RESULTS_FILES)+1

app.config['APP_ROOT'] = APP_ROOT
app.config['TRAIN_FOLDER'] = TRAIN_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['TRAIN_FILES'] = TRAIN_FILES
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


@app.route('/train/<userid>/', defaults={'num':'0'})
@app.route('/train/<userid>/<num>')
def present_train(userid, num):
    # If we have completed all training examples, redirect
    num = int(num)
    if num >= len(app.config['TRAIN_FILES']):
        return redirect('/begin/'+userid)

    # Load the file for this test
    filename = app.config['TRAIN_FILES'][num]
    return render_template('train.html', filename=filename, n=num, userid=userid)


@app.route('/submittrain/<userid>', methods=['POST'])
def score_train(userid):
    # Get the data
    last_n = request.form['n']
    data = request.form['trans']

    # Write their transcription to the results file
    resultLine = 'Training utterance ' + last_n + ' at timestamp ' + \
            str(time.time()) + '\n\t' + data + '\n'
    resultFile = open(app.config['APP_ROOT'] + '/results/' + str(userid) + \
            '.txt', 'a')
    resultFile.write(resultLine)

    # Get the actual transcription
    audiofilename = app.config['TRAIN_FILES'][int(last_n)]
    transcriptionfilename = audiofilename.replace('.wav','.txt')
    transcriptionfile = open(app.config['TRAIN_FOLDER'] + '/' + \
            transcriptionfilename)
    transcriptionlines = transcriptionfile.readlines()

    transcription = " "
    if (int(userid) % 2 == 0):
        transcription = transcriptionlines[0]
    else:
        transcription = transcriptionlines[1]

    return render_template('train.html', filename=audiofilename, \
            transcription=transcription, user=data, n=int(last_n), userid=userid)

@app.route('/begin/<userid>')
def begin(userid):
    return render_template('begin.html', userid=userid)


@app.route('/transcribe/<userid>/', defaults={'num':'0'})
@app.route('/transcribe/<userid>/<num>')
def present_file(userid, num):
    # Load the file for this test
    num = int(num)
    filename = app.config['AUDIO_FILES'][num]
    return render_template('transcribe.html', filename=filename, n=num, userid=userid)


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
    if n >= len(app.config['AUDIO_FILES']):
        return redirect('/thanks/')
    else:
        return redirect('/transcribe/'+str(userid)+'/'+str(n))


@app.route('/thanks/')
def thanks():
    return render_template('thanks.html')
    

#
# If calling this as a script, run it
#
if __name__ == "__main__":
    app.run(debug=True)
