
from importPy import *

def eega_plot_artifacts(EEG,args):
	if(args != []):
		bct = args
		data = EEG._data
	elif(hasattr(EEG,'artifacts')):
		bct = EEG.artifacts.BCT
		data = EEG._data
	else:
		print("eega_plot_artifacts : No artifacts detected in data")
	print(np.sum(bct))
	if(len(data.shape)>2):
		nEp,nEl,nS = data.shape
	else:
		nEp = 1
		nEl,nS = data.shape

	"""for ep in range(nEp):
		if(len(data.shape)>2):
			d = data[ep]
		else:
			d = data
		for el in range(nEl):
			inds = find(bct[ep][el])
			indsRed = []
			if(inds !=  []):
				c = inds[0]
				for i in range(1,len(inds)-1):
					if(inds[i]+1 != inds[i+1]):
						indsRed.append((c,i))
						c = inds[i+1]
				for x,y in indsRed:
					if(y> x):
						print(el,x,y)
						plt.plot(d[el][x:y])
						plt.show()
					if(y< x):
						print(el,x,y)
						plt.plot(d[el][y:x])
						plt.show()"""
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.imshow(bct[0], aspect='auto', cmap=plt.cm.gray)
	plt.show()
	return EEG
