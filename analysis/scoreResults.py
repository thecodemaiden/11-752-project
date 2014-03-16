import operator
import os
import string
from dtw import dtw


def formatTranscription(transcription):
    """ Given a transcription sentence, normalizes it to a standard form """
    # Convert formats
    transcription = transcription.strip().lower()
    transcription = transcription.replace("??", "UNKNOWN")
    transcription = ''.join(ch for ch in transcription  if ch not in ",.;/?")

    # Remove noise markers
    transcription = " ".join(filter(lambda s : not (s[0] == '[' or s[-1] == ']'),
            transcription.split()))

    # Remove hesitation
    transcription = transcription.replace("uh", "")
    transcription = transcription.replace("um", "")
    transcription = transcription.replace("uhm", "")
    transcription = transcription.replace("umm", "")

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


def readGroundTruth(easyFile, hardFile):
    """ Given paths to file containing the easy and hard groundtruth
        transcriptions, returns an array of strings for those
        transcriptions """
    easy = map(formatTranscription, open(easyFile,'r').readlines())
    hard = map(formatTranscription, open(hardFile,'r').readlines())

    return (easy, hard)


def main():
    # Read in result files
    results = readResults("../app/results")

    # Read in ground truth
    (easyTruth, hardTruth) = readGroundTruth("easy_ground_truth.txt", \
            "hard_ground_truth.txt")

    # Score all results
    easyResults = (0,0,0)
    for user in results["easy"]:
        res = user.testUtterances(easyTruth)
        easyResults = tuple(map(operator.add,easyResults,res))
    easyResults = tuple(map(lambda x: 1.0*x/len(results["easy"]), easyResults))

    hardResults = (0,0,0)
    for user in results["hard"]:
        res = user.testUtterances(hardTruth)
        hardResults = tuple(map(operator.add,hardResults,res))
    hardResults = tuple(map(lambda x: 1.0*x/len(results["hard"]), hardResults))

    # Print results
    print "Easy users had an average (insertions, deletions, substitutions): "
    print "   ", easyResults

    print "Hard users had an average (insertions, deletions, substitutions): "
    print "   ", hardResults


if __name__ == "__main__":
    main()
