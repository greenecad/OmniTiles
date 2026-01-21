import json, tarfile, os, random, time

def json_to_unity(file, inputName):
    input=json.loads(file)
    try:
        os.mkdir("./temp_dir")
    except:
        clean_temp_dir("./temp_dir")
        os.mkdir("./temp_dir")

    image_uid= gen_unity_uid()

    tc=input["tilesets"][0]["tilecount"]
    tile_uids={}
    for i in range(tc):
        tile_uids.update(create_tile_asset(i, image_uid))

    
    create_image_asset(image_uid, input)   
    
    
    create_tilemap_prefab(input, tile_uids)
    
    name = os.path.basename(inputName).split(".")[0]
    create_tar_file(name+".unitypackage", "./temp_dir")
    clean_temp_dir("./temp_dir")
    print("file created: "+name+".unitypackage")


    


def unity_to_json(file_path):
    extract_tar_file(file_path, "./temp_dir")
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

    clean_temp_dir("./temp_dir")

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

def gen_unity_uid():
    uid=""
    for i in range(32):
        uid += random.choice("0123456789abcdef")
    return uid

def create_tile_asset(index, image_uid):
    uid = gen_unity_uid()
    content = """%YAML 1.1\n"""
    content += """%TAG !u! tag:unity3d.com,2011:\n"""
    content += """--- !u!114 &11400000\n"""
    content += """MonoBehaviour:\n  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject:\n    fileID: 0\n  m_PrefabInstance:\n    fileID: 0\n  m_PrefabAsset:\n    fileID: 0\n  m_GameObject:\n    fileID: 0\n  m_Enabled: 1\n  m_EditorHideFlags: 0\n  m_Script:\n"""
    content += f"""    fileID: 13312\n    guid: 0000000000000000e000000000000000\n    type: 0\n"""
    content += f"""  m_Name: tile_{index}\n"""
    content += """  m_EditorClassIdentifier: UnityEngine.dll::UnityEngine.Tilemaps.Tile\n"""
    content += """  m_Sprite:\n"""
    content += f"""    fileID: {21300000 + index * 2}\n    guid: {image_uid}\n    type: 3\n"""
    content += """  m_Color: {r: 1, g: 1, b: 1, a: 1}\n"""
    content += """  m_Transform: \n    e00: 1\n    e01: 0\n    e02: 0\n    e03: 0\n    e10: 0\n    e11: 1\n    e12: 0\n    e13: 0\n    e20: 0\n    e21: 0\n    e22: 1\n    e23: 0\n    e30: 0\n    e31: 0\n    e32: 0\n    e33: 1\n"""
    content += """  m_instancedGameObject:\n    fileID: 0\n  m_Flags: 1\n  m_ColliderType: 1\n"""
    os.mkdir(f"./temp_dir/{uid}")
    with open(f"./temp_dir/{uid}/asset", "w") as out:
        out.write(content)
    with open(f"./temp_dir/{uid}/pathname", "w") as outp:
        outp.write(f"Assets/OmniTiles/Resources/tile_{index}.asset")
    md = create_meta_contents(uid, 11400000)
    with open(f"./temp_dir/{uid}/asset.meta", "w") as outm:
        outm.write(md)
    return {index: uid}
    


