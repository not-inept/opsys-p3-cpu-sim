#! /bin/bash

for i in {0..5}
do
    filename="$(python inputGenerator.py -n)"
    python BananaComquatPeachApplePinenut.py ${filename} > "test/"${filename}"OUTPUT.txt"
    mv simout.txt "test/"${filename}"SIMOUT.txt"
    mv ${filename} "test/"${filename}".txt"
    echo "Wrote test case $i to test/${filename}INPUT.txt and output to test/${filename}.txt"
done
