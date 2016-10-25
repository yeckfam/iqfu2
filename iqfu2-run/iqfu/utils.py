"""
utils.py
--------
Helpful utility functions. Nothing crazy.
"""
import glob
import os

def mkdir(path):
    """Make the specified directory. Swallow directory exists errors."""
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno != 17:
            raise

def expand_paths(globbed_paths):
    """Expand a list of globbed paths into absolute paths."""
    paths = []
    for globbed_path in globbed_paths:
        for path in glob.iglob(globbed_path):
            if os.path.isfile(path):
                paths.append(path)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        paths.append(os.path.join(root, f))
    return paths
