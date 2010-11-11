# -*- coding: utf-8 -*-

import sys

import urllib2
import pytrailer
import re

resMatcher = re.compile(r"_h([0-9]+p?)\.mov")

jsonURL = "http://trailers.apple.com/trailers/home/feeds/genres.json"

movies = pytrailer.getMoviesFromJSON(jsonURL)

i = 0
for movie in movies:
    desc = ", ".join([x["type"] for x in movie.trailers])
    print "%d\t%s [%s]" % (i, movie.title, desc)
    i += 1

sys.stdout.write("Choose movie: ")
selection = sys.stdin.readline()

index = 0
try:
    index = int(selection)
except:
    print "You are a moron!"
    sys.exit(1)

toload = movies[index]

i = 0
for name, trailer in toload.trailerLinks.items():
    print "%d\t%s" % (i, name)
    i += 1

sys.stdout.write("Choose trailer: ")
selection = sys.stdin.readline()

index = 0
try:
    index = int(selection)
except:
    print "You are a moron!"
    sys.exit(1)

selected = toload.trailerLinks.values()[index]
trailerName = toload.trailerLinks.keys()[index]

i = 0
for link in selected:
    print "%d\t%s" % (i, link)
    i += 1

sys.stdout.write("Choose resolution: ")
selection = sys.stdin.readline()

index = 0
try:
    index = int(selection)
except:
    print "You are a moron!"
    sys.exit(1)

link = selected[index]
res = resMatcher.search(link)
if res:
    res = res.group(1)
else:
    res = "unknown"

mov = urllib2.urlopen(urllib2.Request(url=link,headers={"User-Agent": "QuickTime"}))
size = int(mov.info().get("Content-Length"))
if size < 200:
    content = mov.read()
    realfilename = content[44:44+ord(content[43])]
    base = link["url"].rsplit("/", 1)[0]
    reallink = "%s/%s" % (base, realfilename)
    mov = urllib2.urlopen(urllib2.Request(url=reallink,headers={"User-Agent": "QuickTime"}))
    size = int(mov.info().get("Content-Length"))

filename = "%s - %s - %s.mov" % (toload.title, trailerName, res)
target = open(filename, "wb")
print "Downloading %d bytes to %s" % (size, filename)

blocksize = 1024*1024 # one megabyte
full = 0
read = blocksize
while read > 0:
    buffer = mov.read(blocksize)
    read = len(buffer)
    target.write(buffer)
    full += read
    print "got %d of %d bytes" % (full, size)
target.close()
mov.close()

print "DONE!"
