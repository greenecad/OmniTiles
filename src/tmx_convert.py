import json

def json_to_tmx(file):
    inp = json.loads(file) 
    out = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    out += f"""<map version="{inp['version']}" orientation="{inp['orientation']}" renderorder="{inp["renderorder"]}" width="{inp["width"]}" height="{inp["height"]}" tilewidth="{inp["tilewidth"]}" tileheight="{inp["tileheight"]}" infinite="0" nextlayerid="{inp["nextlayerid"]}" nextobjectid="{inp["nextobjectid"]}">\n"""
    if "tilesets" in inp:
        if "image" in inp["tilesets"][0]:
            for tileset in inp["tilesets"]:
                out += f"""<tileset firstgid="{tileset["firstgid"]}" name="{tileset["name"]}" tilewidth="{tileset["tilewidth"]}" tileheight="{tileset["tileheight"]}" tilecount="{tileset["tilecount"]}" columns="{tileset["columns"]}">\n"""
                out += f"""<image source="{tileset["image"]}" width="{tileset["imagewidth"]}" height="{tileset["imageheight"]}" trans="{tileset["transparentcolor"]}"/>\n"""
                if "tiles" in tileset:
                    for tile in tileset["tiles"]:
                        out += f"""<tile id="{tile["id"]}">\n"""
                        if "properties" in tile:
                            out += "<properties>"
                            for prop in tile["properties"]:
                                out += f"""<property name="{prop["name"]}" type="{prop["type"]}" value="{prop["value"]}"/>\n"""
                            out += "</properties>\n"
                        out += "</tile>\n" 
                out += "</tileset>\n"
        else:
            for tileset in inp["tilesets"]:
                out += f"""<tileset firstgid="{tileset["firstgid"]}" source="{tileset["source"]}"/>\n"""
    else:
        out += f"""<tileset firstgid="1" source="no-tileset-defined"/>\n"""
    for layer in inp["layers"]:
        out += f"""<layer id="{layer["id"]}" name="{layer["name"]}" width="{inp["width"]}" height="{inp["height"]}">\n"""
        out += """<data encoding="csv">\n"""
        data = layer["data"]
        s=str(data).replace("[","").replace("]","")
        i = 0
        c = 0 
        m = -1 
        w=inp["width"]
        while i<len(s):
            i = s.find(", ", i+1)
            c += 1
            if i<=m:
                break
            m = i
            if c == w:
                s = s[:i]+",\n"+s[i+2:]
                c = 0
        out += s
        out += "\n</data>\n"
        out += "</layer>\n"
    out += "</map>\n"
    return out


def tmx_to_json(file):
    out = {
        "tilesets": [],
        "layers": [],
        "type":"map"
    }
    file_lines = iter(file.split("\n"))
    next(file_lines)
    d = next(file_lines).replace("<map ","").replace(">","").split(" ")
    for attr in d:
        a = attr.split("=")
        key = a[0]
        value = a[1].replace('"',"")
        if value.isdigit():
            value = int(value)
        out[key]=value
    out["infinite"]=0 # add support for infinite later
    d = next(file_lines)
    
    while d.strip().startswith("<tileset"): 
        tileset = {}
        attrs = d.replace("<tileset ","").replace("/>","").replace(">","").split(" ")
        attrs = [a for a in attrs if a.strip()!=""]
        for attr in attrs:
            a = attr.split("=")
            key = a[0]
            value = a[1].replace('"',"")
            if value.isdigit():
                value = int(value)
            tileset[key]=value
        d = next(file_lines)
        if d.strip().startswith("<image "):
            image_attrs = d.replace("<image ","").replace("/>","").split(" ")
            image = {}
            image_attrs = [a for a in image_attrs if a.strip()!=""]
            for attr in image_attrs:
                a = attr.split("=")
                key = a[0]
                value = a[1].replace('"',"")
                if value.isdigit():
                    value = int(value)
                image[key]=value
            tileset["image"]=image["source"]
            tileset["imagewidth"]=image["width"]
            tileset["imageheight"]=image["height"]
            tileset["transparentcolor"]=image["trans"]
            d = next(file_lines)
        tileset["tiles"]=[]
        while d.strip().startswith("<tile "):
            tile={"properties":[]}
            d = d.replace("<tile ","").replace("/>","").split("=")
            tile["id"]=int(d[1].replace('"',""))
            next(file_lines)
            d = next(file_lines)

            while d.strip().startswith("<property "):
                d = d.replace("</property ", "").replace("/>","").split(" ")
                d= [a for a in d if a.strip()!=""]
                prop={}
                for attr in d:
                    a = attr.split("=")
                    key = a[0]
                    value = a[1].replace('"',"")
                    if value.isdigit():
                        value = int(value)
                    prop[key]=value
                tile["properties"].append(prop)
                d=next(file_lines)
            next(file_lines)
            d=next(file_lines)
            tileset["tiles"].append(tile)
        if len(tileset["tiles"])==0:
            del tileset["tiles"]
        out["tilesets"].append(tileset)
        d = next(file_lines)
    while d.strip().startswith("<layer "):
        layer = {"data":[],
                 "type": "tilelayer",
                 "visible": 1,
                 "opacity": 1
                 }
        attrs = d.replace("<layer ","").replace(">","").split(" ")
        attrs = [a for a in attrs if a.strip()!=""]
        for attr in attrs:
            a = attr.split("=")
            key = a[0]
            value = a[1].replace('"',"")
            if value.isdigit():
                value = int(value)
            layer[key]=value
        next(file_lines)
        d = next(file_lines)
        data = ""
        while not d.strip().startswith("</data>"):
            data += d
            d=next(file_lines)
        data = data.replace("\n","").split(",")
        for n in data:
            if n.strip().isdigit():
                layer["data"].append(int(n.strip()))
        out["layers"].append(layer)
        next(file_lines)
        d = next(file_lines)
    
    return json.dumps(out, indent=3)