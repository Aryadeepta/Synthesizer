import math
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq, ifft
from scipy.io import wavfile
import tkinter
BITRATE=16000
def playAudio(wave):
    PyAudio = pyaudio.PyAudio
    p = PyAudio()
    stream = p.open(format = p.get_format_from_width(1), 
                    channels = 1, 
                    rate = BITRATE, 
                    output = True)
    chunk=2048
    vals=[''.join([chr(max(min(int(wave[0]((i+j)/BITRATE).real*128+128),10000),0)) for j in range(chunk)]) for i in range(0,int(wave[1]*BITRATE),chunk)]
    for i in vals:
        stream.write(i)
    stream.stop_stream()
    stream.close()
    p.terminate()
def static(mu, length):
    return ((lambda t:mu if 0<=t<length else 0),length)
def invert(wave):
    return((lambda t:-wave[0](t)),wave[1])
def sub(wave1, wave2):
    return add(wave1, invert(wave2))
def add(wave1, wave2):
    return ((lambda t:wave1[0](t)+wave2[0](t)),max(wave1[1],wave2[1]))
def append(wave1, wave2):
    return ((lambda t:wave1[0](t) if t<wave1[1] else wave2[0](t-wave1[1])),wave1[1]+wave2[1])
def Avg(wave):
    return sum([wave[0](t) for t in range(int(wave[1]*BITRATE))])/int(wave[1]*BITRATE)
def Amp(wave):
    avg=Avg(wave)
    return (sum([(wave[0](i)-avg)**2 for i in range(int(wave[1]*BITRATE))])/int(wave[1]*BITRATE))**.5
def normalize(wave,mu=0,amp=None,bitrate=BITRATE):
    avg=Avg(wave)
    std=Amp(wave)
    return ((lambda t:mu+(wave[0](t)-avg)*(amp/std if amp!=None else 1)),wave[1])
def volumeMultiplier(wave, m):
    return ((lambda t:wave[0](t)*m),wave[1])
def interpolatedIndexing(ar,ind):
    if ind>=len(ar) or ind<0:
        return 0
    if int(ind)+1>=len(ar):
        return ar[-1]
    return ar[int(ind)]+(ind%1)*(ar[int(ind)+1]-ar[int(ind)])
def echo(wave,offset,decay):
    return ((lambda t: wave[0](t)+decay*wave[0](t-offset)),wave[1]+offset)
def fourier(wave,plot=False):
    sample=np.array([wave[0](i/BITRATE) for i in range(int(wave[1]*BITRATE))])
    if plot:
        plt.plot(fftfreq(int(wave[1]*BITRATE),1/BITRATE),fft(sample))
        plt.show()
    return fft(sample)
def ifourier(f,length):
    return ifft(f,int(length*BITRATE))
def Wave(d):
    return ((lambda t:d[int(t*BITRATE)] if 0<=t*BITRATE<len(d) else 0),len(d)/BITRATE)
def pitchFilter(wave,Filter, ampMultiplier=1):
    return(normalize(Wave(ifourier(Filter(fourier(wave)),wave[1])),amp=Amp(wave)))
def idealLowPassFilter(freq):
    return lambda t:[t[i] if i<freq*len(t)/BITRATE or i>len(t)-freq*len(t)/BITRATE else 0 for i in range(len(t))]
def idealHighPassFilter(freq):
    return lambda t:[t[i] if freq*len(t)/BITRATE<i<len(t)-freq*len(t)/BITRATE else 0 for i in range(len(t))]
def idealBandPassFilter(low, high):
    return lambda t:idealHighPassFilter(low)(idealLowPassFilter(high)(t))
def pitchMultiplier(m):
    return lambda t:[interpolatedIndexing(t,(i if i*2<len(t) else len(t)-i)/m if (i if i*2<len(t) else len(t)-i)/m<len(t)/2 else (len(t)-i if (len(t)-i)*2<len(t) else i)/m) for i in range(len(t))]
