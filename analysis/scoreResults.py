import operator
import os
import string
import re
from dtw import dtw
import numpy
from itertools import combinations


def formatTranscription(transcription):
    """ Given a transcription sentence, normalizes it to a standard form """
    # Convert formats
    transcription = transcription.strip().lower()
    transcription = transcription.replace("??", "UNKNOWN")
    
    #remove noise markers
    transcription = re.sub('\[.*\]', '', transcription)
    
    #remove punctuation
    transcription = re.sub('[\?\.\!\,/]', ' ',transcription)
    
    #remove partial words
    transcription = re.sub(r'(^|\b)[A-Za-z]-', '', transcription)
    transcription = re.sub(r'(^|\b)-[A-Za-z]', '', transcription)
    
    #remove hesitation
    #  uhhhhh uuuuhh uuhhhmmm 
    transcription = re.sub(r'\bu+[mh]+\b', '', transcription)
    return transcription


class UserResult:
    """
    A UserResult contains all the transcriptions for a single user's test run.
    """
    
    def __init__(self, filename):
        """ Initializes the result by reading a specified results file. """
        # First read the entire file into lines
        resultsFile = open(filename, "r")
        lines = map(lambda s : s.strip(), resultsFile.readlines())
        
        # Then strip out the user and difficulty
        line = lines[0].split()
        self.userid = int(line[1].replace(",",""))
        self.difficulty = line[2]
        # get the timestamp at start, so we can calculate the time taken for each utterance
        startTime = float(lines[1].split(":")[1])
        # Now parse each pair of lines
        self.times=[0.0]*27
        self.trainingTranscriptions = [""]*4
        self.transcriptions = [""]*27
        for i in xrange(2, len(lines), 2):
            # Get the utterance type and transcription
            line = lines[i].split()
            training = line[0] == "Training"
            transcription = formatTranscription(lines[i+1])
            
            timestamp = float(line[-1])
            
            # Store the result
            if training:
                utt = int(line[2])
                self.trainingTranscriptions[utt] = transcription
            else:
                utt = int(line[1])
                self.transcriptions[utt] = transcription
                # not storing times for training utts
                self.times[utt] = (timestamp - startTime)
            startTime = timestamp
            
        self.scores = []
    
    def testUtterances(self, groundTruth):
    	""" Given a list of groundTruth utterance text, returns the total
    	number of insertion, deletion and substitution errors the user had """
    	if len(groundTruth) != len(self.transcriptions):
    	    raise Exception("The number of ground truth trancriptions must match"
    	        + " the number of actual transcriptions")
    
    	# For each transcription, DTW
    	results = (0,0,0)
    	for (test,actual) in zip(self.transcriptions, groundTruth):
    	    test = map(lambda s: s.strip(), test.split())
    	    actual = map(lambda s: s.strip(), actual.split())
    	    (dist, ins, dels, subs) = dtw(test, actual)
    
    	    # Add the error counts
    	    results = tuple(map(operator.add, results, (ins,dels,subs)))
    	    # save the score for each utterance
    	    self.scores.append((ins,dels,subs))
    
    	# Return the error counts
    	return results

def readResults(resultsDir):
    """ Given a directory, reads all the result files in that directory.
        Returns a dict of results where res["easy"] and res["hard"] are
        lists of the results for the easy and hard cases """
    if resultsDir[-1] != "/":
        resultsDir += "/"

    results = dict([("easy",[]), ("hard",[])])
    for filename in os.listdir(resultsDir):
        # Parse the results file
        filename = resultsDir+filename
        result = UserResult(filename)
        
        # Store the result by difficulty
        results[result.difficulty].append(result)

    return results


def alignUtterances(users):
    """ Computes average distance between utterances for each uesr in the set,
        then returns the average mean and std between utterances for each user """
    user_pairs = combinations(users, 2)
    align_stats = {}
    n = len(users[0].transcriptions)
    for u,v in user_pairs:
        pair_distances = []
        for i in range(n):
            utt1 = u.transcriptions[i].split()
            utt2 = v.transcriptions[i].split()
            score = dtw(utt1, utt2)
            # just save the distance
            pair_distances.append(score[0])
        # now save the transcription distances 
        stats_key = (u.userid, v.userid)
        align_stats[stats_key] = pair_distances

    # Take compute alignment statistics
    dists = map(lambda l: reduce(operator.add, l), align_stats.values())
    return (numpy.mean(dists), numpy.std(dists))	


