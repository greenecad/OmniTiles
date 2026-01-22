import json, struct, base64, random

def json_to_tscn(file, layer=0):
    inp=json.loads(file)
    id=gen_godot_uid()
    out = f"""[gd_scene load_steps=4 format=4 uid="uid://{id}"]\n\n"""
    if "image" in inp['tilesets'][0]:
        texture_id=gen_id()
        inp['tilesets'][0]['image']=inp['tilesets'][0]['image'].replace("\\","/")
        print(inp['tilesets'][0]['image'][0])
        if inp['tilesets'][0]['image'][0]=="/":
            print("a")
            inp['tilesets'][0]['image']=inp['tilesets'][0]['image'][1:]
        out += f"""[ext_resource type="Texture2D" uid="uid://{gen_godot_uid()}" path="res://{inp["tilesets"][0]["image"]}" id="1_{texture_id}"]\n\n"""
    TSAS_id = gen_id()
    out += f"""[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_{TSAS_id}"]\n"""
    if "name" in inp['tilesets'][0]:
        out+= f"""resource_name = "{inp['tilesets'][0]['name']}"\n"""
    out += f"""texture = ExtResource("1_{texture_id}")\n"""
    out += f"""texture_region_size = Vector2i({inp['tilesets'][0]['tilewidth']}, {inp['tilesets'][0]['tileheight']})\n"""



    if "columns" not in inp["tilesets"][0]:
        ## add warning about missing column data for tileset
        pass
    else:
        for i in range(inp["tilesets"][0]["tilecount"]//inp["tilesets"][0]["columns"]):
            for ii in range(inp["tilesets"][0]["columns"]):
                out += f"{ii}:{i}/0 = 0\n"
        
        out += "\n"
        TileSet_id = gen_id()
        out += f"""[sub_resource type="TileSet" id="TileSet_{TileSet_id}"]\n"""
        if "name" in inp['tilesets'][0]:
            out+= f"""resource_name = "{inp['tilesets'][0]['name']}"\n"""
        out += f"""tile_size = Vector2i({inp['tilesets'][0]['tilewidth']}, {inp['tilesets'][0]['tileheight']})\n"""
        out += f"""sources/0 = SubResource("TileSetAtlasSource_{TSAS_id}")\n"""

        out += """\n[node name="TileMapLayer" type="TileMapLayer"]\n"""
        pbadata=[0, 0, 253, 1, 238, 255, 0, 0, 2, 0, 4, 0, 0, 0]
        x=0
        y=0
        for i in inp["layers"][layer]["data"]:
            if i != 0:
            
                tx = (i - 1) % inp["tilesets"][0]["columns"]
                ty = (i-1) // inp["tilesets"][0]["columns"]
            
                pbadata+=([x, 0, y, 0, 0, 0, tx, 0, ty, 0, 0, 0])
            x += 1
            if x >= inp["width"]:
                x = 0
                y += 1
        pbadata=encode_base64(pbadata)

    pbadata=str(pbadata)
    out += f"""tile_map_data = PackedByteArray("{str(pbadata)[2:len(pbadata)-1]}")\n"""
    out += f"""tile_set = SubResource("TileSet_{TileSet_id}")\n"""
    return out
        


def tscn_to_json(file):
    out = {
        "layers": [ 
            {
                "data": [],
                "type":"tilelayer",
                "name": "Layer_1",
                "visible": True,
                "opacity": 1,
                "x":0,
                "y":0,
                "id":1
            } 
        ],
        "tilesets": [ {
            "firstgid": 1,
            "name": "tileset1",
            "spacing": 0,
            "margin": 0,
            "type": "tileset"
        } ],
        "nextlayerid": 2,
        "nextobjectid": 1,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "version": "1.10",
        "type": "map"
    }
    WH_I= file.find("texture_region_size = Vector2i(")
    WH_E= file.index(")", WH_I)
    wh = file[WH_I+len("texture_region_size = Vector2i("):WH_E]
    out["tilewidth"] = out["tilesets"][0]["tilewidth"] = int(wh.split(",")[0].strip())
    out["tileheight"] = out["tilesets"][0]["tileheight"] = int(wh.split(",")[1].strip())
    
    lmx = 0
    mx = str(file).find("/0 = 0")
    while file.find("/0 = 0", mx+1) != -1:
        lmx = mx
        mx = file.index("/0 = 0", mx+1)
    cols = int(file[lmx+7:mx].split(":")[0]) + 1
    out["tilesets"][0]["columns"] = cols
    out["tilesets"][0]["tilecount"] = cols * (int(file[lmx+7:mx].split(":")[1]) + 1)
    s = file.index("tile_map_data = PackedByteArray(\"") + len("tile_map_data = PackedByteArray(\"")
    e = file.index("\")", s)
    pba_b64 = file[s:e]
    if ", " in pba_b64:
        t_m_data = pba_b64.split(", ")
        t_m_data = [int(i) for i in t_m_data]
    else:
        t_m_data = decode_base64(pba_b64)
    i=14
    data=[]
    mw = 0
    mh = 0
    while i < len(t_m_data):
        x = t_m_data[i]
        y = t_m_data[i+2]
        if mw < x+1:
            mw = x+1
        if mh < y+1:
            mh = y+1
        i += 12
    i=14
    pathI=file.find("path=\"res://")
    if pathI != -1:
        pathE=file.index("\"", pathI+len("path=\"res://"))
        out["tilesets"][0]["image"] = file[pathI+len("path=\"res://"):pathE]
        out["tilesets"][0]["imagewidth"] = cols * out["tilesets"][0]["tilewidth"]
        out["tilesets"][0]["imageheight"] = (out["tilesets"][0]["tilecount"]//cols) * out["tilesets"][0]["tileheight"]
    while i < len(t_m_data):
        x = t_m_data[i]
        y = t_m_data[i+2]
        tx = t_m_data[i+6]
        ty = t_m_data[i+8]
        if len(data) < (y * mw+ x +1):
            data.extend([0]*((y * mw + x +1)-len(data)))
        data[y*mw + x] = (ty) * cols + tx +1
        i += 12
    out["width"] = mw
    out["height"] = mh
    out["layers"][0]["width"] = mw
    out["layers"][0]["height"] = mh
    out["layers"][0]["data"] = data

    return json.dumps(out, indent=3)




def decode_base64(data):
    data = base64.b64decode(data)
    vals= list(struct.unpack('<{}B'.format(len(data)), data))
    return vals
    

def encode_base64(ls):
    for i in range(len(ls)):
        if ls[i]<0:
            print("WARNING: VALUE OUT OF BOUNDS FOR BYTEARRAY ENCODING: "+ str(ls[i]))
            
    data= struct.pack('<{}B'.format(len(ls)), *ls)
    data= base64.b64encode(data)
    return data

def gen_godot_uid():
    return str(random.randint(1000000,9999999))+chr(random.randint(65,90))+chr(random.randint(65,90))+chr(random.randint(65,90))

def gen_id():
    s='abcdefghijklmnopqrstuvwxyz0123456789'
    return random.choice(s) + random.choice(s) + random.choice(s) + random.choice(s) + random.choice(s)

