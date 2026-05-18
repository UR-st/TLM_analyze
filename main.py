import numpy as np
import func_tle as fn_tle
from class_def import TLE_Elements_,TLE_Hex_
import configparser
import os

# 設定ファイルのパス
current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, "config.ini")

# INIファイルの読み込み
config = configparser.ConfigParser()
config.read(config_path, encoding="utf-8")
#TLE変更scriptの作成
if config.getboolean("RUN_SETTINGS", "TLE_MRAM"):
    TLE_HEX = TLE_Hex_
    TLE_HEX = fn_tle.tle_2_MRAM("tle.txt","TLE_cmd")



