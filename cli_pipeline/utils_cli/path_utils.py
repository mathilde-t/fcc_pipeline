import os

def make_norm_dir_name(path):
    parent = os.path.dirname(path)
    name = os.path.basename(path)
    return os.path.join(parent, f"{name}_norm")

def print_out_doubleline(title, n=80):
        print("=" * n)
        print(title)
        print("-" * n)

def print_out_line(n=80):
    print("=" * n)
    print("\n")