from cmu_112_modified_graphics import *
import pyaudio
from pydub import *
from pydub.pyaudioop import *
from pydub.utils import *
import wave
import threading
import numpy as np
from song import Song
import math
import copy

# the bulk of my term project, where the magic happens!
# audio in songFiles is original audio produced by me :)

#######################################################################
#####                       cmu 112 functions                     #####
#######################################################################

def appStarted(app):
    # import button
    app.ix = 75
    app.iy = 50
    app.ir = 30

    # export button
    app.ex = 175
    app.ey = 50
    app.er = 30

    # new track button
    app.tx = 275
    app.ty = 50
    app.tr = 20

    # play button
    app.px = 45
    app.py = app.height - 295
    app.pr = 13

    # record button
    app.rx = 80
    app.ry = app.height - 295
    app.rr = 13

    # stop button
    app.sx = 115
    app.sy = app.height - 295
    app.sr = 13

    #selector 
    app.sx0 = 150
    app.sy0 = 100
    app.sx1 = 150
    app.sy1 = app.height

    # control 
    app.isStopped = False
    app.ohno = False
    app.recording = False
    app.threads = []
    app.streams = []

    # song control
    app.waveStart = 0
    app.counter = 0
    app.startTime = 0
    app.sampleRate = 44100
    app.songs = []
    app.solos = []

    # track interface
    app.names = ["New Track 0"]
    app.rows = [1]
    app.cols = [14]
    app.marginCol = 150
    app.marginRow = 100
    app.soloColor = ['grey']
    app.fxColor = ['grey']
    app.trackStart = 0
    app.trackUserInput = [False]
    app.trackUI = False

    # volume balancer
    app.volcx = [0, 0]
    app.volcy = [0, 0]
    app.volcrx = [0, 0]
    app.volcry = [0, 0]
    app.volAttenuate = [None, None]
    app.vol = [0.0, 0.0]
    app.oldVol = [0.0 , 0.0]

    # screens
    app.fxSplashScreen = [False]
    app.compressorScreen = [False]
    app.highPassScreen = [False]
    app.lowPassScreen = [False]
    app.bandPassScreen = [False]

    # compressor
    app.threshcx = [app.width/2-245]
    app.threshcy = [app.height/2-40]
    app.threshcrx = [10]
    app.threshcry = [15]
    app.thresh = [-20.0]

    app.ratiocx = [app.width/2+80]
    app.ratiocy = [app.height/2-145]
    app.ratiocrx = [4]
    app.ratiocry = [7]
    app.ratio = [4]

    app.attackcx = [744]
    app.attackcy = [app.height/2-105]
    app.attackcrx = [4]
    app.attackcry = [7]
    app.attack = [5]

    app.delaycx = [789]
    app.delaycy = [app.height/2-65]
    app.delaycrx = [4]
    app.delaycry = [7]
    app.delay = [100]

    # low pass
    app.lowSeg1x0 = [app.width/2-150]
    app.lowSeg1y0 = [app.height/2-75]
    app.lowSeg1x1 = [750] 
    app.lowSeg1y1 = [app.height/2-75]

    app.lowSeg2x0 = [750]
    app.lowSeg2y0 = [app.height/2-75]
    app.lowSeg2x1 = [app.width/2+150] 
    app.lowSeg2y1 = [app.height/2+75]

    app.lowPassCutoff = [10000]

    # high pass
    app.highSeg1x0 = [app.width/2-150]
    app.highSeg1y0 = [app.height/2+75]
    app.highSeg1x1 = [560] 
    app.highSeg1y1 = [app.height/2-75]

    app.highSeg2x0 = [560]
    app.highSeg2y0 = [app.height/2-75]
    app.highSeg2x1 = [app.width/2+150] 
    app.highSeg2y1 = [app.height/2-75]

    app.highPassCutoff = [200]

    # band pass
    app.bandSeg1x0 = [app.width/2-150]
    app.bandSeg1y0 = [app.height/2+75]
    app.bandSeg1x1 = [555] 
    app.bandSeg1y1 = [app.height/2-75]

    app.bandSeg2x0 = [555]
    app.bandSeg2y0 = [app.height/2-75]
    app.bandSeg2x1 = [800] 
    app.bandSeg2y1 = [app.height/2-75]

    app.bandSeg3x0 = [800]
    app.bandSeg3y0 = [app.height/2-75]
    app.bandSeg3x1 = [app.width/2+150] 
    app.bandSeg3y1 = [app.height/2+75]

    app.bandPassLowCutoff = [200]
    app.bandPassHighCutoff = [10000]

def appStopped(app):
    # kills running threads
    for i in range(len(app.threads)):
        app.threads[i].join()

def keyPressed(app, event):
    # track user input
    for i in range(len(app.trackUserInput)):
        if app.trackUserInput[i]:
            app.trackUI = True
            if event.key == 'Space':
                app.names[i] += ' '
            elif event.key == 'Backspace':
                app.names[i] = app.names[i][:len(app.names[i])-1]
            elif event.key != 'Enter':
                app.names[i] += event.key
            else:
                app.trackUserInput[i] = False
                app.trackUI = False

    if not app.trackUI:
        # move through tracks
        if event.key == 'Down' and app.trackStart < len(app.names)-5:
            app.trackStart += 1
        
        elif event.key == 'Up' and app.trackStart > 0:
            app.trackStart -= 1
        
        # move through time
        elif event.key == 'Right':
            app.counter += 50
            app.waveStart += 50
            app.startTime += 1/2
            
        elif event.key == 'Left' and app.startTime > 0:
            app.counter -= 50
            app.waveStart -= 50
            app.startTime -= 1/2

