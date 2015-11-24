#! /bin/bash

python Project2FINAL.py > test2.out
if [ -n "$(diff simout.txt simout2.txt)" ]
then
    vimdiff simout.txt simout2.txt
else
    echo "Simulations stats match."
fi

if [ -n "$(diff goodtest.out test2.out)" ]
then
    vimdiff goodtest.out test2.out
else
    echo "Simulation outputs match."
fi
