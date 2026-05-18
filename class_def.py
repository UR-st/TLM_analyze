
class TLE_Elements:
    def __init__(self, ep_year: int, ep_day: float, rev: float, bstar: float, 
                 eqinc: float, ecc: float, mnan: float, argp: float, ascn: float):
        """
        TLE（2行軌道要素形式）から抽出された値を保持する構造体
        """
        # 時刻要素
        self.ep_year = ep_year  # エポック年 (西暦4桁)
        self.ep_day = ep_day    # エポック日 (通算日)

        # 軌道形状・摂動要素
        self.rev = rev          # 平均運動 (Mean Motion [rev/day])
        self.bstar = bstar      # BSTAR項 (大気抵抗係数)
        self.ecc = ecc          # 離心率 (Eccentricity)

        # 角度要素 [deg]
        self.eqinc = eqinc      # 軌道傾斜角 (Inclination)
        self.ascn = ascn        # 昇交点赤経 (RAAN)
        self.argp = argp        # 近地点引数 (Argument of Perigee)
        self.mnan = mnan        # 平均近点離角 (Mean Anomaly)