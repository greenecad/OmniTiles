import json

def json_to_csv(file):
    inp = json.loads(file)
    output= [0]*(inp["width"] * inp["height"])
    for layer in inp["layers"]:
        data = layer["data"]
        i = 0
        for n in data:
            if n!=0:
                output[i]=n
            i+=1
    s = str(output).replace("[","").replace("]","")
    i = 0
    c = 0
    m = -1
    w = inp["width"]
    while i<len(s)-1:
        i = s.find(", ", i+1)
        c += 1
        if i <= m:
            break
        m = i
        if c == w and i < len(s)-2:
            s = s[:i]+"\n"+s[i+2:]
            c = 0
    return s
        

def csv_to_json(file):
    file = file.split("\n")
    d=[]
    for line in file:
        nums = line.split(",")
        for n in nums:
            d.append(int(n.strip()))
    json_file = {
        "compressionlevel": -1,
        "height": len(file),
        "infinite": False,
        "layers":[
            {
                "data": d,
                "height": len(file),
                "width": len(file[0].split(",")),
                "id":1,
                "name": "layer1",
                "type":"tilelayer",
                "visible": True,
                "opacity": 1,
                "x":0,
                "y":0

            }

        ],
        "nextlayerid": 2,
        "nextobjectid": 1,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "version": "1.10",
        "tileheight": 1,
        "tilewidth": 1,
        "width": len(file[0].split(",")),
        "type": "map"


    }
    return json.dumps(json_file, indent=3)
    