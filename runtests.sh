#! /bin/bash

start=$(date +%S)

cd test
count=0
for filename in *INPUT.txt;
do
    count=$(bc<<<"$count+1")
    echo "--------"
    echo "Running: $filename"
    python ../BananaComqautPeachApplePinenut.py ${filename} > ${filename}"OUTPUT.txt"
    mv -f simout.txt ${filename}"SIMOUT.txt"
    echo "--------"
    echo
done

echo

date
end=$(date +%S)

diff=$(bc <<< "$end-$start")
echo "Ran $count test cases. In $diff seconds."

cd ..