def mousePressed(app, event):
    fx = False
    comp = False
    high = False
    low = False
    band = False
    init = None

    # checks if we are in a splash screen
    for i in range(len(app.fxSplashScreen)):
        if app.fxSplashScreen[i]:
            fx = True
            init = i
            break
        elif app.compressorScreen[i]:
            comp = True
            init = i
            break
        elif app.highPassScreen[i]:
            high = True
            init = i
            break
        elif app.lowPassScreen[i]:
            low = True
            init = i
            break
        elif app.bandPassScreen[i]:
            band = True
            init = i
            break
    
    if fx:
        # comp screen
        if (app.width/2-100 < event.x < app.width/2+100 and 
            app.height/2-150 < event.y < app.height/2-100):
            app.compressorScreen[init] = True
            app.fxSplashScreen[init] = False

        # low pass screen
        elif (app.width/2-100 < event.x < app.width/2+100 and
            app.height/2-50 < event.y < app.height/2):
            app.lowPassScreen[init] = True
            app.fxSplashScreen[init] = False

        # high pass screen
        elif (app.width/2-100 < event.x < app.width/2+100 and
            app.height/2+50 < event.y < app.height/2+100):
            app.highPassScreen[init] = True
            app.fxSplashScreen[init] = False

        # band pass screen
        elif (app.width/2-100 < event.x < app.width/2+100 and
            app.height/2+150 < event.y < app.height/2+200):
            app.bandPassScreen[init] = True
            app.fxSplashScreen[init] = False

    elif comp:
        if (app.width/2+25 <= event.x <= app.width/2+85 and
            app.height/2+100 <= event.y <= app.height/2+160):
                app.compressorScreen[init] = False
                song = app.songs[init]
                song.threshold = app.thresh[init]
                song.ratio = app.ratio[init]
                song.attack = app.attack[init]
                song.delay = app.delay[init]
                t2 = threading.Thread(target=compressorInterface, args=(app, song))
                t2.start()
                app.threads.append(t2)
        elif (app.width/2+105 <= event.x <= app.width/2+165 and 
            app.height/2+100 <= event.y <= app.height/2+160):
            app.compressorScreen[init] = False

    elif low:
        if (app.width/2+25 <= event.x <= app.width/2+85 and
            app.height/2+100 <= event.y <= app.height/2+160):
            app.lowPassScreen[init] = False
            song = app.songs[init]
            cutoff = app.lowPassCutoff[init]
            t5 = threading.Thread(target=lowPassFilterInterface, args=(app, song, cutoff))
            t5.start()
            app.threads.append(t5)
        elif (app.width/2+105 <= event.x <= app.width/2+165 and 
            app.height/2+100 <= event.y <= app.height/2+160):
            app.lowPassScreen[init] = False
        elif app.width/2-150 <= event.x <= app.width/2+150 and app.height/2-200 <= event.y <= app.height/2+200:
            app.lowSeg1x1[init] = event.x
            app.lowSeg2x0[init] = event.x
            app.lowPassCutoff[init] = 20*(event.x-550)+6000

    elif high:
        if (app.width/2+25 <= event.x <= app.width/2+85 and
            app.height/2+100 <= event.y <= app.height/2+160):
            app.highPassScreen[init] = False
            song = app.songs[init]
            cutoff = app.highPassCutoff[init]
            t6 = threading.Thread(target=highPassFilterInterface, args=(app, song, cutoff))
            t6.start()
            app.threads.append(t6)
        elif (app.width/2+105 <= event.x <= app.width/2+165 and 
            app.height/2+100 <= event.y <= app.height/2+160):
            app.highPassScreen[init] = False
        elif app.width/2-150 <= event.x <= app.width/2+150 and app.height/2-200 <= event.y <= app.height/2+200:
            app.highSeg1x1[init] = event.x
            app.highSeg2x0[init] = event.x
            app.highPassCutoff[init] = 20*(event.x-550)

    elif band:
        if (app.width/2+25 <= event.x <= app.width/2+85 and
            app.height/2+100 <= event.y <= app.height/2+160):
            app.bandPassScreen[init] = False
            song = app.songs[init]
            lowCutoff = app.bandPassLowCutoff[init]
            highCutoff = app.bandPassHighCutoff[init]
            t7 = threading.Thread(target=bandPassFilterInterface, args=(app, song, lowCutoff, highCutoff))
            t7.start()
            app.threads.append(t7)
        elif (app.width/2+105 <= event.x <= app.width/2+165 and 
            app.height/2+100 <= event.y <= app.height/2+160):
            app.bandPassScreen[init] = False
    
    else:
        # imports songs
        if (app.ix-app.ir+10 <= event.x <= app.ix+app.ir-10 and
            app.iy-app.ir <= event.y <= app.iy+app.ir):
            if len(app.names) < len(app.songs) + 1:
                app.showMessage('Please create a new track first!')
            else:
                fileName = filedialog.askopenfilename(initialdir = "SongFiles/", 
                    title = "Select a File", filetypes = (("Wav files", "*.wav*"),))
                try:
                    if not (fileName == None or fileName == ''):
                        for song in app.songs:
                            if song.seg == AudioSegment.from_wav(fileName):
                                app.ohno = True
                                app.showMessage('You cannot use two of the same audio segments!')
                        if not app.ohno:
                            initSong(app, fileName)
                        else: 
                            app.ohno = False
                except:
                    app.showMessage('Please input a valid path.')

        # exports songs
        elif (app.ex-app.er+10 <= event.x <= app.ex+app.er-10 and
            app.ey-app.er <= event.y <= app.ey+app.er):
            try:
                finalSeg = app.songs[0].seg
                for i in range(1, len(app.songs)):
                    finalSeg = finalSeg.overlay(app.songs[i].seg)
                app.showMessage('Successfully exported!')
                finalSeg.export("SongFiles/FinalSong.mp3", format="mp3")
            except:
                app.showMessage('You have not imported any songs!')

        # new tracks
        elif (app.tx-app.tr <= event.x <= app.tx+app.tr and
            app.ty-app.tr <= event.y <= app.ty+app.tr):
            if len(app.names) < 10:
                # tracks
                app.names.append(f"New Track {len(app.names)}")
                app.rows.append(1)
                app.cols.append(14)
                app.volcx.append(0)
                app.volcy.append(0)
                app.volcrx.append(0)
                app.volcry.append(0)
                app.volAttenuate.append(None)
                app.vol.append(0.0)
                app.oldVol.append(0.0)
                app.soloColor.append('grey')
                app.fxColor.append('grey')
                app.trackUserInput.append(False)

                # screens
                app.fxSplashScreen.append(False)
                app.compressorScreen.append(False)
                app.highPassScreen.append(False)
                app.lowPassScreen.append(False)
                app.bandPassScreen.append(False)

                # compressor
                app.threshcx.append(app.width/2-245)
                app.threshcy.append(app.height/2-40)
                app.threshcrx.append(10)
                app.threshcry.append(15)
                app.thresh.append(-20.0)

                app.ratiocx.append(app.width/2+80)
                app.ratiocy.append(app.height/2-145)
                app.ratiocrx.append(4)
                app.ratiocry.append(7)
                app.ratio.append(4)

                app.attackcx.append(744)
                app.attackcy.append(app.height/2-105)
                app.attackcrx.append(4)
                app.attackcry.append(7)
                app.attack.append(5)

                app.delaycx.append(789)
                app.delaycy.append(app.height/2-65)
                app.delaycrx.append(4)
                app.delaycry.append(7)
                app.delay.append(100)

                # low pass
                app.lowSeg1x0.append(app.width/2-150)
                app.lowSeg1y0.append(app.height/2-75)
                app.lowSeg1x1.append(750) 
                app.lowSeg1y1.append(app.height/2-75)

                app.lowSeg2x0.append(750)
                app.lowSeg2y0.append(app.height/2-75)
                app.lowSeg2x1.append(app.width/2+150)
                app.lowSeg2y1.append(app.height/2+75)

                app.lowPassCutoff.append(10000)

                # high pass
                app.highSeg1x0.append(app.width/2-150)
                app.highSeg1y0.append(app.height/2+75)
                app.highSeg1x1.append(560) 
                app.highSeg1y1.append(app.height/2-75)

                app.highSeg2x0.append(560)
                app.highSeg2y0.append(app.height/2-75)
                app.highSeg2x1.append(app.width/2+150)
                app.highSeg2y1.append(app.height/2-75)

                app.highPassCutoff.append(200)

                # band pass
                app.bandSeg1x0.append(app.width/2-150)
                app.bandSeg1y0.append(app.height/2+75)
                app.bandSeg1x1.append(555) 
                app.bandSeg1y1.append(app.height/2-75)

                app.bandSeg2x0.append(555)
                app.bandSeg2y0.append(app.height/2-75)
                app.bandSeg2x1.append(800) 
                app.bandSeg2y1.append(app.height/2-75)

                app.bandSeg3x0.append(800)
                app.bandSeg3y0.append(app.height/2-75)
                app.bandSeg3x1.append(app.width/2+150) 
                app.bandSeg3y1.append(app.height/2+75)

                app.bandPassLowCutoff.append(200)
                app.bandPassHighCutoff.append(10000)

            else:
                app.showMessage('You can only use 10 tracks!')

        # plays songs
        elif distance(event.x, event.y, app.px, app.py) <= app.pr:
            if app.solos == []:
                tempSongs = copy.copy(app.songs)
                for song in app.songs:
                    t1 = threading.Thread(target=playSong, args=(app, song, tempSongs))
                    t1.start()
                    app.threads.append(t1)
            else:
                tempSongs = copy.copy(app.solos)
                for song in app.solos:
                    t1 = threading.Thread(target=playSong, args=(app, song, tempSongs))
                    t1.start()
                    app.threads.append(t1)

        # records
        elif distance(event.x, event.y, app.rx, app.ry) < app.rr:
            if len(app.names) < len(app.songs) + 1:
                app.showMessage('Please create a new track first!')
            else:
                fileName = app.getUserInput("What would you like to name your recorded file?")
                if fileName != None:
                    t8 = threading.Thread(target=recordSong, args=(app,fileName + '.wav'))
                    t8.start()
                    app.threads.append(t8)

        # stops songs
        elif distance(event.x, event.y, app.sx, app.sy) < app.sr:
            app.isStopped = True

        # controls selector
        if 150 <= event.x < 1357 and app.height - 275 >= event.y >= 100 :
            app.counter += (event.x - app.sx0)//2
            app.sx0 = event.x
            app.sx1 = event.x

        # click all the way left to go back to the very beginning
        elif app.height - 317 >= event.y >= 100 and event.x <= app.marginCol-60:
            app.counter = 0
            app.waveStart = 0
            app.startTime = 0
            app.sx0 = 150
            app.sx1 = 150

        # clicks to go to the next waveform section
        elif app.height - 317 >= event.y >= 100 and event.x >= 1357:
                app.counter += 600
                app.waveStart += 600
                app.startTime += 6
        
        # additional features
        for i in range(len(app.names)):
            # solo button
            if (app.marginCol-20 <= event.x <= app.marginCol and 
                app.marginRow + (3*app.marginRow/4)*(i+1)-20 <= event.y <= app.marginRow + (3*app.marginRow/4)*(i+1)):
                if app.soloColor[i+app.trackStart] == 'grey':
                    app.soloColor[i+app.trackStart] = 'red'
                    try: 
                        app.solos.append(app.songs[i+app.trackStart])
                    except:
                        pass
                else:
                    app.soloColor[i+app.trackStart] = 'grey'
                    try: 
                        app.solos.remove(app.songs[i+app.trackStart])
                    except Exception as e:
                        print(e)
            
            # add fx
            elif (app.marginCol-60 < event.x < app.marginCol-20 and 
                app.marginRow + (3*app.marginRow/4)*(i+1)-20 < event.y < app.marginRow + (3*app.marginRow/4)*(i+1)):
                try:
                    app.songs[i]
                    app.fxSplashScreen[i] = True
                except:
                    app.showMessage('Please import a song first!')

            # delete tracks
            elif (138 + 100 * (i+1) <= event.x <= 50 + 100 * (i+2) and
                app.height - 275 <= event.y <= app.height - 263):
                isDelete = True
                # tracks
                app.names.pop(i)
                app.rows.pop(i)
                app.cols.pop(i)
                app.volcx.pop(i)
                app.volcy.pop(i)
                app.volcrx.pop(i)
                app.volcry.pop(i)
                app.vol.pop(i)
                app.oldVol.pop(i)
                app.soloColor.pop(i)
                app.fxColor.pop(i)
                app.trackUserInput.pop(i)

                # screens
                app.fxSplashScreen.pop(i)
                app.compressorScreen.pop(i)
                app.highPassScreen.pop(i)
                app.lowPassScreen.pop(i)
                app.bandPassScreen.pop(i)

                # compressor
                app.threshcx.pop(i)
                app.threshcy.pop(i)
                app.threshcrx.pop(i)
                app.threshcry.pop(i)
                app.thresh.pop(i)

                app.ratiocx.pop(i)
                app.ratiocy.pop(i)
                app.ratiocrx.pop(i)
                app.ratiocry.pop(i)
                app.ratio.pop(i)

                app.attackcx.pop(i)
                app.attackcy.pop(i)
                app.attackcrx.pop(i)
                app.attackcry.pop(i)
                app.attack.pop(i)

                app.delaycx.pop(i)
                app.delaycy.pop(i)
                app.delaycrx.pop(i)
                app.delaycry.pop(i)
                app.delay.pop(i)

                # low pass
                app.lowSeg1x0.pop(i)
                app.lowSeg1y0.pop(i)
                app.lowSeg1x1.pop(i)
                app.lowSeg1y1.pop(i)

                app.lowSeg2x0.pop(i)
                app.lowSeg2y0.pop(i)
                app.lowSeg2x1.pop(i)
                app.lowSeg2y1.pop(i)

                app.lowPassCutoff.pop(i)

                # high pass
                app.highSeg1x0.pop(i)
                app.highSeg1y0.pop(i)
                app.highSeg1x1.pop(i)
                app.highSeg1y1.pop(i)

                app.highSeg2x0.pop(i)
                app.highSeg2y0.pop(i)
                app.highSeg2x1.pop(i)
                app.highSeg2y1.pop(i)

                app.highPassCutoff.pop(i)

                # band pass
                app.bandSeg1x0.pop(i)
                app.bandSeg1y0.pop(i)
                app.bandSeg1x1.pop(i)
                app.bandSeg1y1.pop(i)

                app.bandSeg2x0.pop(i)
                app.bandSeg2y0.pop(i)
                app.bandSeg2x1.pop(i)
                app.bandSeg2y1.pop(i)

                app.bandSeg3x0.pop(i)
                app.bandSeg3y0.pop(i)
                app.bandSeg3x1.pop(i)
                app.bandSeg3y1.pop(i)

                app.bandPassLowCutoff.pop(i)
                app.bandPassHighCutoff.pop(i)

                if i < len(Song.songList):
                    Song.songList.pop(i)
                    app.songs.pop(i)
                break
                        
            # track names
            elif (app.volcx[i+1]-50 <= event.x <= app.volcx[i+1]+37 and
                app.height - 275 <= event.y <= app.height - 240):
                app.names[i] = ''
                app.trackUserInput[i] = True
            
