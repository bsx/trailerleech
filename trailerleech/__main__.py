# -*- coding: utf-8 -*-

import sys

import urllib2
import json 
import html5lib

baseurl = "http://trailers.apple.com"
trailerinclude = "includes/playlists/web.inc"
movies = json.load(urllib2.urlopen(urllib2.Request(url="http://trailers.apple.com/trailers/home/feeds/genres.json",headers={"User-Agent": "Safari"})))

toload = {}

i = 0
for movie in movies:
    desc = ", ".join([x["type"] for x in movie["trailers"]])
    print "%d\t%s [%s]" % (i, movie["title"], desc)
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

url = "%s%s%s" % (baseurl, toload["location"], trailerinclude)
doc = html5lib.parse(urllib2.urlopen(urllib2.Request(url=url,headers={"User-Agent": "Safari"})), treebuilder="lxml")

trailers = []

match = doc.xpath("//h:ul[@class='trailer-nav']", namespaces={"h": "http://www.w3.org/1999/xhtml"})
if len(match) > 0:
    navigation = match[0]
    for child in navigation.iterchildren(tag="{http://www.w3.org/1999/xhtml}li"):
        name = child.xpath(".//h:span[@class='text']", namespaces={"h": "http://www.w3.org/1999/xhtml"})[0].text
        trailers.append({"name": name})
    content = doc.xpath("//h:div[@class='trailer-content']", namespaces={"h": "http://www.w3.org/1999/xhtml"})[0]
    i = 0
    for child in content.iterchildren(tag="{http://www.w3.org/1999/xhtml}div"):
        trailer = trailers[i]
        trailer["links"] = []
        for link in child.iterdescendants(tag='{http://www.w3.org/1999/xhtml}a'):
            img = link.getchildren()[0]
            href = link.attrib["href"]
            try:
                res = img.attrib["alt"]
                trailer["links"].append({"res": res, "url": href})
            except:
                pass
        i += 1
else:
    match = doc.xpath("//h:li[contains(@class,'trailer')]", namespaces={"h": "http://www.w3.org/1999/xhtml"})
    if len(match) > 0:
        for section in match:
            name = section.xpath(".//h:h3", namespaces={"h": "http://www.w3.org/1999/xhtml"})[0].text
            trailer = {"name": name}
            trailer["links"] = []
            for link in section.xpath(".//h:a[@class='target-quicktimeplayer']", namespaces={"h": "http://www.w3.org/1999/xhtml"}):
                href = link.attrib["href"]
                res = link.text.split(" ")[0]
                trailer["links"].append({"res": res, "url": href})
            trailers.append(trailer)
    else:
        print "BUG: Couldn't parse %s" % url

i = 0
for trailer in trailers:
    resolutions = ", ".join([x["res"] for x in trailer["links"]])
    print "%d\t%s (%s)" % (i, trailer["name"], resolutions)
    i += 1

sys.stdout.write("Choose trailer: ")
selection = sys.stdin.readline()

index = 0
try:
    index = int(selection)
except:
    print "You are a moron!"
    sys.exit(1)

selected = trailers[index]

i = 0
for link in selected["links"]:
    print "%d\t%s" % (i, link["res"])
    i += 1

sys.stdout.write("Choose resolution: ")
selection = sys.stdin.readline()

index = 0
try:
    index = int(selection)
except:
    print "You are a moron!"
    sys.exit(1)

link = selected["links"][index]

mov = urllib2.urlopen(urllib2.Request(url=link["url"],headers={"User-Agent": "QuickTime"}))
size = int(mov.info().get("Content-Length"))
if size < 200:
    content = mov.read()
    realfilename = content[44:44+ord(content[43])]
    base = link["url"].rsplit("/", 1)[0]
    reallink = "%s/%s" % (base, realfilename)
    mov = urllib2.urlopen(urllib2.Request(url=reallink,headers={"User-Agent": "QuickTime"}))
    size = int(mov.info().get("Content-Length"))

filename = "%s - %s - %s.mov" % (toload["title"], selected["name"], link["res"])
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
