import sys
from collections import defaultdict
from math import log
import cPickle as pickle

def save_obj(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_obj(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

class IBM2u:
    def __init__(self):
        self.t = defaultdict(dict)
        self.p = defaultdict(set)
        self.q = defaultdict(dict)

    def load(self, tfile='t_m2.dat', pfile='p_m2.dat', qfile='q_m2.dat'):
        self.t = load_obj(tfile)
        self.p = load_obj(pfile)
        self.q = load_obj(qfile)

    def unscramble(self, scrambled='scrambled.en', original='original.de', output='unscrambled.en'):
        sf = open(scrambled)
        gf = open(original)
        of = open(output, 'w')
        e_sent = map(lambda t: t.strip().split(' '), sf)
        f_sent = map(lambda t: t.strip().split(' '), gf)
        for f in f_sent:
            maxp = float('-inf')
            maxa = []
            maxe = []
            m = len(f)
            for e in e_sent:
                p = 0
                e = ["NULL"] + e
                l = len(e)
                a = [0] * m
                for i in xrange(m):
                    for j in xrange(l):
                        try:
                            if self.t[e[j]][f[i]]*self.q[(i, l, m)][j]>self.t[e[a[i]]][f[i]]*self.q[(i, l, m)][a[i]]:
                                a[i] = j
                        except:
                            pass
                for i in xrange(m):
                    try:
                        p += log(self.t[e[a[i]]][f[i]]*self.q[(i, l, m)][a[i]])
                    except:
                        p += -0xffffff
                if p > maxp:
                    maxp = p
                    maxa = a
                    maxe = e
            of.write("%s\n" % ' '.join(maxe[1:]))

if __name__ == "__main__":
    i = IBM2u()
    i.load()
    i.unscramble()
