

import importPy
from importPy import *
def eega_RunAll(filesNames, pathIn, pathOut, args):
    ##Fonction : Runs all functions in args input on all input files and saves the output
    
    ##Input
    #filesNames : string with the files: "*.set" to search for all set files or "name1 name2"
    #pathin : string with the path where the files are
    #pathout : string with the path where the saved files will be stored
    
    ##Optional Inputs
    #args : array with 
    # [couple func , var  : function to apply with variables related to function , those comes in pairs, and multiples couples can be added
    # 'prename', prename : string with something to add before the filename
    # 'runto', runto : int with how to run eega_RunAll : 1 all files in input folder / 2 all files that are not in output folder ]
    
    ##Usage 
    #eega_RunAll(filesnames,pathIn,pathOut, func1, [vars1], func2, vars2),...,'prename',"xx_",'runto',1)
    
    #Functions to be called habe to be of the form
    #EEG = function(EEG,args)
    
    ## Parameters
    
    prename  =''
    saveformat = 'set'
    doeegall = 0
    runto = 0
    #Taking the optional parameters
    if( len(args)%2 == 1):
        print("eega_RunAll : Error Optional parameters must come in pairs")
    else:
        thefunctions = []
        i = 0
        while( i < len(args)):
            if(args[i] == "runto"):
                runto = args[i+1]
            elif(args[i] == "prename"):
                prename = args[i+1]
            elif(args[i]=="saveformat"):
                saveformat = args[i+1]
            elif(args[i]=="saveeegall"):
                doeegall = args[i+1]
            else:
                if(type(args[i])==str):
                    thefunctions.append((importPy.eega_str2func(args[i]),args[i+1]))
                    print(importPy.eega_str2func(args[i]),args[i+1])
                else:
                    thefunctions.append((args[i],args[i+1]))
            i=i+2
    
    #Asking what to do for each files
    if(runto == 0):
        
        print( 'What would you like to do?\n')
        print( '	1. Run it for all the files found and overwrite previous output files (1)\n')
        print( '	2. Run it only for the new files (2)\n')
        print( '	3. Ask in each case if a previous analysis is found (3)\n')
        while runto not in [1,2,3]:
            print('Chose an option 1, 2 or 3: ')
            runto = int(input())
    filesList = []
    
    #Collectiong all files to be processed   
    if('*.set' in filesNames):#Search for all .set files
        print(".set")
        print(pathIn)
        filesList = glob.glob(pathIn+"**/*.set", recursive=True)
        print(filesList)
    elif('*.mat' in filesNames):#Search for all .set files
        filesList = glob.glob(pathIn+"**/*.mat", recursive=True)
    else: #Assemble filename with directory
        lFilesNames = filesNames.split(" ")
        for i in lFilesNames:
            if(".set" not in i):
                filesList.append(pathIn+i+".set")
            else:
                filesList.append(pathIn+i)
    subjects = len(filesList)
    print(filesList)
    #Creating output folder if it doesn't exist
    if(not os.path.isdir(pathOut)):
        os.makedirs(pathOut)

    #--------------------------------------------------------------------------------------------
    ## Process
    #Run on all files
    print("Loop")
    print(subjects)
    for subj in range(0,subjects):
        t0 = time.time()
        do = True
        
        #Get subject name from file
        subjectName = filesList[subj].split("/")[-1].split("\\")[-1].replace(".set","").replace(".mat","")
        
        #if("set" in saveformat):
        #    nameOut = prename+subjectName+".set"
        #elif("mat" in saveformat):
        #    nameOut = prename+subjectName+".mat"
        #else:
        #    nameOut = []
        nameOut=prename+subjectName+"_processed.fif"
        print("-"*20+"Subject : "+subjectName+"-"*20)
        
        #Produce output file name
        fileNameOut = pathOut+nameOut

        #Checking if files has to be processed
        if(runto == 2 or runto == 3):
            if(os.path.isfile(fileNameOut) and runto==3):
                print("Attention! a file was found for this subject \n")
                print(" Do you want to over_write it? Yes(y)/No(n):")
                resp = input()
                if('n' in resp):
                    do = False
            elif(os.path.isfile(fileNameOut) and runto==2):
                do = False
        if(nameOut == []):
            do = False
        
        #------------------------------------------------------------------------------------
        #File processing
        print(do)
        if(do):
            #------------------------------------------------------------------------------------
      
            #Loading data
            
            EEG =importPy.eega_importdata(filesList[subj],preload=True)
            fun_i = 0
            #------------------------------------------------------------------------------------
            #Running all functions
            while fun_i < len(thefunctions):
                thefun = thefunctions[fun_i][0]
                inputs = thefunctions[fun_i][1]

                if(EEG != []):
                    print(thefun)
                    EEG = thefun(EEG,inputs)
                else:
                    print("Error : Empty data!")
                fun_i=fun_i+1
            print("EEG")
            print(EEG)    
            t = time.time()-t0;
            hours   = round(t / 3600);
            t = t - hours * 3600;
            mins    = round(t / 60);
            t = t - mins * 60;
            secs    = round(t);
            print('\nTotal time fo subject '+subjectName+' : '+str(hours)+'h : '+str(mins)+'m : '+str(secs)+'s\n')

            #------------------------------------------------------------------------------------
            #Saving
            if(do and pathOut !=[]):
                print(subjectName)
                print(pathOut)
                print(nameOut)
                print(fileNameOut)
                print(type(EEG))
                if('set' in saveformat):
                    EEG.save(fileNameOut,overwrite =True)
                    
                elif('mat' in saveformat):
                    #TODO find a way to save all var like matlab's function save
                    None
                
            
    if(doeegall):
        #TODO find a way to save all var like matlab's function save
        None