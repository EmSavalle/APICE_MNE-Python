from importPy import *
            
def eega_getoptions(P,varargin):
    """
    Find if varargin has inputs unrelated and return them
    Also definie parameters in P based on related inputs
    
    Input :
        P: Class with parameters
        varargin: ['func',funcval,'func2',funcval2,...]
        
    Output : 
        P with parameters definer
        OK : False if unrelated inputs present
        extrainput : Unrelateds inputs ['func',funcval,'func2',funcval2,...]
    
    """
    fieldsP = [] #Name attributes of P
    members = inspect.getmembers(P, lambda a:not(inspect.isroutine(a)))
    for ind,val in members:
        if(ind == '__dict__'):
            for i in val:
                fieldsP.append(i)
                
    extraInputs = []
    i = 0
    while(i<len(varargin)):
        field = varargin[i]
        value = varargin[i+1]
        extra = True
        for f in fieldsP:
            if(f.lower() == field.lower()):
                extra = False
                setattr(P,f,value)
        if(extra):
            extraInputs.append(field)
            extraInputs.append(value)
        i+=2
    OK = extraInputs == []
    if(not OK):
        print("eega_getoptions : Extra Inputs")
        print(extraInputs)
    return P,OK,extraInputs