import numpy as np
import math
from sgp4.api import Satrec, WGS72
from class_def import TLE_Elements_, TLE_Hex_
import struct
import json
import os
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
    #tle_2_command_script(tle_hex,file_name_of_json)
    generate_mram_json(tle_hex, file_name_of_json)
    
    # ここでMRAM送信用データへの変換処理を行う想定
    
    return tle_hex
def tle_2_command_script(tle_hex,file_name_of_json):
    file_path = file_name_of_json
    with open(file_path, "w", encoding="utf-8") as f:
    # json.dump で辞書データをファイルに書き込む
    # indent=4 を指定すると、人間が見やすいように改行とインデントを入れてくれます
        json.dump(vars(tle_hex), f, indent=4)

import os
import json

def generate_mram_json(tle_hex_instance, file_out_path: str = "TLE_cmd.json"):
    """
    TLE_Hex_ のデータから、最初の3つのコマンド（MRAM書き込み×2、APP初期化）のみで構成された
    1U用と2U用のJSONスクリプトを自動生成します。
    """
    # 1. 各要素を順番に結合（大文字に統一）
    hex_sequence = (
        tle_hex_instance.ep_year +
        tle_hex_instance.ep_day +
        tle_hex_instance.rev +
        tle_hex_instance.bstar +
        tle_hex_instance.eqinc +
        tle_hex_instance.ecc +
        tle_hex_instance.mnan +
        tle_hex_instance.argp +
        tle_hex_instance.ascn
    ).upper()

    first_command_bytes = 36  # 1パケット目は36バイト
    base_address = 32768

    # === 1つ目のMRAM書き込みコマンド用テレメトリチェック生成 ===
    telemetry_conditions_1 = [
        {
            "obc": "MOBC",
            "packet_id": "MEMDUMP_MRAM3",
            "field_name": "memory_tr_dump_begin_address",
            "value": base_address,
            "condition": "eq",
            "continue_sending_commands": True
        }
    ]
    sub_hex_1 = hex_sequence[0 : first_command_bytes * 2]
    for i in range(first_command_bytes):
        byte_hex = sub_hex_1[i * 2 : i * 2 + 2]
        byte_value_10 = int(byte_hex, 16)
        
        # 配列の添え字が2以下なら MRAM3、3以上なら EEPROM3 (お手本の仕様)
        packet_id = "MEMDUMP_MRAM3" if i <= 2 else "MEMDUMP_EEPROM3"
        
        for tr_num in [1, 2, 3]:
            telemetry_conditions_1.append({
                "obc": "MOBC",
                "packet_id": packet_id,
                "field_name": f"memory_tr{tr_num}_dump_data[{i}]",
                "value": byte_value_10,
                "condition": "eq",
                "continue_sending_commands": True
            })

    # === 2つ目のMRAM書き込みコマンド用テレメトリチェック生成 ===
    address_2 = base_address + first_command_bytes
    telemetry_conditions_2 = [
        {
            "obc": "MOBC",
            "packet_id": "MEMDUMP_MRAM3",
            "field_name": "memory_tr_dump_begin_address",
            "value": address_2,
            "condition": "eq",
            "continue_sending_commands": True
        }
    ]
    sub_hex_2 = hex_sequence[first_command_bytes * 2 :]
    total_bytes_2 = len(sub_hex_2) // 2
    for i in range(total_bytes_2):
        byte_hex = sub_hex_2[i * 2 : i * 2 + 2]
        byte_value_10 = int(byte_hex, 16)
        
        # 2パケット目も同様に、独立して添え字が2以下なら MRAM3、3以上なら EEPROM3
        packet_id = "MEMDUMP_MRAM3" if i <= 2 else "MEMDUMP_EEPROM3"
        
        for tr_num in [1, 2, 3]:
            telemetry_conditions_2.append({
                "obc": "MOBC",
                "packet_id": packet_id,
                "field_name": f"memory_tr{tr_num}_dump_data[{i}]",
                "value": byte_value_10,
                "condition": "eq",
                "continue_sending_commands": True
            })

    # ファイル名（拡張子あり/なし）の分解
    base_name, ext = os.path.splitext(file_out_path)

    # 1U用と2U用のループ処理
    sat_types = ["1U", "2U"]
    for sat_type in sat_types:
        sat_id = f"SAT_{sat_type}"
        gs_id = f"GS_{sat_type}"
        specific_out_path = f"{base_name}_{sat_type}{ext}"

        # 最初の3つのコマンドのみを格納
        scripts = [
            {
                "relative_time_ms": 0,
                "command_satellite_id": sat_id,
                "command_processor_id": "MOBC",
                "command_route": "DIRECT",
                "channel_id": "MEM_MRAM_EEPROM_WRITE",
                "response_packet_id": "ONLY_RESULT_RESPONSE",
                "response_satellite_id": gs_id,
                "response_processor_id": "AFSK",
                "response_route": "DIRECT",
                "issuer_satellite_id": gs_id,
                "issuer_processor_id": "AFSK",
                "args": {
                    "dump_flag": 1,
                    "address": base_address,
                    "write_value": sub_hex_1
                },
                "comment": "MRAMの値を書き換える場合は使用",
                "check": [],
                "command_reply_check": True,
                "telemetry_check_condition": telemetry_conditions_1,
                "auto_resend_limit_count": 7,
                "result": "",
                "doc_id": "H,+-u=4})4/6Kv*=Ic~@"
            },
            {
                "relative_time_ms": 0,
                "command_satellite_id": sat_id,
                "command_processor_id": "MOBC",
                "command_route": "DIRECT",
                "channel_id": "MEM_MRAM_EEPROM_WRITE",
                "response_packet_id": "ONLY_RESULT_RESPONSE",
                "response_satellite_id": gs_id,
                "response_processor_id": "AFSK",
                "response_route": "DIRECT",
                "issuer_satellite_id": gs_id,
                "issuer_processor_id": "AFSK",
                "args": {
                    "dump_flag": 1,
                    "address": address_2,
                    "write_value": sub_hex_2
                },
                "comment": "MRAMの値を書き換える場合は使用",
                "check": [],
                "command_reply_check": True,
                "telemetry_check_condition": telemetry_conditions_2,
                "auto_resend_limit_count": 7,
                "result": "",
                "doc_id": "}[h=Z=uyhxuXI8KxzzoS"
            },
            {
                "relative_time_ms": 0,
                "command_satellite_id": sat_id,
                "command_processor_id": "MOBC",
                "command_route": "DIRECT",
                "channel_id": "AM_INITIALIZE_APP",
                "response_packet_id": "ONLY_RESULT_RESPONSE",
                "response_satellite_id": gs_id,
                "response_processor_id": "AFSK",
                "response_route": "DIRECT",
                "issuer_satellite_id": gs_id,
                "issuer_processor_id": "AFSK",
                "args": {
                    "app_id": 188
                },
                "comment": "書き換えたMRAMがある場合はloadする",
                "check": [],
                "command_reply_check": True,
                "telemetry_check_condition": "NO_CHECK",
                "auto_resend_limit_count": 7,
                "result": "",
                "doc_id": "#o:4.JlE7g^qBFE(CG:E"
            }
        ]

        # 最終テンプレート
        script_template = {
            "absolute_times": {
                "pass_start": "2020-01-01 0:0:0.0"
            },
            "version": 4,
            "is_mixed": True,
            "scripts": scripts
        }

        # JSONファイル出力
        with open(specific_out_path, "w", encoding="utf-8") as f:
            json.dump(script_template, f, indent=4, ensure_ascii=False)

        print(f"再現完了：スクリプトを出力しました: {specific_out_path}")