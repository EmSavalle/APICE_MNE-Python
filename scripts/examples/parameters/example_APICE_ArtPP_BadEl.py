from importPy import *

class P:
    None
class art():
    algorithm = ""
    loops = []
    def __init__(self):
        self.P = P()

class example_APICE_ArtPP_BadEl():
    """
    Artifacts Rejection Parameters 
    Identify bad electrodes
    """
    
    def __init__(self,thresh):
        self.Art = []
        i = 0
        # Reject : electrodes by epochs based on the correlation between channels
        self.Art.append(art())
        self.Art[i].algorithm='eega_tRejCorrCh'
        self.Art[i].loops=[1]
        self.Art[i].P.refdata = 0
        self.Art[i].P.dozscore = 0
        self.Art[i].P.twdur = 4
        self.Art[i].P.twstep = 2
        self.Art[i].P.topcorrch = 5
        self.Art[i].P.thresh = 0.4
        self.Art[i].P.relative = 0

        # Reject : electrodes by epochs based on the power sectrum
        i = i + 1
        self.Art.append(art())
        self.Art[i].algorithm='eega_tRejPwr'
        self.Art[i].loops=[2]
        self.Art[i].P.refdata = 0
        self.Art[i].P.dozscore = 1
        self.Art[i].P.twdur = 4
        self.Art[i].P.twstep = 2
        self.Art[i].P.frqband = [(1,10),(20,40)]
        self.Art[i].P.thresh = [(-thresh,float('inf')),(-float('inf'),thresh) ]
        self.Art[i].P.relative = [1,1]

        # Reject : too short included segments
        i = i + 1
        self.Art.append(art())
        self.Art[i].algorithm='eega_tRejShortGood'
        self.Art[i].loops = 2
        self.Art[i].P.timelim = 2.000
