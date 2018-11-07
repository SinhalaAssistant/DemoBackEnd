# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render
import requests
from django.http import HttpResponse
from .forms import UploadFileForm
from random import randrange

# for converting the file
from pydub import AudioSegment
#for mfcc
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
from scipy.io.wavfile import read
import scipy.io.wavfile as wav
import numpy as np

#Voice to Text
import IntentClasify
import librosa
import soundfile

#for model
from keras.models import load_model
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
from scipy.io.wavfile import read
import scipy.io.wavfile as wav
import numpy as np
import librosa
import tensorflow as tf
model = 0
# Create your views here.
def home(request):
    # ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '')
    # response = requests.get('http://freegeoip.net/json/%s' % ip_address)
    # geodata = response.json()4
    print("*******************************************************************************")
    print("we got a req")
    print("*******************************************************************************")
    # return 1
    return HttpResponse("Hello World!")

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        print("post")
        form = UploadFileForm(request.POST, request.FILES)
        print (request.POST.get("type"))
        intent = handle_uploaded_file(request.FILES['file'],request.FILES['file'].name,request.POST.get("type"))
        # intent = '1'
        print("we got a file")  
        # if form.is_valid():
        #     print("valid")
        #     handle_uploaded_file(request.FILES['file'])
        #     return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})
    return HttpResponse(intent)

def handle_uploaded_file(f,n,type):
    print "in hndling upload"
    fname=n+str(randrange(0,100))+'.webm'
    # saving
    with open("audio/"+fname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        print "done saving"
    # converting
    converter(fname)
    if (type == 'nn') :
        intent = getIntent(fname)
    else :
        wavFile = "/home/ranula/Desktop/Demo/ENV/FYPDemoBackEnd/audio/wav/"+fname.split('.')[0]+".wav"
        wave, sr = librosa.load(wavFile, mono=True, sr=None)
        print(sr)
        wave16k = librosa.resample(wave, sr, 16000)
        librosa.output.write_wav(wavFile, wave16k, 16000)
        data, samplerate = soundfile.read(wavFile)
        print(samplerate)
        soundfile.write(wavFile, data, samplerate, subtype='PCM_16')
        intent = IntentClasify.getIntent(wavFile)
        # IntentClasify.main()
    
    

    print ("Intent is")
    print(intent)
    return intent

def converter(fname):
    print(fname.split('.')[0])
    sound = AudioSegment.from_file("audio/"+fname)
    sound.export("audio/wav/"+fname.split('.')[0]+".wav", format="wav")

def mfcc_gen(fname):
    np.set_printoptions(threshold=np.nan)
    (rate,sig) = wav.read("audio/wav/"+fname.split('.')[0]+".wav")
    mfcc_feat = mfcc(sig,rate,0.025,0.01,13,26,1200)
    #padding begins
    b=np.zeros((14352, 13))
    result= np.zeros(b.shape)
    result[:mfcc_feat.shape[0],:mfcc_feat.shape[1]] = mfcc_feat
    #end of padding
    mfcc_f=result.ravel()  #result.ravel() is the mfcc
    # print(mfcc_f)
    # wavs.append(mfcc_feat)
    write_mffcc(mfcc_f)

def write_mffcc(mfcc_f):
    with open("mfcc.txt", 'wb+') as destination:
        destination.write("%s " % mfcc_f)
        print "done saving mffc features as a text"
# def test(fname):
#     from scipy.io.wavfile import _read_riff_chunk
#     from os.path import getsize

#     with open(filename, 'rb') as f:
#         riff_size, _ = _read_riff_chunk(f)

#     print('RIFF size: {}'.format(riff_size))
#     print('os size:   {}'.format(getsize(filename)))

def getIntent(fname):
    global model
    if (model == 0) :
        model = load_model('model/74_86%.hd5')
        graph = tf.get_default_graph()
        maxSize= 949
        wave, sr = librosa.load("audio/wav/"+fname.split('.')[0]+".wav", mono=True, sr=None)
        trimmed, index = librosa.effects.trim(wave,top_db=40,frame_length=10, hop_length=2)
        mfcc1 = mfcc(trimmed,sr,0.025,0.01,13,26,1200)
        print(mfcc1.shape[0])
        #padding 
        if (maxSize > mfcc1.shape[0]):
            b=np.zeros((maxSize, 13))
            result= np.zeros(b.shape)
            result[:mfcc1.shape[0],:mfcc1.shape[1]] = mfcc1
            mfcc_f=result.ravel()
            global graph
            with graph.as_default():
                intent = str((model.predict_classes(np.array( [mfcc_f,] )))[0] + 1 )
                a = (model.predict_proba(np.array( [mfcc_f,] )))
                print(a)
                return intent
        else:
            return "-1"

    else:
        maxSize= 949
        wave, sr = librosa.load("audio/wav/"+fname.split('.')[0]+".wav", mono=True, sr=None)
        trimmed, index = librosa.effects.trim(wave,top_db=40,frame_length=10, hop_length=2)
        mfcc1 = mfcc(trimmed,sr,0.025,0.01,13,26,1200)
        print(mfcc1.shape[0])
        #padding 
        if (maxSize > mfcc1.shape[0]):
            b=np.zeros((maxSize, 13))
            result= np.zeros(b.shape)
            result[:mfcc1.shape[0],:mfcc1.shape[1]] = mfcc1
            mfcc_f=result.ravel()
            global graph
            with graph.as_default():
                intent = str((model.predict_classes(np.array( [mfcc_f,] )))[0] + 1 )
                a = (model.predict_proba(np.array( [mfcc_f,] )))
                print(a)
                return intent
        else:
            return "-1"


    