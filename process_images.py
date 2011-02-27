#!/usr/bin/python
# Created:20101104
# By Jeff Connelly
#
# Process Alfaerie Omega images

import pprint
import os
import json
import base64
import Image
import ImageOps


HTML_DATA_FILE = "master.html"
HTML_LEGACY_FILE = "master-external.html"
JSON_FILE = "aomega.json"
JSON_DATA_FILE = "aomega-data.json"

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
        #"k": "#000000",     # black - disabled because doesn't work well, black body conflicts with black outline
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
# Disable rotated image generation. Remove to re-enable.
OTHER_ROTATIONS = {"": None}

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
   
    # This syntax (dict comprehension) requires Python 2.7+ 
    #rgbToIndex = {v:k for k, v in enumerate(indexToRGB)}
    # Python 2.6 compatible
    rgbToIndex = {}
    for k,v in enumerate(indexToRGB):
        rgbToIndex[v] = k

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
    if os.path.exists(JSON_FILE):
        # Load existing metadata 
        index = json.loads(file(JSON_FILE).read())
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

    imageDatas = {}

    for name, colors in byName.iteritems():
        if not ("b" in colors and "w" in colors):
            # These are not considered pieces
            print "Warning: missing images:", colors, name
            continue

        if not index.has_key(name):
            print "\n** New piece:", name
            index[name] = {}
            index[name]["set"] = "Alfaerie Beta" #raw_input("Set name? ")
            index[name]["credit"] = raw_input("Credit? ")  
            index[name]["longname"] = raw_input("Long name? ")
            #print "** Please define credits in process_images.py then rerun"
            #raise SystemExit
            #index[name] = {"set": "Alfaerie Beta", "credit": "Jeff Connelly"}   #findImageSet("w"+name+".gif")}
        # Otherwise, leave existing entry (preserve metadata)

        # Read data for each color
        imageDatas[name] = {}
        for color in ["b", "w"]:  #colors:  # TODO: all colors? but then baloons file from <1MB to 13MB!
            imageDatas[name][color] = dataURIfor(color + name + ".gif")

    # TODO: more info (credits, don't overwrite but reconcile existing), make the list a dict

    #file(JSON_FILE, "w").write(json.dumps(index, indent=1))
    # Save as JSON for ease usage in other applications
    # Could simply use json.dumps(index), but want the dictionary keys to
    # be sorted to avoid noisy diffs in version control.
    out = file(JSON_FILE, "w")
    dataout = file(JSON_DATA_FILE, "w")

    def write(code):
        out.write(code)
        dataout.write(code)

    write("{\n")

    for i, name in enumerate(sorted(index.keys())):
        info = index[name]
        write(" %s: {" % (json.dumps(name),))

        def dumpKeys(info):
            s = ""
            for j, key in enumerate(sorted(info.keys())):
                value = info[key]
                s += "%s: %s" % (json.dumps(key), json.dumps(value))
                if j != len(info.keys()) - 1:
                    s += ", "
            return s

        out.write(dumpKeys(info))
        dataInfo = dict(info, **{"data": imageDatas[name]})
        dataout.write(dumpKeys(dataInfo))

        write("}")

        # JSON spec (and IE, but no one cares about them) require omitting
        # comma for last item in list
        if i != len(index.keys()) - 1:
            write(",")

        write("\n")

    write("}\n")
    out.close()

    # Save JSONP for easy <script src> reference
    file(JSON_FILE + "p", "w").write("var INDEX = %s;" % (file(JSON_FILE).read(),))
    file(JSON_DATA_FILE + "p", "w").write("var INDEX = %s;" % (file(JSON_DATA_FILE).read(),))

    print "Loaded %s pieces" % (len(index.keys()),)

    return index

def dataURIfor(filename):
    imageData = file(filename, "rb").read()
    dataURI = "data:image/gif;base64," + base64.encodestring(imageData).replace("\n", "")

    return dataURI

def writeIndexDocuments(index):
    """Write the index in text and HTML formats."""
    text = file("list.txt", "w")
    html = file(HTML_LEGACY_FILE, "w")
    durl = file(HTML_DATA_FILE, "w")

    def writeHTML(code):
        html.write(code)
        durl.write(code)

    writeHTML("""<!DOCTYPE html>
<html>
<head>
<title>Alfaerie Omega - Piece Index</title>
<style>
div { float: left; border: 1px dotted black; }
p { text-align: center; }
</style>
</head>
<body bgcolor="lightgray">
<p>Total pieces: %s
""" % (len(index.keys()),))

    durl.write("""<p><em style="align: center">This page requires data: URI support. <a href="master-external.html">Click here if all the images are broken</a>.</em>""")
    html.write("""<p><em style="align: center">If the images on this page take too long to load, and you have a modern browser, try the <a href="master.html">data URI version of this page</a>.</em>""")

    for name in sorted(index.keys()):
        info = index[name]

        text.write(name + "\n")
	writeHTML("<div>")
        for color in "wb":
            html.write("""<img src="%s%s.gif" width="50" height="50">""" % (color, name))  # TODO: make consistently 50x50!
            durl.write("""<img id="%s%s" src="%s" width="50" height="50">""" % (color, name, dataURIfor(color + name + ".gif"),))
        if len(name) > 12:
            shortname = name[0:4] + ".." + name[-7:-1] + name[-1]  # fit the name in :( TODO: make real names not so long!
        else:
            shortname = name
        text_info = name + "\n"
        for key in sorted(info.iterkeys()):
            text_info += "%s: %s\n" % (key, info[key])
        writeHTML("""<p title="%s">%s</p>""" % (text_info, shortname))
        writeHTML("</div>")

    writeHTML("""
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