def mouseDragged(app, event):
    fx = False
    comp = False
    high = False
    low = False
    band = False
    init = None

    # checks if we are in a splash screen
    for i in range(len(app.fxSplashScreen)):
        if app.fxSplashScreen[i]:
            fx = True
            init = i
            break
        elif app.compressorScreen[i]:
            comp = True
            init = i
            break
        elif app.highPassScreen[i]:
            high = True
            init = i
            break
        elif app.lowPassScreen[i]:
            low = True
            init = i
            break
        elif app.bandPassScreen[i]:
            band = True
            init = i
            break
    # conditionals relating to which splash screen we are in
    if fx:
        pass
    elif comp:
        # threshold
        if (app.threshcx[init]-app.threshcrx[init] <= event.x <= app.threshcx[init]+app.threshcrx[init] and
            app.threshcy[init]-app.threshcry[init] <= event.y <= app.threshcy[init]+app.threshcry[init]):
            if app.height/2-125 <= event.y <= app.height/2+125:
                app.threshcy[init] = event.y
                app.thresh[init] = 4*(2*(app.height - 50 - event.y - 160/2)/8 - 67) - 60
        # ratio
        elif (app.ratiocx[init]-app.ratiocrx[init] <= event.x <= app.ratiocx[init]+app.ratiocrx[init] and
            app.ratiocy[init]-app.ratiocry[init] <= event.y <= app.ratiocy[init]+app.ratiocry[init]):
            if app.width/2+40 <= event.x <= app.width/2+120:
                app.ratiocx[init] = event.x
                app.ratio[init] = int((event.x-780+40)/10) + 1
        # attack
        elif (app.attackcx[init]-app.attackcrx[init] <= event.x <= app.attackcx[init]+app.attackcrx[init] and
            app.attackcy[init]-app.attackcry[init] <= event.y <= app.attackcy[init]+app.attackcry[init]):
            if app.width/2+40 <= event.x <= app.width/2+120:
                app.attackcx[init] = event.x
                app.attack[init] = event.x-780+40+1    
        # delay
        elif (app.delaycx[init]-app.delaycrx[init] <= event.x <= app.delaycx[init]+app.delaycrx[init] and
            app.delaycy[init]-app.delaycry[init] <= event.y <= app.delaycy[init]+app.delaycry[init]):
            if app.width/2+40 <= event.x <= app.width/2+120:
                app.delaycx[init] = event.x
                app.delay[init] = 2*(event.x-780+40)+2
    # appears to be dead code, but necessary to prevent volume sliders
    # from moving while in these splash screens
    elif high:
        pass
    elif low:
        pass
    elif band:
        # controls low/high cutoff frequencies
        if app.width/2-150 <= event.x <= app.width/2+150:
            if distance(event.x, event.y, app.bandSeg2x0[i], app.bandSeg2y0[i]) <= 10:
                app.bandSeg1x1[init] = event.x
                app.bandSeg2x0[init] = event.x
                app.bandPassLowCutoff[init] = 40*(event.x-550)
            elif distance(event.x, event.y, app.bandSeg2x1[i], app.bandSeg2y1[i]) <= 10:
                app.bandSeg2x1[init] = event.x
                app.bandSeg3x0[init] = event.x
                app.bandPassHighCutoff[init] = 40*(event.x-550)
    else:
        # volume sliders !
        for i in range(len(app.volcrx)):
            if (app.volcx[i]-app.volcrx[i] <= event.x <= app.volcx[i]+app.volcrx[i] and
                app.volcy[i]-app.volcry[i] <= event.y <= app.volcy[i]+app.volcry[i]):
                    if app.height - 210 <= event.y <= app.height - 50:
                        app.volAttenuate[i] = event.y - 7
                        app.vol[i] = (app.height - 50 - event.y - 160/2)/8

