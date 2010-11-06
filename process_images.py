#!/usr/bin/python
# Created:20101104
# By Jeff Connelly
#
# Process Alfaerie Omega images

import pprint
import os
import json
import Image

INDEX_FILE = "index.json"

# b*.gif standardize on this blue
BLUE = "#5984bd"

def main():
    names = getPieceIndex()
    for name in names:
        bImage = Image.open("b" + name + ".gif")
        wImage = Image.open("w" + name + ".gif")

        #top = topColorIndex(bImage)
        #pal = colorPalette(bImage)
        #print pal[top]

        top = indexForColor(bImage, BLUE, name)
        #print "@",top

        def replace(pixel):
            if pixel == top:
                return 255
            else:
                return pixel

        new = bImage.point(replace)
        saveImage(new, "/tmp/test/r" + name + ".gif")

def indexForColor(image, rgb, name):
    indexToRGB = colorPalette(image)
    rgbToIndex = {v:k for k, v in enumerate(indexToRGB)}

    index = rgbToIndex.get(rgb)
    if index is None:
        #print "** Image %s has no %s: %s" % (name, rgb, rgbToIndex)
        print name

    return index

def topColorIndex(image):
    """Get the most frequently occurring color index in an image."""

    histogram = image.histogram()
    colors = {}
    maxCount = 0
    top = None

    transparency = image.info.get("transparency")

    for colorIndex, count in enumerate(histogram):
        if colorIndex == transparency:    # transparent is not a color
            continue

        if count > maxCount:
            top = colorIndex
            maxCount = count

    return top


def colorPalette(image):
    """Get the palette mapping the color index to RGB."""

    # This is weird, but we have to call this to make image.im
    histogram = image.histogram()

    # Why isn't this built-into PIL??
    # Based on http://bytes.com/topic/python/answers/444697-retrieve-gifs-palette-entries-using-python-imaging-library-pil
    def chunk(seq, size):
        return [seq[i:i+size] for i in range(0, len(seq), size)]
    palette = image.im.getpalette()
    colors = [map(ord, bytes) for bytes in chunk(palette, 3)]

    # Convert to HTML-like #rrggbb for ease of use
    hexColors = ["#" + "".join(map(lambda octet: "%.2x" % (octet,), rgb)) for rgb in colors]

    return hexColors

def saveImage(image, filename):
    if image.info.has_key("transparency"):
        # PIL Image has no concept of transparency, lame
        # Workaround from http://www.velocityreviews.com/forums/t354000-pil-and-transparent-gifs.html
        kwargs = {"transparency": image.info["transparency"]}
    else:
        kwargs = {}
    image.save(filename, **kwargs)

def getPieceIndex():
    """Get the index of pieces, generating if needed."""
    if False and os.path.exists(INDEX_FILE):
        available = json.loads(file(INDEX_FILE).read())
    else:
        files = os.listdir(".")
        byColor = {}
        byName = {}
        for filename in files:
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

        print " ".join([colors[0] + name + ".gif" for name, colors in byName.iteritems() if len(colors) < 2])

        # Available piece names
        available = [name for name, colors in byName.iteritems() if "b" in colors and "w" in colors]

        # TODO: more info (credits, don't overwrite but reconcile existing), make the list a dict

        file(INDEX_FILE, "w").write(json.dumps(available))

    print "Loaded %s pieces" % (len(available),)

    return available

if __name__ == "__main__":
    main()
