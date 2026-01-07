import json, tarfile

def json_to_unity(file):
    input=json.loads(file)

def unity_to_json(file):
    pass

def extract_tar_file(source, dest):
    tarfile.open(source, mode="r:bz2").extractall(dest)

def create_tar_file(tar_name, source_dir):
    with tarfile.open(tar_name, "w:bz2") as tar:
        tar.add(source_dir, arcname=".")

create_tar_file("archive.unitypackage", "C:\\Users\\caden\\projects\\OmniTiles\\unity_test")