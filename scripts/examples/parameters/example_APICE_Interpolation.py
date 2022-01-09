from importPy import *
class PCA:
    maxTime = 0.100
    nSV = []
    vSV = 0.90
    splicemethod = 1
    maskTime = 0.05
class SPL:
    p = 0.5
    pneigh = 1
    splicemethod = 1
    minGoodTime = 2.0
    minInterTime = 0.1
    maskTime = 1.00
class example_APICE_Interpolation():
    def __init__(self):
        self.PCA = PCA()
        self.Spl = SPL()
