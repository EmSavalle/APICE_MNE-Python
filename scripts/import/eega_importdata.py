from importPy import *
def eega_importdata(filename,preload=False):
	# This function import data 
	path,name= os.path.split(filename)
	name,ext = name.split(".")

	print("Importing file "+name+" ...")
	print("File type "+ext)
	print("File name : "+filename)
	
	if(ext == "set"):
		EEG = mne.io.read_raw_eeglab(filename,preload=preload)
	elif(ext == "mff"):
		EEG = mne.io.read_raw_egi(filename,preload=preload)
	elif(ext == "vhdr"):
		EEG = mne.io.read_raw_brainvision(filename,preload=preload)
	elif(ext == "egi"):
		EEG = mne.io.read_raw_egi(filename,preload=preload)
	else:
		print(name,ext)
	EEG.fileName = name
	return EEG