def create_image_asset(image_uid, input):
    if "image" not in input["tilesets"][0]:
        if "source" not in input["tilesets"][0]:
            raise ValueError("Tileset image missing, cannot convert to unitypackage")
        try:
            with open(input["tilesets"][0]["source"], "r") as imgf:
                tsx_data = imgf.read()
        except Exception as e:
            raise ValueError("Tileset source file "+input["tilesets"][0]["source"]+" not found, cannot convert to unitypackage")
    else:
        try:
            with open(input["tilesets"][0]["image"], "rb") as imgf:
                img_data = imgf.read()
            
            
            os.mkdir(f"./temp_dir/{image_uid}")
            with open(f"./temp_dir/{image_uid}/asset", "wb") as outi:
                outi.write(img_data)
            
            with open(f"./temp_dir/{image_uid}/pathname", "w") as outp:
                outp.write(f"Assets/OmniTiles/Resources/{os.path.basename(input['tilesets'][0]['image'])}")
            md = ""
            md += f"""fileFormatVersion: 2\nguid: {image_uid}\nTextureImporter:\n  internalIDToNameTable:\n"""
            for i in range(0, input["tilesets"][0]["tilecount"]):
                md += f"""  - first:\n      213: {21300000 + i * 2}\n    second: tile_{i}\n"""
            md += """  externalObjects: {}\n  serializedVersion: 13\n"""
            md += """  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 0\n    sRGBTexture: 1\n    linearTexture: 0\n    fadeOut: 0\n    borderMipMap: 0\n    mipMapsPreserveCoverage: 0\n    alphaTestReferenceValue: 0.5\n    mipMapFadeDistanceStart: 1\n    mipMapFadeDistanceEnd: 3\n"""
            md += """  bumpmap:\n    convertToNormalMap: 0\n    externalNormalMap: 0\n    heightScale: 0.25\n    normalMapFilter: 0\n    flipGreenChannel: 0\n"""
            md += """  isReadable: 0\n  streamingMipmaps: 0\n  streamingMipmapsPriority: 0\n  vTOnly: 0\n  ignoreMipmapLimit: 0\n  grayScaleToAlpha: 0\n  generateCubemap: 6\n  cubemapConvolution: 0\n  seamlessCubemap: 0\n  textureFormat: 1\n"""
            md += f"""  maxTextureSize: 32768\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 1\n    wrapV: 1\n    wrapW: 0\n  nPOTScale: 0\n  lightmap: 0\n  compressionQuality: 50\n  spriteMode: 2\n  spriteExtrude: 1\n  spriteMeshType: 1\n  alignment: 0\n  spritePivot: {{x: 0.5, y: 0.5}}\n  spritePixelsToUnits: {round(float(input["tilesets"][0]["tilewidth"]))}\n  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}\n  spriteGenerateFallbackPhysicsShape: 1\n  alphaUsage: 1\n  alphaIsTransparency: 1\n  spriteTessellationDetail: -1\n  textureType: 8\n  textureShape: 1\n  singleChannelComponent: 0\n  flipbookRows: 1\n  flipbookColumns: 1\n  maxTextureSizeSet: 0\n  compressionQualitySet: 0\n  textureFormatSet: 0\n  ignorePngGamma: 0\n  applyGammaDecoding: 1\n  swizzle: 50462976\n  cookieLightType: 1\n  platformSettings:\n  - serializedVersion: 4\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: 32768\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 0\n    compressionQuality: 50\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n    ignorePlatformSupport: 0\n    androidETC2FallbackOverride: 0\n    forceMaximumCompressionQuality_BC6H_BC7: 0\n  - serializedVersion: 4\n    buildTarget: Standalone\n    maxTextureSize: 32768\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 0\n    compressionQuality: 50\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n    ignorePlatformSupport: 0\n    androidETC2FallbackOverride: 0\n    forceMaximumCompressionQuality_BC6H_BC7: 0\n  - serializedVersion: 4\n    buildTarget: WebGL\n    maxTextureSize: 32768\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 0\n    compressionQuality: 50\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n    ignorePlatformSupport: 0\n    androidETC2FallbackOverride: 0\n    forceMaximumCompressionQuality_BC6H_BC7: 0\n"""
            md += "  spriteSheet:\n    serializedVersion: 2\n    sprites:\n"
            for i in range(0, input["tilesets"][0]["tilecount"]):
                tx = (i) % input["tilesets"][0]["columns"]
                ty = (i) // input["tilesets"][0]["columns"]
                md += f"""    - serializedVersion: 2\n      name: tile_{i}\n      rect:\n        serializedVersion: 2\n        x: {float(tx * input["tilesets"][0]["tilewidth"])}\n        y: {float(input["tilesets"][0]["tileheight"] *(input["tilesets"][0]["tilecount"]//input["tilesets"][0]["columns"]-1) - ty * input["tilesets"][0]["tileheight"])}\n        width: {round(float(input["tilesets"][0]["tilewidth"]))}\n        height: {round(float(input["tilesets"][0]["tileheight"]))}\n      alignment: 0\n      pivot: {{x: 0, y: 0}}\n      border: {{x: 0, y: 0, z: 0, w: 0}}\n      outline: []\n      physicsShape: []\n      tessellationDetail: 0\n      bones: []\n      spriteID: {21300000 + i * 2}\n      internalID: {21300000 + i * 2}\n      vertices: []\n      indices: \n      edges: []\n      weights: []\n      secondaryTextures: []\n      spriteCustomMetadata:\n        entries: []\n"""
            
            md += "    outline: []\n    customData: \n    physicsShape: []\n    bones: []\n    spriteID: \n    internalID: 0\n    vertices: []\n    indices: \n    edges: []\n    weights: []\n    secondaryTextures: []\n    spriteCustomMetadata:\n      entries: []\n    nameFileIdTable: {}\n  mipmapLimitGroupName: \n  pSDRemoveMatte: 0\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"""
            
            with open(f"./temp_dir/{image_uid}/asset.meta", "w") as outm:
                outm.write(md)
        except Exception as e:
            raise ValueError("Tileset image file "+input["tilesets"][0]["image"]+" not found, cannot convert to unitypackage")
    return image_uid