def mouseReleased(app, event):
    for i in range(len(app.volcrx)):
        if (app.volcx[i]-app.volcrx[i] <= event.x <= app.volcx[i]+app.volcrx[i] and
        app.volcy[i]-app.volcry[i] <= event.y <= app.volcy[i]+app.volcry[i]):
            try:
                if i != 0:
                    song = app.songs[i-1]
                    song.volChange = (app.vol[i] - app.oldVol[i] + app.vol[0] - app.oldVol[0])
                    t10 = threading.Thread(target=volumeBalancerInterface, args=(app, song))
                    t10.start()
                    app.threads.append(t10)
                    app.oldVol[i] = app.vol[i]
                else:
                    for song in app.songs:
                        song.volChange = (app.vol[0] - app.oldVol[0])
                        t10 = threading.Thread(target=volumeBalancerInterface, args=(app, song))
                        t10.start()
                        app.threads.append(t10)
                    app.oldVol[i] = app.vol[i]
            except:
                pass

#######################################################################
#####                           features                          #####
#######################################################################

# mostly a wrapper function for the real volume balancer
def volumeBalancerInterface(app, song):
    newStream = volumeBalancer(app, song)
    for i in range(len(app.songs)):
        if song == app.songs[i]:
            app.songs[i] = Song(newStream)
            Song.songList.pop()
            storeSong(app, app.songs[i])

# changes the overall volume of a song
def volumeBalancer(app, song):
    # calculates number of frames needed
    totalFrames = int(song.seg.frame_count())

    result = []

    # for every frame
    for i in range(totalFrames):
        currFrame = song.seg.get_frame(i)
        currFrame = audioop.mul(currFrame,
                            song.seg.sample_width,
                            10 ** (float(song.volChange) / 10))
        result.append(currFrame)

    # resets the vol change
    song.volChange = None

    # stores all frames in a new audio segment
    newStream = song.seg._spawn(data=b''.join(result))
    return newStream

# mostly a wrapper function for the real compressor
# shows new compressed waveform for debugging purposes
def compressorInterface(app, song):
    newStream = compressor(song.seg, song.threshold, song.ratio, 
            song.attack, song.delay)
    for i in range(len(app.songs)):
        if song == app.songs[i]:
            app.songs[i] = Song(newStream)
            Song.songList.pop()
            storeSong(app, app.songs[i])

# reduces the dynamic range of a song
# inspired by <https://github.com/jiaaro/pydub/blob/master/pydub/effects.py>,
# loosely referenced
def compressor(stream, threshold, ratio, attack, delay):
    # converts threshold to RMS
    newThresh = (10 ** (float(threshold) / 10))
    threshRMS = stream.max_possible_amplitude * newThresh

    # changes volume levels
    volChange = 0.0
    result = []

    # calculates types of frames needed
    totalFrames = int(stream.frame_count())
    attackFrames = int(stream.frame_count(ms=attack))
    delayFrames = int(stream.frame_count(ms=delay))
    
    # for every frame
    for i in range(totalFrames):

        currRMS = stream.get_sample_slice(i - attackFrames, i + delayFrames).rms

        # amount in db curr value is greater than the threshold
        if currRMS == 0: 
            amountOver = 0.0
        else:
            amountOver = 20 * log(float(currRMS/threshRMS), 10)
            if amountOver < 0:
                amountOver = 0.0

        # want to increase by 1db for every ratio amount over threshold
        maxVolChange = (1 - (1.0 / ratio)) * amountOver

        # reduces dynamic range
        if currRMS > threshRMS:
            volChange = maxVolChange/10

        # changes volume of current frame if attenuated 
        currFrame = stream.get_frame(i)

        newFrames = []
        if volChange != 0.0:
            currFrame = audioop.mul(currFrame,
                                stream.sample_width,
                                10 ** (float(-volChange) / 10))
        result += [currFrame]

    # stores all frames in a new audio segment
    newStream = stream._spawn(data=b''.join(result))
    return newStream

# mostly a wrapper function for the real band pass function
def bandPassFilterInterface(app, song, lowCutoff, highCutoff):
    newStream = bandPassFilter(app, song, lowCutoff, highCutoff)
    for i in range(len(app.songs)):
        if song == app.songs[i]:
            app.songs[i] = Song(newStream)
            Song.songList.pop()
            storeSong(app, app.songs[i])

# band pass filter
def bandPassFilter(app, song, lowCutoff, highCutoff):
    lowPassedSeg = lowPassFilter(app, song.seg, highCutoff)
    newSeg = highPassFilter(app, lowPassedSeg, lowCutoff)
    return newSeg

