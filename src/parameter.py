import numpy as np

class suns:
    def __init__(self, px_DCM, mx_DCM, py_DCM, my_DCM, pz_DCM):
        self.px_DCM = px_DCM  # 属性（プロパティ）
        self.mx_DCM = mx_DCM
        self.py_DCM = py_DCM
        self.my_DCM = my_DCM
        self.pz_DCM = pz_DCM
suns.px_DCM = np.array([[1,1,1],[0,1,1],[0,0,1]])
suns_mx_DCM = np.array([[1,0,0],[0,1,0],[0,0,1]])
suns_py_DCM = np.array([[1,0,0],[0,1,0],[0,0,1]])
suns_my_DCM = np.array([[1,0,0],[0,1,0],[0,0,1]])
suns_pz_DCM = np.array([[1,0,0],[0,1,0],[0,0,1]])

print(suns.px_DCM)