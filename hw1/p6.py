import sys
from collections import defaultdict
import math
import re

def usage():
    print """
    python p6.py [count_file] [untagged_file] > [output_file]
        Improved trigram hmm tagger
    """

dic = set(file("google-tenthousand-english.txt","r").read().splitlines())

def rare_classify(word):
    p_abbr = re.compile("^[A-Z.]+$")
    p_con = re.compile('\+|\-|/|:|,|\.')
    if word.replace(",","").replace(".","").isdigit():
        return "_RARE_NUM_"
    elif p_con.sub("", word).isdigit():
        return "_RARE_NO_"
    elif p_abbr.match(word):
        return "_RARE_ABBR_"
    elif word.upper()==word:
        return "_RARE_ACAP_"
    elif word.startswith(word[0].upper()) and word.lower() in dic:
        return "_RARE_CAPENG_"
    elif word.startswith(word[0].upper()):
        return "_RARE_NAME_"
    else:
        return "_RARE_"


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

def sentence_iterator(untagged_file):
    current_sentence = []
    l = untagged_file.readline()
    while l:
        line = l.strip()
        if line:
            current_sentence.append(line)
        else:
            if current_sentence:
                yield current_sentence
                current_sentence = []
            else:
                sys.stderr.write("WARNING: Got empty input file/stream.\n")
                raise StopIteration
        l = untagged_file.readline()


class Tagger(object):
    """
    Tagging words in dev data
    """

    def __init__(self):
        self.e = defaultdict(int)
        self.q = defaultdict(int)
        self.gc = defaultdict(int)
        self.xyc = defaultdict(dict)

    def train(self, count_file):
        """
        Train: calc q(y3|y1,y2)
        """

        self.xyc = defaultdict(dict)
        words = set()
        tags = set()
        lbd = 0.93
        totwc = 0

        for count, tag, word in word_tag_iterator(count_file):
            #if t.startswith("B-"):
            #    t.replace("B-","I-")
            self.xyc[tag][word] = count
            self.gc[word] += count
            totwc += count
            words.add(word)
            tags.add(tag)

        # smooth emission with lambda
        for tag in self.xyc:
            tagc = sum(self.xyc[tag].values())
            for word in self.xyc[tag]:
                self.e[(tag, word)] = lbd*float(self.xyc[tag][word])/tagc + (1-lbd)*float(self.gc[word])/totwc

        for w in words:
            for t in tags:
                if self.e[(t, w)] == 0:
                    self.e[(t, w)] = (1-lbd)*float(self.gc[w])/totwc

        for count, n, ne_tags in ngram_iterator(count_file):
            self.gc[ne_tags] = count
            if n==3:
                self.q[ne_tags] = float(count) / self.gc[ne_tags[:-1]]

    def predict(self, untagged_file, output):
        """
        Predict: trigram HMM model with Viterbi algorithm
        """

        K = self.e.keys()
        K = set(map(lambda x: x[0], K))
        #print K
        q = self.q
        e = self.e
        #print q
        #print e
        for sent in sentence_iterator(untagged_file):
            origin_sent = sent
            sent = map(lambda x: rare_classify(x) if self.gc[x]==0 else x, sent)
            #print sent
            pi = defaultdict(int)
            bp = defaultdict(str)
            pi[(0, "*", "*")] = 1
            n = len(sent)
            for k in range(1, n+1):
                for v in K:
                    if k==1:
                        u = "*"
                        w = "*"
                        pi[(k, u, v)] = pi[(k-1, w, u)]*q[w, u, v]*e[(v, sent[k-1])]
                        bp[(k, u, v)] = w
                    elif k==2:
                        w = "*"
                        for u in K:
                            tv = pi[(k-1, w, u)]*q[(w, u, v)]*e[(v, sent[k-1])]
                            if tv > pi[(k, u, v)]:
                                pi[(k, u, v)] = tv
                                bp[(k, u, v)] = w
                    else:
                        for u in K:
                            for w in K:
                                tv = pi[(k-1, w, u)]*q[(w, u, v)]*e[(v, sent[k-1])]
                                if tv > pi[(k, u, v)]:
                                    pi[(k, u, v)] = tv
                                    bp[(k, u, v)] = w
            maxP = 0
            maxu = ""
            maxv = ""
            if n==1:
                u = "*"
                for v in K:
                    if pi[(n,u,v)]*q[(u,v, "STOP")]>maxP:
                        maxP = pi[(n,u,v)]*q[(u,v, "STOP")]
                        maxu = u
                        maxv = v
            else:
                for u in K:
                    for v in K:
                        if pi[(n,u,v)]*q[(u,v,"STOP")]>maxP:
                            maxP = pi[(n,u,v)]*q[(u,v,"STOP")]
                            maxu = u
                            maxv = v
            v = maxv
            u = maxu
            tags = [v, u]
            logp = [math.log(maxP), math.log(pi[(n, u, v)])]
            for k in xrange(n, 1, -1):
                w = bp[(k, u, v)]
                tags.append(w)
                logp.append(math.log(pi[(k-1, w, u)]))
                v = u
                u = w

            tags.reverse()
            logp.reverse()

            for i, word in enumerate(origin_sent):
                output.write("%s %s %f\n" % (word, tags[i+1], logp[i]))
            output.write("\n")


if __name__ == "__main__":

    if len(sys.argv)!=3: # Expect exactly two argument
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