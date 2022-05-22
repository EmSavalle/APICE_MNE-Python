from importPy import *
def eega_tRejTimeVar(EEG,args):
	# -------------------------------------------------------------------------
	# Function that performs an artefact rejection algorithm based on the
	# variace of the signal. The time windows showing an abnormal variance
	# are rejected
	#
	# INPUT
	# EEG   EEG structure
	#
	# OPTIONAL INPUTS
	#   - thresh		lower and upper threshold [thresh_low, thresh_up] (default [-2 2]))
	#   - refdata	   referenced average the data before (1) or not (0) (default 0)
	#   - refbaddata	how to treat bad data when reference average ('replacebynan' / 'none' / 'zero', default 'none')
	#   - dozscore	  z-score the data per electrodes before (1) or not (0) (default 0)
	#   - relative	  appply relative (1) or absolute (0) thresholds (default 1)
	#   - xelectrode	appply the threhold per electrode (1) or over all electrodes (0) (default 1)
	#   - twdur		 time window length in seconds (default 0.5s)
	#   - twstep		time window step in seconds (default 0.1s)
	#   - mask		  time to mask bad segments (default 0)
	#
	# OUTPUTS
	#   EEG	 output data
	#   BCT	 bad data 
	#   T	   threshold
	#
	# -------------------------------------------------------------------------
	print('### Rejecting based on the time variance ###\n' )
	## ------------------------------------------------------------------------
	## Parameters
	P = p()
	P.thresh = [-3,3]
	P.refdata = 0
	P.refbaddata = 'none' # 'replacebynan' / 'none' / 'zero'
	P.dozscore = 0
	P.twdur = 0.5
	P.twstep = 0.1
	P.relative = 1
	P.xelectrode = 1
	P.mask = 0

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1


	P, OK, extrainput = eega_getoptions(P, args)
	print(P.thresh,P.relative,P.xelectrode)
	if not OK:
		raise ValueError('eega_tRejTimeVar: Non recognized inputs')
	# Check the inputs
	if type(P.dozscore) == list or (P.dozscore != 0 and P.dozscore != 1):
		raise ValueError('eega_tRejTimeVar: dozscore has to be 0 / 1')
	
	if (P.relative != 0 and P.relative != 1): #Verifie si les valeures de P.relative sont bien soit 1 soit 0
		raise ValueError('eega_tRejTimeVar: relative has to have values 0 / 1')

	if (P.xelectrode != 0 and P.xelectrode != 1):
		raise ValueError('eega_tRejTimeVar: xelectrode has to have values 0 / 1')

	if(type(P.thresh) == list):
		if(len(P.thresh)%2 != 0):
			print(len(P.thresh))
			raise ValueError('eega_tRejTimeVar : thresh must be a list of 2')
	else:
		raise ValueError('eega_tRejTimeVar : thresh must be a list of 2')

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
	## Define the time windows
	if (P.twdur != []) and not (P.twdur==math.inf) :
		twdur = round(P.twdur*EEG.info["sfreq"])
		twstep = round(P.twstep*EEG.info["sfreq"])
		ntw = round((nS-twdur+1)/twstep)+1
	else:
		ntw = 1
		twdur = nS
	if ntw<=0:
		print('The time window is too long')
		return

	i_t = list(np.linspace(0,nS-twdur, ntw))
	i_t = [round(i) for i in i_t]

	bct_tw = [[[0 for i in range(ntw)] for i in range(nEl)] for i in range(nEp)]


	## ------------------------------------------------------------------------
	## Time variability computation
	STD = [[0 for i in range(ntw)] for i in range(nEl)]
	for ep in range(nEp):
		for el in range(nEl):
			d= []
			if(len(shape)>2):
				d = EEG._data[ep][el]
			else:
				d = EEG._data[el]
			dtw = [d[i_t[i]:i_t[i]+twdur] for i in range(len(i_t))]
			if(np.sum(np.logical_not(np.isnan(dtw)))>2):
				STD[el]=np.nanstd(dtw,axis=1)

	for i in range(ntw):
			for ep in range(nEp):
				for el in range(nEl):
					v = sum(EEG.artifacts.BCT[ep][el][i_t[i]:i_t[i]+twdur]) >= 1*twdur
					bct_tw[ep][el][i] = v
	Ru = [[0 for i in range(ntw)] for i in range(nEl)]
	Rl = [[0 for i in range(ntw)] for i in range(nEl)]
	T = np.empty((nEl,2))
	if(P.relative):
		if(P.xelectrode):
			STD = np.log(STD/np.nanmedian(STD))
			ru_sum = 0
			rl_sum = 0
			for el in range(nEl):
				STD_el = np.array(STD[el]).T
				for tw in range(ntw):
					if(not bct_tw[0][el][tw]):
						STD_el[tw]=float("nan")
				
				perc = np.nanpercentile(STD_el, [25,50,75])
				IQ = perc[2]-perc[0]
				t_l_el = perc[0]+P.thresh[0]*IQ
				t_u_el = perc[2]+P.thresh[1]*IQ
				Ru[el] = np.logical_or(Ru[el],STD[el]>t_u_el)
				Rl[el] = np.logical_or(Rl[el],STD[el]<t_l_el)
				T[el][0] = t_u_el
				T[el][1] = t_l_el
				ru_sum = ru_sum+np.nansum(STD[el]>t_u_el)
				rl_sum = rl_sum+np.nansum(STD[el]<t_l_el)
				del STD_el
		else:
			for el in range(nEl):
				for tw in range(ntw):
					if(not bct_tw[0][el][tw]):
						STD[el][tw]=float("nan")
			perc = np.nanpercentile(STD,[25,50,75])
			IQ = perc[2]-perc[0]
			t_l = perc[0]+P.thresh[0]*IQ
			t_u = perc[2]+P.thresh[1]*IQ
			
			Ru = np.logical_or(Ru,STD>t_u)
			Rl = np.logical_or(Rl,STD<t_l)
			T[:,0]=t_l
			T[:,1]=t_u
			ru_sum = np.sum(STD>t_u)
			rl_sum = np.sum(STD<t_l)
	else:
		t_u = P.thresh[1]
		t_l = P.thresh[0]
		Ru = np.logical_or(Ru,STD>t_u)
		Rl = np.logical_or(Rl,STD<t_l)
		T[:,0]=t_l
		T[:,1]=t_u
		ru_sum = np.sum(STD>t_u)
		rl_sum = np.sum(STD<t_l)

	bct = [[[0 for i in range(nS)] for i in range(nEl)] for i in range(nEp)]
	R = np.logical_or(Rl,Ru)
	for ep in range(0,nEp):
		for el in range(0,nEl):
			for tw in range(ntw):
				if(R[el][tw]):
					for ind in range(i_t[i],i_t[i]+twdur):
						bct[ep][el][ind] = True

	# Update rejection matrix
	EEG.artifacts.BCT = np.logical_or(EEG.artifacts.BCT,bct)

	if( P.updatesummary and hasattr(importPy,'eega_summaryartifacts')):
		EEG.artifacts.summary = importPy.eega_summaryartifacts(EEG)
	if(P.updatealgorithm):
		EEG.artifacts.algorithm.parameters += [P]
		EEG.artifacts.algorithm.rejxstep += np.sum(bct)
	
	# Data back
	if P.dozscore:
		EEG._data = np.dot(EEG._data,npm.repmat(sd,nEp,nS))+ npm.repmat(mu,nEp,nS)
	if P.refdata:
		#EEG._data = EEG._data + npm.repmat(reference,EEG._data.shape[0],1);
		print('eega_tRejAmp : TODO fix refdata')
	
	#Display rejected data
	n=nEp*nEl*nS
	print("eega_tRejTimeVar : Total data rejected "+ str(np.sum(bct)/n)+"%")

	return EEG,bct