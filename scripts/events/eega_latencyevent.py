from importPy import *
def correctlatency(EEG,valnum,editval):
    EEG.event[valnum].latency = editval
    # TODO fonctions beaucoup plus longue dans matlab -> voir utilité de recopier
    
    return EEG
def eega_latencyevent(EEG, args):
    """ 
    % This function corrects the latency of the events indicated in "events"
     using another event type, "eventT".
    
     Usually "eventsT" are DINs. %
     INPUTS:
    
       EEG         = MNE Raw with field : field Eeg.fileName and EEG.event from eega_importinfoevents 
       eventT      = event indicating the correct latency
       events      = cell array of strings with the events to correct
       correctEvT  = number of requiered eventT after the event. if it's not
                   provided this is not checked
    """
    print("### Correct latencies ###")
    
    eventT = args[0]
    events = args[1]
    correctEvT = []
    if(len(args)>2):
        correctEvt = args[2]
    
    nEv = len(EEG.event)
    etype = [0]*nEv
    elatency = [0]*nEv
    
    for i in range(0,nEv):
        etype[i]=strip(EEG.event[i].type)
        elatency[i]=EEG.event[i].latency
    noEvT = [i for i in range(0,len(etype))if(etype[i] != eventT)]
    
    iii = 0
    correction = []
    print(events)
    for E in events:
        isE = [i for i in range(0,len(etype))if(etype[i] == E)]
        print("############")
        if(isE != []):
            for j in range(0,len(isE)):
                
                dochange = 1
                next = [i for i in range(0,len(noEvT)) if noEvT[i] > isE[j]]
                if(next == []):
                    dinafter = [1 if(elatency[i]>elatency[isE[j]]) else 0 for i in range(0,len(elatency)) ]
                    ndinafter = sum(dinafter)
                    theEvT = find(dinafter)
                else:
                    next = noEvT[next[0]]
                    dinafter = [1 if(elatency[i]>elatency[isE[j]] and elatency[i]<elatency[next]) else 0 for i in range(0,len(elatency))]
                    ndinafter = sum(dinafter)
                    theEvT = find(dinafter)
                
                if(theEvT != []):
                    theEvT = theEvT[0]
                else:
                    dochange = 0
                
                if( correctEvT != []):
                    if(ndinafter != correctEvT[E]):
                        print("Warning : Incorrect number of "+eventT+" events found !!!")
                        print(' Number of %s events after %s: %d\n'%(eventT, E, sum(dinafter)))
                
                #Change
                if (dochange):
                    iii = iii + 1
                    print('Correcting the latency of event %s by %s - event %d - change %d...\n'%(E, eventT, isE[j], iii))
                    
                    correction.append(EEG.event[theEvT].latency - EEG.event[isE[j]].latency)
                    
                    #The event
                    EEG = correctlatency(EEG,isE[j],EEG.event[theEvT].latency)
    correction = [i/EEG.info['sfreq']*1000 for i in correction];
    print('The latency of %d events was corrected\n'%iii)
    print('- Mean delay %f ms\n'%(sum(correction)/len(correction)))
    print('- SD of the delay %f ms\n'%np.std(correction))
    print('- min of the delay %f ms\n'%min(correction))
    print('- max of the delay %f ms\n'%max(correction))
    return EEG