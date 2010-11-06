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
    index = updatePieceIndex()
    for name in index.keys():
        bImage = Image.open("b" + name + ".gif")
        wImage = Image.open("w" + name + ".gif")

        #top = topColorIndex(bImage)
        #pal = colorPalette(bImage)
        #print pal[top]

        blue = indexForColor(bImage, BLUE)
        if blue is None:
            print "Warning: missing blue (%s):" % (BLUE,), "b"+name+".gif"

        #print "@",top

        def replace(pixel):
            if pixel == blue:
                return 255
            else:
                return pixel

        new = bImage.point(replace)
        saveImage(new, "/tmp/test/r" + name + ".gif")

def indexForColor(image, rgb):
    indexToRGB = colorPalette(image)
    rgbToIndex = {v:k for k, v in enumerate(indexToRGB)}

    index = rgbToIndex.get(rgb)

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

def updatePieceIndex():
    """Get the index of pieces, generating if needed."""
    if os.path.exists(INDEX_FILE):
        # Preserve existing metadata if any
        index = json.loads(file(INDEX_FILE).read())
    else:
        index = {}

    # Go through each image
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

    for name, colors in byName.iteritems():
        if "b" in colors and "w" in colors:
            index[name] = {
                    # TODO: Remove this. All colors should be available!
                    "colors": colors
                    }
        else:
            # These are not considered pieces
            print "Warning: missing images:", colors, name

    # TODO: more info (credits, don't overwrite but reconcile existing), make the list a dict

    file(INDEX_FILE, "w").write(json.dumps(index, indent=1))

    print "Loaded %s pieces" % (len(index.keys()),)

    return index

if __name__ == "__main__":
    main()
