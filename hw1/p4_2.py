import sys
from collections import defaultdict
import math

def usage():
    print """
    python p4_2.py [tagcount_file] [untagged_file] > [output_file]
        Baseline tagger
    """

def word_tag_iterator(count_file):
    """
    yield (count, ne_tag, word)
    """
    l = count_file.readline()
    r = count_file.tell()

    while l:
        line = l.strip()
        if line:
            fields = line.split(" ")
            if fields[1]=='WORDTAG':
                count = int(fields[0])
                word = fields[-1]
                ne_tag = fields[-2]
                yield count, ne_tag, word
            else:
                count_file.seek(r)
                return
        r = count_file.tell()
        l = count_file.readline()

class Tagger(object):
    """
    Tagging words in dev data
    """

    def __init__(self):
        self.ep = defaultdict(dict)
        self.wc = defaultdict(int)

    def train(self, count_file):
        """
        Train: calc emission probabilities for all words
        """

        cxy = defaultdict(dict)
        for count, tag, word in word_tag_iterator(count_file):
            #if t.startswith("B-"):
            #    t.replace("B-","I-")
            cxy[tag][word] = count
            self.wc[word] += count
        for tag in cxy:
            tagc = sum(cxy[tag].values())
            self.ep[tag] = {word: float(cxy[tag][word])/tagc for word in cxy[tag]}

    def predict(self, untagged_file, output):
        """
        Predict: predict tag on dev data with baseline rule
        """
        l = untagged_file.readline()
        while l:
            line = l.strip()
            if line:
                word = line
                if self.wc[word]==0:
                    word = "_RARE_"
                maxTag = ""
                maxE = 0
                for tag in self.ep:
                    if self.ep[tag].has_key(word) and self.ep[tag][word]>maxE:
                        maxE = self.ep[tag][word]
                        maxTag = tag
                output.write("%s %s %f\n" % (line, maxTag, math.log(maxE)))
            else:
                output.write("\n")
            l = untagged_file.readline()

if __name__ == "__main__":

    if len(sys.argv)!=3: # Expect exactly one argument
        usage()
        sys.exit(2)

    try:
        tagcount_file = file(sys.argv[1],"r")
        untagged_file = file(sys.argv[2],"r")

    except IOError:
        sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
        sys.exit(1)

    t = Tagger()
    t.train(tagcount_file)
    t.predict(untagged_file, sys.stdout)


