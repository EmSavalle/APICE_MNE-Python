from importPy import *
class example_APICE_ArtPP_Mot2():
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
        i=0

        ## ABSOLUTE threshold for ALL electrodes

        # REJECT: if the amplitud is bigger than a threshold (ABSOLUTE THRESHOLD)
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejAmp'
        self.Art[i].loops            = [1]
        self.Art[i].P.refdata        = 0
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.thresh         = 500  
        self.Art[i].P.relative       = 0
        self.Art[i].P.xelectrode     = 0
        self.Art[i].P.mask           = 0.500
        i = i+1

        ## NON average reference data, RELATIVE threshold for EACH electrode

        # REJECT: if the amplitud is bigger than a threshold (RELATIVE THRESHOLD)
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejAmp'
        self.Art[i].loops            = [2, 3]
        self.Art[i].P.refdata        = 0
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.thresh         = thresh  
        self.Art[i].P.relative       = 1
        self.Art[i].P.xelectrode     = 1
        self.Art[i].P.mask           = 0.05
        i = i+1

        # REJECT: electrode based on time variance 
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejTimeVar'
        self.Art[i].loops            = [2, 3]
        self.Art[i].P.refdata        = 0
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.twdur          = 0.500
        self.Art[i].P.twstep         = 0.100
        self.Art[i].P.thresh         = [-thresh, thresh]
        self.Art[i].P.relative       = 1 
        self.Art[i].P.xelectrode     = 1
        i = i+1

        # REJECT: using the weighted running average Net Station algorithm 
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejRunningAvg'
        self.Art[i].loops            = [2, 3]
        self.Art[i].P.refdata        = 0
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.thresh_fa      = thresh  
        self.Art[i].P.thresh_da      = thresh
        self.Art[i].P.relative       = 1
        self.Art[i].P.xelectrode     = 1
        self.Art[i].P.mask           = 0.05
        i = i+1

        ## Average reference data, RELATIVE threshold for ALL electrodes

        # REJECT: if the amplitud is bigger than a threshold (RELATIVE THRESHOLD)
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejAmp'
        self.Art[i].loops            = [4, 5]
        self.Art[i].P.refdata        = 1
        self.Art[i].P.refbaddata     = 'replacebynan'
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.thresh         = thresh  
        self.Art[i].P.relative       = 1
        self.Art[i].P.xelectrode     = 0
        self.Art[i].P.mask           = 0.05
        i = i+1

        # REJECT: electrode based on time variance 
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejTimeVar'
        self.Art[i].loops            = [4, 5]
        self.Art[i].P.refdata        = 1
        self.Art[i].P.refbaddata     = 'replacebynan'
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.twdur          = 0.500
        self.Art[i].P.twstep         = 0.100
        self.Art[i].P.thresh         = [-thresh, thresh]
        self.Art[i].P.relative       = 1 
        self.Art[i].P.xelectrode     = 0
        i = i+1

        # REJECT: using the weighted running average Net Station algorithm 
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejRunningAvg'
        self.Art[i].loops            = [4, 5]
        self.Art[i].P.refdata        = 1
        self.Art[i].P.refbaddata     = 'replacebynan'
        self.Art[i].P.dozscore       = 0
        self.Art[i].P.thresh_fa      = thresh  
        self.Art[i].P.thresh_da      = thresh
        self.Art[i].P.relative       = 1
        self.Art[i].P.xelectrode     = 0
        self.Art[i].P.mask           = 0.05
        i = i+1

        # REJECT: using the variance across electrodes
        self.Art.append(art())
        self.Art[i].algorithm         = 'eega_tRejAmpElecVar'
        self.Art[i].loops             = [5]
        self.Art[i].P.refdata         = 1
        self.Art[i].P.refbaddata      = 'replacebynan'
        self.Art[i].P.dozscore        = 0
        self.Art[i].P.thresh          = thresh
        self.Art[i].P.mask            = 0.05
        i = i+1

        ## Include / reject data based on rejected data

        # REJECT: too short rejected segments are marked as good
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tIncShortBad'
        self.Art[i].loops            = 5
        self.Art[i].P.timelim        = 0.100
        i = i+1

        # REJECT: too short included segments
        self.Art.append(art())
        self.Art[i].algorithm        = 'eega_tRejShortGood'
        self.Art[i].loops            = 5
        self.Art[i].P.timelim        = 2.000
