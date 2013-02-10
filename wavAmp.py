import os, sys
from scipy.io import wavfile

fn1 = sys.argv[1]

print "reading", fn1
typ, d1 = wavfile.read(fn1)

mx = 0

for frm in d1:
    for samp in frm:
        if abs(samp) > mx:
            mx = abs(samp)

print "max abs(sample):", mx
