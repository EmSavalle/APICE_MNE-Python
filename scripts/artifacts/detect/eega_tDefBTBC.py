
from importPy import *

def eega_tDefBTBC(EEG,args):
	"""
	This function defines where there are artifacts affecting all the electrodes and which are bad channels
	Input : 
		EEG : MneRaw Struct
		Args : 
			DefBT
			DefBC
			DefBCAll
			(optionnal)
			maskTime : time to mask bad times
		 	minBadTime : Periods with artifacts shorter than this (s) are not included
		    keeppre : keep previuos values
			plot : plot the rejection
	Output :
		EEG Output data
		BTnew : bad times , logical indexes
		BCnew : bad electrodes , logical indexes
	"""

	#Inputs : 
	DefBT = args[0]
	DefBC = args[1]
	DefBCAll = args[2]
	varargin = []
	if(len(args)>3):
		varargin = args[3:]
	P = p()
	P.keeppre = 0
	P.plot = 0
	P.minBadTime = 0
	P.maskTime = 0
	P.minGoodTime = 0
	P,OK,extrainput = eega_getoptions(p,varargin)

	if( not OK):
		raise ValueError("eega_tDefBTBC : Non recognized inputs")

	ncycle = set([len(DefBT),len(DefBC),len(DefBCAll)])
	if(len(ncycle) != 1):
		raise ValueError("eega_tDefBTBC : all the thresholds have to have the same length")


	#----------------------------------------------------------------------------------
	##Get the data from the EEG structure
	shape = EEG.get_data().shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS
	else:
		nEl,nS = shape
		nEp = 1
	

	#----------------------------------------------------------------------------------
	##Define artifacts
	if (type(P.keeppre) in [float,int]):
		if (P.keeppre == 1):
			if( hasattr(EEG.artifacts,"BC")):
				BCold = EEG.artifacts.BC
			else:
				BCold = [[0 for i in range(nEl)] for i in range(nEp)]

			if( hasattr(EEG.artifacts,"BT")):
				BTold = EEG.artifacts.BT
			else:
				BTold =[[0 for i in range(nS)] for i in range(nEp)]
		else:
			BCold = [[0 for i in range(nEl)] for i in range(nEp)]
			BTold = [[0 for i in range(nS)] for i in range(nEp)]
	elif(type(P.keeppre) == str):
		if (P.keeppre == 'BT'):
			if( hasattr(EEG.artifacts,"BT")):
				BTold = EEG.artifacts.BT
				BCold = [[0 for i in range(nEl)] for i in range(nEp)]
			else:
				BTold = [[0]*nS]*nEp
				BCold = [[0 for i in range(nEl)] for i in range(nEp)]

		elif(P.keeppre == 'BC'):
			if( hasattr(EEG.artifacts,"BC")):
				BCold = EEG.artifacts.BC
				BTold = [[0 for i in range(nS)] for i in range(nEp)]
			else:
				BCold = [[0 for i in range(nEl)] for i in range(nEp)]
				BTold = [[0 for i in range(nS)] for i in range(nEp)]

	BCnew = BCold
	BTnew = BTold
	#BCBTnew : Array of size nEp*nEl*nS with value being 1 if data is bad (if the electrode or time is bad)
	
	BCBTnew = [[[1 for i in range(nS)] for i in range(nEl)] for i in range(nEp)]
	for ep in range(nEp):
		for el in range(nEg):
			for s in range(nS):
				if(BCnew[ep][el] == 1):
					BCBTnew[ep][el][s] = 1
				if(BTnew[ep][el] == 1):
					BCBTnew[ep][el][s] = 1

	#BCall : Array of size nEl being 1 if the electrode is bad for every epoch
	BCall = [0 for i in range(nEl)]
	for i in BCnew:
	    BCall = [BCall[ind]+i[ind] for ind in range(len(i))]
	BCall = [1 if i == nEp else 0 for i in BCall]

	if(hasattr(EEG.artifacts,'BCmanual')):#If channels has been manually defined as bad
		for ch in EEG.artifacts.BCmanual:
			BCall[ch] = 1
			for epoch in range(len(BCnew)):
				BCnew[epoch][ch] = 1

	for icyc in range(1,ncycle):

		## DEFINE BAD SAMPLES BASED ON ABSOLUTE THRESHOLD

		# number of bad channels per sample
		thrsBadCh = DefBT[icyc]
		bct = EEG.artifacts.bct
		sumBad = [[0 for i in range(nS)] for i in range(nEp)]
		sumNotBad = [[0 for i in range(nS)] for i in range(nEp)]
		for ep in range(nEp):
			for el in range(nEl):
				for s in range(nS):
					if(BCnew[ep][el] == 1):
						bct[ep][el][s] = 0
					sumBad[ep][s]=sumBad[ep][s]+bct[ep][el][s]
					sumNotBad[ep][s]=sumNotBad[ep][s]+(BCnew[ep][el][s]+1)%2
		


		#number of bad samples per channel
		thrsBadSAll = DefBCAll[icyc]
		bct = EEG.artifacts.bct
		nbadSall = [0 for i in range(nEl)]
		nnotbadSall = [0 for i in range(nEl)]
		for ep in range(nEp):
			for el in range(nEl):
				for s in range(nS):
					if(BTnew[ep][s] == 1):
						bct[ep][el][s]=0
					nbadSAll[el] = nbadSAll[el]+bct[ep][el][s]
					nnotbadSall[el] = nbadSAll[el]+(BTnew[ep][el][s]+1)%2


		thrsBadSAll = DefBCAll[icyc]
		thrsBadS = DefBC[icyc]
		thrsBadCh = DefBT[icyc]
		
		bct = EEG.artifacts.bct
		bct2 = EEG.artifacts.bct

		#number of bad samples per channel
		nbadSall = [0 for i in range(nEl)]
		nnotbadSall = [0 for i in range(nEl)]

		# number of bad channels per sample
		nbadCh = [[0 for i in range(nS)] for i in range(nEp)]
		nnotbadCh = [[0 for i in range(nS)] for i in range(nEp)]

		#number of bad samples per channel
		nbadS = [[0 for i in range(nEl)] for i in range(nEp)]
		nnotbadS = [[0 for i in range(nEl)] for i in range(nEp)]
		for ep in range(nEp):
			for el in range(nEl):
				for s in range(nS):
					if(BCnew[ep][el] == 1):
						bct[ep][el][s] = 0
					nbadCh[ep][s]=nbadCh[ep][s]+bct[ep][el][s]
					nnotbadCh[ep][s]=nnotbadCh[ep][s]+(BCnew[ep][el][s]+1)%2

					if(BTnew[ep][s] == 1):
						bct2[ep][el][s]=0

					nbadSAll[el] = nbadSAll[el]+bct2[ep][el][s]
					nnotbadSall[el] = nbadSAll[el]+(BTnew[ep][el][s]+1)%2

					nbadS[ep][el] = nbadS[ep][el]+bct2[ep][el][s]
					nnotbadS[ep][el] = nnotbadS[ep][el]+(BTnew[ep][el][s]+1)%2
		
		## DEFINE BAD SAMPLES BASED ON ABSOLUTE THRESHOLD
		pbadCh = [[0 for i in range(nS)] for i in range(nEp)]
		for ep in range(nEp):
			for s in range(nS):
				pbadCh[ep][s] = sumBad[ep][s]/sumNotBad[ep][s]
		
		## DEFINE BAD CHANNELS DURING THE WHOLE RECORDING ON ABSOLUTE THRESHOLD
		pbadSAll = [nbadSAll[i]/nnotbadSall[i] for i in range(nEl)]

		## DEFINE BAD CHANNELS PER EPOCH ON ABSOLUTE THRESHOLD
		pbadS = [[0 for i in range(nS)] for i in range(nEp)]
		for ep in range(nEp):
			for el in range(nEl):
				pbadS[ep][el] = nbadS[ep][el]/nnotbadS[ep][el]

		## Rejection
		for ep in range(nEp):
			for el in range(nEl):
				BCall[el] = int(BCall[el] or (pbadSAll[el]>thrsBadCh))
				BCnew[ep][el] = int(BCnew[ep][el] or BCall[el] or (pbadS[ep][el]>thrsBadS))
				for s in range(nS):
					BTnew[ep][s] = int(BTnew[ep][s] or (pbadCh[ep][s]>thrsBadCh))

		# Test if the definition has changed
		bcbt = [[[0 for i in range(nS)] for i in range(nEl)] for i in range(nEp)]
		T = [[[0 for i in range(nS)] for i in range(nEl)] for i in range(nEp)]
		for ep in range(nEp):
			for el in range(nEl):
				for s in range(nS):
					if(BCnew[ep][el] == 1):
						bcbt[ep][el][s] = 1
					if(BTnew[ep][s] == 1):
						bcbt[ep][el][s] = 1
					if(bcbt[ep][el][s] != BCBTnew[ep][el][s]):
						T[ep][el][s]=1
		sumDifference = sum([sum([sum(j) for j in i])for i in T])
		BCBTnew = bcbt
		print("Cycle "+str(icyc)+" , new rejected data "+str(100*sumDifference/(nEp*nEl*nS)))

	## Update
	for ep in range(nEp):	
		for el in range(nEl):
			BC[ep][el] = int(BCold[ep][el] or BCnew[ep][el])
			for s in range(nS):
				BT[ep][s] = int(BTold[ep][s] or BTnew[ep][s])
	
	## Samples rejection 
	#remove too short artifacts
	P.minBadTime = P.minBadTime * EEG.info['sfreq']
	if(P.minBadTime != 0):
		for ep in range(nEp):
			isbadsmpl = [BT[ep][i] for i in range(0,nS)]
			tbad = [BT[ep][i] for i in range(0,nS)]
			bad = [int(tbad[i]-tbad[i-1]==1) for i in range(1,len(tbad)-1)]
			badi = [tbad[0]]+bad

			bad = [int(tbad[i]-tbad[i+1]==1) for i in range(0,len(tbad)-2)]
			badf = bad+[tbad[len(tbad)-1]]

			badi = find(badi)
			badf = find(badf)
			idx = [1 if(badf[i]-badi[i] < P.minBadTime) else 0 for i in range(len(badi))]
			for i in idx:
				for j in range(badi[i],badf[i]+1):
					isbadsmpl[j]=0
			for s in range(nS):
				BT[ep][s] = isbadsmpl[s]

	# Mask around
	if(P.maskTime != 0):
		P.maskTime = P.maskTime * EEG.info['sfreq']
		art_buffer = round(P.maskTime)
		for ep in range(nEp):
			bt = [BT[ep][i] for i in range(0,nS)]
			bad_idx = find(bt)

			#Eliminate time point before or after motion artifacts
			if(bad_idx != []):
				for i in bad_idx:
					limmin = max(0,i-2*art_buffer)
					limmax = min(i+2*art_buffer,nS)

					for sam in range(limmin,limmax+1):
						BT[ep][sam] = 1

	#Remove too short periods with non artifacts
	P.minGoodTime = P.minGoodTime * EEG.info['sfreq']
	if(P.minGoodTime != 0 and P.minGoodTime < nS-2):
		for ep in range(nEp):
			isbadsmpl = [BT[ep][i] for i in range(0,nS)]
			tgood= [(BT[ep][i]+1)%2 for i in range(0,nS)]
			
			good = [int(tgood[i]-tgood[i-1]==1) for i in range(1,len(tgood)-1)]
			goodi = [tgood[0]]+tgood

			good = [int(tgood[i]-tgood[i+1]==1) for i in range(0,len(tgood)-2)]
			goodf = good+[tgood[len(tgood)-1]]

			goodi = find(goodi)
			goodf = find(goodf)
			idx = [1 if(goodf[i]-goodi[i] < P.minGoodTime) else 0 for i in range(len(goodi))]
			for i in idx:
				for j in range(goodi[i],goodf[i]+1):
					isbadsmpl[j]=1
			for s in range(nS):
				BT[ep][s] = int(BT[ep][s] or isbadsmpl[s])

	## Display rejected data
	d = nEp*1*nS
	cptnew = 0
	cptall = 0
	for ep in range(nEp):	
		for s in range(nS):
			cptnew+=int(BT[ep][s] and not BTold[ep][s])
			cptall+=BT[ep][s]
	print('Total new bad times ____________'+str(cptnew/d*100))
	print('Total bad times ________________'+str(cptall/d*100))

	d = nEp*nEl*1
	cptnew = 0
	cptall = 0
	for ep in range(nEp):	
		for s in range(nEl):
			cptnew+=int(BC[ep][el] and not BCold[ep][el])
			cptall+=BC[ep][el]
	print('Total new bad channels per epoch ____________'+str(cptnew/d*100))
	print('Total bad channels per epoch ________________'+str(cptall/d*100))

	
	sBC = [0 for i in range(nEl)]
	sBCold = [0 for i in range(nEl)]
	for i in BC:
	    sBC = [sBC[ind]+i[ind] for ind in range(len(i))]
	for i in BCold:
	    sBCold = [sBCold[ind]+(i[ind]+1)%2 for ind in range(len(i))]
	
	alld = sum([1 if(i == nEp)  else 0 for i in sBC])
	newd = [1 if(sBCold[i] == nEp and sBC[i] == nEp) else 0 for i in range(len(sBCold))]

	print('Total new bad channels____________'+str(cptnew))
	print('Total bad channels ________________'+str(cptall))

	## Update the rejection matrix
	EEG.artifacts.BT = BT
	EEG.artifacts.BC = BCnew
	EEG.reject.rejmanualE = EEG.artifacts.BC
	if(hasattr(None,'eega_summarypp')):
		EEG = eega_summarypp(EEG)

	## Plot rejection matrix
	if(P.plot):
		if(hasattr(None,'eega_plot_artifacts')):
			eega_plot_artifacts(EEG)
	return EEG