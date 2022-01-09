from importPy import *

class p:
    None

# -------------------------------------------------------------------------
# This function identifies segments of bad data based on the amount of
# power in different frequency bands
# It is a aplied in a slidding time windows.
# In the case of a relative threshold it is determined across all time
# windows and across all electrodes
    
# INPUTS
# EEG   EEG structure
    
# OPTIONAL INPUTS
#   - thresh        upper and lower thresholds. Size n x 2 
#                   n = number of frequncy bands
#                   first column = lower limit
#                   second column = upper limit
#                   Default [-Inf 3]
#   - refdata       referenced average the data before (1) or not (0) (default 0)
#   - refbaddata    how to teat bad data when reference average ('replacebynan' / 'none' / 'zero', default 'none')
#   - dozscore      1/0 (default 1)
#   - relative      appply relative (1) or absolute (0) thresholds (default 1)
#   - twdur         time window length in seconds (default 5s)
#   - twstep        time window step in seconds (default 2s)
#   - frqband       frequncy band. Size n x 2 (default [20 40])
#                   n = number of frequency bands 
#   - mask          time to mask bad segments (default 0)
    
# OUTPUTS
#   EEG     output data
#   BCTS  rejection matrix
#   Ti    thresholds
    
    # -------------------------------------------------------------------------
    
    
def eega_tRejPwr(EEG,varargin):

    print('### Rejecting based on the spectrum ###\n')
    ## ------------------------------------------------------------------------
    ## Parameters
    P = p()
    P.refdata = 0
    P.refbaddata ='none' #'replacebynan' / 'none' / 'zero'
    P.twdur = 4
    P.twstep = 2
    P.dozscore = 1
    P.frqband = [[1,10],[20,40]]
    P.relative = [1,1]
    P.thresh = [[- 3,math.inf],[0,3]]
    P.mask = 0

    P.updateBCT = 1
    P.updatesummary = 1
    P.updatealgorithm = 1
    
    P,OK,extrainput=eega_getoptions(P,varargin)
    if not OK:
        raise Error('eega_tRejSpectrum: Non recognized inputs')
    
    if len(P.relative) < len(P.frqband):
        n=len(P.frqband) - len(P.relative)
        P.relative=P.relative+[P.relative[-1]]*n
    
    # Check the inputs
    if type(P.dozscore) == list or (P.dozscore != 0 and P.dozscore != 1):
        raise ValueError('eega_tRejPwr: dozscore has to be 0 / 1')
    
    if any([True if(i != 0 and i != 1) else False for i in P.relative]): #Verifie si les valeures de P.relative sont bien soit 1 soit 0
        raise ValueError('eega_tRejPwr: relative has to have values 0 / 1')
    
    if len(P.thresh[0]) != 2:
        raise ValueError('eega_tRejPwr: The threshold has to be a matrix of size n x 2')
    
    if len(P.thresh) != len(P.frqband):
        raise ValueError('eega_tRejPwr: The number of raws of the threshold matrix has to be equeal to number of raws of the frequency bands matrix')
    
    if len(P.thresh) != len(P.relative):
        print('eega_tRejPwr: relative = %d for all frequency bands'%P.relative)
        P.relative =0
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

    
    print('- referenced data: %d\n'%P.refdata)
    print('- z-score data: %d\n'%P.dozscore)
    print('- relative threshold: '+str(P.relative))
    print('\n')
    ## ------------------------------------------------------------------------
    ## Get data and check that the artifact structure exists
    shape = EEG.get_data().shape
    nEl,nS,nEp = (0,0,0)
    if(len(shape)> 2):
        nEp,nEl,nS = shape
    else:
        nEl,nS = shape
        nEp = 1
    
    EEG=eeg_checkart(EEG)

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

    Fs = EEG.info['sfreq']
    bct_u = np.zeros([nEp,nEl,nS,len(P.frqband)])
    bct_l = np.zeros([nEp,nEl,nS,len(P.frqband)])
    if(nEp == 1):
        for band in range(len(P.frqband)):
            fmin = P.frqband[band][0]
            fmax = P.frqband[band][1]

            #Compute the power spectrum on all data for comparison
            psd,fre = mne.time_frequency.psd_multitaper(EEG,fmin=fmin,fmax=fmax,verbose=False)
            psd = 10 * np.log10(psd) 
            perctotal = np.percentile(psd,[25,50,75])
            limmin = P.thresh[band][0]
            limmax = P.thresh[band][1]
            IQ = perctotal[2]-perctotal[0]

            #Automatic threshold detection
            t_l = perctotal[0]+limmin*IQ
            t_u = perctotal[2]+limmax*IQ
            cptb=0
            for i in i_t:
                #Compute the power spectrum on the time window
                psd,fre = mne.time_frequency.psd_multitaper(EEG,tmin=i/Fs,tmax=(i+twdur)/Fs,fmin=fmin,fmax=fmax,verbose=False)
                psd = 10 * np.log10(psd) 
                for psd_chan in range(len(psd)):
                    #If any power spectrum value pass a threshold, the time windows is detected 
                    if(any(psd[psd_chan]>t_u)):
                        for ind in range(i,i+twdur):
                            bct_u[0][psd_chan][ind][band]=1
                        cptb+=1
                    elif(any(psd[psd_chan]<t_l)):
                        for ind in range(i,i+twdur):
                            bct_l[0][psd_chan][ind][band]=1
                        cptb+=1
    else:
        raise ValueError("Power spectrum rejection must be applied on non-epoched data")

    #
    n=nEp*nEl*nS
    print("Data rejected frequency band "+str(P.frqband[0])+ " thresh l : "+ str(np.sum(bct_l[:,:,:,0])/n*100)+ " thresh u : "+ str(np.sum(bct_u[:,:,:,0])/n*100)+"%")
    print("Data rejected frequency band "+str(P.frqband[1])+ " thresh l : "+ str(np.sum(bct_l[:,:,:,1])/n*100)+ " thresh u : "+ str(np.sum(bct_u[:,:,:,1])/n*100)+"%")
    bct = np.logical_or(bct_u[:,:,:,0],bct_u[:,:,:,1])
    bct = np.logical_or(bct,bct_l[:,:,:,0])
    bct = np.logical_or(bct,bct_l[:,:,:,1])


    if( P.updatesummary and hasattr(importPy,'eega_summaryartifacts')):
        EEG.artifacts.summary = importPy.eega_summaryartifacts(EEG)
    if(P.updatealgorithm):
        EEG.artifacts.algorithm.parameters += [P]
        EEG.artifacts.algorithm.rejxstep += np.sum(np.sum(np.sum(bct,0),0),0)
    
    # Data back
    #if P.dozscore:
    #    EEG._data = np.dot(EEG._data,npm.reshape(sd,nEp,nS))+ npm.reshape(mu,nEp,nS)
    if P.refdata:
        EEG._data = EEG._data + npm.repmat(reference,size(EEG.data,1),1);
    
    # Mask around
    if P.mask != [] and P.mask != 0:
        EEG,bctmask = eega_tMask(EEG,'tmast',P.mask)
        for ep in range(nEp):
                for el in range(nEl):
                    for s in range(nS):
                        bct[ep][el][s] = bct[ep][el][s] or bctmask[ep][el][s]
        del bctmask
    EEG.artifacts.BCT = np.logical_or(EEG.artifacts.BCT,bct)
    eega_plot_artifacts(EEG,bct)
    return EEG,bct

