from importPy import *
def eega_tRejAmp(EEG,args):
	# -------------------------------------------------------------------------
	# Function that rejects based on the mean of the absolute amplitud
	# 
	# INPUTS
	# EEG   EEG structure
	#
	# OPTIONAL INPUTS
	#   - thresh		upper threshold (default 2)
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
	print('### Rejecting based on the amplitud ###\n' )

	## ------------------------------------------------------------------------
	## Parameters
	P=p()
	P.thresh = 3
	P.refdata = 0
	P.refbaddata = 'none' # 'replacebynan' / 'none' / 'zero'
	P.dozscore = 0
	P.relative = 1
	P.xelectrode = 1
	P.mask = 0.05

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1
	varargin = args



	P, OK, extrainput = eega_getoptions(P, varargin)
	if not OK:
		raise ValueError('eega_tRejAmp: Non recognized inputs')

	# Check the inputs
	if type(P.dozscore) == list or (P.dozscore != 0 and P.dozscore != 1):
		raise ValueError('eega_tRejAmp: dozscore has to be 0 / 1')
	
	if (P.relative != 0 and P.relative != 1): #Verifie si les valeures de P.relative sont bien soit 1 soit 0
		raise ValueError('eega_tRejAmp: relative has to have values 0 / 1')

	if (P.xelectrode != 0 and P.xelectrode != 1):
		raise ValueError('eega_tRejAmp: xelectrode has to have values 0 / 1')


	print('- referenced data: '+str(P.refdata))
	print('- z-score data: '+str(P.dozscore))
	print('- relative threshold: '+str(P.relative))
	print('- threshold per electrode: '+str(P.xelectrode))

	shape = EEG._data.shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS = shape
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
	## Reject
	T = np.zeros(nEl)
	Ru = np.zeros((nEp,nEl,nS))
	if(P.relative == 1):
		if(P.xelectrode == 1):
			ru_sum = 0
			rl_sum = 0
			for ep in range(nEp):
				d = []
				if(len(shape)>2):
					d = EEG._data[ep]
				else:
					d = EEG._data
				for el in range(nEl):
					dat = d[el]
					dat[EEG.artifacts.BCT[ep][el]]=float("nan")
					perc = np.percentile(dat,75)
					IQ = 2 * perc
					t_u_el = perc + P.thresh*IQ
					Ru[ep][el] = np.logical_or(Ru[ep][el],abs(dat)>t_u_el)
					T[el]=t_u_el
					ru_sum = ru_sum+np.sum( abs(dat)>t_u_el)
		else:
			dd = abs(EEG._data)
			perc = np.percentile(dd[np.logical_not(EEG.artifacts.BCT[0])],75)
			IQ = 2 * perc
			t_u = perc + P.thresh*IQ
			Ru = np.logical_or(Ru,abs(EEG._data)>t_u)
			ru_sum = sum(abs(EEG._data)>t_u)
	else:
		t_u = P.thresh
		Ru = np.logical_or(Ru, abs(EEG._data)>t_u)
		T[:] = t_u
		ru_sum=sum(abs(EEG._data)>t_u) 

	##Display rejected data
	n = nEl*nS*nEp
	print('Data rejected thresh_u '+ str(ru_sum/n*100))
	BCT = Ru
	del Ru

	## Mask around
	if(P.mask !=0):
		print("- Mask around "+str(P.mask))
		BCT,ar = eega_maskmatrix(BCT,[P.mask, EEG.info['sfreq']])
	if(P.updateBCT):
		EEG.artifacts.BCT = np.logical_or(EEG.artifacts.BCT,BCT)
	if(P.updatesummary):
		EEG.artifacts.summary = eega_summaryartifacts(EEG)
	if(P.updatealgorithm):
		EEG.artifacts.algorithm.parameters += [P]
		EEG.artifacts.algorithm.rejxstep += np.sum(BCT)
	# Data back
	if P.dozscore:
		EEG._data = np.dot(EEG._data,npm.repmat(sd,nEp,nS))+ npm.repmat(mu,nEp,nS)
	if P.refdata:
		#EEG._data = EEG._data + npm.repmat(reference,EEG._data.shape[0],1);
		print('eega_tRejAmp : TODO fix refdata')
	return EEG,BCT