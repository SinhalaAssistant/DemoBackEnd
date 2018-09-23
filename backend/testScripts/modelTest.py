from keras.models import load_model

model = load_model('71_%.hd5')
# for generating mfcc
    #for mfcc
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
from scipy.io.wavfile import read
import scipy.io.wavfile as wav
import numpy as np
import librosa
maxSize= 949

wave, sr = librosa.load("test.wav", mono=True, sr=None)
trimmed, index = librosa.effects.trim(wave,top_db=40,frame_length=10, hop_length=2)
mfcc1 = mfcc(trimmed,sr,0.025,0.01,13,26,1200)
#padding 
if (maxSize > mfcc1.shape[0]):
    b=np.zeros((maxSize, 13))
    result= np.zeros(b.shape)
    result[:mfcc1.shape[0],:mfcc1.shape[1]] = mfcc1
    mfcc_f=result.ravel()
    print(mfcc_f.shape)
    model.predict_classes(mfcc_f)

#end of padding
