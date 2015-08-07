# -*- coding: utf-8 -*-
"""
Copyright 2009 iACT, universite de Montreal, Jean Piche, Olivier Belanger, Dominic Thibault

This file is part of Cecilia 4.

Cecilia 4 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cecilia 4 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cecilia 4.  If not, see <http://www.gnu.org/licenses/>.
"""
import csnd6
import wx
import sys, os, time, threading, re, math, codecs
from types import ListType, TupleType
import CeciliaLib
from constants import *
from subprocess import Popen, PIPE
from pyo import pa_get_output_devices, pa_get_default_output, pa_get_input_devices, pa_get_default_input, pm_get_input_devices, pm_get_default_input, sndinfo

# TODO: This is no more correct...
if '/Cecilia.app' in os.getcwd():
    csnd6.csoundSetGlobalEnv("OPCODEDIR", 
            os.getcwd() + "/../Frameworks/CsoundLib.framework/Versions/5.2/Resources/Opcodes")

class Callback(threading.Thread):
    def __init__(self, time, function, arg=None):
        threading.Thread.__init__(self)
        self.t = time
        self.arg = arg
        self.function = function
        self._terminated = False
        
    def run(self):
        while not self._terminated:
            if self.arg == None:
                self.function()
            else:
                self.function(self.arg)    
            time.sleep(self.t)
        
    def stop(self):    
        self._terminated = True

