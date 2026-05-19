import numpy as np
import math
from class_dir.class_def import TLE_Elements_, TLE_Hex_
import struct
import json
import os
import pandas
import builtins

def suns_print():
    builtins.print("s")

# Backward-compatible alias (avoid shadowing builtins inside this module)
def test():
    return suns_print()
