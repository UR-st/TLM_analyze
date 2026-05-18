import numpy as np
import func_tle as fn_tle
from class_def import TLE_Elements_, TLE_Hex_
import configparser
import os

# --- パス指定の修正（ここを書き換えます） ---
# バッチファイルを実行した場所（プロジェクトのルート）を基準にする
base_dir = os.getcwd() 

config_path = os.path.join(base_dir, "config.ini")
tle_input_path = os.path.join(base_dir, "tle.txt")
# ------------------------------------------

# INIファイルの読み込み
config = configparser.ConfigParser()
config.read(config_path, encoding="utf-8")

# TLE変更scriptの作成
if config.getboolean("RUN_SETTINGS", "TLE_MRAM"):
    TLE_HEX = TLE_Hex_
    # 関数に渡すファイル名に変数を指定
    TLE_HEX = fn_tle.tle_2_MRAM(tle_input_path, "TLE_cmd")