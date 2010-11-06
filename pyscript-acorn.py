#!/usr/bin/python2.6
# Created:20101106
# By Jeff Connelly
#
# TODO: Create modified pieces
# By scripting the Acorn image editor http://flyingmeat.com/acorn/

import os
import json
import Foundation
import ScriptingBridge

index = json.loads(file("index.json").read())
acorn = ScriptingBridge.SBApplication.applicationWithBundleIdentifier_("com.flyingmeat.Acorn")
for name in sorted(index.keys()):

    path = os.path.join(os.getcwd(), "b"+name+".gif")
    acorn.open_(path)
    doc = acorn.documents()[0]

    doc.rotateCanvasAngle_(180)

    # TODO: apply color filter (doFilterName_)
    # TODO: save 
    doc.saveIn_as_("/tmp/a.gif", 0)

    raise SystemExit

