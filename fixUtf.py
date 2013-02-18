#!/usr/bin/python
import sys, os, codecs

f = codecs.open(sys.argv[1], 'r', "utf-8")
s = f.read()
print "len:", len(s)
f.close()

f = open(sys.argv[2], "w")

i = 0
for c in s:
    if ord(c) > 127:
        print "bad char at", i, hex(ord(c))
        if ord(c) == 0xffa0:
            c = chr(0xa0)
    f.write(c)
    i += 1

f.close()
