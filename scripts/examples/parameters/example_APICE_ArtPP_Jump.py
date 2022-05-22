from importPy import *
class example_APICE_ArtPP_Jump():
    """
    Artifacts Rejection Parameters 
    Identify bad electrodes
    """
    class art:
        algorithm = ""
        loops = []
        class P:
            None
    def __init__(self,thresh):
        self.Art = []

        # REJECT: if a big change happens in a small interval (RELATIVE THRESHOLD)
        i = 0
        self.Art.append(art())
        self.Art[i].algorithm         = 'eega_tRejFastChange'
        self.Art[i].loops             = [1]
        self.Art[i].P.refdata         = 0
        self.Art[i].P.dozscore        = 0
        self.Art[i].P.tmotion         = 0.020
        self.Art[i].P.thresh          = thresh  
        self.Art[i].P.relative        = 1
        self.Art[i].P.xelectrode      = 1
        


        # Average reference data, RELATIVE threshold for ALL electrodes
        #REJECT: if a big change happens in a small interval (RELATIVE THRESHOLD)
        i = i + 1
        self.Art.append(art())
        self.Art[i].algorithm         = 'eega_tRejFastChange'
        self.Art[i].loops             = [2]
        self.Art[i].P.refdata         = 1
        self.Art[i].P.refbaddata      = 'replacebynan'
        self.Art[i].P.dozscore        = 0
        self.Art[i].P.tmotion         = 0.020
        self.Art[i].P.thresh          = thresh  
        self.Art[i].P.relative        = 1
        self.Art[i].P.xelectrode      = 0
        

        ## Include / reject data based on rejected data

        # REJECT: too short rejected segments are marked as good
        i = i + 1
        self.Art.append(art())
        self.Art[i].algorithm         = 'eega_tIncShortBad'
        self.Art[i].loops             = 2
        self.Art[i].P.timelim         = 0.020

        # REJECT: too short not included segments
        i=i+1
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejShortGood'
        self.Art[i].loops            = 2
        self.Art[i].P.timelim        = 0.100