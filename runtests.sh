#! /bin/bash

start=$(date +%S)

cd test
count=0
for filename in *[!T].txt;
do
    count=$(bc<<<"$count+1")
    echo "--------"
    echo "Running: $filename"
    python ../BananaComquatPeachApplePinenut.py ${filename} > ${filename:0:${#filename}-3}"OUTPUT.txt"
    mv -f simout.txt ${filename:0:${#filename}-4}"SIMOUT.txt"
    echo "--------"
    echo
done

echo

date
end=$(date +%S)

diff=$(bc <<< "$end-$start")
echo "Ran $count test cases. In $diff seconds."

cd ..
