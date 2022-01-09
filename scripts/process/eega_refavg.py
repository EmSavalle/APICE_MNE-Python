from importPy import *

def eega_refavg(EEG,args):
	# Performs an average reference
	print("undefined function")
	return EEG,""
	print("### Reference to the mean ###")

	#---------------------------------------------------------------------------------------
	## Parameters
	P = p()
	P.BadData = 'none' # 'replacebynan' / 'none' / 'zero'
	P.SaveRef = 0 #Keep the reference as an electrode

	P,OK,extrainput = eega_getoptions(P,args)

	if not OK:
		raise ValueError('eega_refavg: Non recognized inputs')

	#---------------------------------------------------------------------------------------
	## Reference
	shape = EEG.get_data().shape
	nEl,nS,nEp = (0,0,0)
	if(len(shape)> 2):
		nEp,nEl,nS
	else:
		nEl,nS = shape
		nEp = 1
	
	v,data_good = eega_rmvbaddata(EEG,['BadData',P.BadData])

	#Reference to the mean
	ref = sum(data_good)/len(data_good)
	#if
	raise ValueError('eega_refavg : function unfinished')
