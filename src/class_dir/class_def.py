class TLE_Elements_:
    # 各引数の後ろに「= None」を付け、型ヒントに「| None」を追加
    def __init__(self, ep_year: int | None = None, ep_day: float | None = None, rev: float | None = None, 
                 bstar: float | None = None, eqinc: float | None = None, ecc: float | None = None, 
                 mnan: float | None = None, argp: float | None = None, ascn: float | None = None, norad_id: str | None = None, sat: str | None = None):
        """
        TLE（2行軌道要素形式）から抽出された値を保持する構造体
        """
        self.norad_id = norad_id# norad id (5桁)
        self.sat = sat          # sat名
        self.ep_year = ep_year  # エポック年 (西暦4桁)
        self.ep_day = ep_day    # エポック日 (通算日)
        self.rev = rev          # 平均運動 (Mean Motion [rev/day])
        self.bstar = bstar      # BSTAR項 (大気抵抗係数)
        self.ecc = ecc          # 離心率 (Eccentricity)
        self.eqinc = eqinc      # 軌道傾斜角 (Inclination)
        self.ascn = ascn        # 昇交点赤経 (RAAN)
        self.argp = argp        # 近地点引数 (Argument of Perigee)
        self.mnan = mnan        # 平均近点離角 (Mean Anomaly)
        


class TLE_Hex_:
    # 各引数の後ろに「= ""」を付ける（文字列なので空文字が自然）
    def __init__(self, ep_year: str = "", ep_day: str = "", rev: str = "", bstar: str = "", 
                 eqinc: str = "", ecc: str = "", mnan: str = "", argp: str = "", ascn: str = "",
                   norad_id: str  = "",sat: str = ""):
        """
        TLE（2行軌道要素形式）から抽出された値を保持する構造体（16進数文字列）
        """
        self.norad_id = norad_id# norad id (5桁)
        self.sat = sat          # sat名
        self.ep_year = ep_year  # エポック年 (西暦4桁)
        self.ep_day = ep_day    # エポック日 (通算日)
        self.rev = rev          # 平均運動 (Mean Motion [rev/day])
        self.bstar = bstar      # BSTAR項 (大気抵抗係数)
        self.ecc = ecc          # 離心率 (Eccentricity)
        self.eqinc = eqinc      # 軌道傾斜角 (Inclination)
        self.ascn = ascn        # 昇交点赤経 (RAAN)
        self.argp = argp        # 近地点引数 (Argument of Perigee)
        self.mnan = mnan        # 平均近点離角 (Mean Anomaly)