def create_tilemap_prefab(input, tile_uids):
    uid = gen_unity_uid()
    content = """%YAML 1.1\n"""
    content += """%TAG !u! tag:unity3d.com,2011:\n"""
    content += """--- !u!1001 &100100000\n"""
    content += """Prefab:\n  m_IsPrefabParent: 1\n  m_Modification:\n    m_Modifications: []\n    m_RemovedComponents: []\n    m_TransformParent: \n      fileID: 0\n"""
    content += """  m_ObjectHideFlags: 1\n  m_ParentPrefab:\n    fileID: 0\n  m_RootGameObject:\n    fileID: 1000000000000000\n  serializedVersion: 2\n\n"""

    content += """--- !u!1 &1000000000000000\n"""
    content += """GameObject:\n  m_component:\n  - component: \n      fileID: 1000000000000001\n  - component: \n      fileID: 1000000000000000000\n"""
    content += """  m_IsActive: 1\n  m_Layer: 0\n  m_Name: spritesheet\n  m_NavMeshLayer: 0\n  m_ObjectHideFlags: 0\n  m_PrefabInternal:\n    fileID: 100100000\n  m_PrefabParentObject:\n    fileID: 0\n"""
    content += """  m_StaticEditorFlags: 0\n  m_TagString: Untagged\n  serializedVersion: 5\n\n"""

    content += """--- !u!156049354 &1000000000000000000\n"""
    content += """Grid:\n  m_CellGap:\n    x: 0\n    y: 0\n    z: 0\n  m_CellLayout: 0\n  m_CellSize:\n    x: 1\n    y: 1\n    z: 0\n  m_CellSwizzle: 0\n  m_Enabled: 1\n  m_GameObject:\n    fileID: 1000000000000000\n  m_ObjectHideFlags: 1\n  m_PrefabInternal:\n    fileID: 100100000\n  m_PrefabParentObject:\n    fileID: 0\n\n"""

    content += """--- !u!4 &1000000000000001\n"""
    content += """Transform:\n  m_Children:\n  - fileID: 3000000000000000\n  m_Father:\n    fileID: 0\n  m_GameObject:\n    fileID: 1000000000000000\n  m_LocalEulerAnglesHint:\n    x: 0\n    y: 0\n    z: 0\n  m_LocalPosition:\n    x: 0\n    y: 0\n    z: 0\n  m_LocalRotation:\n    w: 1\n    x: 0\n    y: 0\n    z: 0\n  m_LocalScale:\n    x: 1\n    y: 1\n    z: 1\n  m_ObjectHideFlags: 1\n  m_PrefabInternal:\n    fileID: 100100000\n  m_PrefabParentObject:\n    fileID: 0\n  m_RootOrder: 0\n\n"""

    for layer_index in range(len(input["layers"])):
        content += f"""--- !u!1 &{2000000000000000+layer_index}\n"""
        content += f"""GameObject:\n  m_component:\n  - component: \n      fileID: {3000000000000000+layer_index}\n  - component: \n      fileID: {5000000000000000+layer_index}\n  - component: \n      fileID: {4000000000000000+layer_index}\n"""
        content += f"""  m_Icon:\n    fileID: 0\n  m_IsActive: 1\n  m_Layer: 0\n  m_Name: {input["layers"][layer_index]["name"]}\n  m_NavMeshLayer: 0\n  m_ObjectHideFlags: 0\n  m_PrefabInternal:\n    fileID: 100100000\n  m_PrefabParentObject:\n    fileID: 0\n  m_StaticEditorFlags: 0\n  m_TagString: Untagged\n  serializedVersion: 5\n\n"""

        content += f"""--- !u!4 &{3000000000000000+layer_index}\n"""
        content += f"""Transform:\n  m_Children: []\n  m_Father:\n    fileID: 1000000000000001\n  m_GameObject:\n    fileID: {2000000000000000+layer_index}\n"""
        content += f"""  m_LocalEulerAnglesHint:\n    x: 0\n    y: 0\n    z: 0\n  m_LocalPosition:\n    x: 0\n    y: 0\n    z: 0\n  m_LocalRotation:\n    w: 1\n    x: 0\n    y: 0\n    z: 0\n  m_LocalScale:\n    x: 1\n    y: 1\n    z: 1\n  m_ObjectHideFlags: 1\n  m_PrefabInternal:\n    fileID: 100100000\n  m_PrefabParentObject:\n    fileID: 0\n  m_RootOrder: 0\n\n"""

        content += f"""--- !u!483693784 &{4000000000000000+layer_index}\n"""
        content += """TilemapRenderer:\n  m_AutoUVMaxAngle: 89\n  m_AutoUVMaxDistance: 0.5\n  m_CastShadows: 0\n  m_ChunkSize:\n    x: 32\n    y: 32\n    z: 32\n  m_DynamicOccludee: 1\n  m_Enabled: 1\n"""
        content += f"""  m_GameObject:\n    fileID: {2000000000000000+layer_index}\n"""
        content += """  m_IgnoreNormalsForChartDetection: 0\n  m_ImportantGI: 0\n  m_LightProbeUsage: 0\n  m_LightProbeVolumeOverride:\n    fileID: 0\n  m_LightmapParameters:\n    fileID: 0\n  m_MaskInteraction: 0\n  m_Materials:\n  - fileID: 10754\n    guid: 0000000000000000f000000000000000\n    type: 0\n  m_MaxChunkCount: 16\n  m_MaxFrameAge: 16\n  m_MinimumChartSize: 4\n  m_MotionVectors: 1\n  m_ObjectHideFlags: 1\n  m_PrefabInternal:\n    fileID: 100100000\n"""
        content += """  m_PrefabParentObject:\n    fileID: 0\n  m_PreserveUVs: 0\n  m_ProbeAnchor:\n    fileID: 0\n  m_ReceiveShadows: 0\n  m_ReflectionProbeUsage: 0\n  m_ScaleInLightmap: 1\n  m_SelectedEditorRenderState: 0\n  m_SortOrder: 0\n  m_SortingLayer: 0\n  m_SortingLayerID: 0\n  m_SortingOrder: 6\n  m_StaticBatchInfo:\n    firstSubMesh: 0\n    subMeshCount: 0\n  m_StaticBatchRoot:\n    fileID: 0\n  m_StitchLightmapSeams: 0\n\n"""

        content += f"""--- !u!1839735485 &{5000000000000000+layer_index}\n"""
        content += """Tilemap:\n  m_AnimatedTiles: {}\n  m_AnimationFrameRate: 1\n  m_Color:\n    r: 1\n    g: 1\n    b: 1\n    a: 1\n  m_Enabled: 1\n  m_GameObject:\n"""
        content += f"""    fileID: {2000000000000000+layer_index}\n"""
        content += """  m_ObjectHideFlags: 1\n  m_Origin:\n    x: 0\n    y: 0\n    z: 0\n  m_PrefabInternal:\n    fileID: 100100000\n  m_PrefabParentObject:\n    fileID: 0\n  m_TileAnchor:\n    x: 0.5\n    y: 0.5\n    z: 0\n"""
        content += """  m_TileAssetArray:\n"""
        for i in range(len(tile_uids)):
            content += f"""  - m_Data:\n      fileID: 11400000\n      guid: {tile_uids[i]}\n      type: 2\n    m_RefCount: 1\n"""
        content += """  m_TileColorArray:\n  - m_Data:\n      a: 1\n      b: 1\n      g: 1\n      r: 1\n    m_RefCount: 1\n"""
        content += """  - m_Data:\n      e00: 1\n      e01: 0\n      e02: 0\n      e03: 0\n      e10: 0\n      e11: 1\n      e12: 0\n      e13: 0\n      e20: 0\n      e21: 0\n      e22: 1\n      e23: 0\n      e30: 0\n      e31: 0\n      e32: 0\n      e33: 1\n    m_RefCount: 1\n"""
        content += """  m_TileOrientation: 0\n  m_TileOrientationMatrix:\n    e00: 1\n    e01: 0\n    e02: 0\n    e03: 0\n    e10: 0\n    e11: 1\n    e12: 0\n    e13: 0\n    e20: 0\n    e21: 0\n    e22: 1\n    e23: 0\n    e30: 0\n    e31: 0\n    e32: 0\n    e33: 1\n"""
        content += """  m_TileRefreshArray:\n"""
        for i in range(len(tile_uids)):
            content += f"""  - m_DirtyIndex: 0\n    serializedVersion: 1\n"""
        content += """  m_TileSpriteArray:\n"""
        for i in range(len(tile_uids)):
            content += f"""  - m_Data:\n      fileID: {21300000 + i * 2}\n      guid: {tile_uids[i]}\n      type: 3\n    m_RefCount: 1\n"""

        content += """  m_Tiles:\n"""
        i=0
        for tile in input["layers"][layer_index]["data"]:
            if tile > 0:
                content += f"""  - first: \n      x: { i % input["width"] }\n      y: { input["height"] - 1 - i // input["width"]}\n      z: 0\n"""
                content += f"""    second:\n      m_ColliderType: 1\n      m_ObjectToInstantiate:\n        fileID: 0\n      m_TileColorIndex: 0\n      m_TileFlags: 1\n      m_TileIndex: '{tile - 1}'\n      m_TileMatrixIndex: 0\n      m_TileSpriteIndex: '{tile - 1}'\n"""
            i+=1
        content += "\n"


    os.mkdir(f"./temp_dir/{uid}")
    with open(f"./temp_dir/{uid}/asset", "w") as out:
        out.write(content)
    with open(f"./temp_dir/{uid}/pathname", "w") as outp:
        outp.write(f"Assets/OmniTiles/Maps/Tilemap.prefab")
    md = create_meta_contents(uid, 100100000)
    with open(f"./temp_dir/{uid}/asset.meta", "w") as outm:
        outm.write(md)



def create_meta_contents(uid, object_id):
    md = f"""fileFormatVersion: 2\nguid: {uid} \ntimeCreated: {str(time.time())}\nlicenseType: Free\n"""
    md += f"""NativeFormatImporter:\n  externalObjects: {{}}\n  fileIDToRecycleName: {object_id}\n  serializedVersion: 3\n  assetBundleName: ''\n  assetBundleVariant: ''\n"""
    return md
    