def main():
    # Read in result files
    results = readResults("../app/results")
    
    # Read in ground truth
    truth = map(formatTranscription, open('gold_standard.txt', 'r').readlines())
    
    # Score all results
    # Save the scores to compare group consistency, question ease, etc.
    #easyScores = []
    easyResults = (0,0,0)
    for user in results["easy"]:
    	res = user.testUtterances(truth)
        #   easyScores.append(res)
    	easyResults = tuple(map(operator.add,easyResults,res))
    easyResults = tuple(map(lambda x: 1.0*x/len(results["easy"]), easyResults))
    
    hardResults = (0,0,0)
    #hardScores = []
    for user in results["hard"]:
    	res = user.testUtterances(truth)
    #	hardScores.append(res)
    	hardResults = tuple(map(operator.add,hardResults,res))
    hardResults = tuple(map(lambda x: 1.0*x/len(results["hard"]), hardResults))
    
    # Print results
    print "Easy users had an average (insertions, deletions, substitutions): "
    print "\t", easyResults, ", total: " + \
            str(reduce(operator.add, list(easyResults)))
    print
    
    print "Hard users had an average (insertions, deletions, substitutions): "
    print "\t", hardResults, ", total: " + \
            str(reduce(operator.add, list(hardResults)))
    print
    
    # Find the hardest problem
    difficultyEasy = {i:(0,0,0) for i in range(len(truth))}
    difficultyHard = {i:(0,0,0) for i in range(len(truth))}
    difficultyOverall = {i:(0,0,0) for i in range(len(truth))}
    
    timeTakenEasy = [0]*len(truth)
    timeTakenHard = [0]*len(truth)
    timeTakenOverall = [0]*len(truth)
    
    for i in range(len(truth)):
        for user in results["easy"]:
            res = user.scores[i]
            difficultyEasy[i] = tuple(map(operator.add, difficultyEasy[i], res))
            difficultyOverall[i] = tuple(map(operator.add, difficultyOverall[i], res))
            timeTakenEasy[i] =  timeTakenEasy[i] + user.times[i]
            timeTakenOverall[i] =  timeTakenOverall[i]+ user.times[i]
        for user in results["hard"]:
            res = user.scores[i]
            difficultyHard[i] = tuple(map(operator.add, difficultyHard[i], res))
            difficultyOverall[i] = tuple(map(operator.add, difficultyOverall[i], res))
            timeTakenHard[i] = timeTakenHard[i] + user.times[i]
            timeTakenOverall[i] = timeTakenOverall[i] + user.times[i]
    
    # sort the problems, take the 3 hardest
    easyOrder = sorted(difficultyEasy, key=lambda x: sum(difficultyEasy[x]), 
            reverse=True)	
    
    hardOrder = sorted(difficultyHard, key=lambda x: sum(difficultyHard[x]), 
            reverse=True)	
    
    bothOrder = sorted(difficultyOverall, key=lambda x: sum(difficultyOverall[x]),
            reverse=True)	
    
    
    print "Hardest 3 problems:"
    print "\tEasy:", easyOrder[:2]
    print "\tHard:", hardOrder[:2]
    print "\tBoth:", bothOrder[:2]
    print
    
    # list problems from most to least time taken
    easyTimes = sorted(range(len(timeTakenEasy)), key = lambda x:timeTakenEasy[x], reverse=True)
    hardTimes = sorted(range(len(timeTakenHard)), key = lambda x:timeTakenHard[x], reverse=True)
    bothTimes = sorted(range(len(timeTakenOverall)), key = lambda x:timeTakenOverall[x], reverse=True)
    
    print "Most time taken on problems:"
    print "\tEasy:", easyTimes
    print "\tHard:", hardTimes
    print "\tBoth:", bothTimes
    print
    
    # now the alignment consistency.... oh boy
    print "Consistency:"
    print "\t", alignUtterances(results["easy"])
    print "\t", alignUtterances(results["hard"])


if __name__ == "__main__":
    main()
