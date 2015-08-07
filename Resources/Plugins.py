# encoding: utf-8
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

import wx, math
from constants import *
import CeciliaLib
from Widgets import *

class PluginKnob(ControlKnob):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), size=(50,70), 
                log=False, outFunction=None, integer=False, backColour=None, label=''):
        ControlKnob.__init__(self, parent, minvalue, maxvalue, init, pos, size, 
                            log, outFunction, integer, backColour, label) 

        self.Bind(wx.EVT_RIGHT_DOWN, self.MouseRightDown)
        self.name = ''
        self.longLabel = ''
        self.rate = 'k'
        self.gliss = 0
        self.midictl = None
        self.midichan = 1
        self.midictlLabel = ''
        self.midiLearn = False
        self.automationLength = None
        self.automationData = []
        self.path = None
        self.tableNum = None
        self.play = False
        self.rec = False

    def getValue(self):
        return self.GetValue()
        
    def setValue(self, x):
        self.SetValue(x)
            
    def getRate(self):
        return self.rate

    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def setLongLabel(self, label):
        self.longLabel = label

    def getLongLabel(self):
        return self.longLabel
        
    def setPlay(self, x):
        if x:
            self.mode = 2
            data = CeciliaLib.getGrapher().plotter.data
            for line in data:
                if line.getName() == self.name:
                    line.setShow(1)
                    CeciliaLib.getGrapher().plotter.draw()
        else:
            self.mode = 0
        self.Refresh()        

    def setRec(self, x):
        if x:
            self.mode = 1
        else:
            self.mode = 0
        self.Refresh()        

    def getPlay(self):
        if self.mode == 2:
            return True
        else:
            return False    

    def getPlayState(self):
        return self.mode
        
    def getRec(self):
        if self.mode == 1:
            return True
        else:
            return False    

    def setTable(self,table):
        self.tableNum = table

    def getTable(self):
        return self.tableNum

    def getPath(self):
        return self.path

    def getState(self):
        return [self.getValue(), self.getPlayState(), self.getMidiCtl(), self.getMidiChannel()]

    def setState(self, values):
        self.setValue(values[0])
        self.setPlay(values[1])
        self.setMidiCtl(values[2])
        if len(values) >= 4:
            self.setMidiChannel(values[3])

    def inMidiLearnMode(self):
        self.midiLearn = True
        self.Refresh()

    def setMidiCtl(self, ctl):
        if ctl == None:
            self.midictl = None
            self.midichan = 1
            self.midictlLabel = ''
            self.midiLearn = False
        else:    
            self.midictl = int(ctl)
            self.midictlLabel = str(self.midictl)
            self.midiLearn = False
        self.Refresh()

    def getMidiCtl(self):
        return self.midictl

    def setMidiChannel(self, chan):
        self.midichan = int(chan)
        
    def getMidiChannel(self):
        return self.midichan
            
    def getWithMidi(self):
        if self.getMidiCtl() != None and CeciliaLib.getUseMidi():
            return True
        else:
            return False

    def setAutomationLength(self, x):
        self.automationLength = x

    def getAutomationLength(self):
        return self.automationLength

    def setAutomationData(self, data):
        # convert values on scaling
        temp = []
        log = self.getLog()
        minval = self.getMinValue()
        maxval = self.getMaxValue()
        automationlength = self.getAutomationLength()
        frac = automationlength / CeciliaLib.getTotalTime()
        virtuallength = len(data) / frac
        data.extend([data[-1]] * int(((1 - frac) * virtuallength)))
        totallength = float(len(data))
        oldpos = 0
        oldval = data[0]
        if log:
            maxOnMin = maxval / minval
            torec = math.log10(oldval/minval) / math.log10(maxOnMin)
        else:
            maxMinusMin = maxval - minval
            torec = (oldval - minval) / maxMinusMin
        temp.append([0.0, torec])

        for i, val in enumerate(data):
            length = (i - oldpos) / totallength
            pos = oldpos / totallength + length
            if log:
                torec = math.log10(val/minval) / math.log10(maxOnMin)
            else:
                torec = (val - minval) / maxMinusMin 
            temp.append([pos, torec])
            oldval = val
            oldpos = i

        self.automationData = temp

    def getAutomationData(self):
        return [[x[0],x[1]] for x in self.automationData]

    def update(self, val):
        if not self.HasCapture() and self.getPlay() == 1 or self.getWithMidi():
            self.setValue(val)

    def MouseRightDown(self, evt):
        if self._enable:                
            rec = wx.Rect(5, 13, 45, 45)
            pos = evt.GetPosition()
            if rec.Contains(pos):
                if evt.ShiftDown():
                    self.setMidiCtl(None)
                else:    
                    CeciliaLib.getCsound().midiLearn(self)
                    self.inMidiLearnMode()
        evt.Skip()

