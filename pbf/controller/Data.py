import yaml

from .. import data_path

yamldata = {}

with open(data_path, encoding="UTF-8") as fs:
    yamldata = yaml.load(fs, Loader=yaml.FullLoader)

def loadYamldata(filename: str = data_path, content: dict = None):
    # 打开yaml文件
    global yamldata
    if content is not None:
        yamldata = content
    else:
        with open(filename, encoding="UTF-8") as fs:
            yamldata = yaml.load(fs, Loader=yaml.FullLoader)