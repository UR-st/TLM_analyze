import numpy as np
import math
from sgp4.api import Satrec, WGS72
from class_dir.class_def import TLE_Elements_, TLE_Hex_
import struct
import json
import os
import requests

EARTH_MU_KM3_S2 = 398600.8

def get_tle_lines_from_web(norad_id):
    """CelestrakからNORAD IDを指定して最新のTLEを3行のリストで取得する"""
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise ConnectionError(f"TLEデータの取得に失敗しました。ステータスコード: {response.status_code}")
        
    # テキストを行ごとに分割し、空行を除去
    lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
    
    if len(lines) < 3:
        raise ValueError(f"有効なTLEが見つかりません。NORAD ID ({norad_id}) を確認してください。")
        
    return lines[:3]

def get_tle_lines(file_name):
    """TLEファイルを読み込み、3行のリストを返す"""
    with open(file_name, "r", encoding="utf-8") as f:
        # 空行を除去
        lines = [line.strip() for line in f if line.strip()]
    
    if len(lines) < 3:
        raise ValueError("TLE file must have at least 3 lines.")
    return lines[:3]

def tle_2_param(lines,norad_id):
    """ライブラリを用いてTLEを解析し、TLE_Elementsクラスに値を格納する"""
    # インスタンス化 (クラスの定義に合わせて修正してください)
    tle = TLE_Elements_()
    
    # sgp4ライブラリでパース
    # lines[1]が1行目、lines[2]が2行目
    sat = Satrec.twoline2rv(lines[1], lines[2], WGS72)
    
    # --- 値の抽出と格納 ---
    
    #norad_idを抽出
    tle.norad_id = norad_id
    #sat名を抽出
    tle.sat = lines[0]
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
    print(f"Norad ID: {tle.norad_id}")
    print(f"SAT: {tle.sat}")
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

def calculate_geocentric_distance_at_epoch(n_rev_per_day: float, e: float, M_deg: float) -> float:
    """
    TLEの元期における地心距離(m)をケプラー運動として近似計算する
    """
    # 地球の標準重力パラメータ (m^3/s^2)
    MU = 3.986004418e14 
    
    # ステップ1: 平均運動から軌道長半径 a を求める
    n_rad_per_sec = n_rev_per_day * (2 * math.pi / 86400.0)
    a = (MU / (n_rad_per_sec ** 2)) ** (1.0 / 3.0)
    
    # ステップ2: 平均近点角をラジアンに変換
    M0 = math.radians(M_deg)
    
    # ステップ3: ケプラー方程式をニュートン・ラプソン法で解く (E0を求める)
    E = M0 # 初期値
    for _ in range(10): # 10回程度反復すれば十分収束します
        E = E - (E - e * math.sin(E) - M0) / (1.0 - e * math.cos(E))
        
    # ステップ4: 地心距離 r を計算
    r = a * (1.0 - e * math.cos(E))
    
    return r

def tle_2_orbital_elements(lines, norad_id=None, print_result=True):
    """TLE から古典的な軌道六要素を計算して返す。"""
    sat = Satrec.twoline2rv(lines[1], lines[2], WGS72)

    mean_motion_rad_s = sat.no_kozai / 60.0
    semi_major_axis_km = (EARTH_MU_KM3_S2 / (mean_motion_rad_s ** 2)) ** (1.0 / 3.0)

    orbital_elements = {
        "norad_id": norad_id,
        "satellite_name": lines[0],
        "semi_major_axis_km": semi_major_axis_km,
        "eccentricity": sat.ecco,
        "inclination_deg": math.degrees(sat.inclo),
        "raan_deg": math.degrees(sat.nodeo),
        "argument_of_perigee_deg": math.degrees(sat.argpo),
        "mean_anomaly_deg": math.degrees(sat.mo),
    }

    if print_result:
        print(f"Norad ID: {orbital_elements['norad_id']}")
        print(f"SAT:      {orbital_elements['satellite_name']}")
        print(f"a [km]:   {orbital_elements['semi_major_axis_km']}")
        print(f"e [-]:    {orbital_elements['eccentricity']}")
        print(f"i [deg]:  {orbital_elements['inclination_deg']}")
        print(f"RAAN:     {orbital_elements['raan_deg']}")
        print(f"argp:     {orbital_elements['argument_of_perigee_deg']}")
        print(f"M [deg]:  {orbital_elements['mean_anomaly_deg']}")

    return orbital_elements


def tle_file_2_orbital_elements(file_name, print_result=True):
    """TLE ファイルから古典的な軌道六要素を計算して返す。"""
    lines = get_tle_lines(file_name)

    return tle_2_orbital_elements(lines, print_result=print_result)

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

def tle_2_MRAM(norad_id, file_name_of_json, app_id=188):
    #lines = get_tle_lines(file_name)
    # Webから取得する新しい関数に書き換える！
    lines = get_tle_lines_from_web(norad_id)
    tle_params = tle_2_param(lines,norad_id)
    tle_hex = param_2_hex(tle_params, type)
    #tle_2_command_script(tle_hex,file_name_of_json)
    generate_mram_json_for_tle(tle_hex, file_name_of_json, app_id=app_id)
    
    # ここでMRAM送信用データへの変換処理を行う想定
    
    return tle_hex


"""以下json生成部"""
def tle_2_command_script(tle_hex,file_name_of_json):
    file_path = file_name_of_json
    with open(file_path, "w", encoding="utf-8") as f:
    # json.dump で辞書データをファイルに書き込む
    # indent=4 を指定すると、人間が見やすいように改行とインデントを入れてくれます
        json.dump(vars(tle_hex), f, indent=4)

def generate_mram_json_for_tle(tle_hex_instance, file_out_path: str = "TLE_cmd.json", app_id: int = 188):
    """
    TLE_Hex_ のデータから、最初の3つのコマンド（MRAM書き込み×2、APP初期化）のみで構成された
    1U用と2U用のJSONスクリプトを自動生成します。
    ファイル名に必ず「.json」の拡張子が付くように修正しました。
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
        
        # 配列の添え字が2以下なら MRAM3、3以上なら EEPROM3
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

    # 【修正箇所】ファイル名から拡張子をいったん完全に分離し、ベース名だけを取り出す
    base_name, _ = os.path.splitext(file_out_path)

    # 1U用と2U用のループ処理
    sat_types = ["1U", "2U"]
    for sat_type in sat_types:
        sat_id = f"SAT_{sat_type}"
        gs_id = f"GS_{sat_type}"
        
        # 【修正箇所】末尾に必ず「_1U.json」または「_2U.json」が結合されるように固定
        specific_out_path = f"{base_name}_{sat_type}.json"

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
                    "app_id": app_id
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
