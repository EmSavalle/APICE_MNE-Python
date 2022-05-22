from importPy import *
def eega_tRejAmpElecVar(EEG,args):
# -------------------------------------------------------------------------
# Function that performs an artefact rejection algorithm based on the 
# variace of the signal across electrodes: if at a given sample the 
# amplitud for a given electrode is too far away from the median of all electrodes it is rejected
# 
# INPUTS
# EEG   EEG structure
#
# OPTIONAL INPUTS
#   - thresh		number of interquartil range above or bellow from the meadian (default 2)
#   - refdata	   referenced average the data before (1) or not (0) (default 0)
#   - refbaddata	how to teat bad data when reference average ('replacebynan' / 'none' / 'zero', default 'none')
#   - dozscore	  z-score the data per electrodes before (1) or not (0) (default 0)
#   - mask		  time to mask bad segments (default 0)
#
# OUTPUTS
#   EEG	 output data
#   BCT	 bad data 
#   T	   threshold
#
# -------------------------------------------------------------------------
	print('### Rejecting based on the variance across electrodes ###\n' )

	## ------------------------------------------------------------------------
	## Parameters
	P=p()
	P.thresh = 3
	P.refdata = 0
	P.refbaddata = 'none' # 'replacebynan' / 'none' / 'zero'
	P.dozscore = 0
	P.mask = 0.05

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1
	P, OK, extrainput = eega_getoptions(P, args)
	if not OK:
		raise ValueError('eega_tRejAmpElecVar: Non recognized inputs')

	print('- referenced data: '+str(P.refdata))
	print('- z-score data: '+str(P.dozscore))
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

	## ------------------------------------------------------------------------
	##Find the thresholds
	D = EEG._data
	#Do not consider bad data and bad time where the majority of electrodes are bad
	for el in range(nEl):
	    for s in range(nS):
	        if(EEG.artifacts.BCT[0][el][s]):
	            D[el][s]=float("nan")
	bt = np.logical_or(EEG.artifacts.BT, np.sum(EEG.artifacts.BCT,1)/nEl>0.5)
	D[:,bt[0]] = float("nan")

	#Normalization
	Dmean = np.nanmean(D,axis=0)
	Dstd = np.nanstd(D,axis=0)
	D = (D-Dmean)/Dstd

	#Obtain threshold
	perc = np.percentile(D,[25,50,75])
	IQ = perc[2]-perc[0]
	t_u = perc[2]+P.thresh*IQ
	t_l = perc[0]-P.thresh*IQ
	T = [t_l,t_u]

	## ------------------------------------------------------------------------
	##Rejection
	D = EEG._data

	#Normalization
	Dmeanbad = np.nanmean(D,axis=0)
	Dstdbad = np.nanstd(D,axis=0)
	Dmean[bt[0]]=Dmeanbad[bt[0]]
	Dstd[bt[0]]=Dstdbad[bt[0]]
	D = (D-Dmean)/Dstd

	#Reject
	BCT = np.logical_or(D>t_u,D<t_l)

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
	print("eega_tRejAmpElecVar : Total data rejected "+ str(np.sum(np.sum(np.sum(BCT,0),0),0)/n*100)+"%")

	return [EEG,BCT]