class Csound():
    def __init__(self):
        self.loglines = []
        self.channelValues = {}
        self.activeSliders = []
        self.perf = None
        self.csound = csnd6.Csound()
        self.csdfile = None
        self.midiLearnSlider = None
        self.midiLearnEndFlag = False
        self.callbackPass = 0

    def logger(self, str):
        self.logfile.write(str)
        self.loglines.append(str)

    def runForSyntaxCheck(self, csdfile):
        try:
            os.remove(os.path.join(TMP_PATH, 'csoundLog.txt'))
        except:
            pass    
        CeciliaLib.setDayTime()
        self.logfile = open(os.path.join(TMP_PATH, 'csoundLog.txt'), 'w')
        
        cs = csnd6.Csound()
        cs.SetMessageCallback(self.logger)
        cs.Compile('--syntax-check-only', csdfile)
        
        self.logfile.close()
        
    def callback(self):
        state = self.csound.GetChannel('ready')
        CeciliaLib.csoundIsRunning(state)
            
        time = self.csound.GetChannel('time')
        wx.CallAfter(CeciliaLib.getCeciliaEditor().setTime, time)
        
        if CeciliaLib.getInterface():
            wx.CallAfter(CeciliaLib.getControlPanel().updateTime, time)
            
            amps = []
            for i in range(CeciliaLib.getNchnls()):
                amps.append(self.csound.GetChannel('rms%i' % i))   
            wx.CallAfter(CeciliaLib.getControlPanel().updateAmps, amps)

            if self.callbackPass == 1:
                for slider in self.activeSliders:
                    name = slider.getName()
                    if type(slider.getValue()) in [ListType, TupleType]:
                        val = []
                        val.append(self.csound.GetChannel(str(name) + '_min'))
                        val.append(self.csound.GetChannel(str(name) + '_max'))
                    else:    
                        val = self.csound.GetChannel(str(name))
                    if self.channelValues[name] != val:
                        self.channelValues[name] = val
                        wx.CallAfter(slider.update, val)
            else:
                self.callbackPass = 1
                
        stop = self.csound.GetChannel('stop')
        if stop == 1:
            CeciliaLib.stopCeciliaSound()
            self.call.stop()
            
    def findLineError(self, csdfile, errLine=None, errText=None):
        f = open(csdfile, 'r')
        if errLine != None:
            line = CeciliaLib.ensureNFD(f.readlines()[errLine-1].rstrip())
        elif errText != None:
            line = errText.strip()    
        f.close()
        ceciliaEditor = CeciliaLib.getCeciliaEditor()
        orchEditor = ceciliaEditor.orchestraPanels[ceciliaEditor.activeOrchestra].editor
        text = orchEditor.GetText()
        if text.find(line) != -1:
            start = text.find(line)
            end = len(line) + start
            orchEditor.SetSelection(start, end)
            return str(orchEditor.LineFromPosition(start) + 1), line
        else:
            return '', line

    def AnalyseLogFile(self, error):
        last = len(self.loglines) - 1
        for i, line in enumerate(self.loglines):
            if line.find('INIT ERROR') != -1 or line.find('error') != -1 or line.find('PortMIDI: error:') != -1:
                if line.find('MIDI') != -1:
                    CeciliaLib.showErrorDialog('Failed to initialized Midi.', line)
                    break
                if line.find('error') != -1 and line.find('unknown label') != -1:
                    line = "Error in instr %s\n" % self.loglines[i-1]
                    lineText = self.loglines[i].replace(':', '').split('.')[1]
                elif line.find('error') != -1:
                    if self.loglines[i+1].find('illegal character') != -1:
                        continue
                    logline = self.loglines[i+2].split('line')[1].replace(':', '').strip(' ')
                    logline = logline.split("\n")
                    errLine = int(logline[0])
                    lineNum, lineText = self.findLineError(self.csdfile, errLine)
                    if lineNum != '':
                        line = self.loglines[i+1] + ', line %s\n\n' % lineNum
                    else:
                        line = self.loglines[i+1] + '\n\n'  
                CeciliaLib.showErrorDialog('Error in csound file','\n' + line + '\n' + lineText)
                break
        if i == last:
            CeciliaLib.showErrorDialog('No syntax error!', 'If useMidi option is checked, be sure there is a valid Midi interface connected!\nIf audio input is enable, be sure there is a valid audio input interface connected!')

    def startCsound(self, csdfile):
        self.csdfile = csdfile
        self.loglines = []
        self.channelValues = {}
        self.activeSliders = []
        self.callbackPass = 0
        plugins = CeciliaLib.getPlugins()

        for slider in CeciliaLib.getSamplerSliders():
            if slider.getPlay():
                self.channelValues[slider.getCName()] = -999999999
        for slider in CeciliaLib.getUserSliders():
            if slider.getPlay() or slider.getMidiCtl() != None:
                self.activeSliders.append(slider)
                self.channelValues[slider.getName()] = -999999999
        for plug in plugins:
            if plug != None:
                for knob in plug.getKnobs():
                    if knob.getPlay() or knob.getMidiCtl() != None:
                        self.activeSliders.append(knob)
                        self.channelValues[knob.getName()] = -999999999
                        
        res = self.csound.Compile(self.csdfile)
        if res == 0:
            self.call = Callback(0.075, self.callback)
            self.call.start()
            self.perf = csnd6.CsoundPerformanceThread(self.csound)
            self.perf.Play()
            if CeciliaLib.getGainSlider():
                self.setChannel('masterVolume', CeciliaLib.getGainSlider().GetValue())
                plugins = CeciliaLib.getPlugins()
                for plug in plugins:
                    if plug != None:
                        plug.initCsoundChannels()
            for slider in CeciliaLib.getSamplerSliders():
                self.setChannel('%s_value' % slider.getCName(), slider.getValue())
            for slider in CeciliaLib.getUserSliders():
                if type(slider.getValue()) in [ListType, TupleType]:
                    self.setChannel('%s_value_min' % slider.getName(), slider.getValue()[0])
                    self.setChannel('%s_value_max' % slider.getName(), slider.getValue()[1])
                else:    
                    self.setChannel('%s_value' % slider.getName(), slider.getValue())
            for togPop in CeciliaLib.getUserTogglePopups():
                if togPop.getRate() != 'table':
                    self.setChannel('%s_value' % togPop.getName(), togPop.getValue())
        else:
            CeciliaLib.stopCeciliaSound()
            self.runForSyntaxCheck(self.csdfile)
            self.AnalyseLogFile(csnd6.csoundCfgErrorCodeToString(res))    

    def stopCsound(self):
        if self.perf != None:
            if self.perf.GetStatus() == 0:
                self.call.stop()
                self.perf.Stop()
                self.perf.Join()
        self.csound.Reset()

    def isCsoundRunning(self):
        if self.perf != None:
            if self.perf.GetStatus() == 0:
                return True
            else:
                return False
        else:
            return False            
        
    def setChannel(self, name, value):
        if type(value) in [ListType, TupleType]:
            self.csound.SetChannel(str(name)+'_min', value[0])
            self.csound.SetChannel(str(name)+'_max', value[1])
        else:    
            self.csound.SetChannel(str(name), value)

    def midiLearnCallback(self, rangeSlider=False):
        if rangeSlider:
            ctrl = self.csound.GetChannel('midictrl')
            chan = self.csound.GetChannel('midichannel')
            if ctrl != 0.0 and ctrl not in self.rangeCtrl:
                self.rangeCtrl.append(int(ctrl))
                self.rangeChan.append(int(chan))
                if len(self.rangeCtrl) == 2:
                    self.midiLearnSlider.setMidiCtl(self.rangeCtrl)
                    self.midiLearnSlider.setMidiChannel(self.rangeChan)
                    self.call.stop()
                    self.stopCsound()    
                    self.midiLearnEndFlag = False        
        else:
            ctrl = self.csound.GetChannel('midictrl')
            chan = self.csound.GetChannel('midichannel')
            if ctrl != 0.0:
                self.midiLearnSlider.setMidiCtl(ctrl)
                self.midiLearnSlider.setMidiChannel(chan)
                self.call.stop()
                self.stopCsound()
                self.midiLearnEndFlag = False

    def midiLearn(self, slider, rangeSlider=False):
        if self.isCsoundRunning():
            CeciliaLib.showErrorDialog("Csound is already started!", "Stop Csound before running Midi learn.")
        
        if rangeSlider: 
            self.rangeCtrl = []
            self.rangeChan = []
        res = self.csound.Compile(os.path.join(RESOURCES_PATH + "/getMidiCtl.csd"))
        if res == 0:
            self.midiLearnEndFlag = True
            self.midiLearnSlider = slider
            self.call = Callback(0.075, self.midiLearnCallback, rangeSlider)
            self.call.start()
            self.perf = csnd6.CsoundPerformanceThread(self.csound)
            self.perf.Play()
            wx.CallLater(30000, self.checkMidiLearnEnd)
        else:
            CeciliaLib.showErrorDialog("Abort Csound...", "Be sure there is a valid Midi interface connected!")    

    def checkMidiLearnEnd(self):
        if self.midiLearnEndFlag:
            self.midiLearnSlider.setMidiCtl(None)

    def testFunc(self, *args):
        self.csoundloglines.append(args[0])

    def getAvailableAudioMidiDrivers(self):
        inputDriverList, inputDriverIndexes = pa_get_input_devices()
        selectedInputDriver = inputDriverList[inputDriverIndexes.index(pa_get_default_input())]
        outputDriverList, outputDriverIndexes = pa_get_output_devices()
        selectedOutputDriver = outputDriverList[outputDriverIndexes.index(pa_get_default_output())]
        midiDriverList, midiDriverIndexes = pm_get_input_devices()
        if midiDriverList == []:
            selectedMidiDriver = ""
        else:
            selectedMidiDriver = midiDriverList[midiDriverIndexes.index(pm_get_default_input())]
        return inputDriverList, selectedInputDriver, outputDriverList, selectedOutputDriver, midiDriverList, selectedMidiDriver

    def getSoundInfo(self, path):
        """
        Retrieves information of the sound and prints it to the console.
    
        return (number of channels, sampling rate, duration, 
                fraction of a table, length in samples, bitrate)
        """
        print '--------------------------------------'
        print path

        info = sndinfo(path)
        if info is not None:
            type = info[4]
            samprate = int(info[2])
            chnls = info[3]
            nsamps = info[0] 
            dur = info[1]
            bitrate = INV_BIT_DEPTHS.get(info[5], -1)
            for i in range(24):
                size = math.pow(2,(i+1))
                if size > nsamps:
                    break
            tableFrac = nsamps / size
            
            
            print "channels = %d" % chnls
            print "sampling rate = %s" % samprate
            print "number of samples = %s" % nsamps
            print "duration in sec. = %s" % dur
            print "bitrate = %s" % bitrate
            print "type = %s" % type

            return (chnls, samprate, dur, tableFrac, nsamps, bitrate, type)
        else:
            print "Unable to get sound infos..."
            return None

    def getSoundsFromList(self, pathList):
        soundDict = dict()
        for path in pathList:
            if os.path.isfile(path):
                infos = self.getSoundInfo(path)
                if infos != None:
                    sndfile = os.path.split(path)[1] 
                    if sndfile not in soundDict.keys():
                        soundDict[CeciliaLib.ensureNFD(sndfile)] = {'samprate': infos[1],
                                        'chnls': infos[0],
                                        'dur': infos[2],
                                        'bitrate': infos[5],
                                        'type': infos[6],
                                        'path': path}
            else:
                print 'not a file'
        return soundDict
