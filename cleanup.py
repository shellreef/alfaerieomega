# Cleanup index.json
#
import json
d = json.loads(file("index.json").read())
for k in d:
    if d[k]["set"] in ("Alfaerie", "Alfaerie Expansion Set 1", "Alfaerie Expansion Set 2"):
        d[k]["credit"] = "David Howe"
    elif d[k]["set"] == "Alfaerie Expansion Set 3":
        if k in ("wildebeest2", "cardinal2", "cavalier", "crusader", "diplomat", "duchess", 
                "empress2", "envoy", "gorgona", "marshal2", "medusa", "minister2", "paladin2", 
                "viceroy"):
            d[k]["credit"] = "Michael Howe"
        else:
            d[k]["credit"] = "David Howe"
    elif d[k]["set"] == "Alfaerie Expansion Set 4":
        if k == "frog":
            d[k]["credit"] = "Tucker Kao"
        elif k == "coppergeneral":
            d[k]["credit"] = "Peter Aronson"
        elif k == "templar":
            d[k]["credit"] = "Adrian Alvarez de la Campa"
        elif k == "elephantwarmachinerider":
            d[k]["credit"] = "Larry Wheeler"
        elif k in ("jumpinggeneral", "highpriestess", "knightwarmachinewazir", "knightwarmachine",
                "zigzaggeneral", "lightningwarmachine", "oliphant", "flexibleknight", "slidinggeneral"):
            d[k]["credit"] = "Joe Joyce and Peter Joyce"
        else:
            d[k]["credit"] = "Christine Bagley-Jones"
    elif d[k]["set"] == "Alfaerie Expansion Set 5":
        if k in ("battlement", "bishop2", "cavalry", "dDeacon", "diplomat2",
                "envoy2", "general3", "gorgona2", "hero", "hero2", "juggernaut", "medusa2", "parapet", "swordsman"):
            d[k]["credit"] = "Michael Howe"
        elif k in ("friend", "friendlyorphan", "orphanfriend"):
            d[k]["credit"] = "Jeremy Good"
        elif k in ("highpriestess2", "knightwarmachinewazir2", "knightwarmachine2"):
            d[k]["credit"] = "Joe Joyce"
        else:
            d[k]["credit"] = "Christine Bagley-Jones"
    elif d[k]["set"] == "Alfaerie Expansion Set 6":
        d[k]["credit"] = "Matthew La Vallee"

file("index.json","w").write(json.dumps(d))
