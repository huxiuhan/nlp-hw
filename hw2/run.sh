## Question 4:
# replace infrequent words in original training data with _RARE_
python p4.py parse_train.dat > ./output/rare_parse_train.dat
python count_cfg_freq.py ./output/rare_parse_train.dat > ./output/rare_parse_train.counts

# pretty print the new training data
python pretty_print_tree.py ./output/rare_parse_train.dat > ./output/rare_parse_train_pretty.dat

## Question 5:
# use CKY algorithm to compute parse tree with maximized probabilities on the test data
time python p5.py ./output/rare_parse_train.counts parse_dev.dat > ./output/p5_prediction

echo --------------BASIC CKY RESULT---------------
python eval_parser.py parse_dev.key ./output/p5_prediction

## Question 6:
# Again, replace infrequent words in original training data `parse_train_vert.dat`
# But we use Count(x) < 2 as threshold for infrequent words
python p4.py parse_train_vert.dat 2 > ./output/rare_parse_train_vert.dat
python count_cfg_freq.py ./output/rare_parse_train_vert.dat > ./output/rare_parse_train_vert.counts

# use CKY algorithm again to get result
time python p6.py ./output/rare_parse_train_vert.counts parse_dev.dat > ./output/p6_prediction

echo ---CKY RESULT FOR VERTICAL MARKOVIZATION DATA---
python eval_parser.py parse_dev.key ./output/p6_prediction
