from p5 import *

class HM3(HM2):

    def get_feat(self, history, sent):
        hs = history.split()
        word = sent[int(hs[0])-1].split()[0]
        prevword = sent[int(hs[0])-2].split()[0] if int(hs[0])>1 else '*'
        nextword = sent[int(hs[0])].split()[0] if int(hs[0])<len(sent) else 'STOP'

        return [":".join(("TAG", word, hs[2]))] + \
        [":".join(("BIGRAM", hs[1], hs[2]))] + \
        [":".join(("SUFF", word[-i:], hs[2])) for i in range(1, 1+min(3, len(word)))] + \
        [":".join(("PREF", word[:i], hs[2])) for i in range(1, 1+min(2, len(word)))] + \
        [":".join(("PREVTAG", word, hs[1], hs[2]))] + \
        [":".join(("PREVWORD", prevword, hs[2]))] + \
        [":".join(("PREVSUFF", prevword[-i:], hs[2])) for i in range(1, 1+min(3, len(word)))] + \
        [":".join(("NEXTSUFF", nextword[-i:], hs[2])) for i in range(1, 1+min(3, len(word)))]

if __name__ == "__main__":
    m = HM3()
    m.init()
    m.train(outfile='best_tagger.model')
    m.test(outfile="tag_dev_best.out")