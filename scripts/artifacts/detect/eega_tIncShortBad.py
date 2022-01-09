from importPy import *
def eega_tIncShortBad(EEG,args):
	print('### Rejecting short good segments ###\n' )

	## ------------------------------------------------------------------------
	## Parameters
	P=p()
	P.timelim = 2.000

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1
	P,OK,extrainput=eega_getoptions(P,varargin)

	shape = EEG.get_data().shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS = shape
	else:
		nEl,nS = shape
		nEp = 1


	timelim = round(P.timelim*EEG.info['sfreq']);
	if nS<=timelim:
		timelim = nS-1
	bctin =np.logical_not(EEG.artifacts.BCT)
	bct = np.zeros((nEp,nEl,nS))
	if(len(shape) == 2):
		for el in range(nEl):
			#This detect a chain of 1 in an array that is shorter thant timelim and set them to 0
			a = np.array(bctin[0][el])
			
			goodi = [int(int(a[i])-int(a[i-1])==1) for i in range(1,len(a)-1)]
			#goodi = (a[1:(len(a))]-a[0:(len(a)-1)] == 1)
			goodi = np.array([bool(a[0])]+goodi)
			goodi = goodi!=0
			goodf =  [int(int(a[i])-int(a[i+1])==1) for i in range(0,len(a)-2)]
			#goodf = (a[0:(len(a)-1)]-a[1:(len(a))] == 1)
			goodf = np.array(goodf+[a[len(a)-1]==1])
			goodf = goodf!=0
			fgoodi = find(goodi)
			fgoodf = find(goodf)
			for i in range(0,len(fgoodi)):
				if(fgoodf[i]-fgoodi[i]<timelim):
					bct[0][el][fgoodi[i]: fgoodf[i]+1]=True
	
	EEG.artifacts.BCT = np.logical_or(EEG.artifacts.BCT,bct)

	n = nEl*nS*nEp;
	sumNew = sum(bct);
	print('Total data rejected : '+str(sumNew/n*100 ))
	eega_plot_artifacts(EEG,bct)
	return EEG,bct