import json, tarfile, os

def json_to_unity(file):
    input=json.loads(file)
    os.mkdir("/temp_dir")
    


def unity_to_json(file_path):
    extract_tar_file(file_path, "temp_dir")
    out= {
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
    for root, dirs, files in os.walk("temp_dir"):
        for file in files:
            with open(os.path.join(root, file), "r") as f:
                try:
                    content = f.read()
                    if content.endswith(".prefab"):
                        pfdata = get_prefab_data(os.path.join(root, "asset"))
                        out["layers"] = pfdata["layers"]
                        out["nextlayerid"] = pfdata["nextlayerid"]
                        out["width"] = pfdata["layers"][0]["width"]
                        out["height"] = pfdata["layers"][0]["height"]
                    if content.endswith(".png"):
                        try:
                            with open(os.path.join(root, "asset"), "rb") as imgf:
                                img_data = imgf.read()
                            content=content.split("/")
                            with open(f"{content[len(content)-1]}", "wb") as outi:
                                outi.write(img_data)
                            out["tilesets"][0]["image"]=f"{os.path.abspath(content[len(content)-1])}"
                            with open(os.path.join(root, "asset.meta")) as am:
                                amdata = am.read()
                            i = amdata.find("sprites:")
                            ii = amdata.find("rect:", i)
                            ii = amdata.find("height:", ii)
                            height = round(float(amdata[ii+7: amdata.find("\n", ii)].strip()))
                            ii = amdata.find("width:", i)
                            width = round(float(amdata[ii+6: amdata.find("\n", ii)].strip()))
                            out["tilesets"][0]["tilewidth"]=width
                            out["tilesets"][0]["tileheight"]=height
                            out["tilewidth"]=width
                            out["tileheight"]=height

                            i = amdata.find(" - ", i)
                            count = 0
                            mx=0
                            my=0
                            while i != -1:
                                count += 1
                                ii = amdata.find("rect:", i)
                                ii = amdata.find("x:", ii)
                                x = round(float(amdata[ii+3: amdata.find("\n", ii)].strip()))
                                if x > mx:
                                    mx = x
                                
                                i = amdata.find(" - ", ii + 1)
                            out["tilesets"][0]["tilecount"]=count
                            out["tilesets"][0]["columns"]= (mx // width) + 1
                        except Exception as e:
                            print("Error processing PNG asset:", e)



                except:
                    pass

    clean_temp_dir("temp_dir")

    return json.dumps(out, indent=3)

def extract_tar_file(source, dest):
    tarfile.open(source, mode="r").extractall(dest)

def create_tar_file(tar_name, source_dir):
    with tarfile.open(tar_name, "w:bz2") as tar:
        tar.add(source_dir, arcname=".")


def clean_temp_dir(dir_path):
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(dir_path)

def get_prefab_data(prefab_path):
    pfdata = {
        "layers": []
    }
    with open(prefab_path, "r") as file:
        data = file.read()
        i=0
        c=0
        namei= data.find("\nGameObject:")
        if namei != -1:
            namei = data.find("m_Name:", namei)+1
            name =  data[namei+7: data.find("\n", namei)].strip()

        while data.find("!u!1839735485", i) != -1:
            i=data.find("!u!1839735485", i) + 1
            layer_data = {
                "data": [],
                "type":"tilelayer",
                "name": f"{name}",
                "visible": True,
                "opacity": 1,
                "x":0,
                "y":0,
                "id":c+1
            }
            
            try:

                ii=data.find("m_Color:", i)
                layer_data["opacity"] = float(data[data.find("a:", ii)+2: data.find("\n", data.find("a:", ii))].strip())
                

                ii=data.find("m_Origin:", i)
                layer_data["x"] = int(data[data.find("x:", ii)+2: data.find("\n", data.find("x:", ii))].strip())
                layer_data["y"] = int(data[data.find("y:", ii)+2: data.find("\n", data.find("y:", ii))].strip())
                ii=data.find("m_Size:", i)
                layer_data["width"] = int(data[data.find("x:", ii)+2: data.find("\n", data.find("x:", ii))].strip())
                layer_data["height"] = int(data[data.find("y:", ii)+2: data.find("\n", data.find("y:", ii))].strip())

                ii=data.find("m_GameObject:", i)
                objid = data[data.find("fileID:", ii)+7: data.find("\n", data.find("fileID:", ii))].strip()
                ii = data.find(f"!u!1 &{objid}")
                ii=data.find("m_Name", ii)
                layer_data["name"] = data[ii+7: data.find("\n", ii)].strip()
                
                ii=data.find("m_Tiles:", i)
                layer_data["data"] = [0] * (layer_data["width"] * layer_data["height"])

                while data.find("- first:", ii) != -1 and (data.find("- first:", ii) < data.find("!u!", ii) or data.find("!u!", ii) == -1):
                    ii=data.find("- first:", ii) + 1
                    tile_index = int(data[data.find("m_TileIndex:", ii)+12: data.find("\n", data.find("m_TileIndex:", ii))].strip().replace("'", ""))
                    tile_x = round(float(data[data.find(" x:", ii)+3: data.find("\n", data.find(" x:", ii))].strip())) - layer_data["x"]
                    tile_y = round(float(data[data.find(" y:", ii)+3: data.find("\n", data.find(" y:", ii))].strip())) - layer_data["y"]
                    
                    index_in_layer = (layer_data["height"]-tile_y-1) * layer_data["width"] + tile_x
                    layer_data["data"][index_in_layer] = tile_index + 1 

                #Tiled is weird
                layer_data["x"] = 0
                layer_data["y"] = 0
                pfdata["layers"].append(layer_data)
                c+=1
                namei= data.find("\nGameObject:", namei)
                if namei != -1:
                    namei = data.find("m_Name:", namei)+1
                    name =  data[namei+7: data.find("\n", namei)].strip()
            except Exception as e:
                print("Error parsing prefab data:", e)
                continue
    
    pfdata["layers"] = list(reversed(pfdata["layers"]))
    pfdata["nextlayerid"] = c + 1
    return pfdata