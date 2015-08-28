import sys
from collections import defaultdict
import math

def usage():
    print """
    python p4_1.py [corpus_file] [count_file] > [output_file]
        Replace rare word with _RARE_.
    """

def word_tag_iterator(corpus_file):
    """
    yield (count, ne_tag, word)
    """
    l = corpus_file.readline()
    r = corpus_file.tell()

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
                corpus_file.seek(r)
                return
        r = corpus_file.tell()
        l = corpus_file.readline()

def simple_conll_corpus_iterator(corpus_file):
    """
    Get an iterator object over the corpus file. The elements of the
    iterator contain (word, ne_tag) tuples. Blank lines, indicating
    sentence boundaries return (None, None).
    """
    l = corpus_file.readline()
    while l:
        line = l.strip()
        if line: # Nonempty line
            # Extract information from line.
            # Each line has the format
            # word pos_tag phrase_tag ne_tag
            fields = line.split(" ")
            ne_tag = fields[-1]
            #phrase_tag = fields[-2] #Unused
            #pos_tag = fields[-3] #Unused
            word = " ".join(fields[:-1])
            yield word, ne_tag
        else: # Empty line
            yield (None, None)
        l = corpus_file.readline()



def replace_rare(corpus_file, count_file, output):
    """
    replace rare words in the original corpus file with _RARE_
    """

    cx = defaultdict(int)
    for c, t, w in word_tag_iterator(count_file):
        cx[w] += c

    for w, t in simple_conll_corpus_iterator(corpus_file):
        if w==None:
            output.write("\n")
        elif cx[w]<5:
            output.write("_RARE_ %s\n" % t)
        else:
            output.write("%s %s\n" % (w, t))


if __name__ == "__main__":

    if len(sys.argv)!=3: # Expect exactly two argument
        usage()
        sys.exit(2)

    try:
        corpus_file = file(sys.argv[1],"r")
        count_file = file(sys.argv[2],"r")

    except IOError:
        sys.stderr.write("ERROR: Cannot read input file %s.\n" % arg)
        sys.exit(1)

    replace_rare(corpus_file, count_file, sys.stdout)

