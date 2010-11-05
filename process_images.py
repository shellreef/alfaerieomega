#!/usr/bin/python
# Created:20101104
# By Jeff Connelly
#
# Process Alfaerie Omega images

import pprint
import os
import Image

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

print pprint.pprint(byName)

print [(name, colors) for name, colors in byName.iteritems() if len(colors) < 2]