def slice(wave,t1,t2):
    if t1>t2:
        a=t1
        t1=t2
        t2=t1
    return ((lambda t:wave[0](t) if t<t1 else 0),t1),((lambda t:wave[0](t) if t1<=t<t2 else 0),t2-t1),((lambda t:wave[0](t) if t2<=t else 0),max(wave[1]-t2,0))
def loop(wave,times=2):
    return ((lambda t:wave[0](t%wave[1]) if t<wave[1]*times else 0),wave[1]*times)
def plot(wave):
    plt.plot([i/BITRATE for i in range(int(wave[1]*BITRATE))],[wave[0](i/BITRATE) for i in range(int(wave[1]*BITRATE))])
    plt.show()
def beat(freq,length,beatlength=1):
    return ((lambda t:max(beatlength/2-abs(t*freq%1-beatlength/2),0)/beatlength if 0<=t<length else 0),length)
def sinWave(freq, length):
    return ((lambda t:math.sin(t*freq*(2*math.pi)) if 0<=t<length else 0),length)
def sawWave(freq, length):
    return ((lambda t:-1+2*((t*freq)%1) if 0<=t<length else 0),length)
def squareWave(freq, length):
    return ((lambda t:-1+2*int((t*freq)%1>.5) if 0<=t<length else 0),length)
def linearInterpolation(x1,y1,x2,y2):
    return (lambda t:(t-x1)/(x2-x1)*(y2-y1)+y1) if x1!=x2 else (lambda t:y2)
def logarithmicInterpolation(x1,x2,y1,y2):
    y1,y2=max(.0001,y1),max(.0001,y2)
    return (lambda t:((y2/y1)**((t-x1)/(x2-x1)))*y1) if x1!=x2 else (lambda t:y2)
def ADSR(a,d,s,r,interpolate=linearInterpolation):
    return lambda wave:(lambda t:((interpolate(0,0,a,1)(t) if t<a else interpolate(a,1,a+d,s)(t)) if t<a+d else (interpolate(wave[1]-r,s,wave[1],0)(t) if t+r>=wave[1] else s))*wave[0](t),wave[1])
NOTES=['C','C# Db','D','D# Eb','E','F','F# Gb','G','G# Ab','A','A# Bb','B']
def note2freq(note):
    note=note.upper()
    octave=4
    i=-1
    while note[i] in '1234567890':
        i-=1
    i+=1
    if i!=0:
        octave=int(note[i:])
        note=note[:i]
    if note=='R':
        return 1/BITRATE
    for i in range(len(NOTES)):
        if note in NOTES[i].split():
            return 440*(2**((i-9)/12+(octave-4)))
    return .000001/BITRATE
def noteStream(notes,instrument=sinWave,envelope=ADSR(0.1,0.05,.8,0.1),bpm=60):
    audio=static(0,0)
    for c in notes:
        current=static(0,0)
        for n in c[0].split():
            current=add(current,envelope(instrument(note2freq(n), c[1]*60/bpm)))
    audio=append(audio,current)
    return audio
def song(notes, instrument=sinWave,envelope=ADSR(0.05,0.05,.8,0.05),bpm=60):
    audio=static(0,0)
    for c in notes:
        for n in c[1].split():
            audio=add(audio,append(static(0,c[0]*60/bpm),envelope(instrument(note2freq(n), c[2]*60/bpm))))
    return audio
def download(wave,file):
    wavfile.write(file,BITRATE,np.array([wave[0](i/BITRATE) for i in range(int(BITRATE*wave[1]))]).astype(np.float32))
def intinput(n,q=False,yn=False):
    option=None
    while option==None:
        option=input()
        if option in [str(i+1) for i in range(n)]:
            option=int(option)
        else:
            if q and option.lower()=='q':
                option=n
            elif yn and option.lower()=='y':
                option=1
            elif yn and option.lower()=='y':
                option=2
            else:
                print("Sorry, please enter one of the options above")
    return option
