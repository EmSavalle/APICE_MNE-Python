from importPy import *
def diff(L):
	ret = [ x-y for (x,y) in zip(L[1:],L[:-1]) ]
	if (len(ret) == 1):
		return ret[0]
	return ret

def str2func(str):
	return 

def find(array):
	# Return indices of non zeros in array
	ret = []
	for i in range(0,len(array)):
		if(array[i] != 0 ):
			ret.append(i)
	return ret 
def strip(st):
	#Remove spaces from str
	st = st.replace(" ","")
	return st

def unique(L):
	""" Return list made with all uniques elements of L"""
	new_L = []
	for i in L:
		if(i not in new_L):
			new_L.append(i)
	return new_L
def fieldnames(P):
	fieldsP = []
	members = inspect.getmembers(P, lambda a:not(inspect.isroutine(a)))
	for ind,val in members:
		if(ind == '__dict__'):
			for i in val:
				if(i[0] != "_"):
					fieldsP.append(i)
	return fieldsP