# mostly a wrapper function for the real low pass function
def lowPassFilterInterface(app, song, cutoff):
    newStream = lowPassFilter(app, song.seg, cutoff)
    for i in range(len(app.songs)):
        if song == app.songs[i]:
            app.songs[i] = Song(newStream)
            Song.songList.pop()
            storeSong(app, app.songs[i])

# this function creates a simple RC low pass filter
# basically analyzes what happens in an RC circuit and emulates it here
# RC circuit referenced <https://www.electronics-tutorials.ws/filter/filter_2.html>
def lowPassFilter(app, seg, cutoff):
    # initializes two arrays storing unfiltered samples
    arrayOrig = seg.get_array_of_samples()
    arrayNew = seg.get_array_of_samples()

    # frequency cutoff is 1/(2*pi*RC), where RC is our time constant so...
    RC = 1 / (2 * math.pi * cutoff)
    # sample period is 1/frame_rate frequency
    dt = 1 / seg.frame_rate
    a = dt / (RC + dt)

    # manually changes first filter point
    arrayNew[0] = int(a * arrayOrig[0])

    # for every element, it's ok not to use channels here since we
    # aren't working with mirrored elements
    for i in range(1, len(arrayNew)):
        # uses the recurrence relation found by analyzing the RC circuit
        # based on current element + additional change bolstered by
        # the past element 
        arrayNew[i] = int(a * arrayOrig[i] + (1-a) * arrayNew[i-1])
    
    return seg._spawn(data=arrayNew)

# mostly a wrapper function for the real high pass function
def highPassFilterInterface(app, song, cutoff):
    newStream = highPassFilter(app, song.seg, cutoff)
    for i in range(len(app.songs)):
        if song == app.songs[i]:
            app.songs[i] = Song(newStream)
            Song.songList.pop()
            storeSong(app, app.songs[i])

# this function creates a simple RC high pass filter
# RC circuit referenced <https://www.electronics-tutorials.ws/filter/filter_3.html> 
def highPassFilter(app, seg, cutoff):
    # so far identical to our low pass...
    arrayOrig = seg.get_array_of_samples()
    arrayNew = seg.get_array_of_samples()
    
    RC = 1 / (2 * math.pi * cutoff)
    dt = 1 / seg.frame_rate
    # alpha changed for the sake of clarity
    a = RC / (RC + dt)

    for i in range(1, len(arrayNew)):
        # new recurrence relation 
        # based on decay from previous element + change when our element changes
        # from the past element to the current element)
        arrayNew[i] = int(a * arrayNew[i-1] + a * (arrayOrig[i] - arrayOrig[i-1]))
    
    return seg._spawn(data=arrayNew)

# distance formula !
def distance(x0, y0, x1, y1):
    return ((x0-x1)**2 + (y0-y1)**2)**(1/2)

# stores waveform
def storeSong(app, song):
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=p.get_format_from_width(song.seg.sample_width),
                        channels=song.seg.channels,
                        rate=song.seg.frame_rate,
                        output=True)
        for chunk in make_chunks(song.seg, 10):
            numData = abs(np.frombuffer(chunk._data,
                        dtype=np.int16))
            if not (numData.size > 0):
                return
            peak = np.average(numData)
            song.peakArray.append(peak)
    except:
        print('Error while storing song')

# initializes song
def initSong(app, fileName):
    song = Song(AudioSegment.from_wav(fileName))
    app.songs += [song]
    storeSong(app, song)
    app.vol[len(app.songs)-1] = 0.0
    app.oldVol[len(app.songs)-1] = 0.0
    app.volAttenuate[len(app.songs)-1] = None
    if app.soloColor[len(app.songs)-1] == 'red':
        app.solos.append(song)
    app.fxColor[len(app.songs)-1] = 'green'
    song.volChange = app.vol[0]
    t4 = threading.Thread(target=volumeBalancerInterface, args=(app, song))
    t4.start()
    app.threads.append(t4)

# plays song 
# modified to oblivion <https://realpython.com/playing-and-recording-sound-python/#pyaudio> 
def playSong(app, song, tempSongs):
    if app.counter == 0:
        seg = song.seg
    else:
        seg = song.seg[app.counter*10:]

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(seg.sample_width),
                    channels=seg.channels,
                    rate=seg.frame_rate,
                    output=True)

    for chunk in make_chunks(seg, 10):
        if app.isStopped:
            break
        stream.write(chunk._data)
        if song == tempSongs[0]:
            app.counter += 1
            app.sx0 += 2
            app.sx1 += 2 
        if app.sx0 >= 1357:
            app.waveStart = app.counter
            app.startTime += 6
            app.sx0 = 150
            app.sx1 = 150

    stream.stop_stream()
    stream.close()
    p.terminate()
    app.isStopped = False

    tempSongs.remove(song)

# records song
# modified from <https://www.thepythoncode.com/article/play-and-record-audio-sound-in-python>
def recordSong(app, fileName):
    app.recording = True
    chunk = 1024 

    p = pyaudio.PyAudio()  
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    frames_per_buffer=chunk,
                    input=True)

    frames = [] 

    while not app.isStopped:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    output = wave.open("SongFiles/" + fileName, 'wb')
    output.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    output.setnchannels(2)
    output.setframerate(44100)
    output.writeframes(b''.join(frames))
    output.close()

    app.recording = False
    app.isStopped = False
    initSong(app, "SongFiles/" + fileName)

#######################################################################
#####                      draw functions                         #####
#######################################################################

# draws buttons
def drawButtons(app, canvas):
    # import button!
    canvas.create_rectangle(app.ix-app.ir+10, app.iy-app.ir, app.ix+app.ir-10, app.iy+app.ir, fill='light yellow')
    canvas.create_rectangle(app.ix+5, app.iy-5, app.ix+app.ir, app.iy+5, fill='orange')
    canvas.create_polygon(app.ix-5, app.iy, app.ix+10, app.iy-10, app.ix+10, app.iy+10, fill='orange')
    canvas.create_line(app.ix-5, app.iy, app.ix+10, app.iy-10)
    canvas.create_line(app.ix+10, app.iy+10, app.ix-5, app.iy)
    canvas.create_line(app.ix+10, app.iy-10, app.ix+10, app.iy-3)
    canvas.create_line(app.ix+10, app.iy+4, app.ix+10, app.iy+10)

    # export button
    canvas.create_rectangle(app.ex-app.er+10, app.ey-app.er, app.ex+app.er-10, app.ey+app.er, fill='light yellow')
    canvas.create_rectangle(app.ex, app.ey-5, app.ex+app.er-5, app.ey+5, fill='orange')
    canvas.create_polygon(app.ex+app.er+5, app.ey, app.ex+app.er-10, app.ey-10, app.ex+app.er-10, app.ey+10, fill='orange')
    canvas.create_line(app.ex+app.er+5, app.ey, app.ex+app.er-10, app.ey-10)
    canvas.create_line( app.ex+app.er-10, app.ey+10, app.ex+app.er+5, app.ey)
    canvas.create_line(app.ex+app.er-10, app.ey-10, app.ex+app.er-10, app.ey-3)
    canvas.create_line(app.ex+app.er-10, app.ey+4, app.ex+app.er-10, app.ey+10)

    # new track button
    canvas.create_rectangle(app.tx-app.tr, app.ty-app.tr, app.tx+app.tr, app.ty+app.tr, fill='silver')
    canvas.create_line(app.tx-app.tr+12, app.ty, app.tx+app.tr-12, app.ty, fill='black')
    canvas.create_line(app.tx, app.ty-app.tr+12, app.tx, app.ty+app.tr-12, fill='black')

    # play button
    canvas.create_oval(app.px-app.pr, app.py-app.pr, app.px+app.pr, app.py+app.pr, fill='silver')
    canvas.create_polygon(app.px-((1/5)*app.pr), app.py-((2/5)*app.pr), app.px+((2/5)*app.pr), app.py, app.px-((1/5)*app.pr), app.py+((2/5)*app.pr), fill="black")

    # record button
    canvas.create_oval(app.rx-app.rr, app.ry-app.rr, app.rx+app.rr, app.ry+app.rr, fill='silver')
    canvas.create_oval(app.rx-((1/3)*app.rr), app.ry-((1/3)*app.rr), app.rx+((1/3)*app.rr), app.ry+((1/3)*app.rr), outline='maroon', fill='maroon')

    # stop button
    canvas.create_oval(app.sx-app.sr, app.sy-app.sr, app.sx+app.sr, app.sy+app.sr, fill='silver')
    canvas.create_rectangle(app.sx-((1/4)*app.sr), app.sy-((1/4)*app.sr), app.sx+((1/4)*app.sr), app.sy+((1/4)*app.sr), fill='black')

