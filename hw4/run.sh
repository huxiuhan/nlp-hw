## Question 4:
# Load tag.model and use model to test on tag_dev.dat
# Input: tag.model, tag_dev.dat
# Output: tag_dev.out
echo "--------Question 4--------"
time python p4.py
python eval_tagger.py tag_dev.key tag_dev.out

## Question 5:
# Load train model with SUFF feature and use model to test on tag_dev.dat
# Input: tag_train.dat, tag_dev.dat
# Output: suffix_tagger.model, tag_dev_suffix.out
echo "--------Question 5--------"
time python p5.py
python eval_tagger.py tag_dev.key tag_dev_suffix.out

## Question 6:
# Use three different set of features to train model
# Input: tag_train.dat, tag_dev.dat
echo "--------Question 6--------"

# Output1: prefix_tagger.model, tag_dev_prefix.out
echo "--------Q6P1: TAG, BIGRAM, SUFF(3), PREF(2)--------"
time python p6_1.py
python eval_tagger.py tag_dev.key tag_dev_prefix.out

# Output2: prevword_tagger.model, tag_dev_prevword.out
echo "--------Q6P2: TAG, BIGRAM, SUFF(3), PREF(2), PREVWORD--------"
time python p6_2.py
python eval_tagger.py tag_dev.key tag_dev_prevword.out

# Output3: best_tagger.model, tag_dev_best.out
echo "--------Q6P3: TAG, BIGRAM, SUFF(3), PREF(2), PREVWORD, PREVTAG, PREVSUFF, NEXTSUFF --------"
time python p6_3.py
python eval_tagger.py tag_dev.key tag_dev_best.out