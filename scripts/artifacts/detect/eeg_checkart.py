from importPy import *
# Class needed for parameters
class Cnf:
	None
class Algorithm:
	None
class Artifacts:
	None
	
def eeg_checkart(EEG):
	shape = EEG.get_data().shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS
	else:
		nEl,nS = shape
		nEp = 1
	

	if(not hasattr(EEG,'artifacts')):
		EEG.artifacts = Artifacts()
		if(not hasattr(EEG.artifacts,'algorithm')):
			EEG.artifacts.algorithm = Algorithm()
		EEG.artifacts.algorithm.parameters = []
		EEG.artifacts.algorithm.stepname = []
		EEG.artifacts.algorithm.rejxstep = []
		EEG.artifacts.BCT = [[[False]*nEl]*nS]*nEp
		EEG.artifacts.BC = [[[False]*nEl]]*nEp
		EEG.artifacts.BCmanual = []
		EEG.artifacts.BT = [[[False]]*nS]*nEp
		EEG.artifacts.BE = [[[False]]]*nEp
		EEG.artifacts.BS = [False]

	if(not hasattr(EEG.artifacts,'BCT')):
		EEG.artifacts.BCT = [[[False]*nEl]*nS]*nEp


	return EEG
