# Cleanup index.json
#
import json
d = json.loads(file("index.json").read())
for k in d:
    d[k]["longname"] = k[0].upper() + k[1:]

file("index.json","w").write(json.dumps(d))
