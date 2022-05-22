from importPy import *

def eega_tArtifacts(EEG,args):
    """
    Function that identifies motion artifacts. by appling different
    algorithms.
    The steps to be applied for the identification are indicated in the 
    structure Art
    Input : 
        EEG : Mne Raw struct
        Art : Structure with algorithms to apply
        Args : TODO remplir
    """
    #Inputs
    Art = args[0]
    Art = Art.Art
    varargin = args[1:]
    
    #Possible steps to detect artifacts
    StepsDetect = ['eega_tRejPwr','eega_tRejCorrCh','eega_tRejTimeVar',
                  'eega_tRejAmp','eega_tRejRunningAvg','eega_tRejFastChange',
                  'eega_tRejDerivate','eega_tRejAmpElecVar']
    
    #Possible steps that are applid always at the end of each loop
    StepsPostDetect = ['eega_tRejChPercSmpl','eega_tRejSmplPercCh',
                      'eega_tIncShortBad','eega_tRejShortGood','eega_tMask']
    
    #----------------------------------------------------------------------
    ##Parameters
    #Default params

    cnf = Cnf()
    cnf.FilterLp = []
    cnf.FilterHp = []
    cnf.KeepRejPre = 1
    cnf.KeepRejCause = 0
    cnf.MaxLoop = []
    cnf.RejTolerance = 0
    cnf.Lim2RejSbj = 1
    
    #get extra_inputs
    cnf,OK,extrainput = eega_getoptions(cnf,varargin)
    if(not OK):
        raise ValueError("eega_tArtifacts : Non recognized inputs")
        
    Steps = []
    ArtLoops = []

    for i in range(len(Art)):
        if(hasattr(Art[i],'algorithm') and Art[i].algorithm != []):
            Steps.append(Art[i].algorithm)
        else:
            raise ValueError('eega_tArtifacts: Field ".algorithm" is missing for step '+str(i))
        if(hasattr(Art[i],'loops')):
            if(type(Art[i].loops) == list):
                print(Art[i])
                print(Art[i].algorithm)
                print(Art[i].loops)
                ArtLoops.append(Art[i].loops[0])
            else:
                ArtLoops.append(Art[i].loops)
        else:
            raise ValueError('eega_tArtifacts: Field ".loops" is missing for step '+str(i))
        if(not hasattr(Art[i],'P')):
            raise ValueError('eega_tArtifacts: Field ".P" is missing for step '+str(i))
    
    # Determine the maximum number of loops
    if (cnf.MaxLoop == []):
        cnf.MaxLoop = max(ArtLoops)
    print(cnf.MaxLoop)
    cnf.FilterDo = (cnf.FilterLp != []) or (cnf.FilterHp != [])
    
    #------------------------------------------------------------------------
    # Show the info regarding the parameters
    shape = EEG._data.shape
    nEp,nEl,nS = (0,0,0)
    if(len(shape)> 2):
        nEp,nEl,nS = shape
    else:
        nEl,nS = shape
        nEp = 1
    
    nsmpl = nEl*nS*nEp
    nSteps = len(Art)
    print('\n')
    print('### MOTION ARTIFACT REJECTION ALGORITHMS ###\n')
    print('\n')
    print('%d electrodes, %d samples, %d epoch\n'%(nEl, nS,nEp))
    print('Initial number of samples: %d\n'%(nEl*nS))
    print('\n')
    if cnf.KeepRejCause==0:
        print('- The rejection cause will not be saved \n')
    else:
        print('- The rejection cause will be saved \n')
    if cnf.KeepRejPre==0:
        print('- BCT will be reset \n')
    else:
        print('- The previous BCT will be kept \n')
    if cnf.FilterLp!= []:
        print('- Data will be low-pass filtered before detection: %5.2f Hz\n'%cnf.FilterLp)
    if cnf.FilterHp != []:
        print('- Data will be low-pass filtered before detection: %5.2f Hz\n'%cnf.FilterHp)
    print('- The rejection algorithms will be applied: \n')
    print('   --> a maximun of %d times \n'% cnf.MaxLoop)
    print('   --> or till the new rejected data is less than '+str(cnf.RejTolerance)+"%")
    print('\n')
    
    #------------------------------------------------------------------
    # Get already rejected data if the rejection structure already exist
    if(not hasattr(EEG,'artifacts')):
        print("eega_tArtifacts : Set BCT")
        EEG.artifacts = Artifacts()
        if(not hasattr(EEG.artifacts,'algorithm')):
            EEG.artifacts.algorithm = Algorithm()
        EEG.artifacts.algorithm.parameters = []
        EEG.artifacts.algorithm.stepname = []
        EEG.artifacts.algorithm.rejxstep = []
        EEG.artifacts.BCT = [[[False for i in range(nS)] for i in range(nEl)] for i in range(nEp)]
        EEG.artifacts.BC = [[False for i in range(nEl)] for i in range(nEp)]
        EEG.artifacts.BCmanual = []
        EEG.artifacts.BT =  [[False for i in range(nS)] for i in range(nEp)]
        EEG.artifacts.BE = [False for i in range(nEp)]
        EEG.artifacts.BS = [False]
    if(cnf.KeepRejPre == 0):
        if(not hasattr(EEG,'artifacts')):
            EEG.artifacts = Artifacts()
        if(not hasattr(EEG.artifacts,'algorithm')):
            EEG.artifacts.algorithm = Algorithm()
        EEG.artifacts.algorithm.parameters = []
        EEG.artifacts.algorithm.stepname = []
        EEG.artifacts.algorithm.rejxstep = []
        EEG.artifacts.BCT = [[[False for i in range(nS)] for i in range(nEl)] for i in range(nEp)]
        EEG.artifacts.BC =  [[False for i in range(nEl)] for i in range(nEp)]
        EEG.artifacts.BT =  [[False for i in range(nS)] for i in range(nEp)]
        EEG.artifacts.BE = [False for i in range(nEp)]
        EEG.artifacts.BS = [False]
    BCT = EEG.artifacts.BCT
    BCTr = [0]*nSteps
    BCTr[0] = BCT
    
    idxpost = [False]*len(Art)
    StepsPost = []
    StepsArt = []
    for i in range(len(Art)):
        iii = Art[i].algorithm in StepsPostDetect
        if(iii):
            StepsPost.append(Steps[i])
        else:
            StepsArt.append(Steps[i])
    
    #-------------------------------------------------------------------
    ## Filter data before rejection if required
    if(cnf.FilterDo):
        dat_orig = EEG._data.copy()
        if(cnf.FilterLp != []):
            EEG = EEG.filter(None, cnf.FilterLp)
        if(cnf.FilterHp != []):
            EEG = EEG.filter(cnf.FilterHp,None)
    
    #-------------------------------------------------------------------
    ## Reject based on the different algorithms
    stepname = [0]*nSteps
    stepdone = [False]*nSteps
    parameters = [0]*nSteps
    RejxStep = [0]*nSteps
    RejxStepNew = [0]*nSteps
    ok = False
    loop = 0
    
    while not ok:
        loop = loop + 1
        print("\n******** LOOP " +str(loop)+" ********\n\n")
        BCT_pre = BCT
        #-------------------------------------------------------------------
        ## Algorithm to detect artifacts
        for i in range(len(Art)):
            do = False
            if(type(Art[i].loops) != list and Art[i].loops == loop):
                do = True
            elif(type(Art[i].loops) == list):
                if(Art[i].loops[0] == loop):
                    do = True
            if(Art[i].algorithm in StepsArt and do):
                step = sum(stepdone)#+1
                thealg = Art[i].algorithm
                fields = fieldnames(Art[i].P)
                vals = [getattr(Art[i].P,f) for f in fields]
                inputs = []
                for j in range(0,len(vals)):
                    inputs.append(fields[j])
                    inputs.append(vals[j])
                    
                print("-"*30)
                print("Rejection step "+str(step)+" : "+thealg)
                
                fhandle = eega_str2func(thealg)
                #print(fhandle)
                EEG,bct = fhandle(EEG,inputs)
                
                
                
                nsmplrej = np.sum(bct)

                bct = np.array(bct)
                nBCT = np.logical_not(np.array(BCT))
                nnewsmplrej = np.logical_and(bct,nBCT)
                nnewsmplrej = np.sum(nnewsmplrej)
                RejxStep[step] = nsmplrej
                RejxStepNew[step] = nnewsmplrej
                BCT = np.logical_or(bct,BCT)
                BCTr[step]=bct

                print("New data rejected : "+str(nnewsmplrej/nsmpl*100)+" %")

                stepdone[step] = 1
                stepname[step] = thealg
                parameters[step]= Art[i].P

        # Update rejection
        BCT = EEG.artifacts.BCT 

        #-------------------------------------------------------------------
        ## Algorithm to reject more data based on the rejected data
        for i in range(len(Art)):
            do = False
            if(type(Art[i].loops) != list and Art[i].loops == loop):
                do = True
            elif(type(Art[i].loops) == list):
                if(Art[i].loops[0] == loop):
                    do = True
            if(Art[i].algorithm in StepsPost and  do):
                step = sum(stepdone)#+1
                thealg = Art[i].algorithm
                fields = fieldnames(Art[i].P)
                vals = [getattr(Art[i].P,f) for f in fields]
                inputs = []
                for j in range(0,len(vals)):
                    inputs.append(fields[j])
                    inputs.append(vals[j])
                    
                fhandle =eega_str2func(thealg)
                #print(fhandle)
                inputs = inputs + ['updatesummary',0,'updatealgorithm',0]
                EEG,bct = fhandle(EEG,inputs)
                
                print("-"*30)
                print("Rejection step "+str(step)+" : "+thealg)
                nsmplchange = np.sum(bct)
                RejxStep[step] = nsmplchange
                RejxStepNew[step] = nsmplchange
                BCTr[step] = bct

                if thealg == 'eega_tIncShortBad':
                    print('New data re-included ' +str((nsmplchange/nsmpl)*100))
                else:
                    print('New data rejected ' +str((nsmplchange/nsmpl)*100) )

                stepdone[step] = 1
                stepname[step] = thealg
                parameters[step]= Art[i].P

        # Update rejection
        BCT = EEG.artifacts.BCT
        
        ## --------------------------------------------------------------------
        ## See if new data was rejected in this loop

        newrej = np.logical_and(BCT,np.logical_not(BCT_pre))
        newrej = np.sum(newrej)/(nEl*nS*nEp)*100

        print("-"*30)
        print('NEW DATA REJECTED LOOP %d: %8.4f %%\n'%(loop, newrej))
        print("-"*30)

        if (cnf.RejTolerance != 0) and (newrej <= cnf.RejTolerance):
            ok=1
        if loop==cnf.MaxLoop:
            ok=1
        eega_plot_artifacts(EEG,[])
    
    print("\nEnd of loops")

    ## --------------------------------------------------------------------
    ## Originial data back
    if(cnf.FilterDo):
        EEG._data = dat_orig

    ## --------------------------------------------------------------------
    ## Summary
    step_tot = sum(stepdone)
    TotSmpl = nEl*nS*nEp
    TotSmplRej = np.sum(BCT)
    TotSmplRem = TotSmpl-TotSmplRej
    ProRejxStep = np.sum(RejxStep) / TotSmpl*100
    ProRejxStepNew = np.sum(RejxStepNew) / TotSmpl*100

    print("-"*30)
    
#    for i in range(step_tot):    
#        stp = stepname[i]
#        print('  - Step %02d: %s %s  (% 5.1f %%) / New %12d (% 5.1f %%) \n'%(i, stp, RejxStep[i], ProRejxStep, RejxStepNew[i], ProRejxStepNew))
    
    print('/'*80)
    print('Rejected samples:  %010d (%2.1f %%)\n'%(TotSmplRej, TotSmplRej/TotSmpl*100))
    print('Remaining samples: %010d (%2.1f %%)\n'%(TotSmplRem, TotSmplRem/TotSmpl*100))
    print('/'*80)

    ## ========================================================================
    ## Update EEG
    #EEG.artifacts.algorithm.parameters = EEG.artifacts.algorithm.parameters+parameters
    ##EEG.artifacts.algorithm.stepname = EEG.artifacts.algorithm.stepname+stepname
    #EEG.artifacts.algorithm.rejxstep = EEG.artifacts.algorithm.rejxstep+RejxStep
    if(hasattr(None,'eega_summarypp')):
        EEG = eega_summarypp(EEG)
    
    if cnf.KeepRejCause:
        EEG.artifacts.BCTSr = BCTr
    

    return EEG