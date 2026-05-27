import numpy as np
import math
from sgp4.api import Satrec, WGS72
from class_dir.class_def import TLE_Elements_, TLE_Hex_
import struct
import json
import os
import requests
import random
import string  # ランダム文字列生成用に追加

# --- ランダムID生成用の補助関数 ---
def generate_random_doc_id(length=20):
    """20文字のランダムな英数字文字列を生成します"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_mram_json(hex_sequence: str, base_address: int, file_out_path: str = "TLE_cmd.json", app_id: int = 188):
    """
    16進数文字列データから、MRAM書き込みコマンドとAPP初期化コマンドで構成された
    JSONスクリプトを自動生成します。doc_idは20文字のランダムな値になります。
    """
    hex_sequence = hex_sequence.upper()
    max_command_bytes = 40

    # --- MRAM書き込みコマンド作成用の内部関数 ---
    def create_mram_write_script(sat_id, gs_id, start_address, hex_data):
        # doc_idをここで生成
        doc_id_str = generate_random_doc_id()

        data_bytes = len(hex_data) // 2

        telemetry_conditions = [
            {
                "obc": "MOBC",
                "packet_id": "MEMDUMP_MRAM3",
                "field_name": "memory_tr_dump_begin_address",
                "value": start_address,
                "condition": "eq",
                "continue_sending_commands": True
            }
        ]
        
        for i in range(data_bytes):
            byte_hex = hex_data[i * 2 : i * 2 + 2]
            byte_value_10 = int(byte_hex, 16)
            packet_id = "MEMDUMP_MRAM3" if i <= 2 else "MEMDUMP_EEPROM3"
            
            for tr_num in [1, 2, 3]:
                telemetry_conditions.append({
                    "obc": "MOBC",
                    "packet_id": packet_id,
                    "field_name": f"memory_tr{tr_num}_dump_data[{i}]",
                    "value": byte_value_10,
                    "condition": "eq",
                    "continue_sending_commands": True
                })

        return {
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
                "address": start_address,
                "write_value": hex_data
            },
            "comment": f"MRAMの値を書き換える場合は使用 (Address: {start_address})",
            "check": [],
            "command_reply_check": True,
            "telemetry_check_condition": telemetry_conditions,
            "auto_resend_limit_count": 7,
            "result": "",
            "doc_id": doc_id_str
        }

    base_name, _ = os.path.splitext(file_out_path)

    sat_types = ["1U", "2U"]
    for sat_type in sat_types:
        sat_id = f"SAT_{sat_type}"
        gs_id = f"GS_{sat_type}"
        specific_out_path = f"{base_name}_{sat_type}.json"
        
        scripts = []
        current_address = base_address
        total_hex_len = len(hex_sequence)
        chunk_size_chars = max_command_bytes * 2
        
        for offset in range(0, total_hex_len, chunk_size_chars):
            chunk_hex = hex_sequence[offset : offset + chunk_size_chars]
            script_cmd = create_mram_write_script(sat_id, gs_id, current_address, chunk_hex)
            scripts.append(script_cmd)
            current_address += len(chunk_hex) // 2

        # APP初期化コマンドのdoc_idもランダムにする場合
        scripts.append({
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
            "args": { "app_id": app_id },
            "comment": "書き換えたMRAMがある場合はloadする",
            "check": [],
            "command_reply_check": True,
            "telemetry_check_condition": "NO_CHECK",
            "auto_resend_limit_count": 7,
            "result": "",
            "doc_id": generate_random_doc_id()
        })

        script_template = {
            "absolute_times": { "pass_start": "2020-01-01 0:0:0.0" },
            "version": 4,
            "is_mixed": True,
            "scripts": scripts
        }

        with open(specific_out_path, "w", encoding="utf-8") as f:
            json.dump(script_template, f, indent=4, ensure_ascii=False)

        print(f"スクリプトを出力しました: {specific_out_path}")
