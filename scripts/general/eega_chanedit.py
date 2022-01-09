from importPy import *
def eega_chanedit(EEG,args):
	"""
	Extract montage from location and apply it to the EEG data
	Input : 
		EEG : Raw Mne data structure
		args:
			filechanloc : File of the montage
	return Raw mne data structure with montage set
	"""
	filechanloc = args[0]
	print(filechanloc)
	montage = mne.channels.read_custom_montage(filechanloc)
	print(montage)
	EEG = EEG.set_montage(montage)
	return EEG