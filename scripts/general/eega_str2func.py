from importPy import *
import importPy
def eega_str2func(func):
	#Convert a the string name of a function to the function itself
	if('.' in func):
		mod,fun = func.split('.')
		if(mod == "octave"):
			return getattr(octave,fun)
		if(mod == "io"):
			return getattr(io,fun)
		else:
			return mod
	else:
		if(hasattr(importPy,func)):
			return getattr(importPy,func)
		else:
			return globals()[func]