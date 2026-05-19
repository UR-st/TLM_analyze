import numpy as np
import os
import sys

# Ensure local modules under ./src are importable regardless of CWD/runner.
_SRC_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_SRC_DIR, "function"))
sys.path.insert(0, os.path.join(_SRC_DIR, "class"))

import function.func_tle as fn_tle
from class_dir.class_def import TLE_Elements_, TLE_Hex_
import configparser
import function.func_suns as fn_suns
from gui.gui import start_app

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
    start_app()
    """TLE_HEX = TLE_Hex_
    # 関数に渡すファイル名に変数を指定
    TLE_HEX = fn_tle.tle_2_MRAM(tle_input_path, "TLE_cmd")
"""
fn_suns.test()
