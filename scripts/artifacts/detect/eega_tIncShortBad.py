from importPy import *
def eega_tIncShortBad(EEG,args):
	print('### Rejecting short bad segments ###\n' )

	## ------------------------------------------------------------------------
	## Parameters
	P=p()
	P.timelim = 2.000

	P.updateBCT = 1
	P.updatesummary = 1
	P.updatealgorithm = 1
	P,OK,extrainput=eega_getoptions(P,args)

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
	bct = EEG.artifacts.BCT
	bctold = EEG.artifacts.BCT
	if(len(shape) == 2):
		for el in range(nEl):
			#This detect a chain of 1 in an array that is shorter thant timelim and set them to 0
			a = np.array(bct[0][el])
			
			badi = [int(int(a[i])-int(a[i-1])==1) for i in range(1,len(a)-1)]
			badi = np.array([bool(a[0])]+badi)
			badi = badi!=0
			badf =  [int(int(a[i])-int(a[i+1])==1) for i in range(0,len(a)-2)]
			badf = np.array(badf+[a[len(a)-1]==1])
			badf = badf!=0
			fbadi = find(badi)
			fbadf = find(badf)
			for i in range(0,min(len(fbadf),len(fbadi))):
				if(fbadf[i]-fbadi[i]<timelim):
					bct[0][el][fbadi[i]: fbadf[i]+1]=True
	
	EEG.artifacts.BCT = np.logical_and(EEG.artifacts.BCT,bct)

	n = nEl*nS*nEp;
	sumNew = sum(bct);
	print('eega_tIncShortBad : Total data rejected : '+str(sumNew/n*100 ))
	return EEG,bct