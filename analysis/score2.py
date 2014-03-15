import operator
import os
import string
import re
from dtw import dtw


####
# According to the handout, we don't care about partial words
# so I removed them, and removed all punctuation from the gold standard
###

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

        # Now parse each pair of lines
        self.trainingTranscriptions = [""]*4
        self.transcriptions = [""]*28
        for i in xrange(2, len(lines), 2):
            # Get the utterance type and transcription
            line = lines[i].split()
            training = line[0] == "Training"
            transcription = formatTranscription(lines[i+1])

            # Store the result
            if training:
                utt = int(line[2])
                self.trainingTranscriptions[utt] = transcription
            else:
                utt = int(line[1])
                self.transcriptions[utt] = transcription

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
			print '  ',test
			print '  ',actual
			print '-\n'
			(dist, ins, dels, subs) = dtw(test, actual)

			# Add the error counts
			results = tuple(map(operator.add, results, (ins,dels,subs)))

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


def main():
    # Read in result files
    results = readResults("../app/results")

    # Read in ground truth
    truth = map(formatTranscription, open('gold_standard.txt', 'r').readlines())

    # Score all results
    easyResults = (0,0,0)
    for user in results["easy"]:
        res = user.testUtterances(truth)
        easyResults = tuple(map(operator.add,easyResults,res))
    easyResults = tuple(map(lambda x: 1.0*x/len(results["easy"]), easyResults))

    hardResults = (0,0,0)
    for user in results["hard"]:
        res = user.testUtterances(truth)
        hardResults = tuple(map(operator.add,hardResults,res))
    hardResults = tuple(map(lambda x: 1.0*x/len(results["hard"]), hardResults))

    # Print results
    print "Easy users had an average (insertions, deletions, substitutions): "
    print "   ", easyResults

    print "Hard users had an average (insertions, deletions, substitutions): "
    print "   ", hardResults

if __name__ == "__main__":
    main()
