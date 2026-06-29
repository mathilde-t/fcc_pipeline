import os

def make_norm_dir_name(path):
    parent = os.path.dirname(path)
    name = os.path.basename(path)
    return os.path.join(parent, f"{name}_norm")