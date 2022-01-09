
from importPy import *
#Path 
# Folder where EEGLAB is:
Path2EEGLAB = os.path.join('C:/Users/emile/Documents/Projet CNN APICE/Matlab','eeglab2021.1');
# Folder where the function for APICE are:
Path2APICE = os.path.join('C:/Users/emile/Documents/Projet CNN APICE/Matlab','eeg_preprocessing');
# Folder where iMARA is:
Path2iMARA = os.path.join('C:/Users/emile/Documents/Projet CNN APICE/Matlab','iMARA-main');
# Current path:
Path0 = 'C:/Users/emile/Documents/Projet CNN APICE/Matlab/eeg_preprocessing-main/examples';
# Folder where the scripts defining the parameters are:
Path2Parameters = os.path.join(Path0,'parameters');
# Channels location file
filechanloc = os.path.join(Path0,'DATA','ElectrodesLayout','GSN-HydroCel-128.sfp');
# Folder where the event files are:
Path2DataEvent = os.path.join(Path0,'DATA','evt');
# Folder where the data imported to EEGLAB is: 
Path2DataSet = os.path.join(Path0,'DATA','set');
# Folder where the continuos preprocess data will be saved
Path2DataPrp = os.path.join(Path0,'DATA','prp');
# Folder where the ERPs will be saved
Path2DataERP = os.path.join(Path0,'DATA','erp');

Ppp = ParametersPreProcessing()
Ppp.Files2Read = '*.set'
Ppp.importevnt0 = 'STRT'
Ppp.eventcorrlat=EventCorrlat()
Ppp.eventcorrlat.event1 = ['Icue', 'Iout', 'Ieye'];  
Ppp.eventcorrlat.event2 = 'DIN6';    

Ppp.eventrmv = ['DIN6'];
Ppp.filt_highpass   = 0.1;

Ppp.filt_lowpass    = 40;
Ppp.ArtBadEl = example_APICE_ArtPP_BadEl(3);
Ppp.ArtJump = example_APICE_ArtPP_Jump(3);
Ppp.ArtMot1 = example_APICE_ArtPP_Mot1(3);
Ppp.ArtMot2 = example_APICE_ArtPP_Mot2(3);

Ppp.Int = example_APICE_Interpolation();
inputsInterPCA = [Ppp.Int.PCA.nSV, Ppp.Int.PCA.vSV,
    'maxTime', Ppp.Int.PCA.maxTime,'maskTime', Ppp.Int.PCA.maskTime,'splicemethod', Ppp.Int.PCA.splicemethod]

inputsInterSegmentsSpline = [Ppp.Int.Spl.p, 'pneigh', Ppp.Int.Spl.pneigh, 'splicemethod', Ppp.Int.Spl.splicemethod,
    'mingoodtime', Ppp.Int.Spl.minGoodTime, 'minintertime', Ppp.Int.Spl.minInterTime, 'masktime', Ppp.Int.Spl.maskTime]

Ppp.BCall.nbt           = [0.70, 0.50, 0.30];
Ppp.BTall.nbc           = [0.70, 0.50, 0.30];
Ppp.BTall.minGoodTime   = 1.000;
Ppp.BTall.minBadTime    = 0.100;   
Ppp.BTall.maskTime      = 0.500;        

inputsDefBTBC = [Ppp.BTall.nbc, Ppp.BCall.nbt, Ppp.BCall.nbt, 'keeppre', 0,
    'minBadTime', Ppp.BTall.minBadTime, 'minGoodTime', Ppp.BTall.minGoodTime, 'maskTime', Ppp.BTall.maskTime]
Ppp.report.patternname = 'data';  
Ppp.report.patternn = [];

FilesIn = '*.set'

FilesOut = 'prp_'

runto = 1

eega_RunAll(FilesIn,
            Path2DataSet,
            Path2DataPrp,
            ['eega_chanedit',               [filechanloc],
            'eega_importinfoevents',        [Path2DataEvent, Ppp.importevnt0],
            'eega_latencyevent',            [Ppp.eventcorrlat.event2, Ppp.eventcorrlat.event1],
            'eega_removeevent',             [Ppp.eventrmv,  [], 'all'],
            'eega_demean',                  [],
            #'octave.pop_eegfiltnew',               [[], Ppp.filt_lowpass,  [], 0, [], [], 0],
            #'octave.pop_eegfiltnew',               [Ppp.filt_highpass, [], [], 0, [], [], 0],
            #'eega_tArtifacts',              [Ppp.ArtBadEl, 'KeepRejPre', 1],
            #'eega_tArtifacts',              [Ppp.ArtMot1, 'KeepRejPre', 1],
            #'eega_tArtifacts',              [Ppp.ArtJump, 'KeepRejPre', 1],
            #'eega_tDefBTBC',                inputsDefBTBC,
            #'eega_tTargetPCAxElEEG',        inputsInterPCA,
            'eega_demean',                  [],
            #'octave.pop_eegfiltnew',               [Ppp.filt_highpass, [], [], 0, [], [], 0],
            'eega_tDefBTBC',                inputsDefBTBC,
            'eega_tInterpSpatialSegmentEEG',inputsInterSegmentsSpline,
            'eega_demean',                  [],
            #'octave.pop_eegfiltnew',               [Ppp.filt_highpass, [], [], 0, [], [], 0],
            'eega_tInterpSpatialEEG',       [Ppp.Int.Spl.p, 'pneigh', Ppp.Int.Spl.pneigh],
            #'eega_tArtifacts',              [Ppp.ArtMot2, 'KeepRejPre', 0],
            'eega_tDefBTBC',                inputsDefBTBC,
            'prename',FilesOut,'runto', runto]);
