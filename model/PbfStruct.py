import yaml

fs = open("data.yaml",encoding="UTF-8")
yamldata = yaml.load(fs,Loader=yaml.FullLoader)