# bars made out of peaks ! 
def getBar(peak, startHeight, startWidth):
    barLength = 200*peak/(2**16)
    x0 = startWidth
    y0 = startHeight - barLength
    x1 = startWidth
    y1 = startHeight + barLength
    return x0, y0, x1, y1

# more bars made out of peaks ! 
def getModifiedBar(peak, startHeight, startWidth):
    barLength = 500*peak/(2**16)
    x0 = startWidth
    y0 = startHeight
    x1 = startWidth
    y1 = startHeight - 2*(barLength)
    return x0, y0, x1, y1

# waveform !
def drawWaveform(app, canvas):  
    for c in range(len(Song.songList)-app.trackStart):
        for j in range(app.waveStart, len(Song.songList[c+app.trackStart].peakArray)):
            x0, y0, x1, y1 = getBar(Song.songList[c+app.trackStart].peakArray[j], 
            137.5 + c*75, 150 + (j-app.waveStart)*2)
            if x0 < 1355:
                canvas.create_line(x0, y0, x1, y1)
        if Song.songList != app.songs:
            for d in range(len(Song.songList)):
                if Song.songList[d] != app.songs[d]:
                    Song.songList[d] = app.songs[d]

# fairly standard cell bounds function
def getCellBounds(app, row, col, i):
    gridWidth  = 1157 + 2*app.marginCol
    x0 = app.marginCol + (gridWidth-50) * col / app.cols[i]
    x1 = app.marginCol + (gridWidth-50) * (col+1) / app.cols[i]
    y0 = app.marginRow + 75 * i / app.rows[i]
    y1 = app.marginRow + 75 * (i+1) / app.rows[i]
    return (x0, y0, x1, y1)

# draw tracks
def drawTracks(app, canvas):
    for i in range(len(app.names)-app.trackStart):
        for row in range(app.rows[i]):
            for col in range(app.cols[i]):
                (x0, y0, x1, y1) = getCellBounds(app, row, col, i)
                if col == app.cols[i]-2:
                    canvas.create_rectangle(x0, y0, x1, y1, fill='silver')
                    canvas.create_line(x0+15, (y0+y1)/2, x0+30, (y0+y1)/2)
                    canvas.create_polygon(x0+25, (y0+y1)/2-3, x0+30, (y0+y1)/2, x0+25, (y0+y1)/2+3)
                else:
                    canvas.create_rectangle(x0, y0, x1, y1, fill='grey')
                if i == 0:
                    canvas.create_text(x0, y0-7, text=f'{app.startTime + col/2}')
        canvas.create_rectangle(5, app.marginRow + 75 * i / app.rows[i], app.marginCol, 
            app.marginRow + (3*app.marginRow/4)*(i+1), fill='silver')
        canvas.create_text(((5+app.marginCol)/2), (5*app.marginRow/8 + 
            (3*app.marginRow/4)*(i+1)), text=f'{app.names[i+app.trackStart]}')

        # solo button
        canvas.create_rectangle(app.marginCol-20, app.marginRow + 
            (3*app.marginRow/4)*(i+1)-20, app.marginCol, app.marginRow + 
            (3*app.marginRow/4)*(i+1), fill=f'{app.soloColor[i+app.trackStart]}')
        canvas.create_text((app.marginCol-20 + app.marginCol)/2, (app.marginRow + 
            (3*app.marginRow/4)*(i+1)-20 + app.marginRow + 
            (3*app.marginRow/4)*(i+1))/2, text='S', fill='white')

        # fx control button
        canvas.create_rectangle(app.marginCol-60, app.marginRow + 
            (3*app.marginRow/4)*(i+1)-20, app.marginCol-20, app.marginRow + 
            (3*app.marginRow/4)*(i+1), fill=f'{app.fxColor[i+app.trackStart]}')
        canvas.create_text((app.marginCol-60 + app.marginCol-20)/2, (app.marginRow + 
            (3*app.marginRow/4)*(i+1)-20 + app.marginRow + 
            (3*app.marginRow/4)*(i+1))/2, text='FX', fill='white')

        # track #
        canvas.create_rectangle(app.marginCol-20, 
            app.marginRow + 75 * i / app.rows[i], app.marginCol, 
            app.marginRow + 75 * i / app.rows[i]+20)
        canvas.create_text((app.marginCol-20 + app.marginCol)/2, 
            (app.marginRow + 75 * i / app.rows[i] + app.marginRow + 75 * i / app.rows[i]+20)/2,
            text=f'{i}')

# draws volume balancer
def drawVolumeBalancer(app, canvas):
    # master control
    canvas.create_rectangle(5, app.height, 150,   
        app.height - 275, fill='grey')
    canvas.create_text(80, (app.height - 240 + app.height - 275) / 2, text='Master')
    canvas.create_line(5, app.height - 240, 5 + 150, app.height - 240)

    # slider line
    canvas.create_line(80, app.height - 210, 80, app.height - 50)

    app.volcx[0] = (60 + 100)/2
    app.volcy[0] = (2*app.height - 275)/2
    if app.volAttenuate[0] != None:
        app.volcy[0] = app.volAttenuate[0]
    app.volcrx[0] = 10
    app.volcry[0] = 15

    # master volume tag
    canvas.create_rectangle(app.volcx[0]+app.volcrx[0], app.volcy[0]+app.volcry[0], 
        app.volcx[0]-app.volcrx[0], app.volcy[0]-app.volcry[0], fill='dark grey')
    canvas.create_text(80, (app.height - 240 + app.height - 275) / 2 + 30, text=f'{app.vol[0]} dB')

    # track control
    for i in range(len(app.names)):
        canvas.create_rectangle(50 + 100 * (i+1), app.height, 50 + 100 * (i+2), 
            app.height - 275, fill='dark grey')

        canvas.create_line(50 + 100 * (i+1), app.height - 240, 50 + 100 * (i+2), app.height - 240)
        
        # delete button
        canvas.create_rectangle(138 + 100 * (i+1), app.height - 263, 50 + 100 * (i+2), 
            app.height - 275, fill='maroon')

        canvas.create_line(138 + 100 * (i+1), app.height - 263, 50 + 100 * (i+2), 
            app.height - 275)
        canvas.create_line(138 + 100 * (i+1), app.height - 275, 50 + 100 * (i+2), 
            app.height - 263)

        app.volcx[i+1] = (50 + 100 * (i+1) + 50 + 100 * (i+2))/2
        app.volcy[i+1] = (2*app.height - 275)/2
        if app.volAttenuate[i+1] != None:
            app.volcy[i+1] = app.volAttenuate[i+1]
        app.volcrx[i+1] = 10
        app.volcry[i+1] = 15

        # slider line
        canvas.create_line(app.volcx[i+1], app.height - 210, app.volcx[i+1], app.height - 50)

        try:
            x0, y0, x1, y1 = getModifiedBar(Song.songList[i].peakArray[app.counter], 
            app.height - 50, app.volcx[i+1])
            canvas.create_rectangle(x0-5, y0, x1+5, y1-10, fill='grey')
        except:
            pass

        canvas.create_text(app.volcx[i+1], (app.height - 240 + app.height - 275) / 2, text=f'{app.names[i]}')

        # volume tag
        canvas.create_rectangle(app.volcx[i+1]+app.volcrx[i+1], app.volcy[i+1]+app.volcry[i+1], 
            app.volcx[i+1]-app.volcrx[i+1], app.volcy[i+1]-app.volcry[i+1], fill='silver')
        canvas.create_text(app.volcx[i+1], (app.height - 240 + app.height - 275) / 2 + 30, text=f'{app.vol[i+1]} dB')

