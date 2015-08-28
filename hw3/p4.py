import sys
from collections import defaultdict
from itertools import *
import gzip
import cPickle as pickle

# Save an object to a file
def save_obj(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

class IBM1:
    def __init__(self):
        self.t = defaultdict(dict)
        self.p = defaultdict(set)
    def load(self, engz='corpus.en.gz', degz='corpus.de.gz'):
        # Load trainning data from corpus files
        enfi = gzip.open(engz)
        defi = gzip.open(degz)
        self.para = map(lambda t: (t[0].strip().split(' '), t[1].strip().split(' ')), izip(enfi, defi))
    def init(self):
        # Generate possible pair of words according to parallel sentence
        for e, f in self.para:
            self.p["NULL"].update(f)
            for ew in e:
                self.p[ew].update(f)
        # Initialize t(f|e) = 1/n(e)
        for ew in self.p:
            ne = len(self.p[ew])
            t = 1./ne
            for fw in self.p[ew]:
                self.t[ew][fw] = t
    def train(self, S=5):
        # run S rounds of EM iteration
        for s in range(S):
            c1 = defaultdict(float)
            c2 = defaultdict(float)
            for e, f in self.para:
                # Add a NULL to the head of English sentence
                e = ["NULL"] + e
                m, l = len(f), len(e)
                for i in xrange(m):
                    sd = 0
                    for j in xrange(l):
                        sd += self.t[e[j]][f[i]]
                    for j in xrange(l):
                        delta = self.t[e[j]][f[i]] / sd
                        c2[(e[j], f[i])] += delta
                        c1[e[j]] += delta
                        #c[(j, i, l, m)] += delta
                        #c[(i, l, m)] += delta
            # Update t according to c
            for ew in self.p:
                for fw in self.p[ew]:
                    self.t[ew][fw] = c2[(ew, fw)]/c1[ew]
    def trans_words(self, infile='devwords.txt', outfile='t_model1.txt'):
        infi = open(infile)
        oufi = open(outfile, 'w')
        for w in infi:
            oufi.write(w)
            ew = w.strip()
            fws = self.p[ew]
            wd = { fw:self.t[ew][fw] for fw in fws }
            topten = sorted(wd, key=wd.get, reverse=True)[:10]
            oufi.write("%s\n\n" % map(lambda x: (x, wd[x]), topten))
    def alignments(self, n=20, outfile='alignment_model1.txt'):
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
                    # find argmax t(f_i|e_j)
                    if self.t[e[j]][f[i]]>self.t[e[a[i]]][f[i]]:
                        a[i] = j
            oufi.write("%s\n\n" % a)
    def output_parameters(self, tfile='t_m1.dat', pfile='p_m1.dat'):
        save_obj(self.t, tfile)
        save_obj(self.p, pfile)



if __name__ == "__main__":
    i = IBM1()
    i.load()
    i.init()
    i.train()
    i.trans_words()
    i.alignments()
    i.output_parameters()