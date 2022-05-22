from importPy import *
def eega_tRejRunningAvg(EEG,args):
	# -------------------------------------------------------------------------
	# Function that performs a weighted running average algorithm to detect
	# artifacts. Periods with a too big fast running average or with a too big
	# difference between a fast and slow runnig average are discarted
	#
	# INPUTS
	# EEG   EEG structure
	#
	# OPTIONAL INPUTS
	#   - thresh_fa	 fast running average threshold (default 2)
	#   - thresh_da	 difference running average threshold (default 2)
	#   - refdata	   referenced average the data before (1) or not (0) (default 0)
	#   - refbaddata	how to teat bad data when reference average ('replacebynan' / 'none' / 'zero', default 'none')
	#   - dozscore	  z-score the data per electrodes before (1) or not (0) (default 0)
	#   - relative	  appply relative (1) or absolute (0) thresholds (default 1)
	#   - xelectrode	appply the threhold per electrode (1) or over all electrodes (0) (default 1)
	#   - mask		  time to mask bad segments (default 0)
	#
	# OUTPUTS
	#   EEG	 output data
	#   BCT	 bad data 
	#   T	   threshold
	#
	# -------------------------------------------------------------------------
	## ------------------------------------------------------------------------
	## Parameters
	P=p()
	P.thresh_fa = 3
	P.thresh_da = 3
	P.refdata = 0
	P.refbaddata = 'none' 
	P.dozscore = 0
	P.relative = 1
	P.xelectrode = 1
	P.mask = 0.05

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1


	P, OK, extrainput = eega_getoptions(P, args)
	if not OK:
		raise ValueError('eega_tRejRunningAvg: Non recognized inputs')

	# Check the inputs
	if type(P.dozscore) == list or (P.dozscore != 0 and P.dozscore != 1):
		raise ValueError('eega_tRejRunningAvg: dozscore has to be 0 / 1')
	
	if (P.relative != 0 and P.relative != 1): #Verifie si les valeures de P.relative sont bien soit 1 soit 0
		raise ValueError('eega_tRejRunningAvg: relative has to have values 0 / 1')

	if (P.xelectrode != 0 and P.xelectrode != 1):
		raise ValueError('eega_tRejRunningAvg: xelectrode has to have values 0 / 1')

	print('- referenced data: '+str(P.refdata))
	print('- z-score data: '+str(P.dozscore))
	print('- relative threshold: '+str(P.relative))
	print('- threshold per electrode: '+str(P.xelectrode))
	shape = EEG._data.shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS = shape
		print("eega_tRejRunningAvg : not prepared for epoched data")
	else:
		nEl,nS = shape
		nEp = 1
	## ------------------------------------------------------------------------
	## Get data and check that the artifact structure exists 
	EEG = importPy.eeg_checkart(EEG)
	
	## ------------------------------------------------------------------------
	## Reference data
	if P.refdata:
		EEG, reference = eega_refavg( EEG ,['BadData',P.refbaddata,'SaveRef',0])

	## ------------------------------------------------------------------------
	## Z-score
	if P.dozscore:
		EEG, mu, sd = eega_ZscoreForArt(EEG)

	## Running average algorithm

	#Removing baseline from data
	data = EEG._data.copy()
	baseline = []
	for i in range(len(data)):
		mu = np.mean(data[i])
		for j in range(len(data[i])):
			data[i][j]-=mu

	AvgFast = np.zeros((nEl,nS))
	AvgSlow = np.zeros((nEl,nS))
	for el in range(nEl):
		AvgFast[el][0]=0.2*data[el][0]
		AvgSlow[el][0]=0.025*data[el][0]
		for j in range(1,nS):
			AvgFast[el][j] = 0.8*AvgFast[el][j-1]+0.2*data[el][j]
			AvgSlow[el][j] = 0.975*AvgSlow[el][j-1]+0.025*data[el][j]
	AvgDiff = AvgFast - AvgSlow

	del data
	del AvgSlow

	## Reject
	T = np.zeros((nEl,2))
	BCT_fast = np.zeros((nEl,nS))
	BCT_diff = np.zeros((nEl,nS))
	BCT_old = EEG.artifacts.BCT[0]
	if(P.relative):
		# Remove periods already signaled as bad
		AvgFast_el = abs(AvgFast)
		AvgFast_el[BCT_old]=float("nan")

		AvgDiff_el = abs(AvgDiff)
		AvgDiff_el[BCT_old]=float("nan")

		#Obtain the thresholds
		perc_fast = np.percentile(AvgFast_el,75,axis = 1)
		IQ = 2*perc_fast
		t_fa = perc_fast + P.thresh_fa*IQ
		
		perc_diff = np.percentile(AvgDiff_el,75,axis = 1)
		IQ = 2*perc_diff
		t_da = perc_diff + P.thresh_da*IQ

		#reject
		#bctfast = AvgFast > t_fa
		#bctdiff = AvgFast > t_da
		bctfast = AvgFast > npm.repmat(P.thresh_fa,1,nS)
		bctdiff = AvgDiff > npm.repmat(P.thresh_da,1,nS)

		BCT_fast = np.logical_or(BCT_fast,bctfast)
		BCT_diff = np.logical_or(BCT_diff,bctdiff)
		T[:,0]=t_fa
		T[:,0]=t_fa
	else:
		bctfast = AvgFast > npm.repmat(P.thresh_fa,nEl,nS)
		bctdiff = AvgDiff > npm.repmat(P.thresh_da,nEl,nS)

		BCT_fast = np.logical_or(BCT_fast,bctfast)
		BCT_diff = np.logical_or(BCT_diff,bctdiff)
		T[:,0]=t_fa
		T[:,0]=t_fa

	del AvgFast

	BCT = np.logical_or(BCT_fast,BCT_diff)
	
	 # Update rejection matrix
	EEG.artifacts.BCT = np.logical_or(EEG.artifacts.BCT,BCT)
	
	if( P.updatesummary and hasattr(importPy,'eega_summaryartifacts')):
		EEG.artifacts.summary = importPy.eega_summaryartifacts(EEG)
	if(P.updatealgorithm):
		EEG.artifacts.algorithm.parameters += [P]
		EEG.artifacts.algorithm.rejxstep += np.sum(np.sum(np.sum(BCT,0),0),0)
	
	# Data back
	if P.dozscore:
		EEG._data = np.dot(EEG._data,npm.repmat(sd,nEp,nS))+ npm.repmat(mu,nEp,nS)
	if P.refdata:
		#EEG._data = EEG._data + npm.repmat(reference,EEG._data.shape[0],1);
		print('eega_tRejAmp : TODO fix refdata')
	
	# Mask around
	if P.mask != [] and P.mask != 0:
		EEG,bctmask = eega_tMask(EEG,['tmast',P.mask])
		BCT = np.logical_or(BCT,bctmask)
		del bctmask

	#Display rejected data
	n=nEp*nEl*nS
	print("Total data rejected "+ str(np.sum(np.sum(np.sum(BCT,0),0),0)/n*100)+"%")
	return [EEG,BCT]