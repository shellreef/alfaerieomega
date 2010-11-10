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

    script = '''function main(input) {
   var doc    = Acorn.open("/tmp/bking.gif");
   var layer  = doc.layers().objectAtIndex(0);
   var img    = layer.CIImage();

   log("here");

   // TSReplaceColorFilter is undocumented, but it probably won't change anytime soon.
   // if you really wanted to, you could write your own CIFitler to do the same, it's not tough.
   var filter = [CIFilter filterWithName:"TSReplaceColorFilter"];
   var lookForColor = [CIColor colorWithRed:0.34901960784313724 green:0.5176470588235295 blue:0.7411764705882353 alpha:1];
   var replaceColor = [CIColor colorWithRed:1 green:0 blue:0 alpha:1]; 
   var tolerance    = [NSNumber numberWithFloat:32];

   [filter setValue:img          forKey:"inputImage"];
   [filter setValue:lookForColor forKey:"inputColor"];
   [filter setValue:replaceColor forKey:"inputColor2"];
   [filter setValue:tolerance    forKey:"inputTolerance"];

   [layer applyCIImageFromFilter:[filter valueForKey:"outputImage"]];
}

'''

    #acorn.open_(path)
    #doc = acorn.documents()[0]
    #doc.rotateCanvasAngle_(180)
    #layer = doc.layers()[0]

    print acorn.doJavaScript_(script)

    # TODO: apply color filter (doFilterName_)
    # TODO: save 
    #doc.saveIn_as_("/tmp/a.gif", 0)
    #doc.close()


    raise SystemExit

