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
    
def generate_mram_json(tle_hex_instance, file_out_path: str = "TLE_cmd.json", mram_interval_ms: int = 5000):
    """
    TLE_Hex_ のデータから、MRAM書き込み（1つ目:36バイト、2つ目:32バイト）とモード遷移コマンドを含むJSONを生成する
    """
    # 1. 各要素を順番に結合（大文字統一）
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

    base_address = 32768
    
    # 【仕様に合わせた厳密な分割】
    # 1つ目は36バイト(72文字)、2つ目は残り32バイト(64文字)
    first_command_bytes = 36 

    # MRAM書き込みコマンド（要素）を生成する内部関数
    def create_mram_script_element(start_byte_idx, end_byte_idx, current_address, relative_time):
        sub_hex = hex_sequence[start_byte_idx * 2 : end_byte_idx * 2]
        
        # テレメトリチェック部分のベース（開始アドレスチェック）
        telemetry_conditions = [
            {
                "obc": "MOBC",
                "packet_id": "MEMDUMP_MRAM3",
                "field_name": "memory_tr_dump_begin_address",
                "value": current_address,
                "condition": "eq",
                "continue_sending_commands": True
            }
        ]

        # 各バイトのチェック条件を追加
        for byte_index in range(start_byte_idx, end_byte_idx):
            local_idx = byte_index - start_byte_idx
            byte_hex = sub_hex[local_idx * 2 : local_idx * 2 + 2]
            byte_value_10 = int(byte_hex, 16)

            # 重要：パケットが変わるため、OBCから返るインデックスは常に 0 からスタートする
            telemetry_idx = local_idx 

            # パケットIDの判定（元データ全体の通算インデックスが5以降ならEEPROM）
            packet_id = "MEMDUMP_MRAM3" if byte_index <= 4 else "MEMDUMP_EEPROM3"

            for tr_num in [1, 2, 3]:
                condition_packet = {
                    "obc": "MOBC",
                    "packet_id": packet_id,
                    "field_name": f"memory_tr{tr_num}_dump_data[{telemetry_idx}]",
                    "value": byte_value_10,
                    "condition": "eq",
                    "continue_sending_commands": True
                }
                telemetry_conditions.append(condition_packet)

        element = {
            "relative_time_ms": relative_time,
            "command_satellite_id": "SAT_2U",
            "command_processor_id": "MOBC",
            "command_route": "DIRECT",
            "channel_id": "MEM_MRAM_EEPROM_WRITE",
            "response_packet_id": "ONLY_RESULT_RESPONSE",
            "response_satellite_id": "GS_2U",
            "response_processor_id": "AFSK",
            "response_route": "DIRECT",
            "issuer_satellite_id": "GS_2U",
            "issuer_processor_id": "AFSK",
            "args": {
                "dump_flag": 1,
                "address": current_address,
                "write_value": sub_hex
            },
            "comment": "MRAMの値を書き換える場合は使用",
            "check": [],
            "command_reply_check": True,
            "telemetry_check_condition": telemetry_conditions,
            "auto_resend_limit_count": 7,
            "result": "",
            "doc_id": "H,+-u=4})4/6Kv*=Ic~@"
        }

        # 2つ目以降のコマンドにはヘッダーを追加
        if relative_time > 0:
            element = {
                "reference_time": "pass_start",
                "execution_time": 0,
                **element
            }
            
        return element

    # --- 各コマンドの生成 ---

    # 1つ目のMRAM書き込み（0 ～ 36バイト目 / アドレス 32768）
    script_mram_1 = create_mram_script_element(
        start_byte_idx=0, 
        end_byte_idx=first_command_bytes, 
        current_address=base_address, 
        relative_time=0
    )

    # 2つ目のMRAM書き込み（36 ～ 68バイト目 / アドレス 32804）
    script_mram_2 = create_mram_script_element(
        start_byte_idx=first_command_bytes, 
        end_byte_idx=len(hex_sequence) // 2, 
        current_address=base_address + first_command_bytes, 
        relative_time=mram_interval_ms
    )

    # 3つ目のコマンド：モード遷移
    transition_time_ms = mram_interval_ms * 2
    script_transition = {
        "reference_time": "pass_start",
        "execution_time": 0,
        "relative_time_ms": transition_time_ms,
        "command_satellite_id": "SAT_2U",
        "command_processor_id": "MOBC",
        "command_route": "DIRECT",
        "channel_id": "MM_START_TRANSITION",
        "response_packet_id": "ONLY_RESULT_RESPONSE",
        "response_satellite_id": "GS_2U",
        "response_processor_id": "AFSK",
        "response_route": "DIRECT",
        "issuer_satellite_id": "GS_2U",
        "issuer_processor_id": "AFSK",
        "args": {},
        "comment": "書き換えたMRAMがある場合はloadする",
        "check": [],
        "command_reply_check": True,
        "telemetry_check_condition": [
            {
                "obc": "MOBC",
                "packet_id": "MEMDUMP_MRAM3",
                "field_name": "memory_tr_dump_begin_address",
                "value": 0,
                "condition": "eq",
                "continue_sending_commands": True
            }
        ],
        "auto_resend_limit_count": 7,
        "result": "",
        "doc_id": "#o:4.JlE7g^qBFE(CG:E"
    }

    # 全体のJSON構造に統合
    script_template = {
        "absolute_times": {
            "pass_start": "2020-01-01 0:0:0.0"
        },
        "version": 4,
        "is_mixed": True,
        "scripts": [script_mram_1, script_mram_2, script_transition]
    }

    # JSONファイルとして書き出し
    with open(file_out_path, "w", encoding="utf-8") as f:
        json.dump(script_template, f, indent=4, ensure_ascii=False)

    print(f"正常に正規仕様に準拠したコマンドスクリプトを生成しました: {file_out_path}")