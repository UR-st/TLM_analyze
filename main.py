import numpy as np
import func_tle as fn_tle
from class_def import TLE_Elements_,TLE_Hex_
TLE_HEX = TLE_Hex_
TLE_HEX = fn_tle.tle_2_MRAM("tle.txt","TLE_cmd")

print(vars(TLE_HEX))


