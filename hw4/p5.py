from collections import defaultdict
from p4 import *

class HM2(HM):

    def init(self, train_file='tag_train.dat'):
        self.gold_server = Server(["python", "tagger_history_generator.py",  "GOLD"])
        self.train_sents = list(sentence_iterator(open(train_file)))
        self.enum = []
        self.gold = []
        for sent in self.train_sents:
            rsent = "\n".join(sent)
            self.enum.append(self.enum_server.call(rsent))
            self.gold.append(self.gold_server.call(rsent))


    def get_feat(self, history, sent):
        hs = history.split()
        word = sent[int(hs[0])-1].split()[0]
        return [":".join(("TAG", word, hs[2]))] + \
        [":".join(("BIGRAM", hs[1], hs[2]))] + \
        [":".join(("SUFF", word[-i:], hs[2])) for i in range(1, 1+min(3, len(word)))]


    def train(self, K=5, outfile='suffix_tagger.model'):
        of = open(outfile, 'w')
        for k in range(K):
            for i in range(len(self.train_sents)):
                sent = self.train_sents[i]
                rsent = "\n".join(sent)
                enum = self.enum[i]
                gold = self.gold[i]
                scored_h = []
                for h in enum:
                    feat = self.get_feat(h, sent)
                    score = sum(map(lambda f:self.model[f], feat))
                    scored_h.append(h + "\t" + str(score))
                scored_h = "\n".join(scored_h)
                result = self.decoder_server.call(scored_h)
                for i in range(len(sent)):
                    gh = gold[i]
                    rh = result[i]
                    if gh!=rh:
                        feat_g = self.get_feat(gh, sent)
                        feat_r = self.get_feat(rh, sent)

                        for f in feat_g:
                            self.model[f] += 1
                        for f in feat_r:
                            self.model[f] -= 1

        for key in self.model:
            if self.model[key]:
                of.write("%s %d\n" % (key, self.model[key]))


if __name__ == "__main__":
    m = HM2()
    m.init()
    m.train()
    m.test(outfile="tag_dev_suffix.out")