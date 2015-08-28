import sys
from collections import defaultdict
from itertools import *
import gzip
import cPickle as pickle

def save_obj(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_obj(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

class IBM2:
    def __init__(self):
        self.t = defaultdict(dict)
        self.p = defaultdict(set)
        self.q = defaultdict(dict)
    def load(self, engz='corpus.en.gz', degz='corpus.de.gz'):
        enfi = gzip.open(engz)
        defi = gzip.open(degz)
        self.para = map(lambda t: (t[0].strip().split(' '), t[1].strip().split(' ')), izip(enfi, defi))
    def init(self, tfile='t_m1.dat', pfile='p_m1.dat'):
        for e, f in self.para:
            e = ["NULL"] + e
            m, l = len(f), len(e)
            for i in xrange(m):
                for j in xrange(l):
                    # Initialize q(j|i,l,m) = 1 / l
                    # Because l is already added 1
                    self.q[(i, l, m)][j] = 1. / l
        self.t = load_obj(tfile)
        self.p = load_obj(pfile)

    def train(self, S=5):
        # run S rounds of EM iteration
        for s in range(S):
            c1 = defaultdict(float)
            c2 = defaultdict(float)
            c3 = defaultdict(float)
            c4 = defaultdict(float)
            for e, f in self.para:
                e = ["NULL"] + e
                m, l = len(f), len(e)
                for i in xrange(m):
                    sd = 0
                    for j in xrange(l):
                        sd += self.t[e[j]][f[i]] * self.q[(i, l, m)][j]
                    for j in xrange(l):
                        delta = self.t[e[j]][f[i]] * self.q[(i, l, m)][j] / sd
                        c2[(e[j], f[i])] += delta
                        c1[e[j]] += delta
                        c4[(j, i, l, m)] += delta
                        c3[(i, l, m)] += delta
            for ew in self.p:
                for fw in self.p[ew]:
                    self.t[ew][fw] = c2[(ew, fw)]/c1[ew]
            for e, f in self.para:
                e = ["NULL"] + e
                m, l = len(f), len(e)
                for i in xrange(m):
                    for j in xrange(l):
                        self.q[(i, l, m)][j] = c4[(j, i, l, m)] / c3[(i, l, m)]
    def alignments(self, n=20, outfile='alignment_model2.txt'):
        oufi = open(outfile, 'w')
        for k in xrange(n):
            e, f = self.para[k]
            oufi.write("%s\n" % " ".join(e))
            oufi.write("%s\n" % " ".join(f))
            e = ["NULL"] + e
            m, l = len(f), len(e)
            a = [0] * m
            for i in xrange(m):
                for j in xrange(l):
                    # find argmax q(j|i,l,m)*t(f_i|e_j)
                    if self.t[e[j]][f[i]]*self.q[(i, l, m)][j]>self.t[e[a[i]]][f[i]]*self.q[(i, l, m)][a[i]]:
                        a[i] = j
            oufi.write("%s\n\n" % a)

    def output_parameters(self, tfile='t_m2.dat', pfile='p_m2.dat', qfile='q_m2.dat'):
        save_obj(self.t, tfile)
        save_obj(self.p, pfile)
        save_obj(self.q, qfile)

if __name__ == "__main__":
    i = IBM2()
    i.load()
    i.init()
    i.train()
    i.alignments()
    i.output_parameters()