# draws selector point
def drawSelector(app, canvas):
    # selector line
    canvas.create_line(app.sx0, app.sy0, app.sx1, app.sy1, width=2, fill='navy blue')

    # selector tip
    canvas.create_line(app.sx0, app.sy0, app.sx0-7, app.sy0-7, width=2)
    canvas.create_line(app.sx0, app.sy0, app.sx0+7, app.sy0-7, width=2)
    canvas.create_line(app.sx0-7, app.sy0-7, app.sx0+7, app.sy0-7, width=2)

# draw background
def drawBG(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'#adb4e6')

# draw recording sign
def drawRecordingSign(app, canvas):
    i = len(app.songs)

    canvas.create_rectangle(app.marginCol, app.marginRow + 75 * i / app.rows[i], app.width, 
        app.marginRow + (3*app.marginRow/4)*(i+1), fill='red')
    canvas.create_text((app.marginCol + app.width)//2, 
        (app.marginRow + 75 * i / app.rows[i] + ((3*app.marginRow/4)*(i+1)))//2 + 50, 
        text='RECORDING IN PROGRESS', fill='white', font='Arial 12')

# draws playback 
def drawPlaybackInterface(app, canvas):
    canvas.create_rectangle(5, app.height-317, app.width, app.height, fill='#535353')
    canvas.create_rectangle(5, app.height-317, app.width, app.height-275, fill='slate grey')
    timeSplit1, timeSplit2 = str(app.counter/100).split('.')
    
    timeSplit = [0] * 3 
    time = ''

    timeSplit[1], timeSplit[2] = str(app.counter/100).split('.')
    
    timeSplit[0] = int(timeSplit[1])//60
    timeSplit[1] = int(timeSplit[1])%60
    timeSplit[2] = int(int(timeSplit[2])/100*60)

    for i in range(len(timeSplit)):
        if timeSplit[i] < 10:
            timeSplit[i] = '0' + str(timeSplit[i])
        else:
            timeSplit[i] = str(timeSplit[i])
        time += timeSplit[i]
        if i != len(timeSplit)-1:
            time += ':'

    canvas.create_text(180, (app.height-317 + app.height-275)/2, text=time, font='Arial 12')

# draws FX screen
def drawFXScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'#adb4e6')
    canvas.create_rectangle(app.width/2-200, app.height/2-300, 
        app.width/2+200, app.height/2+300, fill='slate grey')
    canvas.create_line(app.width/2-200, app.height/2-200, 
        app.width/2+200, app.height/2-200)
    canvas.create_text(app.width/2, (app.height/2-300 + app.height/2-200)/2, 
        text='FX MANAGER', fill='white', font='Arial 15')

    # fx buttons
    canvas.create_rectangle(app.width/2-100, app.height/2-150, app.width/2+100, app.height/2-100, fill='light blue')
    canvas.create_text(app.width/2, (app.height/2-150 + app.height/2-100)/2, text='COMPRESSOR')

    canvas.create_rectangle(app.width/2-100, app.height/2-50, app.width/2+100, app.height/2, fill='light blue')
    canvas.create_text(app.width/2, (app.height/2-50 + app.height/2)/2, text='LOW PASS FILTER')

    canvas.create_rectangle(app.width/2-100, app.height/2+50, app.width/2+100, app.height/2+100, fill='light blue')
    canvas.create_text(app.width/2, (app.height/2+50 + app.height/2+100)/2, text='HIGH PASS FILTER')

    canvas.create_rectangle(app.width/2-100, app.height/2+150, app.width/2+100, app.height/2+200, fill='light blue')
    canvas.create_text(app.width/2, (app.height/2+150 + app.height/2+200)/2, text='BAND PASS FILTER')

# draws apply/cancel buttons
def drawApplyCancel(app, canvas):
    # apply
    canvas.create_rectangle(app.width/2+25, app.height/2+100, 
        app.width/2+85, app.height/2+160, fill='green')
    canvas.create_line((app.width/2+25 + app.width/2+85)/2-5, 
        (app.height/2+100 + app.height/2+160)/2+10+5, app.width/2+45-5, 
        app.height/2+100+20+10+5, fill='light green', width=2)
    canvas.create_line((app.width/2+25 + app.width/2+85)/2-5, 
        (app.height/2+100 + app.height/2+160)/2+10+5, app.width/2+75-5, 
        app.height/2+100+20-10+5, fill='light green', width=2)

    # cancel
    canvas.create_rectangle(app.width/2+105, app.height/2+100, 
        app.width/2+165, app.height/2+160, fill='maroon')
    canvas.create_line(app.width/2+105+15, app.height/2+100+15, 
        app.width/2+165-15, app.height/2+160-15, fill='red', width=2)
    canvas.create_line(app.width/2+105+15, app.height/2+160-15, 
        app.width/2+165-15, app.height/2+100+15, fill='red', width=2)

# compressor related
def drawThreshold(app, canvas, i):
    canvas.create_text(app.threshcx[i], 
        (app.height/2-150 + app.height/2-125)/2 - 30, 
        text='THRESHOLD', fill='light grey', font='Arial 12')
    canvas.create_rectangle(app.width/2-280, app.height/2-150, 
        app.width/2-280+70, app.height/2+150, fill='silver')
    canvas.create_line(app.width/2-245, app.height/2-125, 
        app.width/2-245, app.height/2+125)
    canvas.create_rectangle(app.threshcx[i]+app.threshcrx[i], 
        app.threshcy[i]+app.threshcry[i], app.threshcx[i]-app.threshcrx[i], 
        app.threshcy[i]-app.threshcry[i], fill='light grey')
    canvas.create_text(app.threshcx[i], 
        (app.height/2-150 + app.height/2-125)/2, text=f'{app.thresh[i]} dB')

