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

    lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]

    if len(lines) < 3:
        raise ValueError(f"有効なTLEが見つかりません。NORAD ID ({norad_id}) を確認してください。")

    return lines[:3]


def get_tle_lines(file_name):
    """TLEファイルを読み込み、3行のリストを返す"""
    with open(file_name, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 3:
        raise ValueError("TLE file must have at least 3 lines.")
    return lines[:3]


def tle_2_param(lines, norad_id):
    """ライブラリを用いてTLEを解析し、TLE_Elementsクラスに値を格納する"""
    tle = TLE_Elements_()
    sat = Satrec.twoline2rv(lines[1], lines[2], WGS72)

    tle.norad_id = norad_id
    tle.sat = lines[0]
    tle.ep_year = 100 + (sat.epochyr if sat.epochyr < 57 else sat.epochyr - 1900)
    tle.ep_day = sat.epochdays

    tle.rev = sat.no_kozai * (24 * 60) / (2 * math.pi)
    tle.bstar = sat.bstar
    tle.eqinc = math.degrees(sat.inclo)
    tle.ecc = sat.ecco
    tle.mnan = math.degrees(sat.mo)
    tle.argp = math.degrees(sat.argpo)
    tle.ascn = math.degrees(sat.nodeo)

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


def calculate_geocentric_distance_at_epoch(file_name: str, print_result=True) -> float:
    """TLEファイルから epoch 時刻の地心距離を km で計算して返す。"""
    lines = get_tle_lines(file_name)
    sat = Satrec.twoline2rv(lines[1], lines[2], WGS72)

    error_code, position_km, _ = sat.sgp4(sat.jdsatepoch, sat.jdsatepochF)
    if error_code != 0:
        raise ValueError(f"SGP4 propagation failed at epoch. error_code={error_code}")

    geocentric_distance_km = math.sqrt(
        position_km[0] ** 2 +
        position_km[1] ** 2 +
        position_km[2] ** 2
    )

    if print_result:
        print(f"SAT: {lines[0]}")
        print(f"Geocentric distance at epoch [km]: {geocentric_distance_km}")

    return geocentric_distance_km


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
    tle_hex = TLE_Hex_()
    tle_hex.ep_year = struct.pack("<I", param.ep_year).hex()
    tle_hex.ep_day = struct.pack("<d", param.ep_day).hex()
    tle_hex.rev = struct.pack("<d", param.rev).hex()
    tle_hex.bstar = struct.pack("<d", param.bstar).hex()
    tle_hex.eqinc = struct.pack("<d", param.eqinc).hex()
    tle_hex.ecc = struct.pack("<d", param.ecc).hex()
    tle_hex.mnan = struct.pack("<d", param.mnan).hex()
    tle_hex.argp = struct.pack("<d", param.argp).hex()
    tle_hex.ascn = struct.pack("<d", param.ascn).hex()

    return tle_hex


def tle_2_MRAM(norad_id, file_name_of_json, app_id=188):
    lines = get_tle_lines_from_web(norad_id)
    tle_params = tle_2_param(lines, norad_id)
    tle_hex = param_2_hex(tle_params, type)
    generate_mram_json_for_tle(tle_hex, file_name_of_json, app_id=app_id)
    return tle_hex


def tle_2_command_script(tle_hex, file_name_of_json):
    file_path = file_name_of_json
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(vars(tle_hex), f, indent=4)


def generate_mram_json_for_tle(tle_hex_instance, file_out_path: str = "TLE_cmd.json", app_id: int = 188):
    """
    TLE_Hex_ のデータから、最初の3つのコマンド（MRAM書き込み×2、APP初期化）のみで構成された
    1U用と2U用のJSONスクリプトをそれぞれ生成します。
    ファイル名に拡張子 `.json` の指定が無くても正しく処理します。
    """
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

    first_command_bytes = 36
    base_address = 32768

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
    sub_hex_1 = hex_sequence[0:first_command_bytes * 2]
    for i in range(first_command_bytes):
        byte_hex = sub_hex_1[i * 2:i * 2 + 2]
        byte_value_10 = int(byte_hex, 16)
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
    sub_hex_2 = hex_sequence[first_command_bytes * 2:]
    total_bytes_2 = len(sub_hex_2) // 2
    for i in range(total_bytes_2):
        byte_hex = sub_hex_2[i * 2:i * 2 + 2]
        byte_value_10 = int(byte_hex, 16)
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

    base_name, _ = os.path.splitext(file_out_path)

    sat_types = ["1U", "2U"]
    for sat_type in sat_types:
        sat_id = f"SAT_{sat_type}"
        gs_id = f"GS_{sat_type}"
        specific_out_path = f"{base_name}_{sat_type}.json"

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
                "comment": "MRAMの値を書き換える場合の使用",
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
                "comment": "MRAMの値を書き換える場合の使用",
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
                "comment": "書き換えたMRAMがある場合にloadする",
                "check": [],
                "command_reply_check": True,
                "telemetry_check_condition": "NO_CHECK",
                "auto_resend_limit_count": 7,
                "result": "",
                "doc_id": "#o:4.JlE7g^qBFE(CG:E"
            }
        ]

        script_template = {
            "absolute_times": {
                "pass_start": "2020-01-01 0:0:0.0"
            },
            "version": 4,
            "is_mixed": True,
            "scripts": scripts
        }

        with open(specific_out_path, "w", encoding="utf-8") as f:
            json.dump(script_template, f, indent=4, ensure_ascii=False)

        print(f"生成スクリプトを出力しました: {specific_out_path}")
