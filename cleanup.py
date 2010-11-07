# Cleanup index.json
#
import json
d = json.loads(file("index.json").read())
for k in d:
    d[k]["set"] = d[k]["set"][0]

file("index.json","w").write(json.dumps(d))
