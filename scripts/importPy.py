"""

	This file manage all import needed for the preprocessing

"""

import math
import os,sys
from oct2py import octave
pathEEGLAB = "D:/Dev/ProjetCNNAPICE/Matlab/eeglab2021.1/functions"
octave.addpath(pathEEGLAB+'/guifunc')
octave.addpath(pathEEGLAB+'/popfunc')
octave.addpath(pathEEGLAB+'/adminfunc')
octave.addpath(pathEEGLAB+'/sigprocfunc')
octave.addpath(pathEEGLAB+'/miscfunc')
octave.addpath(pathEEGLAB+'/../plugins/firfilt')
import pathlib
currentPath = str(pathlib.Path().resolve())

currentPath = str(pathlib.Path(__file__).parent.resolve())+"/"
print(currentPath)
sys.path.append(currentPath+"scripts")
sys.path.append(currentPath+"scripts/artifacts")
sys.path.append(currentPath+"scripts/artifacts/detect")
sys.path.append(currentPath+"scripts/artifacts/correct")
sys.path.append(currentPath+"scripts/events")
sys.path.append(currentPath+"scripts/import")
sys.path.append(currentPath+"scripts/process")
sys.path.append(currentPath+"scripts/general")
sys.path.append(currentPath+"scripts/dev")
sys.path.append(currentPath+"examples/parameters")
sys.path.append(currentPath+"examples/DATA")
sys.path.append(currentPath+"examples/DATA/set")
sys.path.append(currentPath+"examples/DATA/evt")
sys.path.append(currentPath+"examples/DATA/prp")
sys.path.append(currentPath+"examples/DATA/erp")

import math
import mne
#import mne_bids
import pandas as pd
from mne import io
import numpy as np
import glob, os
import time
import sys
import inspect
import importlib.machinery
import importlib.util
import numpy.matlib as npm
import matplotlib.pyplot as plt

#Look inside the folders and import all .py files
folders = ['artifacts/','artifacts/detect/','artifacts/correct/','plot/','general/','events/','import/','process/','dev/',"examples/parameters/"]
dir = currentPath   
for f in folders:
	for module in os.listdir(dir+f):
		if(".py" in module ):
			print(module)
			#file_dir = os.path.dirname(module)
			#sys.path.append(file_dir)
			# Import mymodule
			loader = importlib.machinery.SourceFileLoader( 'mymodule', dir+f+module )
			spec = importlib.util.spec_from_loader( 'mymodule', loader )
			mymodule = importlib.util.module_from_spec( spec )
			loader.exec_module( mymodule )
			if "__all__" in mymodule.__dict__:
				names = mymodule.__dict__["__all__"]
			else:
				# otherwise we import all names that don't begin with _
				names = [x for x in mymodule.__dict__ if not x.startswith("_")]
			# now drag them in
			globals().update({k: getattr(mymodule, k) for k in names})


class Cnf:
	None
class p:
	None

class P:
	None
class art():
	algorithm = ""
	loops = []
	def __init__(self):
		self.P = P()


class ParametersERP:
	#All parameters for ERP analysis 
	##Filtering params
	
	#Filter high and low pass
	filt_highpass = 0
	filt_lowpass = 40
	
	##Epoching params
	
	class Epoch:
		#Epoch time window
		tw = [0,0]
		#Event relative to wich the data epoched
		ev = {}
	
	##Artifacts interpolation Parameters
	
	#Structure type for artifact Interpolation
	Int = None
	
	##Parameters for BadTime (BT) and Bad Channels (BC)
	class BCall: #Bad Channel All
		nbt = [] #Proportion of BT to define a BC for all recording
	class BCep: #Bad Channel Epoch
		nbt = []#Proportion of BT to define a BC for an epoch
	class BTep: #Bad Time Epoch
		nbc = []#Proportion of BC to define a BT
		minGoodTime = 1.0 #Good segments of less time will be marked as bad
		minBadTime = 0.1 #Bad time shorter will not be considered as bad
		maskTime = 0 #Mark as bad samples surronding a bad time
	##Parameters to define a Bad Epochs based on the amout of bad data
	class DefBEa:
		limBCTa = 1.00 #Max proportion of bad data per epoch
		limBTa = 0 #Max proportion of bad times per epoch
		limBCa = 0.3 #Max proportion of bad channels per epoch
		limCCTa = 0.5 #Max proportion of interpolated data per epoch
		
	##Parameters for experimental factors and averaging	
	
	# Define based on the events the factors that will be used to determine conditions
	# They should be events' properties (e.g., EEG.epoch(i).eventCong) 
	# This factors can be the used for averaging across one or multiple of them to obtain the different experimental conditions
	# The factors are defined in EEG.F For each factor i it contains:
	# - EEG.F{i}.name: name of the factor (e.g., 'eventCong')
	# - EEG.F{i}.val: possible values of the factor (e.g., {'x0'  'x1'})
	# - EEG.F{i}.g: vector with length equal to the number of epochs with the indexes
	# to EEG.F{i}.val indicating the value of the factor (EEG.F.val(EEG.F{i}.g(k)) is the the value of the facto i for epoch k)
	factors = {'eventCong', 'eventProb'}

	# Parameters for averaging across some factors to obtain the ERPs for different conditions
	# After averaging, EEG.data has size (channles) x (samples) x (possible conditions) 
	avgcnd = {'eventCong', 'eventProb'}
	
	##Parameters for baseline correction
	class BL:
		tw = [-100,100] #Time windows to compute the baseline (ms)
		
	##Parameters to generate the report
	class report:
		pattername ="" #Pattern to find the names to create the table (whole filesname usedif empty)
		patternn = []
	
	class DSS:
		# (1) apply | (0) do not apply
		apply	  = 0
		# components to keep in the first PCA
		k		  = 50
		# components to keep in the second PCA
		n		  = 15
		# Define the trials to use to bias the filter. 
		# Different filters can be used for different trials sets
		# If empty, one filter is created using all trials
		fbias	  = []
		# Define the trials to which the DSS is applied 
		# Different filters can be applied for different trials sets
		# If empty, the single filter is applied to all trials
		fapply	 = []