def drawRatio(app, canvas, i):
    canvas.create_text(app.width/2-25, app.height/2-145, 
        text='RATIO', fill='light grey', font='Arial 12')
    canvas.create_rectangle(app.width/2+25, app.height/2-145-10, 
        app.width/2+170, app.height/2-145+10, fill='silver')
    canvas.create_line(app.width/2+40, app.height/2-145, 
        app.width/2+120, app.height/2-145)
    canvas.create_rectangle(app.ratiocx[i]+app.ratiocrx[i], 
        app.ratiocy[i]+app.ratiocry[i], app.ratiocx[i]-app.ratiocrx[i], 
        app.ratiocy[i]-app.ratiocry[i], fill='light grey')
    canvas.create_text(app.width/2+120+25, 
        app.ratiocy[i], text=f'{app.ratio[i]}')

def drawAttack(app, canvas, i):
    canvas.create_text(app.width/2-25, app.height/2-105, 
        text='ATTACK', fill='light grey', font='Arial 12')
    canvas.create_rectangle(app.width/2+25, app.height/2-105-10, 
        app.width/2+170, app.height/2-105+10, fill='silver')
    canvas.create_line(app.width/2+40, app.height/2-105, 
        app.width/2+120, app.height/2-105)
    canvas.create_rectangle(app.attackcx[i]+app.attackcrx[i], 
        app.attackcy[i]+app.attackcry[i], app.attackcx[i]-app.attackcrx[i], 
        app.attackcy[i]-app.attackcry[i], fill='light grey')
    canvas.create_text(app.width/2+120+25, 
        app.attackcy[i], text=f'{app.attack[i]} ms')

def drawDelay(app, canvas, i):
    canvas.create_text(app.width/2-25, app.height/2-65, 
        text='DELAY', fill='light grey', font='Arial 12')
    canvas.create_rectangle(app.width/2+25, app.height/2-65-10, 
        app.width/2+170, app.height/2-65+10, fill='silver')
    canvas.create_line(app.width/2+40, app.height/2-65, 
        app.width/2+120, app.height/2-65)
    canvas.create_rectangle(app.delaycx[i]+app.delaycrx[i], 
        app.delaycy[i]+app.delaycry[i], app.delaycx[i]-app.delaycrx[i], 
        app.delaycy[i]-app.delaycry[i], fill='light grey')
    canvas.create_text(app.width/2+120+25, 
        app.delaycy[i], text=f'{app.delay[i]} ms')

def drawCompScreen(app, canvas, i):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'#adb4e6')
    canvas.create_rectangle(app.width/2-350, app.height/2-275, app.width/2+350, 
        app.height/2+275, fill='grey')
    canvas.create_text(app.width/2, app.height/2-220, text='COMPRESSOR', 
        fill='white', font='Arial 15')

    drawThreshold(app, canvas, i)
    drawRatio(app, canvas, i)
    drawAttack(app, canvas, i)
    drawDelay(app, canvas, i)
    drawApplyCancel(app, canvas)

# filters related
def drawGraph(app, canvas):
    canvas.create_rectangle(app.width/2-200, app.height/2-200, app.width/2+200, app.height/2+200, fill='white')
    canvas.create_line(app.width/2-150, app.height/2-125, app.width/2-150, app.height/2+75)
    canvas.create_line(app.width/2-150, app.height/2-75, app.width/2+150, app.height/2-75)

def drawLowPassScreen(app, canvas, i):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'#adb4e6')
    canvas.create_rectangle(app.width/2-350, app.height/2-275, app.width/2+350, 
        app.height/2+275, fill='grey')
    canvas.create_text(app.width/2, app.height/2-220, text='LOW PASS FILTER', 
        fill='white', font='Arial 15')

    drawGraph(app, canvas)

    # lines
    canvas.create_line(app.lowSeg1x0[i], app.lowSeg1y0[i], app.lowSeg1x1[i], app.lowSeg1y1[i], fill='blue')
    canvas.create_line(app.lowSeg2x0[i], app.lowSeg2y0[i], app.lowSeg2x1[i], app.lowSeg2y1[i], fill='red')
    canvas.create_text(app.width/2, app.height/2-162, text=f'Cutoff: {app.lowPassCutoff[i]} hz')

    drawApplyCancel(app, canvas)

def drawHighPassScreen(app, canvas, i):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'#adb4e6')
    canvas.create_rectangle(app.width/2-350, app.height/2-275, app.width/2+350, 
        app.height/2+275, fill='grey')
    canvas.create_text(app.width/2, app.height/2-220, text='HIGH PASS FILTER', 
        fill='white', font='Arial 15')

    drawGraph(app, canvas)

    # lines
    canvas.create_line(app.highSeg1x0[i], app.highSeg1y0[i], app.highSeg1x1[i], app.highSeg1y1[i], fill='red')
    canvas.create_line(app.highSeg2x0[i], app.highSeg2y0[i], app.highSeg2x1[i], app.highSeg2y1[i], fill='blue')
    canvas.create_text(app.width/2, app.height/2-162, text=f'Cutoff: {app.highPassCutoff[i]} hz')

    drawApplyCancel(app, canvas)

    drawApplyCancel(app, canvas)

def drawBandPassScreen(app, canvas, i):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'#adb4e6')
    canvas.create_rectangle(app.width/2-350, app.height/2-275, app.width/2+350, 
        app.height/2+275, fill='grey')
    canvas.create_text(app.width/2, app.height/2-220, text='BAND PASS FILTER', 
        fill='white', font='Arial 15')

    drawGraph(app, canvas)

    # lines
    canvas.create_line(app.bandSeg1x0[i], app.bandSeg1y0[i], app.bandSeg1x1[i], app.bandSeg1y1[i], fill='red')
    canvas.create_line(app.bandSeg2x0[i], app.bandSeg2y0[i], app.bandSeg2x1[i], app.bandSeg2y1[i], fill='blue')
    canvas.create_line(app.bandSeg3x0[i], app.bandSeg3y0[i], app.bandSeg3x1[i], app.bandSeg3y1[i], fill='red')

    # controllers
    canvas.create_oval(app.bandSeg2x0[i]+10, app.bandSeg2y0[i]+10, app.bandSeg2x0[i]-10, app.bandSeg2y0[i]-10, fill='purple')
    canvas.create_oval(app.bandSeg2x1[i]+10, app.bandSeg2y1[i]+10, app.bandSeg2x1[i]-10, app.bandSeg2y1[i]-10, fill='purple')

    canvas.create_text(app.width/2, app.height/2-162, text=f'Low Cutoff: {app.bandPassLowCutoff[i]} hz      High Cutoff: {app.bandPassHighCutoff[i]} hz')

    drawApplyCancel(app, canvas)

def redrawAll(app, canvas):
    drawBG(app, canvas)
    drawTracks(app, canvas)
    drawWaveform(app, canvas)
    drawSelector(app, canvas)
    drawPlaybackInterface(app, canvas)
    drawButtons(app, canvas)
    drawVolumeBalancer(app, canvas)

    if app.recording:
        drawRecordingSign(app, canvas)

    for i in range(len(app.fxSplashScreen)):
        if app.fxSplashScreen[i]:
            drawFXScreen(app, canvas)
        elif app.compressorScreen[i]:
            drawCompScreen(app, canvas, i)
        elif app.lowPassScreen[i]:
            drawLowPassScreen(app, canvas, i)
        elif app.highPassScreen[i]:
            drawHighPassScreen(app, canvas, i)
        elif app.bandPassScreen[i]:
            drawBandPassScreen(app, canvas, i)
        
runApp(width=1400, height=800)