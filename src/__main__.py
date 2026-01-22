import sys, json, os
from csv_convert import json_to_csv, csv_to_json
from tmx_convert import json_to_tmx, tmx_to_json
from tscn_convert import tscn_to_json, json_to_tscn
from unity_convert import json_to_unity, unity_to_json

supportedFiles = ["tmx", "tscn", "unitypackage", "csv", "json"]
conversionFunctions = {
    "csv":{"import":json_to_csv, "export":csv_to_json},
    "tmx":{"import":json_to_tmx, "export":tmx_to_json},
    "tscn":{"import":json_to_tscn, "export":tscn_to_json},
    "unitypackage":{"import":json_to_unity, "export":unity_to_json}
}

if len(sys.argv)==1 or sys.argv[1]=="-h" or sys.argv[1]=="--help":
    print("Usage:")
    print("    OmniTiles input_file output_type [options]")
    print()
    print("    -input_file       File path to file to be converted")
    print("    -output_type      File type to convert to")
    sys.exit(0)
inputFile = sys.argv[1]
outputType = sys.argv[2]

if "--tscn_directory" in sys.argv:
    inputType = "tscn"
else:
    inputType = sys.argv[1].split(".")[1]

if inputType not in supportedFiles:
    raise ValueError("File type ."+inputType+" not supported")
if outputType not in supportedFiles:
    raise ValueError("File type ."+outputType+" not supported")

conv1 = None
conv2 = None

if inputType != "json":
    conv1 = conversionFunctions[inputType]["export"]
if outputType != "json":
    conv2 = conversionFunctions[outputType]["import"]

if inputType == "unitypackage":
    file = unity_to_json(inputFile)
    if outputType == "tscn":
        if not os.path.isdir(inputFile.split(".")[0]):
            os.mkdir(inputFile.split(".")[0])
        json = json.loads(file)
        for layer in range(len(json["layers"])):
            out = json_to_tscn(file, layer)
            result = open(inputFile.split(".")[0]+"/"+os.path.basename( inputFile ).split(".")[0]+f"_layer{layer}."+outputType, "w")
            result.write(out)
            result.close()
            print(f"file created: {inputFile.split(".")[0]+"/"+os.path.basename(inputFile).split('.')[0]}_layer{layer}.{outputType}")
    else:
        if conv2 is not None:
            file = conv2(file)
        result = open(inputFile.split(".")[0]+"."+outputType, "w")
        result.write(file)
        result.close()
        print("file created: "+inputFile.split(".")[0]+"."+outputType)
elif inputType == "tscn": ##add flag/option later
    if os.path.isdir(inputFile):
        out = {}
        i=0
        for layer in iter(os.listdir(inputFile)):
            with open(inputFile+"/"+layer, "r") as file:
                file=file.read()
                if conv1 is not None:
                    file=conv1(file)
                if len(out.keys())==0:
                    out = json.loads(file)
                else:
                    out["layers"].append(json.loads(file)["layers"][0])
                out["layers"][i]["name"]="Layer_"+str(i)
                out["layers"][i]["id"]=i
                i+=1
        for i in range(len(out["layers"])):
            if len(out["layers"][i]["data"])!= out["width"]*out["height"]:
                diff = out["width"]*out["height"] - len(out["layers"][i]["data"])
                for d in range(diff):
                    out["layers"][i]["data"].append(0)
    else:
        with open(inputFile, "r") as file:
            file=file.read()
            if conv1 is not None:
                file=conv1(file)
            out = json.loads(file)
    if outputType == "unitypackage":
        json_to_unity(json.dumps(out), inputFile)
    else:
        if conv2 is not None:
            file = conv2(json.dumps(out))
        result = open(inputFile.split(".")[0]+"."+outputType, "w")
        result.write(file)
        result.close()
        print("file created: "+inputFile.split(".")[0]+"."+outputType)

  
elif outputType == "unitypackage":
    with open(inputFile, "r") as file:
        file=file.read()
        if conv1 is not None:
            file=conv1(file)
        json_to_unity(file, inputFile)
          
                

elif outputType == "tscn": ##add flag/option later
    with open(inputFile, "r") as file:
        file=file.read()
        if conv1 is not None:
            file=conv1(file)
        if not os.path.isdir(inputFile.split(".")[0]):
            os.mkdir(inputFile.split(".")[0])
        json = json.loads(file)
        for layer in range(len(json["layers"])):
            out = json_to_tscn(file, layer)
            result = open(inputFile.split(".")[0]+"/"+os.path.basename( inputFile ).split(".")[0]+f"_layer{layer}."+outputType, "w")
            result.write(out)
            result.close()
            print(f"file created: {inputFile.split(".")[0]+"/"+os.path.basename(inputFile).split('.')[0]}_layer{layer}.{outputType}")

else:
    with open(inputFile, "r") as file:
        file=file.read()
        if conv1 is not None:
            file=conv1(file)
        if conv2 is not None:
            file=conv2(file)

    result = open(inputFile.split(".")[0]+"."+outputType, "w")
    result.write(file)
    result.close()
    print("file created: "+inputFile.split(".")[0]+"."+outputType)
    