class EventCorrlat:
	event1=[]
	event2=""

class ParametersPreProcessing:
	## Parameters for the preprocessing (continuos data)

	# -------------------------------------------------------------------------
	# Parameters for importing the data
	# -------------------------------------------------------------------------

	# Name of the files to read from the Path2DataSet folder
	Files2Read = '*.set' 

	# Add extra information in an even file (.evt) located in Path2DataEventimport 
	# This step should be avoided unless extra information in the event 
	# file is not imported from the raw data to the EEGLAB structure. 
	# The function adding events has been created to add events sent by 
	# Psychtoolbox to EGI. The addition of new events will not work with other
	# acquisition systems. Customized functions might be required
	# (1) add | (0) do not add
	importevntapply = 1   

	# Event to use to align differences in time offsets between the event file 
	# and the EEG structure
	# Only necessary if events are added (Ppp.importevntapply = 1)
	importevnt0 = 'STRT'	
		

	# -------------------------------------------------------------------------
	# Parameters for correcting the events
	# -------------------------------------------------------------------------

	# Correct the latency of a given event using Digital Input events (DINs)
	# (1) apply | (0) do not apply
	eventcorrlatapply = 1   

	# The latency of the events 'Icue' 'Iout' 'Ieye' are corrected by the latency of 'DIN6'
	# Only necessary if events are added (Ppp.eventcorrlatapply = 1)
	eventcorrlat = [] 
	
	# Delete unuseful events
	# (1) apply | (0) do not apply
	eventrmvapply = 1 
	# Events to delete
	# Only necessary if events are added (Ppp.eventrmvapply = 1)
	eventrmv = {'DIN6'} 


	# -------------------------------------------------------------------------
	# Parameters for filtering
	# -------------------------------------------------------------------------

	# High pass filter
	filt_highpass   = 0.1 

	# Low pass filter
	filt_lowpass	= 40 


	# -------------------------------------------------------------------------
	# Parameters for artifacts detection
	# -------------------------------------------------------------------------

	# Generate the structures with the parameters for the artefact detection
	# The functions to generate the structures should be in the path (Path2Parameters)
	# These functions should be modified to change the algorithms applied for
	# artifacts detection

	# In this example, we use a relative threshold of 3 for all types of
	# artifacts (APICE(3))

	# Algorithms to detect bad electrodes
	ArtBadEl = example_APICE_ArtPP_BadEl(3) 
	# Algorithms to detect jumps in the signal
	ArtJump = example_APICE_ArtPP_Jump(3) 
	# Algorithms to detect motion artifacts
	ArtMot1 = example_APICE_ArtPP_Mot1(3) 
	# Algorithms to detect motion artifacts
	ArtMot2 = example_APICE_ArtPP_Mot2(3) 


	# -------------------------------------------------------------------------
	# Parameters for transient artifacts interpolation
	# -------------------------------------------------------------------------

	# Apply the interpolation of transient artifacts using target PCA
	# (1) apply (APICE) | (0) do not apply (APICEa, APICE+W-ICA)
	IntTransientArtPCA = 1 

	# Apply the interpolation of transient artifacts using spherical spline
	# (1) apply (APICE, APICE+W-ICA) | (0) do not apply (APICEa)
	IntTransientArtSpline = 1 

	# Generate the structures with the parameters for the artifact correction
	# The functions to generate the structures should be in the path (in Path2Parameters)
	# This function should be modified to change the algorithms applied for
	# artifacts interpolation
	Int = example_APICE_Interpolation 


	# -------------------------------------------------------------------------
	# Parameters to define Bad Times (BT) and Bad Channels (BC) 
	# -------------------------------------------------------------------------
	class BCall:
		# Limits for the proportion of BT to define a BC (the last value is the final/effective one)
		nbt		   = [0.70, 0.50, 0.30] 
	# Limits for the proportion of BC to define a BT (the last value is the final/effective one)
	class BTall:
		nbc		   = [0.70, 0.50, 0.30] 
		# Shorter intervals between bad segments will be marked as bad
		minGoodTime   = 1.000 
		# Shorter periods will not be considered as bad
		minBadTime	= 0.100	
		# Also mark as bad surronding samples within this value 
		maskTime	  = 0.500		 

	# -------------------------------------------------------------------------
	# Parameters for W-ICA
	# -------------------------------------------------------------------------
	class ICA:
		# Run or not ICA
		# (1) apply | (0) do not apply
		apply		   = 0	 
		

	# -------------------------------------------------------------------------
	# Parameters to generate the report
	# -------------------------------------------------------------------------
	class report:
	# Pattern to find in the names to create the table (subjetcs identifier). 
	# If empty, the whole files name are used
		patternname = 'data'   
	# Number of caracters to use from the begiging of the patter to create the table. 
	# If empty, the name is extracted from the begign of the patter till the
	# end of the name
		patternn = [] 


