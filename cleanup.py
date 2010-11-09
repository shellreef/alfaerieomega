# Cleanup index.json
#
import json
d = json.loads(file("index.json").read())
for k in d:
    tags = d[k].get("tags", [])
    if k in ("king", "queen", "rook", "bishop", "knight", "pawn"):
        tags.append("fide")
    if k.endswith("inv") or k.endswith("ccw") or k.endswith("cw"):
        tags.append("rotated")
    if k in ("camel", "giraffe", "lion", "unicorn", "grasshopper", "ram", "ox", "gryphon", "squirrel", "dragon", "rhino", "zebra", "pegasus", "bird", "bird2", "tiger", "kangaroo",
            "butterfly", "lizard", "monkey", "spider", "crab2", "panda", "wildebeest", "wildebeest2", "bat", "highpriestess", "oliphant", "frog", "grasshopper2") or "camel" in k \
                    or "elephant" in k or "highpriest" in k or "giraffe" in k or "horse" in k:
        tags.append("animal")
    if k in ("tank", "airplane", "rocket", "bulldozer", "gun"):
        tags.append("modern")
    if k.startswith("half") or k in ("narrowknight", "wideknight", "crab", "barc", "1bishop", "1bishop2", "1rook"):
        tags.append("diminished")
    if k in ("horse", "elephant", "cannon", "vao", "chinesepawn", "moo", "moa", "mao"):
        tags.append("chinese")
    if k in ("goldgeneral", "silvergeneral", "horse", "lance", "pawn", "dragonking", "dragonhorse", "promotedsilvergeneral", "promotedhorse", "promotedpawn"):
        tags.append("japanese")
    if k in ("blindmonkey", "blindtiger", "chinesecock", "coiledserpent", "drunkenelephant", "evilwolf", "ferociousleopard",
            "irongeneral", "oldmonkey", "recliningdragon", "stonegeneral", "tilegeneral"):
        tags.append("japanese")
    if k in ("faalcon", "falcon", "falcon2", "bird", "flyingkingfisher", "wader", "bird2"):
        tags.append("avian")

    d[k]["tags"] = tags

file("index.json","w").write(json.dumps(d))
