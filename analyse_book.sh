#!/bin/bash

# $0 is the script name, $1 id the first ARG, $2 is second...

python convert_to_wav_and_merge.py $1 $2
python split_book.py $2
python long_segments.py $2
python text_format.py $2
python data_set_from_wav_text.py $2
mkdir /media/sam/seraph/data/data-$2
cp -a data/$2* /media/sam/seraph/data/data-$2
rm -rf data/$2*