def floatInput(prompt='',nn=True):
    inp=None
    while inp==None:
        inp=input(prompt)
        try:
            inp=float(inp)
            if nn and inp<0:
                print('must be nonnegative')
                inp=None
        except ValueError:
            print('invalid float')
            inp=None
    return inp
def menu(options,title=None,q=False,yn=False):
    if title:
        print(title)
    if yn:
        print('[Y] {}'.format(options[0]))
        print('[N] {}'.format(options[1]))
        if q:
            print('[Q] Quit')
        return intinput(2+q,q=q,yn=True)
    for i in range(len(options)):
        print("[{}] {}".format(i+1,options[i]))
    if q:
        print('[{}] Quit'.format(len(options)+1))
    return intinput(len(options)+q,q=q)    
if __name__=="__main__":
    stream=[('C',.5),('C',.5),('G',.5),('G',.5),('A',.5),('A',.5),('G',1),('F',.5),('F',.5),('E',.5),('E',.5),('D',.5),('D',.5),('C',1),('G',.5),('G',.5),('F',.5),('F',.5),('E',.5),('E',.5),('D',1),('G',.5),('G',.5),('F',.5),('F',.5),('E',.5),('E',.5),('D',1),('C',.5),('C',.5),('G',.5),('G',.5),('A',.5),('A',.5),('G',1),('F',.5),('F',.5),('E',.5),('E',.5),('D',.5),('D',.5),('C',1)]
    right=[(0,'C5 E5 A6',.5),(.5,'C5 E5 A6',.5),(1,'C5 E5 A6',.5),(1.5,'C5 E5 A6',.5),(2,'C5 E5 A6',.5),(2.5,'C5 E5 A6',.5),(3,'C5 E5 A6',.5),(3.5,'C5 E5 A6',.5),(4,'B5 E5 A6',.5),(4.5,'B5 E5 A6',.5),(5,'B5 E5 A6',.5),(5.5,'B5 E5 G5',.5),(6,'B5 E5 G5',.5),(6.5,'B5 E5 G5',.5),(7,'B5 E5 G5',.5),(7.5,'B5 E5 G5',.5)]
    left=[(0,'A3 A4',1.5),(3, 'B3 B4', 1),(4,'E2 E3',1.5),(7,'E2 E3',1)]
    twinkle=noteStream(stream)
    dre=add(song(right,bpm=100, instrument=sawWave, envelope=ADSR(0.02,0.1,.4,0.1)),volumeMultiplier(song(left,bpm=100, instrument=squareWave, envelope=ADSR(0.05,0.01,.7,0.2)),.25))
    names=["demo1","demo2"]
    audios=[twinkle,dre]
    options=["Play audio","Import note stream","Import song","Modify samples","Delete audio","Download audio"]
    instrumentNames=['Sine Wave','Sawtooth Wave','Square Wave']
    instruments=[sinWave,sawWave,squareWave]
    audioOptions=['copy','invert','sub','add','append','normalize','volume multiplier','echo','pitch effects','slice','loop','plot']
    nq=True
    while nq:
        match menu(options,"~~~Menu~~~",q=True):
            case 1:
                op = menu(names,"Pick an audio",q=True)-1
                if op<len(audios):
                    print("Playing {}".format(names[op]))
                    playAudio(audios[op])
            case 2:
                print("Please enter each chord as space-separated notes (R for rest), followed by the length of the chord")
                print("Enter Q to finish")
                notes=[]
                c='___'
                while c[0]!='Q':
                    c=input().upper()
                    if c[0]=='Q':
                        break
                    c=c.split()
                    try:
                        c[-1]=float(c[-1])
                        if c[-1]<0:
                            c[-1]=float('bruh')
                        notes.append((' '.join(c[:-1]),c[-1]))
                    except ValueError:
                        print("Please enter a valid note length")
                instrument=instruments[menu(instrumentNames,'Pick an instrument')-1]
                if menu(['Custom ADSR','Basic ADSR'],'Choose an ADSR Style')==1:
                    names.append(input("Name of audio: "))
                    audios.append(noteStream(notes,instrument=instrument,bpm=floatInput("BPM: "),envelope=ADSR(floatInput('Attack: '),floatInput('Decay: '),floatInput('Sustain: '),floatInput('Release: '))))
                else:
                    names.append(input("Name of audio: "))
                    audios.append(noteStream(notes,instrument=instrument,bpm=floatInput("BPM: ")))
            case 3:
                print("Please enter each chord as the start time of the chord, followed by the space-separated notes of the chord (R for rest), followed by the length of the chord")
                print("Enter Q to finish")
                notes=[]
                c='___'
                while c[0]!='Q':
                    c=input().upper()
                    if c[0]=='Q':
                        break
                    c=c.split()
                    try:
                        c[0]=float(c[0])
                        c[-1]=float(c[-1])
                        if c[-1]<0:
                            c[-1]=float('bruh')
                        notes.append((c[0],' '.join(c[1:-1]),c[-1]))
                    except ValueError:
                        print("Please enter a valid note length")
                instrument=instruments[menu(instrumentNames,'Pick an instrument')-1]
                if menu(['Custom ADSR','Basic ADSR'],'Choose an ADSR Style')==1:
                    names.append(input("Name of audio: "))
                    audios.append(song(notes,instrument=instrument,bpm=floatInput("BPM: "),envelope=ADSR(floatInput('Attack: '),floatInput('Decay: '),floatInput('Sustain: '),floatInput('Release: '))))
                else:
                    names.append(input("Name of audio: "))
                    audios.append(song(notes,instrument=instrument,bpm=floatInput("BPM: ")))
            case 4:
                sm=menu(audioOptions,"~~~Sample Modification Sub-Menu~~~",q=True)
                match sm:
                    case 1:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            name=input('name: ')
                            na=audios[op]
                            for i in range(len(names)):
                                if name==names[i]:
                                    audios[i]=na
                                    break
                            else:
                                names.append(name)
                                audios.append(na)
                    case 2:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            name=input('name: ')
                            na=invert(audios[op])
                            for i in range(len(names)):
                                if name==names[i]:
                                    audios[i]=na
                                    break
                            else:
                                names.append(name)
                                audios.append(na)
                    case 3:
                        op1=menu(names,"Pick first sample",q=True)-1
                        if op1==len(audios):
                            op2=menu(names,"Pick second sample",q=True)-1
                            if op2<len(audios):
                                name=input('name: ')
                                na=sub(audios[op1],audios[op2])
                                for i in range(len(names)):
                                    if name==names[i]:
                                        audios[i]=na
                                        break
                                else:
                                    names.append(name)
                                    audios.append(na)
                    case 4:
                        op1=menu(names,"Pick first sample",q=True)-1
                        if op1==len(audios):
                            op2=menu(names,"Pick second sample",q=True)-1
                            if op2<len(audios):
                                name=input('name: ')
                                na=add(audios[op1],audios[op2])
                                for i in range(len(names)):
                                    if name==names[i]:
                                        audios[i]=na
                                        break
                                else:
                                    names.append(name)
                                    audios.append(na)
                    case 5:
                        op1=menu(names,"Pick first sample",q=True)-1
                        if op1==len(audios):
                            op2=menu(names,"Pick second sample",q=True)-1
                            if op2<len(audios):
                                name=input('name: ')
                                na=append(audios[op1],audios[op2])
                                for i in range(len(names)):
                                    if name==names[i]:
                                        audios[i]=na
                                        break
                                else:
                                    names.append(name)
                                    audios.append(na)
                    case 6:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            name=input('name: ')
                            na=normalize(audios[op])
                            for i in range(len(names)):
                                if name==names[i]:
                                    audios[i]=na
                                    break
                            else:
                                names.append(name)
                                audios.append(na)
                    case 7:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            name=input('name: ')
                            na=volumeMultiplier(audios[op],floatInput('volume: '))
                            for i in range(len(names)):
                                if name==names[i]:
                                    audios[i]=na
                                    break
                            else:
                                names.append(name)
                                audios.append(na)
                    case 8:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            name=input('name: ')
                            na=echo(audios[op],floatInput('offset: '),floatInput('decay: '))
                            for i in range(len(names)):
                                if name==names[i]:
                                    audios[i]=na
                                    break
                            else:
                                names.append(name)
                                audios.append(na)
                    case 9:
                        pitchOptions=["Low Pass Filter","High Pass Filter","Band Pass Filter","Pitch Multiplier"]
                        match menu(pitchOptions,"~~~Pitch Sub-Menu~~~",q=True):
                            case 1:
                                op=menu(names,"Pick a sample",q=True)-1
                                if op<len(audios):
                                    name=input('name: ')
                                    na=pitchFilter(audios[op],idealLowPassFilter(floatInput('low: ')))
                                    for i in range(len(names)):
                                        if name==names[i]:
                                            audios[i]=na
                                            break
                                    else:
                                        names.append(name)
                                        audios.append(na)
                            case 2:
                                op=menu(names,"Pick a sample",q=True)-1
                                if op<len(audios):
                                    name=input('name: ')
                                    na=pitchFilter(audios[op],idealHighPassFilter(floatInput('high: ')))
                                    for i in range(len(names)):
                                        if name==names[i]:
                                            audios[i]=na
                                            break
                                    else:
                                        names.append(name)
                                        audios.append(na)
                            case 3:
                                op=menu(names,"Pick a sample",q=True)-1
                                if op<len(audios):
                                    name=input('name: ')
                                    na=pitchFilter(audios[op],idealBandPassFilter(floatInput('low: '),floatInput('high: ')))
                                    for i in range(len(names)):
                                        if name==names[i]:
                                            audios[i]=na
                                            break
                                    else:
                                        names.append(name)
                                        audios.append(na)
                            case 4:
                                op=menu(names,"Pick a sample",q=True)-1
                                if op<len(audios):
                                    name=input('name: ')
                                    na=pitchFilter(audios[op],pitchMultiplier(floatInput('multiplier: ')))
                                    for i in range(len(names)):
                                        if name==names[i]:
                                            audios[i]=na
                                            break
                                    else:
                                        names.append(name)
                                        audios.append(na)
                    case 10:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            nas=volumeMultiplier(audios[op],floatInput('time 1: '),floatInput('time 2: '))
                            for j in range(3):
                                na=nas[i]
                                name=input('name for slice {}: '.format(j+1))
                                for i in range(len(names)):
                                    if name==names[i]:
                                        audios[i]=na
                                        break
                                else:
                                    names.append(name)
                                    audios.append(na)
                    case 11:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            name=input('name: ')
                            na=loop(audios[op],floatInput('loops: '))
                            for i in range(len(names)):
                                if name==names[i]:
                                    audios[i]=na
                                    break
                            else:
                                names.append(name)
                                audios.append(na)
                    case 12:
                        op=menu(names,"Pick a sample",q=True)-1
                        if op<len(audios):
                            plot(audios[op])
            case 5:
                op = menu(names,"Pick an audio",q=True)-1
                if op<len(audios):
                    print("Deleting {}".format(names[op]))
                    del audios[op]
                    del names[op]
            case 6:
                op = menu(names,"Pick an audio",q=True)-1
                name = input('filename: ')
                if op<len(audios):
                    print("Downloading {} as {}".format(names[op],name))
                    download(audios[op],name)
            case _:
                nq=False
                break
        print("Thank you for using my synthesizer!")
