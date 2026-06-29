import json

with open("scripts/data_configs.json") as f:
    DATACONFS = json.load(f)

# class Config:
#     def __init__(self, cfg):
#         self.inputDir = cfg["inputDir"]
#         self.outputDir = cfg["outputDir"]
#         self.procDict = cfg["procDict"]
#         self.processList = cfg["processList"]

# the same class as above but not repetitive, 
# appends automatically ato data_config.json changes

class Config:
    def __init__(self, cfg):
        for key, value in cfg.items():
            setattr(self, key, value)

            # syntax : setattr(object, attribute_name, value)
            # >>>>>> : object.attribute_name = value

def get_config(name):
    return Config(DATACONFS[name])