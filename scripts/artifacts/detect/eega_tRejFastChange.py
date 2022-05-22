from importPy import *
def eega_tRejFastChange(EEG,args):
	## ------------------------------------------------------------------------
	## Parameters
	P=p()
	P.thresh = 3
	P.tmotion = 0.020
	P.refdata = 0
	P.refbaddata = 'none' # 'replacebynan' / 'none' / 'zero'
	P.dozscore = 0
	P.relative = 1
	P.xelectrode = 1
	P.mask = 0.

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1
	varargin = args



	P, OK, extrainput = eega_getoptions(P, varargin)
	if not OK:
		raise ValueError('eega_tRejFastChange: Non recognized inputs')

	# Check the inputs
	if type(P.dozscore) == list or (P.dozscore != 0 and P.dozscore != 1):
		raise ValueError('eega_tRejFastChange: dozscore has to be 0 / 1')
	
	if (P.relative != 0 and P.relative != 1): #Verifie si les valeures de P.relative sont bien soit 1 soit 0
		raise ValueError('eega_tRejFastChange: relative has to have values 0 / 1')

	if (P.xelectrode != 0 and P.xelectrode != 1):
		raise ValueError('eega_tRejFastChange: xelectrode has to have values 0 / 1')


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
	## Calculate the max change

	#Nm of samples in the time window
	smpls_amp = round(P.tmotion * EEG.info["sfreq"])
	if(smpls_amp%2 == 1):
		smpls_amp = smpls_amp -1
	ids = np.array(list(range(int(-smpls_amp/2),int(smpls_amp/2))))
	#First derivative
	d = np.diff(EEG._data,1,len(shape)-1)
	
	change = np.zeros(shape)
	for ep in range(nEp):
		for el in range(nEl):
			for s in range(nS):
				sampStud = ids+s
				sampStud[sampStud<0]=0
				sampStud[sampStud>nS-2]=nS-2
				v = sum(d[el][sampStud])
				if(len(shape)>2):
					change[ep][el][s]=v
				else:
					change[el][s]=v
	change = np.abs(change)   

	T = np.zeros(nEl)
	Ru = np.zeros((nEp,nEl,nS))
	if(P.relative == 1):
		if(P.xelectrode == 1):
			ru_sum = 0
			for ep in range(nEp):
				d = []
				print(shape)
				if(len(change.shape)>2):
					d = change[ep]
				else:
					d = change
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
			dd = change
			perc = np.percentile(dd[np.logical_not(EEG.artifacts.BCT[0])],75)
			IQ = 2 * perc
			t_u = perc + P.thresh*IQ
			Ru = np.logical_or(Ru,change>t_u)
			ru_sum = sum(change>t_u)
	else:
		dd = change
		t_u = P.thresh
		Ru = np.logical_or(Ru, change>t_u)
		T[:] = t_u
		ru_sum=sum(change>t_u) 
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
