## Question 4:
# Implement IBM Model 1 to get t(f|e) and find alignments
# Input: corpus.en.gz, corpus.de.gz, devwords.txt
# Output: 
# t_model1.txt: the list of the 10 foreign words with the highest t(f|e) for words in devwords.txt
# alignment_model1.txt: the alignments for first 20 sentence pairs in the trainning data
# t_m1.dat: t(f|e) parameters for any pair of words
# p_m1.dat: possible pairs of words in two languages
python -m cProfile ./p4.py


## Question 5:
# Implement IBM Model 2 to get t(f|e), q(j|i,l,m) and find alignments
# Input: corpus.en.gz, corpus.de.gz, t_m1.dat, p_m1.dat
# Output: 
# alignment_model2.txt: the alignments for first 20 sentence pairs in the trainning data
# t_m2.dat: t(f|e) parameters for any pair of words
# p_m2.dat: possible pairs of words in two languages
# q_m2.dat: q(j|i,l,m) parameters for all possible (j, i, l, m) tuple
python -m cProfile ./p5.py

## Question 6:
# Use built IBM Model 2 to find best matched English-German sentence pairs
# Input: t_m2.dat, p_m2.dat, q_m2.dat, scrambled.en, original.de
# Output: 
# unscrambled.en: best sentence match from scrambled.en in order of the original German sentences
python -m cProfile ./p6.py
# evaluate the accuracy
python eval_scramble.py unscrambled.en original.en
