#! /usr/bin/python

__date__ ="$Mar 9, 2015"

import sys, json
from collections import defaultdict

"""
CKY Algorithm for PCFG
"""

class CKY:
  def __init__(self):
    self.q = defaultdict(float)
    self.ur = defaultdict(set)
    self.br = defaultdict(set)
    self.N = defaultdict(int)
    self.words = set()

  def read_counts(self, counts_file):
    # read counts file to tran parameters we need for CKY algorithm
    for l in open(counts_file):
      line = l.strip()
      if line:
        fields = line.split(" ")
        if fields[1] == "NONTERMINAL":
          # record all non-terminals and their counts
          self.N[fields[2]] = int(fields[0])
        elif fields[1] == "UNARYRULE":
          # q(X->w) = C(X->w)/C(X)
          self.q[(fields[2], fields[3])] = float(fields[0])/self.N[fields[2]]
          # add w to the unary rules set of X
          self.ur[fields[2]].add(fields[3])
          # add w to words dictionary
          self.words.add(fields[3])
        elif fields[1] == "BINARYRULE":
          # q(X->Y1Y2) = C(X->Y1Y2)/C(X)
          self.q[(fields[2], fields[3], fields[4])] = float(fields[0])/self.N[fields[2]]
          # add (Y1, Y2) to binary rule set of X
          self.br[fields[2]].add((fields[3], fields[4]))

  def cky(self, sent):
    pi = defaultdict(float)
    bp = defaultdict(tuple)

    n = len(sent)
    # To align the sentence with pi, the first char of s is s[1]
    sent = ['*'] + sent
    # store the original sentence
    origin_sent = list(sent)
    # replace unseen words with _RARE_
    for i in xrange(1, n+1):
      if sent[i] not in self.words:
        sent[i] = "_RARE_"
    # init pi(i,i,X) = q(X, xi)
    for i in xrange(1, n+1):
      for X in self.ur:
        pi[(i, i, X)] = self.q[(X,sent[i])]

    # main loops for CKY algorithm
    for l in xrange(1, n):
      for i in xrange(1, n-l+1):
        j = i + l
        for X in self.br:
          for Y,Z in self.br[X]:
            for s in xrange(i, j):
              npi = self.q[(X, Y, Z)]*pi[(i,s,Y)]*pi[(s+1,j,Z)]
              if pi[(i, j, X)]< npi:
                # dp function
                pi[(i, j, X)] = npi
                # back pointer
                bp[(i, j, X)] = (Y, Z, s)

    # position for answer in pi
    ran = (1, n, "S")

    # if we cant find (1, n, S), we search the max value on all non-terminals
    if not pi[ran]:
      for X in self.N:
        if pi[(1, n, X)]>pi[ran]:
          ran = (1, n, X)

    # function to build parse tree in required data structure recursively
    def buildtree(ran):
      i, j, X = ran
      if i==j:
        return [X, origin_sent[i]]
      Y, Z, s = bp[ran]
      # left part
      lp = (i, s, Y)
      # right part
      rp = (s+1, j, Z)
      return [X, buildtree(lp), buildtree(rp)]

    # get the built parse tree
    return buildtree(ran)

  def parse(self, corpus_file, output):
    # for every sentence in parse tree, we run cky to get prediction
    for l in open(corpus_file):
      sent = l.strip().split(" ")
      t = self.cky(sent)
      output.write("%s\n" % json.dumps(t))

def main(counts_file, corpus_file, output):
  c = CKY()
  c.read_counts(counts_file)
  c.parse(corpus_file, output)

def usage():
    sys.stderr.write("""
    Usage: python p5.py [counts_file] [corpus_file] > [tree_file]
        CKY algorithm parsing sentence in corpus_file.\n""")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    usage()
    sys.exit(1)
  main(sys.argv[1], sys.argv[2], sys.stdout)