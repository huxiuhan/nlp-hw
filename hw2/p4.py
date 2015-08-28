#! /usr/bin/python

__date__ ="$Mar 9, 2015"

import sys, json
from collections import defaultdict


"""
Count rule frequencies in a binarized CFG.
Replace infrequent words with _RARE_
"""

class Counts:
  def __init__(self):
    self.words = defaultdict(int)

  def count(self, tree):
    """
    Count the frequencies of words in the tree.
    """
    if isinstance(tree, basestring): return

    # Count the non-terminal symbol.

    if len(tree) == 3:
      # recursive dealing with children tree
      self.count(tree[1])
      self.count(tree[2])
    elif len(tree) == 2:
      # leaf node denote the X->w rules, do word count
      self.words[tree[1]] += 1

  def rarewords(self, tree, threshold):
    """
    Replace infrequent words with _RARE_.
    """
    if isinstance(tree, basestring): return
    if len(tree) == 3:
      # recurive replacing rare words
      self.rarewords(tree[1], threshold)
      self.rarewords(tree[2], threshold)
    elif len(tree) == 2:
      if self.words[tree[1]]<threshold:
        tree[1] = "_RARE_"

def main(parse_file, output, threshold):
  counter = Counts()
  # read all data in parse_file and count words
  for l in open(parse_file):
    t = json.loads(l)
    counter.count(t)

  # according to word counts, replace infrequent words with _RARE_
  for l in open(parse_file):
    t = json.loads(l)
    counter.rarewords(t, threshold)
    #output the json file with json.dumps
    output.write("%s\n" % json.dumps(t))


def usage():
    sys.stderr.write("""
    Usage: python p4.py [tree_file] [OPTIONAL threshold]
        Replace infrequent words (count < threshold) with _RARE_ in a corpus of trees.\n""")

if __name__ == "__main__":
  if len(sys.argv) != 2 and len(sys.argv) != 3:
    usage()
    sys.exit(1)
  try:
    threshold = int(sys.argv[2])
  except:
    threshold = 5
  main(sys.argv[1], sys.stdout, threshold)
  
