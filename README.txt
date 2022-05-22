This text file describe what has been done for the translation of the APICE pipeline using MNE-Python

Structure :
The structure of the python code is based on the Matlab's structure, and is almost exactly the same

The functions are stored in seperate folder based on their utility.
To add a new functions, write it on a separate python file, and add it inside the designated folder. It will automatically be integrated to the pipeline
If you need to add a folder for functions, you need to modify the 'importPy.py' file. The ligne 54 specify which folder to look at, in order to detect functions to add.

importPy.py file : 
This is a core python file, who scan the folders in order to detect existing file and algorithm.
Every function needs to have the line "from importPy import *" in order to have access to every functions writen for the pipeline

Artifacts structure : 
Again this is based on the Matlab structure
We add a structure to the Raw (or Epoch) variable
EEG.artifacts :
	EEG.artifacts.BCT : Boolean array (same size as our data array) that specify (if at True) that the time sample contains an artifact and must be rejected.
	EEG.artifacts.BC : Boolean array that define if a channel is corrupted/contains artefacts and need to be rejected
	EEG.artifacts.BT : Boolean array that define if a time sample contains artifacts (accross all electrodes) and needs to be rejected



Untranslated functions : 
There is some functions that still needs to be programmed, they can be executed but will display "functions : Undefined functions" when executed.

How to add functions :
Every functions is used the same way, since their application is automatised by the pipeline, they have a fixed way of using
They need two arguments :
  	- The EEG variable
  	- an array that defines the parameters ["nameOfParemeters1","valueOfParameters1","nameOfParemeters2","valueOfParameters2",...]
And the functions needs to return two variable
	- The EEG variable
	- an array, usually the updated artifacts structure (the EEG.artifacts.BCT or a similar array)

How to use it : 
There is some example file of how to use the pipeline. These are Jupyter Notebook called "example_details", "example_APICEa_preprocessing"
There are the direct translation of the same file in Matlab

For mosts questions related to the functionning of the pipeline, you can refer to the matlab code and the two PDF files (APICE and EEGanalysis_notes) that are made by Ana Flõ and describe how the pipeline works and some details on how it has been programmed
And if there is any problems, don't hesitate to ask me directly : emile.savalle@gmail.com