class Plugin(wx.Panel):
    def __init__(self, parent, choiceFunc, order):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition)
        self.SetBackgroundColour(BACKGROUND_COLOUR)

    def getKnobs(self):
        return [self.knob1, self.knob2, self.knob3]

    def getParams(self):
        return [self.knob1.GetValue(),self.knob2.GetValue(),self.knob3.GetValue(),self.preset.getIndex()]

    def getStates(self):
        return [self.knob1.getState(),self.knob2.getState(),self.knob3.getState()]
        
    def setStates(self, states):    
        self.knob1.setState(states[0])
        self.knob2.setState(states[1])
        self.knob3.setState(states[2])
        
    def setParams(self, params):
        self.knob1.SetValue(params[0])
        self.knob2.SetValue(params[1])
        self.knob3.SetValue(params[2])
        self.preset.setByIndex(params[3])

    def initCsoundChannels(self):
        self.onChangeKnob1(self.knob1.GetValue())
        self.onChangeKnob2(self.knob2.GetValue())
        self.onChangeKnob3(self.knob3.GetValue())
        self.onChangePreset(self.preset.getIndex())
        
    def onChangeKnob1(self, x):
        CeciliaLib.getCsound().setChannel("%s_value" % self.knob1.getName(), x)

    def onChangeKnob2(self, x):
        CeciliaLib.getCsound().setChannel("%s_value" % self.knob2.getName(), x)

    def onChangeKnob3(self, x):
        CeciliaLib.getCsound().setChannel("%s_value" % self.knob3.getName(), x)

    def onChangePreset(self, x, label=None):
        CeciliaLib.getCsound().setChannel("%s_value" % self.presetName, x)
        
    def getParamsText(self):
        knobs = [self.knob1, self.knob2, self.knob3]
        orchtext = ''
        scotext = ''
        for knob in knobs:
            if knob.getRate() == 'k':    
                orchtext += 'instr Cecilia_%s\n' % knob.getName()
                orchtext += 'ksliderValue init %f\n' % knob.GetValue()
                orchtext += 'kgetValue init %f\n' % knob.GetValue()

                if knob.getWithMidi() and not knob.getPlay():
                    orchtext += 'kmidiValue init %f\n' % knob.GetValue()
                    if not knob.getLog():
                        init = (knob.GetValue() - knob.getMinValue()) / (knob.getMaxValue() - knob.getMinValue()) - (1./254)
                        if init <= 0:
                            orchtext += 'initc7 %d, %d, 0\n' % (knob.getMidiChannel(), knob.getMidiCtl())
                        else:
                            orchtext += 'initc7 %d, %d, %f\n' % (knob.getMidiChannel(), knob.getMidiCtl(), init)
                        orchtext += 'kmidiValue ctrl7 %d, %d, %f, %f\n' % (knob.getMidiChannel(), knob.getMidiCtl(), knob.getMinValue(), knob.getMaxValue())
                    else:
                        init = math.log10(knob.GetValue() / knob.getMinValue()) / math.log10(knob.getMaxValue() / knob.getMinValue()) - (1./254)
                        if init <= 0:
                            orchtext += 'initc7 %d, %d, 0\n' % (knob.getMidiChannel(), knob.getMidiCtl())
                        else:
                            orchtext += 'initc7 %d, %d, %f\n' % (knob.getMidiChannel(), knob.getMidiCtl(), init)
                        orchtext += 'kmiditemp ctrl7 %d, %d, 0, 1\n' % (knob.getMidiChannel(), knob.getMidiCtl())
                        orchtext += 'kmidiValue pow 10, kmiditemp * %f + %f\n' % ((math.log10(knob.getMaxValue()) - math.log10(knob.getMinValue())), math.log10(knob.getMinValue()))

                orchtext += 'kgetValue chnget "%s_value"\n' % knob.getName()

                if knob.getWithMidi() and not knob.getPlay():
                    orchtext += 'ksliderDown init 0\n'
                    orchtext += 'ksliderDown chnget "%s_down"\n' % knob.getName()
                    orchtext += 'if ksliderDown == 1 then\n'
                    orchtext += 'ksliderValue = kgetValue\n'
                    orchtext += 'else\n'
                    orchtext += 'ksliderValue = kmidiValue\n'
                    orchtext += 'endif\n\n'
                    orchtext += 'gk%s port ksliderValue, %f, %f\n' % (knob.getName(), knob.gliss, knob.GetValue())
                    orchtext += 'chnset gk%s, "%s"\n' % (knob.getName(), knob.getName())                
                elif knob.getPlay():
                    orchtext += 'kreadValue init %f\n' % knob.GetValue()
                    orchtext += 'ksliderDown init 0\n'
                    orchtext += 'ksliderDown chnget "%s_down"\n' % knob.getName()
                    orchtext += 'kphase phasor 1/p3\n'
                    orchtext += 'kreadValue tablei kphase, %d, 1\n' % knob.getTable()
                    orchtext += 'if ksliderDown == 1 then\n'
                    orchtext += 'gk%s port kgetValue, %f, %f\n' % (knob.getName(), knob.gliss, knob.GetValue())
                    orchtext += 'else\n'
                    orchtext += 'gk%s = kreadValue\n' % knob.getName()
                    orchtext += 'endif\n\n'
                    orchtext += 'chnset gk%s, "%s"\n' % (knob.getName(), knob.getName())
                else:
                    orchtext += 'gk%s port kgetValue, %f, %f\n' % (knob.getName(), knob.gliss, knob.GetValue())   

                if knob.getRec():
                    knob.path = os.path.join(AUTOMATION_SAVE_PATH, '%s.auto' % knob.getName())
                    knob.path = CeciliaLib.convertWindowsPath(knob.getPath())
                    orchtext += 'dumpk gk%s, "%s", 8, 4/kr\n\n' % (knob.getName(), knob.getPath())    
                orchtext += 'endin\n\n'

                scotext += 'i "Cecilia_%s" 0 %f\n' % (knob.getName(), CeciliaLib.getTotalTime())

        return orchtext, scotext

    def getUdoText(self):
        return '', ''

    def getName(self):
        return self.pluginName
        
class NonePlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'None'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0, 1, 0, size=(43,70))    
        self.knob1.setEnable(False)    
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0, 1, 0, size=(43,70))        
        self.knob2.setEnable(False)    
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, 1, 0, size=(43,70))        
        self.knob3.setEnable(False)    
        self.sizer.Add(self.knob3)
        
        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='None', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)
        
        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['None'], init='None', size=(93,18), colour=CONTROLLABEL_BACK_COLOUR)
        self.preset.setEnable(False)
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)
        
        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

class ReverbPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Reverb'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0, 1, 0.25, size=(43,70), log=False, outFunction=self.onChangeKnob1, label='Mix')
        self.knob1.setName('plugin_%d_reverb_mix' % self.order)       
        self.knob1.setLongLabel('plugin %d Reverb Mix' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0.01, 10, 1, size=(43,70), log=False, outFunction=self.onChangeKnob2, label='Time')        
        self.knob2.setName('plugin_%d_reverb_time' % self.order)       
        self.knob2.setLongLabel('plugin %d Reverb Time' % (self.order+1))       
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, 1, 0.5, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Damp')        
        self.knob3.setName('plugin_%d_reverb_damp' % self.order)       
        self.knob3.setLongLabel('plugin %d Reverb Damp' % (self.order+1))       
        self.sizer.Add(self.knob3)
        
        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Reverb', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)
        
        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_reverb_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)
        
        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)
            
    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]
        
        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        text += 'if k%s == 1 then\n' % self.presetName
        for i in range(CeciliaLib.getNchnls()):
            text += 'arev%d_%d nreverb %s*0.5, gk%s, gk%s, 0, 32, gicomb%d, 8, giallp%d\n' % (self.order, i, globalOuts[i], self.knob2.getName(), self.knob3.getName(), (i%4), (i%4))
            text += '%s = %s * (1 - gk%s) + arev%d_%d * gk%s\n' % (globalOuts[i], globalOuts[i], self.knob1.getName(), self.order, i, self.knob1.getName())
        text += 'endif\n'
        return text
        
class FilterPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Filter'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0, 2, 1, size=(43,70), log=False, outFunction=self.onChangeKnob1, label='Level')
        self.knob1.setName('plugin_%d_filter_level' % self.order)       
        self.knob1.setLongLabel('plugin %d Filter Level' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 20, 18000, 1000, size=(43,70), log=True, outFunction=self.onChangeKnob2, label='Freq')        
        self.knob2.setName('plugin_%d_filter_freq' % self.order)       
        self.knob2.setLongLabel('plugin %d Filter Freq' % (self.order+1))  
        self.knob2.setFloatPrecision(0)     
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0.1, 10, 1, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Q')        
        self.knob3.setName('plugin_%d_filter_q' % self.order)       
        self.knob3.setLongLabel('plugin %d Filter Q' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Filter', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Lowpass', 'Highpass', 'Bandpass', 'Bandreject'], init='Lowpass', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_filter_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getUdoText(self):
        return """
opcode	plugin_varfilter, a, akkkk
ain,klevel,kfreq,kres,ktype xin 
kfreq limit kfreq, 20, 18000
if ktype == 0 then
    aout = ain
elseif ktype == 1 then
 	aout bqrez ain*0.5, kfreq, kres, 0
elseif ktype == 2 then
 	aout bqrez ain*0.5, kfreq, kres, 1
elseif ktype == 3 then
 	aout bqrez ain*0.05, kfreq, kres, 2
elseif ktype == 4 then
 	aout bqrez ain*0.7, kfreq, kres, 3
endif
	xout	aout*klevel
endop

        """, 'plugin_varfilter'

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        for i in range(CeciliaLib.getNchnls()):
            text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
            text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
            text += '%s plugin_varfilter %s, gk%s, gk%s, gk%s, k%s\n' % (globalOuts[i], globalOuts[i], self.knob1.getName(), self.knob2.getName(), self.knob3.getName(), self.presetName)
        return text

class EQPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Para EQ'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 20, 18000, 1000, size=(43,70), log=True, outFunction=self.onChangeKnob1, label='Freq')
        self.knob1.setName('plugin_%d_eq_freq' % self.order)       
        self.knob1.setLongLabel('plugin %d EQ Freq' % (self.order+1))       
        self.knob1.setFloatPrecision(0)     
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 10, 9000, 500, size=(43,70), log=True, outFunction=self.onChangeKnob2, label='BW')        
        self.knob2.setName('plugin_%d_eq_bw' % self.order)       
        self.knob2.setLongLabel('plugin %d EQ BW' % (self.order+1))  
        self.knob2.setFloatPrecision(0)     
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0.001, 10, 1, size=(43,70), log=True, outFunction=self.onChangeKnob3, label='Gain')        
        self.knob3.setName('plugin_%d_eq_gain' % self.order)       
        self.knob3.setLongLabel('plugin %d EQ Gain' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Para EQ', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_eq_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        text += 'if k%s == 1 then\n' % self.presetName
        for i in range(CeciliaLib.getNchnls()):
            text += '%s eqfil %s, gk%s, gk%s, gk%s\n' % (globalOuts[i], globalOuts[i], self.knob1.getName(), self.knob2.getName(), self.knob3.getName())
        text += 'endif\n'
        return text

class EQ3BPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = '3 Bands EQ'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0.001, 10, 1, size=(43,70), log=True, outFunction=self.onChangeKnob1, label='Low')
        self.knob1.setName('plugin_%d_eq3b_low' % self.order)       
        self.knob1.setLongLabel('plugin %d 3 Bands EQ Low' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0.001, 10, 1, size=(43,70), log=True, outFunction=self.onChangeKnob2, label='Mid')        
        self.knob2.setName('plugin_%d_eq3b_mid' % self.order)       
        self.knob2.setLongLabel('plugin %d 3 Bands EQ Mid' % (self.order+1))  
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0.001, 10, 1, size=(43,70), log=True, outFunction=self.onChangeKnob3, label='High')        
        self.knob3.setName('plugin_%d_eq3b_high' % self.order)       
        self.knob3.setLongLabel('plugin %d 3 Bands EQ High' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='3 Bands EQ', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_eq3b_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        text += 'if k%s == 1 then\n' % self.presetName
        for i in range(CeciliaLib.getNchnls()):
            text += '%s pareq %s, 200, gk%s, 0.707, 1\n' % (globalOuts[i], globalOuts[i], self.knob1.getName())
            text += '%s pareq %s, 1500, gk%s, 0.707, 0\n' % (globalOuts[i], globalOuts[i], self.knob2.getName())
            text += '%s pareq %s, 2000, gk%s, 0.707, 2\n' % (globalOuts[i], globalOuts[i], self.knob3.getName())
        text += 'endif\n'
        return text

class ChorusPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Chorus'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0, 1, 0.5, size=(43,70), log=False, outFunction=self.onChangeKnob1, label='Mix')
        self.knob1.setName('plugin_%d_chorus_mix' % self.order)       
        self.knob1.setLongLabel('plugin %d Chorus Mix' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0.001, 1., 0.2, size=(43,70), log=False, outFunction=self.onChangeKnob2, label='Depth')        
        self.knob2.setName('plugin_%d_chorus_depth' % self.order)       
        self.knob2.setLongLabel('plugin %d Chorus Depth' % (self.order+1))  
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, 1, .5, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Feed')        
        self.knob3.setName('plugin_%d_chorus_feed' % self.order)       
        self.knob3.setLongLabel('plugin %d Chorus Feed' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Chorus', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Flange', 'Chorus/Small', 'Chorus/Big', 'Slap', 'Echoes'], init='Flange', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_chorus_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getUdoText(self):
        return """
opcode plugin_chorus, a, akkkk
ain,kmix,kdepth,kfeedback,ktype xin 
giup ftgenonce 0,0,8192,10,1
ain init 0
kspeed init 0
kdel init 0
kfeed init 0
amod init 0
kscale init 0
koffset init 0
kran randomi .8, 1.2, .4
adepth upsamp kdepth
adepth butterlp adepth, 10
amod oscili 1, kspeed*kran, giup
amod = amod + koffset
amod = amod * adepth * kdel * kscale
adel upsamp kdel
adel butterlp adel, 10
aout flanger ain, (adel+amod)*0.001, kfeed*kfeedback, 2
if ktype == 0 then
	aout = ain
	goto outnomix
elseif ktype == 1 then
	koffset = 0
	kdel = 3
	kfeed = .5
	kspeed = .05
    kscale = 1
elseif ktype == 2 then
	koffset = 0
	kdel = 25
	kfeed = .25
	kspeed = .5
    kscale = .1
elseif ktype == 3 then
	koffset = 0
	kdel = 25
	kfeed = .55
	kspeed = .57
  	kscale = .2
elseif ktype == 4 then
	koffset = 1
	kdel = 500
	kfeed = 0
	kspeed = 0
    kscale = 1
elseif ktype == 5 then
	koffset = 1
	kdel = 500
	kfeed = .9
	kspeed = 0
   	kscale = 1
endif
outer:
aout = aout * sqrt(kmix) + ain * (1 - sqrt(kmix))
outnomix:
xout aout
endop

        """, 'plugin_chorus'

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        for i in range(CeciliaLib.getNchnls()):
            text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
            text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
            text += '%s plugin_chorus %s, gk%s, gk%s, gk%s, k%s\n' % (globalOuts[i], globalOuts[i], self.knob1.getName(), self.knob2.getName(), self.knob3.getName(), self.presetName)
        return text

class CompressPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Compress'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, -80, 0, -20, size=(43,70), log=False, outFunction=self.onChangeKnob1, label='Thresh')
        self.knob1.setName('plugin_%d_comp_thresh' % self.order)       
        self.knob1.setLongLabel('plugin %d Compress Thresh' % (self.order+1))       
        self.knob1.setFloatPrecision(1)     
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0.125, 20, 3, size=(43,70), log=False, outFunction=self.onChangeKnob2, label='Ratio')        
        self.knob2.setName('plugin_%d_comp_ratio' % self.order)       
        self.knob2.setLongLabel('plugin %d Compress Ratio' % (self.order+1))  
        self.knob2.setFloatPrecision(3)
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, -24, 24, 0, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Gain')        
        self.knob3.setName('plugin_%d_comp_gain' % self.order)       
        self.knob3.setLongLabel('plugin %d Compress Gain' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Compress', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_comp_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        text += 'if k%s == 1 then\n' % self.presetName
        for i in range(CeciliaLib.getNchnls()):
            text += '%s compress %s, %s, 0, 80+gk%s, 90+gk%s, gk%s, .005, .05, .05 \n' % (globalOuts[i], globalOuts[i], globalOuts[i], self.knob1.getName(), self.knob1.getName(), self.knob2.getName())
            text += '%s = %s * 10^(gk%s/20)\n' % (globalOuts[i], globalOuts[i], self.knob3.getName())
        text += 'endif\n'
        return text

class GatePlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Gate'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, -90, 0, -20, size=(43,70), log=False, outFunction=self.onChangeKnob1, label='Thresh')
        self.knob1.setName('plugin_%d_gate_thresh' % self.order)       
        self.knob1.setLongLabel('plugin %d Gate Thresh' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0, 2, 0, size=(43,70), log=False, outFunction=self.onChangeKnob2, label='Cut')        
        self.knob2.setName('plugin_%d_gate_cut' % self.order)       
        self.knob2.setLongLabel('plugin %d Gate Cut' % (self.order+1))  
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, .5, .005, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Ramp')        
        self.knob3.setName('plugin_%d_gate_ramp' % self.order)       
        self.knob3.setLongLabel('plugin %d Gate Ramp' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Gate', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_gate_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getUdoText(self):
        return """
opcode plugin_gate, a, akkkk
ain,kthresh,kcut,kramp,kactive xin
if kactive == 0 then
aout = ain
else
krms rms ain
krms = dbamp(krms) - 90.
kmul = (krms < kthresh ? kcut : 1)
kgate portk kmul, kramp, %f
aout = ain*kgate
endif
xout aout
endop

        """ % self.knob2.getValue(), 'plugin_gate'

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        for i in range(CeciliaLib.getNchnls()):            
            text += '%s plugin_gate %s, gk%s, gk%s, gk%s, k%s\n' % (globalOuts[i], globalOuts[i], self.knob1.getName(), self.knob2.getName(), self.knob3.getName(), self.presetName)
        return text

class DistoPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Disto'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0, 10, 3, size=(43,70), log=False, outFunction=self.onChangeKnob1, label='Drive')
        self.knob1.setName('plugin_%d_disto_drive' % self.order)       
        self.knob1.setLongLabel('plugin %d Disto Drive' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 100, 18000, 1000, size=(43,70), log=True, outFunction=self.onChangeKnob2, label='Freq')        
        self.knob2.setName('plugin_%d_disto_freq' % self.order)       
        self.knob2.setLongLabel('plugin %d Disto Freq' % (self.order+1))  
        self.knob2.setFloatPrecision(0)     
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, 1, 0.5, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Res')        
        self.knob3.setName('plugin_%d_disto_res' % self.order)       
        self.knob3.setLongLabel('plugin %d Disto Res' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Disto', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_disto_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        text += 'if k%s == 1 then\n' % self.presetName
        for i in range(CeciliaLib.getNchnls()):
            text += '%s lpf18 %s/32768, gk%s, gk%s, gk%s\n' % (globalOuts[i], globalOuts[i], self.knob2.getName(), self.knob3.getName(), self.knob1.getName())
            text += '%s = %s * 32768\n' % (globalOuts[i], globalOuts[i])
        text += 'endif\n'
        return text

class AmpModPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'AmpMod'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 0.001, 1000, 8, size=(43,70), log=True, outFunction=self.onChangeKnob1, label='Freq')
        self.knob1.setName('plugin_%d_ampmod_freq' % self.order)       
        self.knob1.setLongLabel('plugin %d AmpMod Freq' % (self.order+1))       
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0, 1, 1, size=(43,70), log=False, outFunction=self.onChangeKnob2, label='Amp')        
        self.knob2.setName('plugin_%d_ampmod_amp' % self.order)       
        self.knob2.setLongLabel('plugin %d AmpMod Amp' % (self.order+1))  
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, 0.5, 0, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Stereo')        
        self.knob3.setName('plugin_%d_ampmod_stereo' % self.order)       
        self.knob3.setLongLabel('plugin %d AmpMod Stereo' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='AmpMod', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Amplitude', 'RingMod'], init='Amplitude', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_ampmod_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getUdoText(self):
        return """
opcode plugin_ampmod, a, akkkkii
ain,kfreq,kamp,kstereo,kmode,iside,itab xin
if iside == 0 then
kph = 0
else
kph = kstereo
endif
 
if kmode == 0 then
aout = ain
elseif kmode == 1 then
amod osciliktp kfreq, itab, kph
amod = amod * 0.5 + 0.5
aout = ain*(amod*kamp+(1-kamp))
else
amod osciliktp kfreq, itab, kph
aout = ain*(amod*kamp)
endif
xout aout
endop

        """, 'plugin_ampmod'

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'gi_plugin_ampmod_tab ftgenonce 0, 0, 8192, 10, 1\n'
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        for i in range(CeciliaLib.getNchnls()):
            text += '%s plugin_ampmod %s, gk%s, gk%s, gk%s, k%s, %d, gi_plugin_ampmod_tab\n' % (globalOuts[i], globalOuts[i], self.knob1.getName(), 
                                                                    self.knob2.getName(), self.knob3.getName(), self.presetName, (i%2))
        return text

class PhaserPlugin(Plugin):
    def __init__(self, parent, choiceFunc, order):
        Plugin.__init__(self, parent, choiceFunc, order)
        self.pluginName = 'Phaser'
        self.order = order
        self.sizer = wx.FlexGridSizer(1,4,0,0)
        revMenuBox = wx.BoxSizer(wx.VERTICAL)

        self.knob1 = PluginKnob(self, 20, 1000, 100, size=(43,70), log=True, outFunction=self.onChangeKnob1, label='Freq')
        self.knob1.setName('plugin_%d_phaser_freq' % self.order)       
        self.knob1.setLongLabel('plugin %d Phaser Freq' % (self.order+1))       
        self.knob1.setFloatPrecision(2)     
        self.sizer.Add(self.knob1)

        self.knob2 = PluginKnob(self, 0, 1, .5, size=(43,70), log=False, outFunction=self.onChangeKnob2, label='Q')        
        self.knob2.setName('plugin_%d_phaser_q' % self.order)       
        self.knob2.setLongLabel('plugin %d Phaser Q' % (self.order+1))  
        self.sizer.Add(self.knob2)

        self.knob3 = PluginKnob(self, 0, 4, 1, size=(43,70), log=False, outFunction=self.onChangeKnob3, label='Spread')        
        self.knob3.setName('plugin_%d_phaser_spread' % self.order)       
        self.knob3.setLongLabel('plugin %d Phaser Spread' % (self.order+1))       
        self.sizer.Add(self.knob3)

        plugChoiceText = wx.StaticText(self, -1, 'Effects:')
        plugChoiceText.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoiceText.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoiceText, 0, wx.TOP, 0)
        self.choice = CustomMenu(self, choice=PLUGINS_CHOICE, init='Phaser', size=(93,18), colour=GREY_COLOUR, outFunction=choiceFunc)
        self.choice.SetToolTip(CECTooltip(TT_POST_ITEMS))
        revMenuBox.Add(self.choice, 0, wx.TOP, 2)

        plugChoicePreset = wx.StaticText(self, -1, 'Type:')
        plugChoicePreset.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE))
        plugChoicePreset.SetForegroundColour(TEXT_LABELFORWIDGET_COLOUR)
        revMenuBox.Add(plugChoicePreset, 0, wx.TOP, 6)
        self.preset = CustomMenu(self, choice=['Bypass', 'Active'], init='Active', size=(93,18), 
                                colour=CONTROLLABEL_BACK_COLOUR, outFunction=self.onChangePreset)
        self.presetName = 'plugin_%d_phaser_preset' % self.order                     
        revMenuBox.Add(self.preset, 0, wx.TOP, 2)

        self.sizer.Add(revMenuBox, 0, wx.LEFT, 5)
        self.SetSizer(self.sizer)

    def getText(self):
        globalOuts =['gaGlobalOut%d' % i for i in range(CeciliaLib.getNchnls())]

        text = ''
        text += 'k%s init %d\n' % (self.presetName, self.preset.getIndex())
        text += 'k%s chnget "%s_value"\n' % (self.presetName, self.presetName)
        text += 'if k%s == 1 then\n' % self.presetName
        for i in range(CeciliaLib.getNchnls()):
            text += 'aphaser_%d_%d phaser2 %s, gk%s, gk%s, 8, 1, gk%s, .5\n' % (i, self.order, globalOuts[i], self.knob1.getName(), self.knob2.getName(), self.knob3.getName())
            text += '%s = (%s + aphaser_%d_%d) * 0.707 \n' % (globalOuts[i], globalOuts[i], i, self.order)
        text += 'endif\n'
        return text
             
