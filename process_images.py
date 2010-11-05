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
for filename in files:
    prefix = filename[0]
    if "." not in filename[1:]:
        continue
    name, suffix = filename[1:].rsplit(".", 1)
    if suffix != "gif":
        continue

    if not byColor.has_key(prefix):
        byColor[prefix] = {}

    byColor[prefix][name] = True

print pprint.pprint(byColor)
