from importPy import *
def eega_demean(EEG,args):
    """
    For each channels : remove mean from data
    Input :
    EEG : Mne raw file
    """
    print("### Zero mean ###")
    data = EEG._data
    for i in range(len(data)):
        mu = np.mean(data[i])
        for j in range(len(data[i])):
            data[i][j]-=mu
    EEG._data = data
    return EEG