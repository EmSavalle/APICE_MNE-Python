def eega_epoch(EEG,args):
	"""
	Split the EEG data into epochs

	Input:
		EEG : Raw mne data
		args:
			events : event_id to study
			timelim : Epoch latency limits [start,end]

	"""
	events = mne.find_events(EEG)
	event_id = args[0]
	tmin,tmax =args[1]

	epochs = Epochs(raw, events, event_id, tmin, tmax)
