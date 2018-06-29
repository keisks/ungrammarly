#!/bin/bash
# drop all morpho-syntactic information
python generate.py --drop_all_func --source ../rep-gram-acc/corpora/colorlessgreenRNNs/data/wiki-all.txt > ../monolingualGEC/corpora/wiki-all.lemma.txt &
# stochastically inject errors (10%)
python generate.py --source ../rep-gram-acc/corpora/colorlessgreenRNNs/data/wiki-all.txt --error_rate_overall 0.1 > ../monolingualGEC/corpora/wiki-all.e10.txt &
# stochastically inject errors (30%)
python generate.py --source ../rep-gram-acc/corpora/colorlessgreenRNNs/data/wiki-all.txt --error_rate_overall 0.3 > ../monolingualGEC/corpora/wiki-all.e30.txt &
# stochastically inject errors (50%)
python generate.py --source ../rep-gram-acc/corpora/colorlessgreenRNNs/data/wiki-all.txt --error_rate_overall 0.5 > ../monolingualGEC/corpora/wiki-all.e50.txt &

