# Cleanup index.json
#
import json
d = json.loads(file("index.json").read())
for k in d:
    if "Alfaerie Expansion Set 4" in d[k]["set"]:
        d[k]["set"] = ["Alfaerie Expansion Set 4"]
    if "Alfaerie" in d[k]["set"]:
        d[k]["set"] = ["Alfaerie"]


    if len(d[k]["set"]) != 1:
        print k, d[k]

