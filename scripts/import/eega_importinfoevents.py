from importPy import *
    
class Event:
    None
def eega_importinfoevents(EEG, args):
    """
    This functions reads the event file and extract relevant info to integrate to the EEG struc

    Inputs : 
    EEG : Raw MNE data ! Must have defined EEG.fileName
    args:
        filevent : txt file with events
        event0 : event use to align timings if not same (default : first common event)
        eventtype : event type for which extra info is collected (default : all event)
        latlim : tolerance in the latency (in samples) between the latency in the event and the EEG (default : 3)

    Output : EEG
    """
    
    #Input parameters
    print(" ### Importing informations of the events ###")
    pathIn = args[0]
    if(len(args)>1):
        event0 = args[1]
        if(type(event0) != list):
            event0 = [event0]
    else:
        event0 = []
    if(len(args)>2):
        eventtype = args[2]
    else:
        eventtype = []
    if(len(args)>3):
        latlim = args[3]
    else:
        latlim = 3

    #Find event in EEG file
    events,dic = mne.events_from_annotations(EEG)
    inv_map = {v: k for k, v in dic.items()}
    EEGEvent = []
    for i in range(len(events)):
        latency,v,ind = events[i]
        EEGEvent.append(Event())
        EEGEvent[i].latency = latency
        EEGEvent[i].type = inv_map[ind]
        
    if(eventtype == []):
        ev = []
        for e in range(len(EEGEvent)):
            if(EEGEvent[e].type not in ev):
                ev.append(strip(EEGEvent[e].type))
        eventtype = ev
    elif(type(eventtype) == str):
        eventtype = [strip(eventtype)]
    eventtype = unique(eventtype)
    if(event0 != []):
        if(type(event0) == str):
            if(event0.isnumeric()):
                event0 = [EEGEvent[int(event0)].type]
            else:
                event0 = [event0]

    
    #Reading the event-file
    
    if(not hasattr(EEG,"fileName")):
        raise ValueError("eega_importinfoevents : EEG raw missing field EEG.fileName")
    fileEvent =pathIn+"/"+EEG.fileName+".evt"

    #Read event file
    fid = open(fileEvent,"r")
    L = fid.read()
    L = L.split("\n")
    for i in range(0,len(L)):
        L[i]=L[i].split("\t")

    #Find line with columns names
    idx = 0
    while(L[idx][0] != "Code" and idx < len(L)):
        idx+=1
    Ename = L[idx]
    EnameOK = [True if L[idx][i] != [] else False for i in range(len(L[idx]))]

    if(i>=len(L)):
        raise ValueError("eega_importinfoevents : No row with column names found in evt file")

    #Data with event
    Ed = L[idx+1:]

    ## Convert all time to samples for the event file
    id_time = Ename.index('Onset') #Column with time
    id_type = Ename.index('Code') #Column with Code
    for ie in range(0,len(Ed)):
        if(len(Ed[ie])> id_time):
            t_txtx = Ed[ie][id_time]
            tpos = t_txtx.find(":")
            date = t_txtx[tpos-2:]
            date = date.split(":")
            t_sec = int(date[0])*60*60+int(date[1])*60+float(date[2])
            Ed[ie][id_time]=round(t_sec*EEG.info["sfreq"])
    for row in Ed:
        if(len(row)<id_time):
            print(row)
    TIMEevt = [row[id_time] for row in Ed if row != ['']]

    TYPEevt = [row[id_type] for row in Ed]

    ## Get all timing and names of the event for the EEG structure
    TIMEeeg = []
    TYPEeeg = []
    for ie in range(0,len(EEGEvent)):
        TIMEeeg.append(EEGEvent[ie].latency)
        TYPEeeg.append(EEGEvent[ie].type)


    ## Determine the events to use for alignement
    if(event0 == []):
        event0 = [value for value in TYPEeeg if value in TYPEevt]#Choose the event in both TYPEevt ant TYPEeeg
        event0 = [unique(event0)]
        if(event0 == []):
            raise ValueError("eega_importinfoevents : Commond event were not found")

    ## Align the times to the same t0

    #find time zero event
    t0_idx_evt = []
    t0_idx_eeg = []
    for i in range(0,len(event0)):
        for j in range(0,len(EEGEvent)):
            if(strip(EEGEvent[j].type) == strip(event0[i])):
                t0_idx_eeg.append(j)

        for j in range(0,len(TYPEevt)):
            if(strip(TYPEevt[j]) == strip(event0[i])):
                t0_idx_evt.append(j)
    t0_idx_evt.sort()
    t0_idx_eeg.sort()
    # check that all the events in the text file exist in the eeg structure
    if(len(t0_idx_eeg) != len(t0_idx_evt)):
        raise ValueError("eega_importinfoevents : Missmatch in the number of t0 events")

    # check that the difference in timing is constant
    idxjumps = []
    sum_idxjumps = 0
    for i in range(0,len(t0_idx_evt)):
        if(TIMEevt[t0_idx_evt[0]]-TIMEeeg[t0_idx_eeg[0]] >latlim):
            sum_idxjumps+=1
            idxjumps.append(1)
        else:
            idxjumps.append(0)
    if(sum_idxjumps == 0):
        print('Timings are aligned, nothing will be done.')
    elif(sum_idxjumps == 1):
        for i in range(0,len(event0)):
            print('Timing will be aligned based on the first event '+str(event0[i]))
    else:
        print("Dissaliging observed at "+str(sum_idxjumps)+" points!! The data will try to be realigned")

    #Bring to zero between jumps in the timing
    idxjumps = find(idxjumps)

    if(idxjumps != []):

        evt2align = [t0_idx_evt[i] for i in idxjumps]
        eeg2align = [t0_idx_eeg[i] for i in idxjumps]

        # First alignment, apply it for all times before and after
        print('Alignment 1')
        print(' - Alignment based on event %s, event %d in the event file, latency %d \n'%(TYPEevt[evt2align[0]], evt2align[0], TIMEevt[evt2align[0]]))
        print(' - Alignment based on event %s, event %d in the EEG structure, latency %d \n' %(TYPEeeg[evt2align[0]], eeg2align[0], TIMEeeg[eeg2align[0]]))
        t0 = TIMEevt[evt2align[0]] - TIMEeeg[eeg2align[0]]

        if(t0 != 0):
            print('--> A time difference %d samples was found between the event.\n'%(t0))

            for i in range(len(TIMEevt)):
                TIMEevt[i] -=t0
            for ie in range(len(Ed)):
                if(len(Ed[ie])>id_time):
                    Ed[ie][id_time] = Ed[ie][id_time] - t0

        #Further alignement if necessary
        if(len(idxjumps) > 1):
            for ij in range(1,len(idxjumps)):
                print('Alignment '+str(ij))
                print(' - Alignment based on event %s, event %d in the event file, latency %d \n'%(TYPEevt[evt2align[ij]], evt2align[ij], TIMEevt[evt2align[ij]]))
                print(' - Alignment based on event %s, event %d in the EEG structure, latency %d \n' %(TYPEeeg[evt2align[ij]], eeg2align[ij], TIMEeeg[eeg2align[ij]]))
                t0 = TIMEevt[evt2align[ij]] - TIMEeeg[eeg2align[ij]]

                if(t0 != 0):
                    print('--> A time difference %d samples was found between the event.\n'%(t0))

                    for i in range(evt2align[ij],len(TIMEevt)):
                        TIMEevt[i] -=t0
                    for ie in range(evt2align[ij],len(Ed)):
                        Ed[ie][id_time] = Ed[ie][id_time] - t0

    ##Indentify the events to which information will be added
    idxEv = []
    for i in range(len(EEGEvent)):
        idxEv.append(strip(EEGEvent[i].type) in eventtype)
    idxEv = find(idxEv)

    idxEd = []
    for i in range(len(TYPEevt)):
        vals = [0]*len(eventtype)
        if(strip(TYPEevt[i]) in eventtype):
            vals[eventtype.index(strip(TYPEevt[i]))] = 1
        idxEd.append(vals)

    Edev = []
    for i in range(len(Ed)):
        if(1 in idxEd[i]):
            Edev.append(Ed[i])

    ## Search for extra information for each event in EEG
    count = 0
    typeev = [strip(row[0]) for row in Edev]
    latev = [row[id_time] for row in Edev]
    v_diff= []

    for i in range(len(idxEv)):
        ieeg = idxEv[i]
        latieeg = EEGEvent[ieeg].latency
        typeeeg = strip(EEGEvent[ieeg].type)

        #Find the event of the correct type
        typeOK = find([int(typeeeg == i) for i in typeev])
        if(typeOK != []):
            c = [abs(latev[i]-latieeg) for i in typeOK]
            minValue = min(c)
            idx = [i for i, x in enumerate(c) if x == minValue]
            ie = typeOK[idx[0]]
            v_diff.append(v)

            if(v <= latlim):
                #Edit the event
                j = 0
                while j < len(Ename):
                    if(Ename[j] != 'Onset' and Ename[j] != 'Duration'):
                        if(not EnameOK[j] and Edev[ie][j] == []):
                            j = j+2
                        else:
                            thefield = ""
                            if(EnameOK[j]):
                                jj = j
                                thefield = Ename[j]
                                j = j+1
                            elif(not EnameOK[j] and Edev[ie][j] != []):
                                jj=j+1
                                thefield = strip(Edev[ie][j])
                                j = j+2
                            if(not hasattr(EEGEvent[0],thefield)):
                                for iiev in range(len(EEGEvent)):
                                    setattr(EEGEvent[iiev],thefield,[])
                                if(hasattr(EEG,'epoch')):
                                    for iiep in range(len(EEG.epoch)):
                                        setattr(EEG.epoch[iiep].event,thefield,'')
                            setattr(EEGEvent[ieeg],thefield,strip(Edev[ie][jj]))
                            if(hasattr(EEG,'epoch')):
                                for iiep in range(len(EEG.epoch)):
                                    idxEpEv = EEG.epoch[iiep].event == ieeg
                                    if(idxEpEv):
                                        setattr(EEG.epoch[iiep].event,thefield,strip(Edev[ie][jj]))
                    else:
                        j = j+1
                count = count +1
            else:
                print('WARNING!!! %d samples difference for the event %s - %d - urevent %d \n no information was added \n' %(v, EEG.event(ieeg).type, ieeg, EEG.event(ieeg).urevent))
    EEG.event = EEGEvent
    print('\nNew information added to %d events \n\n'%count)
    return EEG