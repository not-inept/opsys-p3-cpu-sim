"""
    Project 3 Input Generator

    John Drogo
    11/23/2015
"""

import random
import sys
import hashlib

maxsize = 50

alpha = [ chr(x) for x in range(65, 91) ]
random.shuffle(alpha)

if (len(sys.argv) == 2 and sys.argv[1] == "-n"):
    filenumber = random.randint(0, 90000);
    sys.stdout.write("sampleFile{0}".format(filenumber))
    sys.stdout = open("sampleFile{0}".format(filenumber), "w")

for process in alpha:
    if (random.randint(0, 1)):
        print "#"+ " ".join([ "".join([ chr(random.randint(32, 124)) for i in range(random.randint(1, 7)) ]) for j in range(random.randint(1, 14)) ])
    print "|".join([process, #id
        str(random.randint(1, 2000)), #arrival time
        str(random.randint(1, 1000)), #burst time
        str(random.randint(1, 10)), #num bursts
        str(random.randint(1, 5000)), #io-time
        str(random.randint(0, 100))]) #memory
