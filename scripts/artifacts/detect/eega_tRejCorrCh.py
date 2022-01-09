
import sys
sys.path.append("../../scripts")
sys.path.append("scripts/artifacts")
sys.path.append("scripts/general")
sys.path.append("scripts/dev")

from importPy import *
import importPy

def eega_tRejCorrCh(EEG,args):
    print("### Rejecting based on the channels correlations ###")
    #----------------------------------------------------------------------------------
    ##Parameters
    P = importPy.p()
    P.thresh = 0.4
    P.refdata = 0
    P.refbaddata = 'none' # 'replacebynan' 'none' 'zero'
    P.twdur = 4
    P.twstep = 2
    P.dozscore = 0
    P.relative = 0
    P.topcorrch = 10 #Precentage of top correlations to compoute the mean
    P.mask = 0

    P.updateBCT = 1
    P.updatesummary = 1
    P.updatealgorithm = 1
    varargin = args

    P,OK,extrainput = importPy.eega_getoptions(P,varargin)
    if(not OK):
        raise Error("eega_tRejCorrCh : Non Recognized inputs")

    # Check the inputs
    if type(P.dozscore)==list or not P.dozscore in [0,1]:
        raise Error('eega_tRejCorrCh: dozscore has to be 0 / 1')
    if P.relative not in [0,1]:
        raise Error('eega_tRejCorrCh: relative has to have values 0 / 1')
    if type(P.thresh)==list:
        raise Error('eega_tRejCorrCh: The threshold has to be a single value')

    print('- referenced data: %d\n'%P.refdata)
    print('- z-score data: %d\n'%P.dozscore)
    print('- relative threshold: %d\n'%P.relative)
    print('\n')

    shape = EEG.get_data().shape
    nEl,nS,nEp = (0,0,0)
    if(len(shape)> 2):
        nEp,nEl,nS = shape
    else:
        nEl,nS = shape
        nEp = 1
    ## ------------------------------------------------------------------------
    ## Get data and check that the artifact structure exists 
    EEG = importPy.eeg_checkart(EEG)
    
    ## ------------------------------------------------------------------------
    ## Reference data
    if P.refdata:
        EEG, reference = eega_refavg( EEG ,['BadData',P.refbaddata,'SaveRef',0])

    ## ------------------------------------------------------------------------
    ## Z-score
    if P.dozscore:
        EEG, mu, sd = eega_ZscoreForArt(EEG)

    ## ------------------------------------------------------------------------
    ## Define the time windows
    if (P.twdur != []) and not (P.twdur==math.inf) :
        twdur = round(P.twdur*EEG.info["sfreq"])
        twstep = round(P.twstep*EEG.info["sfreq"])
        ntw = round((nS-twdur+1)/twstep)+1
    else:
        ntw = 1
        twdur = nS
    if ntw<=0:
        print('The time window is too long')
        return

    i_t = list(np.linspace(0,nS-twdur, ntw))
    i_t = [round(i) for i in i_t]

    bct_tw = [[[0 for i in range(ntw)] for i in range(nEl)] for i in range(nEp)]

    for i in range(ntw):
        for ep in range(nEp):
            for el in range(nEl):
                
                v = sum(EEG.artifacts.BCT[ep][el][i_t[i]:i_t[i]+twdur]) >= 1*twdur
                bct_tw[ep][el][i] = v

    ## Compute the correlation
    CC = [[[float("NAN") for i in range(ntw)] for i in range(nEl)] for i in range(nEp)]
    CC = np.array(CC)

    for ep in range(nEp):
        for itw in range(ntw):
            #Take the data
            d = EEG.get_data()
            if(type(d[0][0]) != list):
                d=d[:,i_t[itw]:i_t[itw]+twdur]
            else:
                d=d[ep,:,i_t[itw]:i_t[itw]+twdur]
            #d=np.around(d,7)
            

            #Compute the correlation with all other channels
            corrs = np.abs(np.corrcoef(d))
    
            #Remove correclation with itself
            for x in range(corrs.shape[0]):
                corrs[x][x]=float("nan")
            ptop = np.nanpercentile(corrs, 100-P.topcorrch , interpolation='midpoint',axis=0)
            
            for i in range(0,128):
                for j in range(0,128):
                    if(corrs[i][j] <= ptop[j]):
                        corrs[i][j] = float("nan")
            avgcorrs = np.nanmean(corrs,axis=0)
            CC[ep,:,itw] = avgcorrs
            
    ## Reject bad electrodes per epoch and time window
    if (P.relative):
        CCi = CC
        for ep in range(nEp):
            for el in range(nEl):
                for itw in range(ntw):
                    if(bct[ep][el][itw]):
                        CCi[ep][el][itw] = float("nan")
        perc = np.nanpercentile(CCi[:],[25,50,75])
        IQ = perc[2]-perc[0]
        t_l = perc[0]-P.thresh*IQ
        t_l=t_l/1000
        R = CC<t_l
    else:
        t_l = P.thresh
        R = CC<t_l
    b = np.sum(R,0)
    rl_sum = np.sum(np.sum(np.sum(R,0),0),0)
    ## Print rejected data
    n = nEl*ntw*nEp
    print('Data rejected due to a low correlation : '+str(rl_sum/n*100)+"%")
    
    BCT = [[[False for i in range(nS)] for i in range(nEl)] for i in range(nEp)]

    # Go back to each sample
    cpt = 0
    for ep in range(0,nEp):
        for el in range(0,nEl):
            rl = R[ep][el]
            inds = np.array(i_t)[rl]
            for ind in inds:
                for samp in range(ind,ind+twdur):
                    cpt+=1
                    BCT[ep][el][samp] = True
    print("Data rejected :"+str(cpt))
    # Update rejection matrix
    EEG.artifacts.BCT = np.logical_or(EEG.artifacts.BCT,BCT)
    
    if( P.updatesummary and hasattr(importPy,'eega_summaryartifacts')):
        EEG.artifacts.summary = importPy.eega_summaryartifacts(EEG)
    if(P.updatealgorithm):
        EEG.artifacts.algorithm.parameters += [P]
        EEG.artifacts.algorithm.rejxstep += np.sum(np.sum(np.sum(BCT,0),0),0)
    
    # Data back
    if P.dozscore:
        EEG._data = np.dot(EEG._data,npm.repmat(sd,nEp,nS))+ npm.repmat(mu,nEp,nS)
    if P.refdata:
        #EEG._data = EEG._data + npm.repmat(reference,EEG._data.shape[0],1);
        print('eega_tRejAmp : TODO fix refdata')
    
    # Mask around
    if P.mask != [] and P.mask != 0:
        EEG,bctmask = eega_tMask(EEG,'tmast',P.mask)
        for ep in range(nEp):
                for el in range(nEl):
                    for s in range(nS):
                        BCT[ep][el][s] = BCT[ep][el][s] or bctmask[ep][el][s]
        del bctmask

    #Display rejected data
    n=nEp*nEl*nS
    print("Total data rejected "+ str(np.sum(np.sum(np.sum(BCT,0),0),0)/n*100)+"%")

    eega_plot_artifacts(EEG,BCT)
    return [EEG,BCT]