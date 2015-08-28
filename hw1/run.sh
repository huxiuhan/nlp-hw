## Preperation
python count_freqs.py ner_train.dat > ./output/ner_origin.counts

## Question 4:
# replace infrequent words in original training data with _RARE_
python p4_1.py ner_train.dat ./output/ner_origin.counts > ./output/ner_train_rare.dat
python count_freqs.py ./output/ner_train_rare.dat > ./output/ner_rare.counts
# use baseline algorithm to get prediction
python p4_2.py ./output/ner_rare.counts ner_dev.dat > ./output/p4_prediction

echo --------------BASELINE RESULT---------------
python eval_ne_tagger.py ner_dev.key ./output/p4_prediction

## Question 5:
# print log probability for each trigram
python p5_1.py ./output/ner_rare.counts > ./output/ner_rare_trigram_p.dat
# use trigram hmm viterbi algorithm to predict tag of words
python p5_2.py ./output/ner_rare.counts ner_dev.dat > ./output/p5_prediction

echo --------------BASIC VITERBI RESULT---------------
python eval_ne_tagger.py ner_dev.key ./output/p5_prediction

## Question 6:
# classify rare words and replace them with a variety of tags
python p6_rare_classify.py ner_train.dat ./output/ner_origin.counts > ./output/ner_train_classified.dat
python count_freqs.py ./output/ner_train_classified.dat > ./output/ner_classified.counts
# use improved viterbi to get result
python p6.py ./output/ner_classified.counts ner_dev.dat > ./output/p6_prediction

echo --------------IMPROVED VITERBI RESULT---------------
python eval_ne_tagger.py ner_dev.key ./output/p6_prediction
