# Cleanup index.json
#
import json
d = json.loads(file("index.json").read())
for k in d:
    tags = d[k].get("tags", [])
    if len(tags) == 0:
        del d[k]["tags"] 

file("index.json","w").write(json.dumps(d))
