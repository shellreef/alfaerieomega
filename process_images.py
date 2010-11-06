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
    writeIndexDocuments(index)

    for name in sorted(index.keys()):
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
        # Load existing metadata 
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
        if not ("b" in colors and "w" in colors):
            # These are not considered pieces
            print "Warning: missing images:", colors, name
            continue

        if not index.has_key(name):
            print "New piece:", name
            index[name] = {"set": ["Alfaerie Expansion Set 6"]}   #findImageSet("w"+name+".gif")}
        # Otherwise, leave existing entry (preserve metadata)

    # TODO: more info (credits, don't overwrite but reconcile existing), make the list a dict

    #file(INDEX_FILE, "w").write(json.dumps(index, indent=1))
    # Save as JSON for ease usage in other applications
    # Could simply use json.dumps(index), but want the dictionary keys to
    # be sorted to avoid noisy diffs in version control.
    out = file(INDEX_FILE, "w")
    out.write("{\n")

    for i, name in enumerate(sorted(index.keys())):
        info = index[name]
        out.write(' "%s": %s' % (name, json.dumps(info)))

        # JSON spec (and IE, but no one cares about them) require omitting
        # comma for last item in list
        if i != len(index.keys()) - 1:
            out.write(",")

        out.write("\n")
    out.write("}\n")

    print "Loaded %s pieces" % (len(index.keys()),)

    return index

def writeIndexDocuments(index):
    """Write the index in text and HTML formats."""
    text = file("list.txt", "w")
    html = file("master.html", "w")

    html.write("""<!DOCTYPE html>
<html>
<head>
<title>Alfaerie Omega - Piece Index</title>
</head>
<body>
<table>
""")

    i = 1
    for name in sorted(index.keys()):
        #info = index[name]

        text.write(name + "\n")
        html.write("<tr><td>%s</td>" % (i,))
        for color in "wb":
            html.write("""<td><img src="%s%s.gif"></td>""" % (color, name))
        html.write("<td>%s</td>" % (name,))
        html.write("</tr>\n")

        i += 1

    html.write("""</table>
</body>
</html>""")

def findImageSet(name):
    """Find the image sets a piece came from.
    
    This is intended to be called only once, and offer a best guess. 
    Renamed images will have to be manually added."""

    found = []

    # Check each set
    for root, dirs, files in os.walk("sets"):
        for filename in files:
            # Only search top-level alfaerie*.html files...
            # except for misc, which has subfiles to search (only)
            if not (filename.startswith("alf") and filename != "alfaeriemisc.html" or ("sets/misc" in root and filename == "index.html")):
                continue

            path = os.path.join(root, filename)

            data = file(path).read()
            if name.lower() in data.lower():

                knownSets = {
                        "alfaerie.html":"Alfaerie",
                        "alfaerie2.html":"Alfaerie Expansion Set 1",
                        "alfaerie3.html":"Alfaerie Expansion Set 2",
                        "alfaerie4.html":"Alfaerie Expansion Set 3",
                        "alfaerie5.html":"Alfaerie Expansion Set 4",
                        "alfaerieplus.html":"Alfaerie Plus",
                        "alfaeriebeta.html":"Alfaerie Beta"}

                if knownSets.has_key(filename):
                    setName = knownSets[filename]
                elif "sets/misc" in root:
                    setName = "Alfaerie Misc: " + root.split("sets/misc/")[1]
                else:
                    setName = path

                #found.append(path)
                found.append(setName)
    return found

if __name__ == "__main__":
    main()
