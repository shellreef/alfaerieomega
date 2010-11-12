# Cleanup index.json
#
import json
import re
d = json.loads(file("index.json").read())
for k in d:
    tags = d[k].get("tags", [])

    print k
    if re.search(r'-[A-Z]', d[k]["longname"]):
        print "*",d[k]["longname"]
        tags.append("compound")

    if len(tags) != 0:
        d[k]["tags"] = tags

file("index.json","w").write(json.dumps(d))
