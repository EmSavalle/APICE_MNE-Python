from importPy import *
def eega_removeevent(EEG, args):
    """
    This functions shows the event of some types and asks which to delete
    Input : 
    EEG : MNE struct
    args:
        showevents : events to show
        exclevents : events to avoid
    """
    if(len(args)<1):
        targetEv = []
    else:
        targetEv = args[0]
    if(len(args)<2):
        exclEv = []
    else:
        exclEv = args[1]
    if(len(args)<3):
        tormv = []
    else:
        tormv = args[2]
    
    if(type(targetEv) == str):
        targetEv = [targetEv]
    if(type(exclEv) == str):
        exclEv = [exclEv]
    
    print("### Remove events ###")
    
    EEGout = EEG.copy()
    
    ne = len(EEG.event)
    
    etypes = [i.type for i in EEG.event]
    isnoev=[]
    if(exclEv != []):
        for i in range(0,len(exclEv)):
            isnoev.append([1 if(strip(etypes[ind]) == exclEv[i])else 0 for ind in range(len(etypes)) ])
    if(isnoev != []):
        v = False
        for i in isnoev:
            if(i):
                v = True
        isnoev = v
    else:
        isnoev = False
    
    iskey = [1]*ne
    if(targetEv != []):
        print(etypes)
        print(targetEv)
        iskey = [iskey]*len(targetEv)
        for i in range(len(targetEv)):
            iskey[i] = [True if(strip(etypes[ind]) == targetEv[i])else False for ind in range(len(etypes))]
    
    isev = [int(not isnoev and i) for i in iskey[0]]
    nisev = sum(isev)
    if(nisev != 0):
        typ = []
        latency = []
        urevent = []
        nievent = []
        i = 1
        for e in range(0,ne):
            if(isev[e]):
                typ.append(EEG.event[e].type)
                latency.append(EEG.event[e].latency/EEG.info['sfreq'])
                if(hasattr(EEG.event[e],'urevent')):
                    urevent.append(EEG.event(e).urevent)
                nievent.append(e)
                i=i+1
        latdiff = diff(latency)
        latdiff = [0]+latdiff
        tbl = []
        for i in range(len(typ)):
            if(hasattr(EEG.event[e],'urevent')):
                tbl.append([nievent[i],urevent[i],typ[i],latency[i],round(latdiff[i],3)])
            else:
                tbl.append([nievent[i],typ[i],latency[i],round(latdiff[i],3)])
        
    ev2delet = []
    if(type(tormv) == str and tormv == 'all'):
        ev2delet = range(0,nisev)
    elif(tormv == []):
        ev2delet = input('Which events do you want to delet? (numbers in column 1): ')
    else:
        v = True
        for i in tormv:
            if(i>nisev or i<0):
                v=False
        if(v):
            ev2delet = tormv
    
    #Remove irrelevant events
    if(ev2delet != []):
        ev2delet = [nievent[i] for i in ev2delet]
        #EEGout = pop_editeventsvals(EEG,'delete',ev2delet) TODO verifier traduction
        
        for i in range(0,len(ev2delet)):
            EEG.event.remove(EEG.event[ev2delet[len(ev2delet)-1-i]])
        print(str(len(ev2delet))+" events where deleted")
    return EEGout