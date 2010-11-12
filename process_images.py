#!/usr/bin/python
# Created:20101104
# By Jeff Connelly
#
# Process Alfaerie Omega images

import pprint
import os
import json
import Image
import ImageOps

INDEX_FILE = "index.json"

# b*.gif standardize on this blue
BLUE = "#5984bd"

# Temporary RGB color for transparency (bright yellow, no one should use that)
TEMP_TRANSPARENT = "#ffff99"

# Temporary RGB color for black
TEMP_BLACK = "#ffffcc"


OTHER_COLORS = {
        #"w": "#fffffff",   # white 
        #"b": BLUE,         # blue ("black player")
        "y": "#ffff00",     # yellow (third player on http://myweb.tiscali.co.uk/ins.chess/varns/4H.htm)
        "r": "#ff0000",     # red (fourth player)
        "g": "#00ff00",     # green
        "c": "#00ffff",     # cyan
        "o": "#ff8000",     # orange
        "p": "#ff00ff",     # pink
        "e": "#cccccc",     # grey
        "k": "#000000",     # black (true)
        }

OTHER_ROTATIONS = {
        "": None,
        "45ccw": 45,
        "90ccw": 90,
        "135ccw": 135,
        "inv": 180,
        "45cw": 360 - 45,
        "90cw": 360 - 90,
        "135cw": 360 - 135,
        }

def main():
    index = updatePieceIndex()
    writeIndexDocuments(index)

    for name in sorted(index.keys()):
        processPiece(name)

def processPiece(name):
    bImage = Image.open("b" + name + ".gif")
    wImage = Image.open("w" + name + ".gif")

    #top = topColorIndex(bImage)
    #pal = colorPalette(bImage)
    #print pal[top]

    blue = indexForColor(bImage, BLUE)
    if blue is None:
        print "Warning: missing blue (%s):" % (BLUE,), "b"+name+".gif"

    for prefix in OTHER_COLORS:
        color = OTHER_COLORS[prefix]

        for suffix in OTHER_ROTATIONS:
            rotation = OTHER_ROTATIONS[suffix]

            makeVariant(bImage, name, color, rotation, prefix, suffix)
    

def makeVariant(bImage, name, newColorHex, rotation, prefix, suffix):
    """Make a new color variant image of a piece by replacing all blue
    pixels in the blue piece image."""

    if rotation is None:
        folder = ""
    else:
        # Less useful, so stash away
        folder = "generated-rotations/" 


    newFilename = folder + prefix + name + suffix + ".gif"

    # Skip creation if already exists (to recreate, delete)
    if os.path.exists(newFilename):
        return

    newColor = hexToColor(newColorHex)

    img = bImage.convert("RGBA")

    if rotation:
        if rotation % 90 != 0:
            # Ugly hack 2: non-orthogonal degree rotations create black corners, when we want transparent
            # Replace black with a temporary color to distinguish it from the black corners
            count = 0
            width, height = img.size
            for px in img.getdata():
                if colorToHex(px)[0:7] == "#000000" and px[3] == 255:
                    img.putpixel((int(count % width), int(count / width)), hexToColor(TEMP_BLACK) + (255,))
                count += 1

        
        # TODO: what filter? NEAREST, BILINEAR, BICUBIC?
        # TODO: can img.info["background"] solve the black corner problem cleaner than temporary color replacement?
        img = img.rotate(rotation)

        if rotation % 90 != 0:
            # Replace temporary black with black, and black (from corner rotations) with temporary transparent
            count = 0
            width, height = img.size
            for px in img.getdata():
                if colorToHex(px)[0:7] == TEMP_BLACK:
                    img.putpixel((int(count % width), int(count / width)), hexToColor("#000000") + (255,))
                elif colorToHex(px)[0:7] == "#000000":
                    img.putpixel((int(count % width), int(count / width)), hexToColor(TEMP_TRANSPARENT) + (0,))
                count += 1


    count = 0
    width, height = img.size
    for px in img.getdata():
        # The main color substitution
        if colorToHex(px)[0:7] == BLUE:
            newColorAlpha = newColor + (px[3],)
            img.putpixel((int(count % width), int(count / width)), newColorAlpha)

        # Special case: black pieces need a white outline
        if prefix == "k" and colorToHex(px)[0:7] == "#000000":
            img.putpixel((int(count % width), int(count / width)), hexToColor("#ffffff") + (255,))

        # If zero alpha, then replace with a color we can recognize as transparent
        if px[3] == 0:
            # Bright yellow, no one should use that
            img.putpixel((int(count % width), int(count / width)), hexToColor(TEMP_TRANSPARENT) + (0,))

        count += 1


    # Convert back to palettized image
    # http://effbot.org/tag/PIL.Image.Image.convert
    img = img.convert("P", dither=Image.NONE) #, palette=Image.ADAPTIVE)   # ADAPTIVE fails with: Image: wrong mode
 
    # Ugly hack. Conversion loses the transparent color index for some reason.
    # We could try to save the RGB of the transparent color, but conversion
    # changes the RGB, too! (#c0c0c0 -> #cccccc), since it uses a 216-color web palette
    img.info["transparency"] = indexForColor(img, TEMP_TRANSPARENT)

    saveImage(img, newFilename)
    print "Creating variant:", newFilename

def indexForColor(image, rgb):
    """Get the palette index for an RGB color."""
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
    hexColors = [colorToHex(rgb) for rgb in colors]

    return hexColors

def colorToHex(rgb):
    """ Convert an RGB 3-tuple to a hexdecimal string.

    >>> colorToHex((1, 2, 3))
    '#010203'
    """
    return "#" + "".join(map(lambda octet: "%.2x" % (octet,), rgb))

def hexToColor(s):
    """Convert a hexadecimal string to a 3-tuple of RGB.
    >>> hexToColor("#01ff80")
    (1, 255, 128)
    """

    if s[0] == "#":
        s = s[1:]

    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)

    return r, g, b



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
            #index[name] = {"set": ["Alfaerie Expansion Set 6"]}   #findImageSet("w"+name+".gif")}
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
        out.write(" %s: {" % (json.dumps(name),))

        for j, key in enumerate(sorted(info.keys())):
            value = info[key]
            out.write("%s: %s" % (json.dumps(key), json.dumps(value)))
            if j != len(info.keys()) - 1:
                out.write(", ");
        out.write("}")

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
