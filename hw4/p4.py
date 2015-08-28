import sys
import subprocess
from collections import defaultdict
from subprocess import PIPE

class Server:
    def __init__(self, args):
      "Create a 'server' to send commands to."
      self.process = subprocess.Popen(args, stdin=PIPE, stdout=PIPE)

    def __del__(self):
        self.process.terminate()

    def call(self, stdin):
      "Send command to a server and get stdout as list."
      process = self.process
      process.stdin.write(stdin + "\n\n")
      output = []
      line = process.stdout.readline().strip()
      while line:
        output.append(line)
        line = process.stdout.readline().strip()
      return output

def sentence_iterator(fin):
    """
    yield sentence from a corpus file
    """
    current_sentence = []
    l = fin.readline()
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
        l = fin.readline()

class HM:
    def __init__(self):
        self.model = defaultdict(float)
        self.enum_server = Server(["python", "tagger_history_generator.py",  "ENUM"])
        self.decoder_server = Server(["python", "tagger_decoder.py",  "HISTORY"])

    def read_model(self, tag_model_file="tag.model"):
        fi = open(tag_model_file)
        tag_model = self.model
        for l in fi:
            t = l.split(' ')
            tag_model[t[0]] = float(t[1])

    def get_feat(self, history, sent):
        hs = history.split()
        word = sent[int(hs[0])-1].split()[0]
        return [":".join(("TAG", word, hs[2]))] + \
        [":".join(("BIGRAM", hs[1], hs[2]))];


    def test(self, untagged_file="tag_dev.dat" ,outfile="tag_dev.out"):
        sents = sentence_iterator(open(untagged_file))
        of = open(outfile, 'w')

        for sent in sents:
            rsent = "\n".join(sent)
            enum = self.enum_server.call(rsent)
            scored_h = []
            for h in enum:
                feat = self.get_feat(h, sent)
                score = sum(map(lambda f:self.model[f], feat))
                scored_h.append(h + "\t" + str(score))
            scored_h = "\n".join(scored_h)
            result = self.decoder_server.call(scored_h)
            for i in range(len(sent)):
                hs = result[i].split()
                word = sent[i]
                of.write("%s\t%s\n" % (word, hs[2]))
            of.write("\n")
        of.close()


if __name__ == "__main__": 
    hm = HM()
    hm.read_model()
    hm.test()