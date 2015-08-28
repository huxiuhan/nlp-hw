import sys
from collections import defaultdict
import math

def usage():
    print """
    python p5_1.py [count_file] > [output_file]
        print log probability for each trigram in count_file
    python p5_1.py [count_file] [trigram_file] > [output_file]
        print log probability for each trigram in trigram_file
    """

def trigram_iterator(trigram_file):
    """
    yield trigram
    """
    l = trigram_file.readline()

    while l:
        line = l.strip()
        if line:
            yield tuple(line.split(" "))
        l = trigram_file.readline()

def ngram_iterator(count_file):
    """
    yield (count, n, ne_tags)
    """
    l = count_file.readline()

    while l:
        line = l.strip()
        if line:
            fields = line.split(" ")
            if fields[1].endswith('-GRAM'):
                count = int(fields[0])
                n = int(fields[1].replace("-GRAM",""))
                ne_tags = tuple(fields[2:])
                yield count, n, ne_tags
        l = count_file.readline()


class Tagger(object):
    """
    Tagging words in dev data
    """

    def __init__(self):
        self.q = defaultdict(int)
        self.gc = defaultdict(int)

    def train(self, count_file):
        """
        Train: calc q(y3|y1,y2)
        """

        for count, n, ne_tags in ngram_iterator(count_file):
            self.gc[ne_tags] = count
            if n==3:
                self.q[ne_tags] = float(count) / self.gc[ne_tags[:-1]]

    def writelogq(self, output, trigram_file = None):
        """
        Print log probability for each trigram q(y3|y1,y2)
        if q(y3|y1,y2)==0 print -inf
        """
        t = self.q.keys()
        if trigram_file:
            t = trigram_iterator(trigram_file)
        for trigram in t:
                if self.q[trigram]:
                    output.write("%s %s %s %f\n" % ( trigram + (math.log(self.q[trigram]),)))
                else:
                    output.write("%s %s %s %s\n" % ( trigram + ("-inf",)))



if __name__ == "__main__":
    if len(sys.argv)!=2 and len(sys.argv)!=3: # Expect exactly one or two argument
        usage()
        sys.exit(2)

    try:
        count_file = file(sys.argv[1],"r")
        if len(sys.argv) == 3:
            trigram_file = file(sys.argv[2],"r")

    except IOError:
        sys.stderr.write("ERROR: Cannot read input file %s.\n" % sys.argv[1:])
        sys.exit(1)

    t = Tagger()
    t.train(count_file)
    if len(sys.argv) == 3:
        t.writelogq(sys.stdout, trigram_file)
    else:
        t.writelogq(sys.stdout)