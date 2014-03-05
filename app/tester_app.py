import os
import time
import re
import shutil
from flask import *

#
# Configure the base app
#
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TRAIN_FOLDER = os.path.join(APP_ROOT, 'static/training')
AUDIO_FOLDER = os.path.join(APP_ROOT, 'static/audio')
LOG_FOLDER = os.path.join(APP_ROOT, 'logs')
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

    # Create their log file
    logFile = open(app.config['APP_ROOT'] + '/logs/' + str(userid) + \
                   '.txt','a')
    logFile.write('User ' + str(userid) + ', ' + difficulty + '\n')
    logFile.write('Started at timestamp: ' + str(time.time()) + '\n')

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

    # choose hard or easy
    if (int(userid) % 2 == 0):
        hard = False
    else:
        hard = True

    render_template('layout.html', hard=hard)
    return render_template('train.html', filename=filename, n=num, userid=userid)


@app.route('/submittrain/<userid>', methods=['POST'])
def score_train(userid):
    # Get the data
    last_n = request.form['n']
    data = request.form['trans']

    # Write their transcription to the log file
    logLine = 'Training utterance ' + last_n + ' at timestamp ' + \
            str(time.time()) + '\n\t' + data + '\n'
    logFile = open(app.config['APP_ROOT'] + '/logs/' + str(userid) + \
            '.txt', 'a')
    logFile.write(logLine)

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

    #Checking whether the user input was correct or wrong
    status = "Correct"
    l1 = re.findall('\[[^]]*\]|\w+', data.lower())
    l2 = re.findall('\[[^]]*\]|\w+', transcription.lower())

    if(len(l1) != len(l2)  ):
        status = "Wrong"
    else:
        for i in range(len(l1)):
            print l1[i], l2[i]
            if( (l1[i].startswith("[")) or (l1[i].endswith("-")) ):
                continue
            elif(l1[i] != l2[i]):
                status = "Wrong"
                
         
    return render_template('train.html', filename=audiofilename, \
            transcription=transcription, user=data, status=status, n=int(last_n), userid=userid)

            
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

    # Write their transcription to the log file
    logLine = 'Utterance ' + last_n + ' at timestamp ' + str(time.time()) + \
            '\n\t' + data + '\n'
    logFile = open(app.config['APP_ROOT'] + '/logs/' + str(userid) + \
            '.txt', 'a')
    logFile.write(logLine)

    # Increment utterance number and redirect
    n = int(last_n)+1
    if n >= len(app.config['AUDIO_FILES']):
        # Copy log file to the result file as the user has completed the entire task
        shutil.copyfile(app.config['APP_ROOT'] + '/logs/' + str(userid) + '.txt', \
                        app.config['APP_ROOT'] + '/results/' + str(userid) + '.txt')
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
