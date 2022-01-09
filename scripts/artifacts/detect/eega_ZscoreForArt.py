from importPy import * 

def eega_ZscoreForArt(EEG):
	shape = EEG.get_data().shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS
	else:
		nEl,nS = shape
		nEp = 1
	

	# Take the d
	d = EEG._data

	# Compute the mean and standard deviation
	mu = [sum(i)/len(i) for i in d]
	sd = [np.std(i) for i in d]

	#zscore
	cpt = 0
	l = 0
	cptd = 0
	ld = 0
	for i in range(0,len(d)):
		for j in range(0,len(d[0])):
			cpt+=EEG._data[i][j]
			l+=1
			d[i][j] = (d[i][j]-mu[i])/sd[i]
			cptd += d[i][j]
	
	EEG._data = d
	return EEG,mu,sd