#!/usr/bin/python
# Created:20101104
# By Jeff Connelly
#
# Process Alfaerie Omega images

import pprint
import os
import Image

def main():
    names = availablePieces()
    print "Loaded %s pieces" % (len(names),)
    for name in names:
        bImage = Image.open("b" + name + ".gif")
        wImage = Image.open("w" + name + ".gif")

        saveImage(bImage, "/tmp/a" + name + ".gif")

def saveImage(image, filename):
    if image.info.has_key("transparency"):
        # PIL Image has no concept of transparency, lame
        # Workaround from http://www.velocityreviews.com/forums/t354000-pil-and-transparent-gifs.html
        kwargs = {"transparency": image.info["transparency"]}
    else:
        kwargs = {}
    image.save(filename, **kwargs)

def availablePieces():
    # TODO: Instead of all this directory junk, read an index (issue #6)
    files = os.listdir(".")
    byColor = {}
    byName = {}
    for filename in files:
        if filename.startswith("gr"):
            prefix = "gr"
            rest = filename[2:]
        elif filename.startswith("lb"):
            prefix = "lb"
            rest = filename[2:]
        else:
            prefix = filename[0]
            rest = filename[1:]

        if "." not in rest:
            continue
        name, suffix = rest.rsplit(".", 1)
        if suffix != "gif":
            continue

        if not byColor.has_key(prefix):
            byColor[prefix] = {}
        if not byName.has_key(name):
            byName[name] = []

        byColor[prefix][name] = True
        byName[name].append(prefix)

    #print [(name, colors) for name, colors in byName.iteritems() if len(colors) < 2]

    # Available pieces
    return [name for name, colors in byName.iteritems() if "b" in colors and "w" in colors]

if __name__ == "__main__":
    main()
