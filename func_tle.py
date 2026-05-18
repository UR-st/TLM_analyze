import numpy as np
import math
from sgp4.api import Satrec, WGS72
from class_def import TLE_Elements_, TLE_Hex_
import struct
import json

def get_tle_lines(file_name):
    """TLEファイルを読み込み、3行のリストを返す"""
    with open(file_name, "r", encoding="utf-8") as f:
        # 空行を除去
        lines = [line.strip() for line in f if line.strip()]
    
    if len(lines) < 3:
        raise ValueError("TLE file must have at least 3 lines.")
    return lines[:3]

def tle_2_param(lines):
    """ライブラリを用いてTLEを解析し、TLE_Elementsクラスに値を格納する"""
    # インスタンス化 (クラスの定義に合わせて修正してください)
    tle = TLE_Elements_()
    
    # sgp4ライブラリでパース
    # lines[1]が1行目、lines[2]が2行目
    sat = Satrec.twoline2rv(lines[1], lines[2], WGS72)
    
    # --- 値の抽出と格納 ---
    
    # エポック (2000年を100とする形式に合わせて変換)
    # sat.epochdays は 1月1日 00:00:00 が 1.0 に相当する
    tle.ep_year = 100 + (sat.epochyr if sat.epochyr < 57 else sat.epochyr - 1900)
    tle.ep_day = sat.epochdays
    
    # 軌道要素 (sgp4内部ではラジアンなので、必要に応じて度数法に変換)
    tle.rev = sat.no_kozai * (24 * 60) / (2 * math.pi) # 平均運動 (回/日)
    tle.bstar = sat.bstar
    tle.eqinc = math.degrees(sat.inclo) # 軌道傾斜角 (deg)
    tle.ecc = sat.ecco                 # 離心率
    tle.mnan = math.degrees(sat.mo)    # 平均近点離角 (deg)
    tle.argp = math.degrees(sat.argpo) # 近地点引数 (deg)
    tle.ascn = math.degrees(sat.nodeo) # 昇交点赤経 (deg)

    # デバッグ表示
    print(f"Year: {tle.ep_year}")
    print(f"Day:  {tle.ep_day}")
    print(f"Rev:  {tle.rev}")
    print(f"B*:   {tle.bstar}")
    print(f"Inc:  {tle.eqinc}")
    print(f"Ecc:  {tle.ecc}")
    print(f"Mnan: {tle.mnan}")
    print(f"Argp: {tle.argp}")
    print(f"Ascn: {tle.ascn}")

    return tle

def param_2_hex(param, type):
    # パラメータを16進数(バイナリ)に変換するロジックをここに記述
    tle_hex = TLE_Hex_()
    tle_hex.ep_year = struct.pack('<I',param.ep_year).hex()
    tle_hex.ep_day = struct.pack('<d',param.ep_day).hex()
    tle_hex.rev = struct.pack('<d',param.rev).hex()
    tle_hex.bstar = struct.pack('<d',param.bstar).hex()
    tle_hex.eqinc = struct.pack('<d',param.eqinc).hex()
    tle_hex.ecc = struct.pack('<d',param.ecc).hex()
    tle_hex.mnan = struct.pack('<d',param.mnan).hex()
    tle_hex.argp = struct.pack('<d',param.argp).hex()
    tle_hex.ascn = struct.pack('<d',param.ascn).hex()
   
    return tle_hex # 仮の実装

def tle_2_MRAM(file_name,file_name_of_json):
    lines = get_tle_lines(file_name)
    tle_params = tle_2_param(lines)
    tle_hex = param_2_hex(tle_params, type)
    tle_2_command_script(tle_hex,file_name_of_json)
    
    # ここでMRAM送信用データへの変換処理を行う想定
    
    return tle_hex
def tle_2_command_script(tle_hex,file_name_of_json):
    file_path = file_name_of_json
    with open(file_path, "w", encoding="utf-8") as f:
    # json.dump で辞書データをファイルに書き込む
    # indent=4 を指定すると、人間が見やすいように改行とインデントを入れてくれます
        json.dump(vars(tle_hex), f, indent=4)
    

"""
def get_tle(file_name):
    element=[]

    with open(file_name, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # 空行を除去して読み込み

    element.append(lines[0].split())
    element.append(lines[1].split())
    element.append(lines[2].split())

    return element
def tle_2_MRAM(file_name):
    tle =   
    elements = get_tle(file_name)
    tle = tle_2_param(elements)
    tle_mram = "e" 
    return tle_mram

def tle_2_param(elements):
    tle =   
    tle.ep_year  = 100 + int(elements[1][3][:2]) #y2000->100,y1900->0
    tle.ep_day = float(elements[1][3][2:]) #1/1 00:00:00utc->1.0
    tle.rev = float(elements[2][7])
    tle.bstar = float("0."+elements[1][6][:-2])*10**(float(elements[1][6][-2:]))
    tle.eqinc = float(elements[2][2])
    tle.ecc = float("0."+elements[2][4])
    tle.mnan = float(elements[2][6])
    tle.argp = float(elements[2][5])
    tle.ascn = float(elements[2][3])

    print(tle.ep_year)
    print(tle.ep_day)
    print(tle.rev)
    print(tle.bstar)
    print(tle.eqinc)
    print(tle.ecc)
    print(tle.mnan)
    print(tle.argp)
    print(tle.ascn)

    return tle

def param_2_hex(param,type):

    return hex




"""