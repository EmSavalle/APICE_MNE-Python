
from importPy import *
import importPy

def eega_filt(EEG,args):
	"""
		Apply a high and low pass filtering to the data
	"""
	h = None
	l = None
	if(len(args)>1):
		h,l = args
	else:
		h = args[0]
	if(l):
		EEG = EEG.filter(None,l)
	if(h):
		EEG = EEG.filter(h,None)
	return EEG