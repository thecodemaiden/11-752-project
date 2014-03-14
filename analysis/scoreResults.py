import os
from dtw import dtw


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
        self.transcriptions = [""]*27
        for i in xrange(2, len(lines), 2):
            # Get the utterance type and transcription
            line = lines[i].split()
            training = line[0] == "Training"
            transcription = lines[i+1]

            # Store the result
            if training:
                utt = int(line[2])
                self.trainingTranscriptions[utt] = transcription
            else:
                utt = int(line[1])
                self.transcriptions[utt] = transcription

    def testUtterances(self, groundTruth):
        """ Given a list of groundTruth utterance text, returns the total
            number of insertion, deletion and substitution errors the user had
            in total """
        if len(groundTruth) != len(self.transcriptions):
            raise Exception("The number of ground truth trancriptions must match"
                    + " the number of actual transcriptions")

        # For each transcription, DTW
        insertions = 0
        deletions = 0
        substitutions = 0
        for (test,actual) in zip(self.transcriptions, groundTruth):
            (dist, ins, dels, subs) = dtw(test.split(), actual.split())

            # Add the error counts
            insertions += ins
            deletions += dels
            substitutions += subs

        # Return the error counts
        return (insertions, deletions, substitutions)


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
    results = readResults("../app/results")

    # TODO: read in ground truth and test


if __name__ == "__main__":
    main()
