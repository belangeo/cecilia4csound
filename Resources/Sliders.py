# encoding: utf-8
"""
Copyright 2015 iACT, universite de Montreal, Olivier Belanger, Jean Piche

This file is part of Cecilia4Csound.

Cecilia4Csound is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cecilia4Csound is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cecilia4Csound.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx, math, time, copy
from types import ListType, IntType, FloatType, TupleType
from constants import *
import CeciliaLib
from constants import *
from Widgets import *

def interpFloat(t, v1, v2):
    "interpolator for a single value; interprets t in [0-1] between v1 and v2"
    return (v2-v1)*t + v1

def tFromValue(value, v1, v2):
    "returns a t (in range 0-1) given a value in the range v1 to v2"
    return float(value-v1)/(v2-v1)

def clamp(v, minv, maxv):
    "clamps a value within a range"
    if v<minv: v=minv
    if v> maxv: v=maxv
    return v

def toLog(t, v1, v2):
    v1 = float(v1)
    return math.log10(t/v1) / math.log10(v2/v1)

def toExp(t, v1, v2):
    return math.pow(10, t * (math.log10(v2) - math.log10(v1)) + math.log10(v1))

class PlayRecButtons(wx.Panel):
    def __init__(self, parent, cecslider, id=wx.ID_ANY, pos=(0,0), size=(40,20)):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, pos=pos, size=size)
        self.SetMaxSize(self.GetSize())
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)  
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.cecslider = cecslider
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
        self.playColour = SLIDER_PLAY_COLOUR_HOT
        self.recColour = SLIDER_REC_COLOUR_HOT
        self.playOver = False
        self.recOver = False
        self.playOverWait = True
        self.recOverWait = True
        self.play = 0
        self.rec = False

        if CeciliaLib.getPlatform() == "win32":
            self.dcref = wx.BufferedPaintDC
        else:
            self.dcref = wx.PaintDC

    def setOverWait(self, which):
        if which == 0:
            self.playOverWait = False
        elif which == 1:
            self.recOverWait = False

    def checkForOverReady(self, pos):
        if not wx.Rect(2, 2, 17, 17).Contains(pos):
            self.playOverWait = True
        if not wx.Rect(21, 2, 38, 17).Contains(pos):
            self.recOverWait = True
                        
    def MouseDown(self, evt):
        pos = evt.GetPosition()
        if wx.Rect(2, 2, 17, 17).Contains(pos):
            self.play = (self.play + 1) % 3
            if self.play == 0: 
                self.playColour = SLIDER_PLAY_COLOUR_HOT
            elif self.play == 1: 
                self.playColour = SLIDER_PLAY_COLOUR_PRESSED
            else:
                self.playColour = SLIDER_PLAY_COLOUR_NO_BIND
            self.setOverWait(0)
        elif wx.Rect(21, 2, 38, 17).Contains(pos):
            if self.rec: 
                self.rec = False
                self.recColour = SLIDER_REC_COLOUR_HOT
            else: 
                self.rec = True
                self.recColour = SLIDER_REC_COLOUR_PRESSED
            self.setOverWait(1)
        self.playOver = False
        self.recOver = False
        self.Refresh()
        self.CaptureMouse()
        evt.Skip()

    def MouseUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMotion(self, evt):
        pos = evt.GetPosition()
        if wx.Rect(2, 2, 17, 17).Contains(pos) and self.playOverWait:
            self.playOver = True
            self.recOver = False
        elif wx.Rect(21, 2, 38, 17).Contains(pos) and self.recOverWait:
            self.playOver = False
            self.recOver = True
        self.checkForOverReady(pos)
        self.Refresh()
        evt.Skip()

    def OnLeave(self, evt):
        self.playOver = False
        self.recOver = False
        self.playOverWait = True
        self.recOverWait = True
        self.Refresh()
        evt.Skip()

    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = self.dcref(self)
        gc = wx.GraphicsContext_Create(dc)

        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR, wx.SOLID))
        dc.Clear()

        dc.SetPen(wx.Pen(BACKGROUND_COLOUR, width=0, style=wx.SOLID))
        dc.DrawRectangle(0, 0, w, h)

        if self.cecslider.getRate() == 'k' and self.cecslider.getUp() == 0:
            # Draw triangle
            if self.playOver: playColour = SLIDER_PLAY_COLOUR_OVER
            else: playColour = self.playColour
            gc.SetPen(wx.Pen(playColour, width=1, style=wx.SOLID))  
            gc.SetBrush(wx.Brush(playColour, wx.SOLID))
            tri = [(14,h/2), (9,4), (9,h-4), (14,h/2)]
            gc.DrawLines(tri)
    
            dc.SetPen(wx.Pen('#333333', width=1, style=wx.SOLID))  
            dc.DrawLine(w/2,4,w/2,h-4)
            
            # Draw circle
            if self.recOver: recColour = SLIDER_REC_COLOUR_OVER
            else: recColour = self.recColour
            gc.SetPen(wx.Pen(recColour, width=1, style=wx.SOLID))  
            gc.SetBrush(wx.Brush(recColour, wx.SOLID))
            gc.DrawEllipse(w/4+w/2-4, h/2-4, 8, 8)

        evt.Skip()

    def setPlay(self, x):
        self.play = x
        if self.play == 0: 
            self.playColour = SLIDER_PLAY_COLOUR_HOT
        elif self.play == 1: 
            self.playColour = SLIDER_PLAY_COLOUR_PRESSED
        else:
            self.playColour = SLIDER_PLAY_COLOUR_NO_BIND
        self.Refresh()

    def getPlay(self):
        return self.play

    def getRec(self):
        return self.rec

    def setRec(self, x):
        if x == 0:
            self.rec = False
            self.recColour = SLIDER_REC_COLOUR_HOT
        else:
            self.rec = True
            self.recColour = SLIDER_REC_COLOUR_PRESSED

class Slider(wx.Panel):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), size=(200,20), 
                 valtype='float', log=False, function=None, rate='k', cecslider=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, pos=pos, size=size, style=wx.NO_BORDER)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)  
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.SetMinSize(self.GetSize())
        self.rate = rate
        self.outFunction = function
        self.cecslider = cecslider
        if valtype.startswith('i'): self.myType = IntType
        else: self.myType = FloatType
        self.log = log
        self.SetRange(minvalue, maxvalue)
        self.borderWidth = 1
        self.fillcolor = SLIDER_BACK_COLOUR
        self.knobcolor = SLIDER_KNOB_COLOUR
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
        self.Bind(wx.EVT_MOTION, self.MouseMotion)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def createSliderBitmap(self):
        w, h = self.GetSize()
        b = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(b)
        dc.SetPen(wx.Pen(BACKGROUND_COLOUR, width=1))
        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR))
        dc.DrawRectangle(0,0,w,h)
        dc.SetBrush(wx.Brush("#777777"))
        dc.SetPen(wx.Pen(WIDGET_BORDER_COLOUR, width=1))
        h2 = self.sliderHeight / 4
        dc.DrawRoundedRectangle(0, h2, w, self.sliderHeight, 4)
        dc.SelectObject(wx.NullBitmap)
        b.SetMaskColour("#777777")
        self.sliderMask = b

    def createKnobMaskBitmap(self):
        w, h = self.knobSize, self.GetSize()[1]
        b = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(b)
        rec = wx.Rect(0, 0, w, h)
        dc.SetPen(wx.Pen(BACKGROUND_COLOUR, width=1))
        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR))
        dc.DrawRectangleRect(rec)
        h2 = self.sliderHeight / 4
        rec = wx.Rect(0, h2, w, self.sliderHeight)
        dc.GradientFillLinear(rec, GRADIENT_DARK_COLOUR, self.fillcolor, wx.BOTTOM)
        dc.SetBrush(wx.Brush("#787878"))
        dc.SetPen(wx.Pen(KNOB_BORDER_COLOUR, width=1))
        dc.DrawRoundedRectangle(0,0,w,h,3)
        dc.SelectObject(wx.NullBitmap)
        b.SetMaskColour("#787878")
        self.knobMask = b

    def setFillColour(self, col1, col2):
        self.fillcolor = col1
        self.knobcolor = col2
        self.createBackgroundBitmap()
        self.createKnobBitmap()
                
    def SetRange(self, minvalue, maxvalue):   
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def scale(self):
        inter = tFromValue(self.pos, self.knobHalfSize, self.GetSize()[self.orient]-self.knobHalfSize)
        return interpFloat(inter, self.minvalue, self.maxvalue)
    
    def MouseDown(self, evt):
        size = self.GetSize()
        self.pos = clamp(evt.GetPosition()[self.orient], self.knobHalfSize, 
                          size[self.orient]-self.knobHalfSize)
        self.value = self.scale()
        self.CaptureMouse()
        self.Refresh()
        if self.cecslider and self.rate == 'k' and not self.cecslider.getUp():
            if self.cecslider.getTable() or self.cecslider.getWithMidi() != None:
                CeciliaLib.getCsound().setChannel("%s_down" % self.cecslider.getName(), 1)
            
    def MouseMotion(self, evt):
        size = self.GetSize()
        if evt.Dragging() and evt.LeftIsDown() and self.HasCapture():
            self.pos = clamp(evt.GetPosition()[self.orient], self.knobHalfSize, 
                             size[self.orient]-self.knobHalfSize)
            self.value = self.scale()
            self.Refresh()
                   
    def MouseUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        if self.cecslider and self.rate == 'k' and not self.cecslider.getUp():
            if self.cecslider.getTable() or self.cecslider.getWithMidi() != None:
                CeciliaLib.getCsound().setChannel("%s_down" % self.cecslider.getName(), 0)
        if self.cecslider.getUp():
            CeciliaLib.getCsound().setChannel("%s_value" % self.cecslider.getName(), self.GetValue())
            
    def OnResize(self, evt):
        self.createSliderBitmap()
        self.createKnobMaskBitmap()
        self.createKnobBitmap()
        self.createBackgroundBitmap()
        self.clampPos()    
        self.Refresh()

    def clampPos(self):
        size = self.GetSize()
        self.pos = tFromValue(self.value, self.minvalue, self.maxvalue) * (size[self.orient] - self.knobHalfSize) + self.knobHalfSize
        self.pos = clamp(self.pos, self.knobHalfSize, size[self.orient]-self.knobHalfSize)

class HSlider(Slider):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), size=(200,15), 
                 valtype='float', log=False, function=None, rate='k', cecslider=None):
        Slider.__init__(self, parent, minvalue, maxvalue, init, pos, size, valtype, log, function, rate, cecslider)
        self.SetMinSize((50, 15))
        self.knobSize = 26
        self.knobHalfSize = 13
        self.sliderHeight = 14
        self.orient = 0
        self.createSliderBitmap()
        self.createKnobMaskBitmap()
        self.createBackgroundBitmap()
        self.createKnobBitmap()
        self.value = 0
        if init != None: self.SetValue(init)
        else: self.SetValue(minvalue)
        self.clampPos()
        self.midictl = ''
        self.midiLearn = False
        self.font = wx.Font(LABEL_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_LIGHT, face=FONT_FACE)

        self.mario = 0
        self.useMario = False
        self.marios = [ wx.Bitmap(os.path.join(ICON_PATH, 'Mario1.png'), wx.BITMAP_TYPE_PNG),
                        wx.Bitmap(os.path.join(ICON_PATH, 'Mario2.png'), wx.BITMAP_TYPE_PNG),
                        wx.Bitmap(os.path.join(ICON_PATH, 'Mario3.png'), wx.BITMAP_TYPE_PNG),
                        wx.Bitmap(os.path.join(ICON_PATH, 'Mario4.png'), wx.BITMAP_TYPE_PNG),
                        wx.Bitmap(os.path.join(ICON_PATH, 'Mario5.png'), wx.BITMAP_TYPE_PNG),
                        wx.Bitmap(os.path.join(ICON_PATH, 'Mario6.png'), wx.BITMAP_TYPE_PNG)
                       ]
                        
    def setSliderHeight(self, height):
        self.sliderHeight = height
        self.createSliderBitmap()
        self.createKnobMaskBitmap()
        self.createBackgroundBitmap()
        self.createKnobBitmap()
        self.Refresh()

    def createBackgroundBitmap(self):
        w,h = self.GetSize()
        self.backgroundBitmap = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(self.backgroundBitmap)

        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR, wx.SOLID))
        dc.Clear()

        # Draw background
        dc.SetPen(wx.Pen(BACKGROUND_COLOUR, width=self.borderWidth, style=wx.SOLID))
        dc.DrawRectangle(0, 0, w, h)

        # Draw inner part
        h2 = self.sliderHeight / 4
        rec = wx.Rect(0, h2, w, self.sliderHeight)
        dc.GradientFillLinear(rec, GRADIENT_DARK_COLOUR, self.fillcolor, wx.BOTTOM)
        dc.DrawBitmap(self.sliderMask, 0, 0, True)
        dc.SelectObject(wx.NullBitmap)

    def createKnobBitmap(self):
        w,h = self.GetSize()
        self.knobBitmap = wx.EmptyBitmap(self.knobSize,h)
        dc = wx.MemoryDC(self.knobBitmap)

        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR, wx.SOLID))
        dc.Clear()

        rec = wx.Rect(0, 0, self.knobSize, h)  
        dc.GradientFillLinear(rec, GRADIENT_DARK_COLOUR, self.knobcolor, wx.RIGHT)
        dc.DrawBitmap(self.knobMask, rec[0], rec[1], True)
        dc.SelectObject(wx.NullBitmap)

    def setMidiCtl(self, str):
        self.midictl = str
        self.midiLearn = False
        
    def inMidiLearnMode(self):
        self.midiLearn = True
        self.Refresh()
        
    def SetValue(self, value):
        self.lastvalue = self.value
        value = clamp(value, self.minvalue, self.maxvalue)
        if self.log:
            t = toLog(value, self.minvalue, self.maxvalue)
            self.value = interpFloat(t, self.minvalue, self.maxvalue)
        else:
            t = tFromValue(value, self.minvalue, self.maxvalue)
            self.value = interpFloat(t, self.minvalue, self.maxvalue)
        if self.myType == IntType:
            self.value = int(self.value)
        self.OnResize(None)

    def GetValue(self):
        if self.log:
            t = tFromValue(self.value, self.minvalue, self.maxvalue)
            val = toExp(t, self.minvalue, self.maxvalue)
        else:
            val = self.value
        if self.myType == IntType:
            return int(val)
        return val

    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetFont(self.font)
        dc.SetTextForeground(LABEL_LABEL_COLOUR)
        pos = self.pos-self.knobHalfSize

        dc.DrawBitmap(self.backgroundBitmap, 0, 0, True)

        # Draw knob
        if not self.useMario:
            dc.DrawBitmap(self.knobBitmap, pos, 0)
        else:
            if self.lastvalue < self.value: marioff = 0
            else: marioff = 3
            bitmario = self.marios[(self.mario % 3) + marioff]
            dc.DrawBitmap(bitmario, self.pos-8, 0)
            self.mario += 1
            
        if not self.midiLearn:    
            dc.DrawLabel(self.midictl, wx.Rect(pos, 0, self.knobSize, h), wx.ALIGN_CENTER)
        else:
            dc.SetFont(wx.Font(LABEL_FONT-1, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_LIGHT, face=FONT_FACE))
            dc.DrawLabel("Move a MIDI controller...", wx.Rect(5, 0, 50, h), wx.ALIGN_CENTER_VERTICAL)
                
        # Send value
        if self.outFunction:
            self.outFunction(self.GetValue())

class CECSlider:
    def __init__(self, parent, minvalue, maxvalue, init=None, 
                 label='slider', unit='', valtype='float', orientation='horizontal', 
                 log=False, name='', tableNum=None, rate='k', gliss=.025, midictl=None, 
                 tooltip='', up=0, function=None):
        self.parent = parent
        self.valtype = valtype
        self.name = name
        self.function = function
        self.tableNum = tableNum
        self.rate = rate
        self.gliss = gliss
        self.automationLength = None
        self.automationData = []
        self.path = None
        self.midictl = None
        self.midichan = 1
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.log = log
        self.up = up
        
        pos = (0,0)
        if orientation.startswith('h'):
            size = (200,16)
            self.slider = HSlider(parent, minvalue, maxvalue, init, pos, size, 
                                  valtype, log, self.writeToEntry, rate, self)
            self.slider.setSliderHeight(11)
        else:
            raise('Vertical sliders are not implemented! Use horizontal sliders')

        self.setMidiCtl(midictl)
        if tooltip != '':
            self.slider.SetToolTip(wx.ToolTip(tooltip))
    
        if self.up == 1:
            self.slider.setFillColour('#BBBBBB', '#999999')
            
        self.label = Label(parent, label, size=(100,16), outFunction=self.onLabelClick)
        self.label.SetToolTip(CECTooltip(TT_SLIDER_LABEL))
        self.entryUnit = EntryUnit(parent, self.slider.GetValue(), unit, size=(120,16),
                                   valtype=valtype, outFunction=self.entryReturn)
        self.entryUnit.SetToolTip(CECTooltip(TT_SLIDER_DISPLAY))                           
        self.buttons = PlayRecButtons(parent, self, size=(40,16))
        self.buttons.SetToolTip(CECTooltip(TT_SLIDER_PLAY + '\n\n' + TT_SLIDER_RECORD))

    def setFillColour(self, col1, col2, col3):
        self.slider.setFillColour(col3, col2)
        self.label.setBackColour(col1)
        self.entryUnit.setBackColour(col1)

    def onLabelClick(self, label, shift=False, alt=False, side='left'):
        # alt is now the right click
        if CeciliaLib.getGrapher() and self.rate != 'i':
            if alt and shift:    
                self.setMidiCtl(None)
            elif shift:
                CeciliaLib.getGrapher().setShowLineSolo(label)
                CeciliaLib.getGrapher().toolbar.menu.setLabel(label, True)
            elif alt:    
                CeciliaLib.getGrapher().toolbar.menu.setLabel(label, True)
                CeciliaLib.getCsound().midiLearn(self)
                self.slider.inMidiLearnMode()
            else:
                CeciliaLib.getGrapher().resetShow()
                CeciliaLib.getGrapher().toolbar.menu.setLabel(label, True)

    def setAutomationLength(self, x):
        self.automationLength = x

    def getAutomationLength(self):
        return self.automationLength

    def sendValue(self, value):
        if self.getPlay() in [0,1] or self.getRec() == 1 and self.rate == 'k':
            CeciliaLib.getCsound().setChannel("%s_value" % self.getName(), value)

    def entryReturn(self, value):
        self.slider.SetValue(value)
        self.sendValue(value)

    def writeToEntry(self, value):                    
        if self.slider.myType == FloatType:
            if value >= 10000:
                self.entryUnit.setValue(float('%5.2f' % value))
            elif value >= 1000:
                self.entryUnit.setValue(float('%5.3f' % value))
            elif value >= -1000:
                self.entryUnit.setValue(float('%5.4f' % value))
            elif value >= -10000:
                self.entryUnit.setValue(float('%5.3f' % value))
            else:
                self.entryUnit.setValue(float('%5.2f' % value))
        else:
            self.entryUnit.setValue(value)
        if not self.getUp():    
            self.sendValue(value)

    def getUp(self):
        return self.up

    def setValue(self, value):
        self.slider.SetValue(value)

    def getValue(self):
        return self.slider.GetValue()

    def getLog(self):
        return self.log

    def getMinValue(self):
        return self.minvalue

    def getMaxValue(self):
        return self.maxvalue

    def getRate(self):
        return self.rate

    def getName(self):
        return self.name

    def setPlay(self, x):
        self.buttons.setPlay(x)

    def setRec(self, x):
        self.buttons.setRec(x)

    def getPlay(self):
        return self.buttons.getPlay()

    def getRec(self):
        return self.buttons.getRec()

    def getState(self):
        return [self.getValue(), self.getPlay(), self.getMidiCtl(), self.getMidiChannel()]

    def setState(self, values):
        self.setValue(values[0])
        self.setPlay(values[1])
        self.setMidiCtl(values[2])
        if len(values) >= 4:
            self.setMidiChannel(values[3])
    
    def setTable(self,table):
        self.tableNum = table
        
    def getTable(self):
        return self.tableNum

    def getPath(self):
        return self.path

    def setMidiCtl(self, ctl):
        if ctl == None:
            self.midictl = None
            self.midichan = 1
            self.slider.setMidiCtl('')
        else:    
            self.midictl = int(ctl)
            self.slider.setMidiCtl(str(self.midictl))
        self.slider.Refresh()
        
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
                
    def getCeciliaText(self):
        orchtext = ''
        scotext = ''
        if self.rate == 'k':    
            orchtext += 'instr Cecilia_%s\n' % self.name
            orchtext += 'ksliderValue init %f\n' % self.getValue()
            orchtext += 'kgetValue init %f\n' % self.getValue()
            
            if self.getWithMidi() and not self.getPlay():
                orchtext += 'kmidiValue init %f\n' % self.getValue()
                if not self.getLog():
                    init = (self.getValue() - self.getMinValue()) / (self.getMaxValue() - self.getMinValue()) - (1./254)
                    if init <= 0:
                        orchtext += 'initc7 %d, %d, 0\n' % (self.getMidiChannel(), self.getMidiCtl())
                    else:
                        orchtext += 'initc7 %d, %d, %f\n' % (self.getMidiChannel(), self.getMidiCtl(), init)
                    orchtext += 'kmidiValue ctrl7 %d, %d, %f, %f\n' % (self.getMidiChannel(), self.getMidiCtl(), self.getMinValue(), self.getMaxValue())
                else:
                    init = math.log10(self.getValue() / self.getMinValue()) / math.log10(self.getMaxValue() / self.getMinValue()) - (1./254)
                    if init <= 0:
                        orchtext += 'initc7 %d, %d, 0\n' % (self.getMidiChannel(), self.getMidiCtl())
                    else:
                        orchtext += 'initc7 %d, %d, %f\n' % (self.getMidiChannel(), self.getMidiCtl(), init)
                    orchtext += 'kmiditemp ctrl7 %d, %d, 0, 1\n' % (self.getMidiChannel(), self.getMidiCtl())
                    orchtext += 'kmidiValue pow 10, kmiditemp * %f + %f\n' % ((math.log10(self.getMaxValue()) - math.log10(self.getMinValue())), math.log10(self.getMinValue()))
            
            orchtext += 'kgetValue chnget "%s_value"\n' % self.name

            if self.getWithMidi() and not self.getPlay():
                orchtext += 'ksliderDown init 0\n'
                orchtext += 'ksliderDown chnget "%s_down"\n' % self.name
                orchtext += 'if ksliderDown == 1 then\n'
                orchtext += 'ksliderValue = kgetValue\n'
                orchtext += 'else\n'
                orchtext += 'ksliderValue = kmidiValue\n'
                orchtext += 'endif\n\n'
                orchtext += 'gk%s port ksliderValue, %f, %f\n' % (self.name, self.gliss, self.getValue())
                orchtext += 'chnset gk%s, "%s"\n' % (self.name, self.name)                
            elif self.getPlay():
                orchtext += 'kreadValue init %f\n' % self.getValue()
                orchtext += 'ksliderDown init 0\n'
                orchtext += 'ksliderDown chnget "%s_down"\n' % self.name
                orchtext += 'kphase phasor 1/p3\n'
                orchtext += 'kreadValue tablei kphase, %d, 1\n' % self.getTable()
                orchtext += 'if ksliderDown == 1 then\n'
                orchtext += 'gk%s port kgetValue, %f, %f\n' % (self.name, self.gliss, self.getValue())
                orchtext += 'else\n'
                orchtext += 'gk%s = kreadValue\n' % self.name
                orchtext += 'endif\n\n'
                orchtext += 'chnset gk%s, "%s"\n' % (self.name, self.name)
            else:
                orchtext += 'gk%s port kgetValue, %f, %f\n' % (self.name, self.gliss, self.getValue())   
    
            if self.getRec():
                self.path = os.path.join(AUTOMATION_SAVE_PATH, '%s.auto' % self.name)
                self.path = CeciliaLib.convertWindowsPath(self.path)
                orchtext += 'dumpk gk%s, "%s", 8, 4/kr\n\n' % (self.name, self.path)    
            orchtext += 'endin\n\n'
            
            scotext += 'i "Cecilia_%s" 0 %f\n' % (self.name, CeciliaLib.getTotalTime())

        return orchtext, scotext

    def update(self, val):
        if not self.slider.HasCapture() and self.getPlay() == 1 or self.getWithMidi():
            self.setValue(val)

class RangeSlider(wx.Panel):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), size=(200,20), 
                 valtype='float', log=False, function=None, rate='k', cecslider=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, pos=pos, size=size, style=wx.NO_BORDER)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)  
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.SetMinSize(self.GetSize())
        self.sliderHeight = 14
        self.borderWidth = 1
        self.orient = 0
        self.action = None
        self.fillcolor = SLIDER_BACK_COLOUR
        self.knobcolor = SLIDER_KNOB_COLOUR
        self.handlecolor = wx.Colour(int(self.knobcolor[1:3])-10, int(self.knobcolor[3:5])-10, int(self.knobcolor[5:7])-10)
        self.rate = rate
        self.outFunction = function
        self.cecslider = cecslider
        if valtype.startswith('i'): self.myType = IntType
        else: self.myType = FloatType
        self.log = log
        self.SetRange(minvalue, maxvalue)
        self.handles = [minvalue, maxvalue]
        if init != None:
            if type(init) in [ListType, TupleType]:
                if len(init) == 1:
                    self.SetValue([init[0],init[0]])
                else:
                    self.SetValue([init[0],init[1]])    
            else: 
                self.SetValue([minvalue,maxvalue])
        else: 
            self.SetValue([minvalue,maxvalue])
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.MouseRightDown)
        self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
        self.Bind(wx.EVT_RIGHT_UP, self.MouseUp)
        self.Bind(wx.EVT_MOTION, self.MouseMotion)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def createSliderBitmap(self):
        w, h = self.GetSize()
        b = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(b)
        dc.SetPen(wx.Pen(BACKGROUND_COLOUR, width=1))
        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR))
        dc.DrawRectangle(0,0,w,h)
        dc.SetBrush(wx.Brush("#777777"))
        dc.SetPen(wx.Pen(WIDGET_BORDER_COLOUR, width=1))
        h2 = self.sliderHeight / 4
        dc.DrawRoundedRectangle(0, h2, w, self.sliderHeight, 4)
        dc.SelectObject(wx.NullBitmap)
        b.SetMaskColour("#777777")
        self.sliderMask = b

    def setFillColour(self, col1, col2):
        self.fillcolor = col1
        self.knobcolor = col2
        self.handlecolor = wx.Colour(self.knobcolor[0]*0.35, self.knobcolor[1]*0.35, self.knobcolor[2]*0.35)
        self.createBackgroundBitmap()

    def SetRange(self, minvalue, maxvalue):   
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def scale(self, pos):
        tmp = []
        for p in pos:
            inter = tFromValue(p, 1, self.GetSize()[self.orient]-1)
            inter2 = interpFloat(inter, self.minvalue, self.maxvalue)
            tmp.append(inter2)
        return tmp

    def MouseRightDown(self, evt):
        size = self.GetSize()
        xpos = evt.GetPosition()[self.orient]
        if xpos > (self.handlePos[0]-5) and xpos < (self.handlePos[1]+5):
            self.lastpos = xpos
            self.length = self.handlePos[1] - self.handlePos[0]
            self.action = 'drag'
            
            self.handles = self.scale(self.handlePos)
            self.CaptureMouse()
            self.Refresh()
            if self.cecslider and self.rate == 'k' and not self.cecslider.getUp():
                if self.cecslider.getTable() or self.cecslider.getWithMidi() != None:
                    CeciliaLib.getCsound().setChannel("%s_down" % self.cecslider.getName(), 1)
        
    def MouseDown(self, evt):
        size = self.GetSize()
        xpos = evt.GetPosition()[self.orient]
        self.middle = (self.handlePos[1] - self.handlePos[0]) / 2 + self.handlePos[0]
        if xpos < self.middle:
            self.handlePos[0] = clamp(xpos, 1, self.handlePos[1])
            self.action = 'left'
        elif xpos > self.middle:
            self.handlePos[1] = clamp(xpos, self.handlePos[0], size[self.orient]-1)
            self.action = 'right'    
        self.handles = self.scale(self.handlePos)
        
        self.CaptureMouse()
        self.Refresh()
        if self.cecslider and self.rate == 'k' and not self.cecslider.getUp():
            if self.cecslider.getTable() or self.cecslider.getWithMidi() != None:
                CeciliaLib.getCsound().setChannel("%s_down" % self.cecslider.getName(), 1)

    def MouseMotion(self, evt):
        size = self.GetSize()
        if evt.Dragging() and self.HasCapture() and evt.LeftIsDown() or evt.RightIsDown():
            xpos = evt.GetPosition()[self.orient]
            if self.action == 'drag':
                off = xpos - self.lastpos
                self.lastpos = xpos
                self.handlePos[0] = clamp(self.handlePos[0] + off, 1, size[self.orient]-self.length) 
                self.handlePos[1] = clamp(self.handlePos[1] + off, self.length, size[self.orient]-1)
            if self.action == 'left':
                self.handlePos[0] = clamp(xpos, 1, self.handlePos[1]-1)
            elif self.action == 'right':
                self.handlePos[1] = clamp(xpos, self.handlePos[0]+1, size[self.orient]-1)
            self.handles = self.scale(self.handlePos)
            self.Refresh()

    def MouseUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        if self.cecslider and self.rate == 'k' and not self.cecslider.getUp():
            if self.cecslider.getTable() or self.cecslider.getWithMidi() != None:
                CeciliaLib.getCsound().setChannel("%s_down" % self.cecslider.getName(), 0)
        if self.cecslider.getUp():
            CeciliaLib.getCsound().setChannel("%s_value_min" % self.cecslider.getName(), self.GetValue()[0])
            CeciliaLib.getCsound().setChannel("%s_value_max" % self.cecslider.getName(), self.GetValue()[1])

    def OnResize(self, evt):
        self.createSliderBitmap()
        self.createBackgroundBitmap()
        self.clampHandlePos()    
        self.Refresh()

    def clampHandlePos(self):
        size = self.GetSize()
        tmp = []
        for handle in [min(self.handles), max(self.handles)]:
            pos = tFromValue(handle, self.minvalue, self.maxvalue) * (size[self.orient])
            pos = clamp(pos, 1, size[self.orient]-1)
            tmp.append(pos)
        self.handlePos = tmp

class HRangeSlider(RangeSlider):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), size=(200,15), 
                 valtype='float', log=False, function=None, rate='k', cecslider=None):
        RangeSlider.__init__(self, parent, minvalue, maxvalue, init, pos, size, valtype, log, function, rate, cecslider)
        self.SetMinSize((50, 15))
        self.createSliderBitmap()
        self.createBackgroundBitmap()
        self.clampHandlePos()
        self.midictl1 = ''
        self.midictl2 = ''
        self.midiLearn = False
        self.font = wx.Font(LABEL_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_LIGHT, face=FONT_FACE)

    def setSliderHeight(self, height):
        self.sliderHeight = height
        self.createSliderBitmap()
        self.createBackgroundBitmap()
        self.Refresh()

    def createBackgroundBitmap(self):
        w,h = self.GetSize()
        self.backgroundBitmap = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(self.backgroundBitmap)

        dc.SetBrush(wx.Brush(BACKGROUND_COLOUR, wx.SOLID))
        dc.Clear()

        # Draw background
        dc.SetPen(wx.Pen(BACKGROUND_COLOUR, width=self.borderWidth, style=wx.SOLID))
        dc.DrawRectangle(0, 0, w, h)

        # Draw inner part
        h2 = self.sliderHeight / 4
        rec = wx.Rect(0, h2, w, self.sliderHeight)
        dc.GradientFillLinear(rec, GRADIENT_DARK_COLOUR, self.fillcolor, wx.BOTTOM)
        dc.DrawBitmap(self.sliderMask, 0, 0, True)
        dc.SelectObject(wx.NullBitmap)

    def setMidiCtl(self, str1, str2):
        self.midictl1 = str1
        self.midictl2 = str2
        self.midiLearn = False

    def inMidiLearnMode(self):
        self.midiLearn = True
        self.Refresh()

    def SetValue(self, values):
        self.lasthandles = self.handles
        tmp = []
        for val in values:
            value = clamp(val, self.minvalue, self.maxvalue)
            if self.log:
                t = toLog(value, self.minvalue, self.maxvalue)
                value = interpFloat(t, self.minvalue, self.maxvalue)
            else:
                t = tFromValue(value, self.minvalue, self.maxvalue)
                value = interpFloat(t, self.minvalue, self.maxvalue)
            if self.myType == IntType:
                value = int(value)
            tmp.append(value)
        self.handles = tmp        
        self.OnResize(None)

    def GetValue(self):
        tmp = []
        for value in self.handles:
            if self.log:
                t = tFromValue(value, self.minvalue, self.maxvalue)
                val = toExp(t, self.minvalue, self.maxvalue)
            else:
                val = value
            if self.myType == IntType:
                val = int(val)
            tmp.append(val)
        tmp = [min(tmp), max(tmp)]    
        return tmp

    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetFont(self.font)
        dc.SetTextForeground(LABEL_LABEL_COLOUR)

        dc.DrawBitmap(self.backgroundBitmap, 0, 0)

        # Draw handles
        dc.SetPen(wx.Pen(self.handlecolor, width=1, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.handlecolor))
        
        rec = wx.Rect(self.handlePos[0], 3, self.handlePos[1]-self.handlePos[0], h-7)  
        dc.DrawRoundedRectangleRect(rec, 4)   

        if not self.midiLearn:    
            dc.DrawLabel(self.midictl1, wx.Rect(10, 0, 30, h), wx.ALIGN_CENTER_VERTICAL)
            dc.DrawLabel(self.midictl2, wx.Rect(w-20, 0, 20, h), wx.ALIGN_CENTER_VERTICAL)
        else:
            dc.SetFont(wx.Font(LABEL_FONT-1, wwx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_LIGHT, face=FONT_FACE))
            dc.DrawLabel("Move 2 MIDI controllers...", wx.Rect(5, 0, 50, h), wx.ALIGN_CENTER_VERTICAL)

        # Send value
        if self.outFunction:
            self.outFunction(self.GetValue())

class CECRange:
    def __init__(self, parent, minvalue, maxvalue, init=None, 
                 label='slider', unit='', valtype='float', orientation='horizontal', 
                 log=False, name='', tableNum=None, rate='k', gliss=.025, midictl=None, 
                 tooltip='', up=0, function=None):
        self.parent = parent
        self.valtype = valtype
        self.name = name
        self.function = function
        self.tableNum = tableNum
        self.rate = rate
        self.gliss = gliss
        self.automationLength = None
        self.automationData = []
        self.path = None
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.log = log
        self.up = up
        self.midictl = None
        self.midichan = [1,1]

        pos = (0,0)
        if orientation.startswith('h'):
            size = (200,16)
            self.slider = HRangeSlider(parent, minvalue, maxvalue, init, pos, size, 
                                  valtype, log, self.writeToEntry, rate, self)
            self.slider.setSliderHeight(11)
        else:
            raise('Vertical sliders are not implemented! Use horizontal sliders')

        self.setMidiCtl(midictl)
        if tooltip != '':
            self.slider.SetToolTip(wx.ToolTip(tooltip))

        if self.up == 1:
            self.slider.setFillColour('#BBBBBB', '#999999')

        self.label = Label(parent, label, size=(100,16), outFunction=self.onLabelClick)
        self.label.SetToolTip(CECTooltip(TT_RANGE_LABEL))
        self.entryUnit = RangeEntryUnit(parent, self.slider.GetValue(), unit, size=(120,16),
                                   valtype=valtype, outFunction=self.entryReturn)
        self.entryUnit.SetToolTip(CECTooltip(TT_SLIDER_DISPLAY))                           
        self.buttons = PlayRecButtons(parent, self, size=(40,16))
        self.buttons.SetToolTip(CECTooltip(TT_SLIDER_PLAY + '\n\n' + TT_SLIDER_RECORD))

    def setFillColour(self, col1, col2, col3):
        self.slider.setFillColour(col3, col2)
        self.label.setBackColour(col1)
        self.entryUnit.setBackColour(col1)

    def onLabelClick(self, label, shift=False, alt=False, side='left'):
        # alt is now the right click
        rightclick = alt
        if side == 'left':
            label = label + ' min'
        else:
            label = label + ' max'    
        if CeciliaLib.getGrapher() and self.rate != 'i':
            if rightclick and shift:    
                self.setMidiCtl(None)
            elif shift:
                CeciliaLib.getGrapher().setShowLineSolo(label)
                CeciliaLib.getGrapher().toolbar.menu.setLabel(label, True)
            elif rightclick:    
                CeciliaLib.getGrapher().toolbar.menu.setLabel(label, True)
                CeciliaLib.getCsound().midiLearn(self, True)
                self.slider.inMidiLearnMode()
            else:
                CeciliaLib.getGrapher().resetShow()
                CeciliaLib.getGrapher().toolbar.menu.setLabel(label, True)

    def setAutomationLength(self, x):
        self.automationLength = x

    def getAutomationLength(self):
        return self.automationLength

    def sendValue(self, value):
        if self.getPlay() in [0,1] or self.getRec() == 1 and self.rate == 'k':
            for val in value: 
                CeciliaLib.getCsound().setChannel("%s_value_min" % self.getName(), value[0])
                CeciliaLib.getCsound().setChannel("%s_value_max" % self.getName(), value[1])

    def entryReturn(self, value):
        self.slider.SetValue(value)
        self.sendValue(value)

    def writeToEntry(self, values):  
        tmp = []
        if self.slider.myType == FloatType:
            for value in values:
                if value >= 10000:
                    val = float('%5.0f' % value)
                elif value >= 1000:
                    val = float('%5.1f' % value)
                elif value >= 100:
                    val = float('%5.2f' % value)
                elif value >= 10:
                    val = float('%5.3f' % value)
                elif value >= -100:
                    val = float('%5.3f' % value)                    
                elif value >= -1000:
                    val = float('%5.2f' % value)
                elif value >= -10000:
                    val = float('%5.1f' % value)
                else:
                    val = float('%5.2f' % value)
                tmp.append(val)    
        else:
            tmp = [i for i in values]
        self.entryUnit.setValue(tmp)    
        if not self.getUp():    
            self.sendValue(tmp)

    def getUp(self):
        return self.up

    def setValue(self, value):
        self.slider.SetValue(value)

    def getValue(self):
        return self.slider.GetValue()

    def getLog(self):
        return self.log

    def getMinValue(self):
        return self.minvalue

    def getMaxValue(self):
        return self.maxvalue

    def getRate(self):
        return self.rate

    def getName(self):
        return self.name

    def setPlay(self, x):
        self.buttons.setPlay(x)

    def setRec(self, x):
        self.buttons.setRec(x)

    def getPlay(self):
        return self.buttons.getPlay()

    def getRec(self):
        return self.buttons.getRec()

    def getState(self):
        return [self.getValue(), self.getPlay(), self.getMidiCtl(), self.getMidiChannel()]

    def setState(self, values):
        self.setValue(values[0])
        self.setPlay(values[1])
        self.setMidiCtl(values[2])
        if len(values) >= 4:
            self.setMidiChannel(values[3])

    def setTable(self,table):
        self.tableNum = table

    def getTable(self):
        return self.tableNum

    def getPath(self):
        return self.path

    def setMidiCtl(self, ctls):
        if ctls == None:
            self.midictl = None
            self.midichan = [1,1]
            self.slider.setMidiCtl('', '')
        else:    
            self.midictl = ctls
            self.slider.setMidiCtl(str(self.midictl[0]), str(self.midictl[1]))
        self.slider.Refresh()

    def getMidiCtl(self):
        return self.midictl

    def setMidiChannel(self, chan):
        self.midichan = chan
        
    def getMidiChannel(self):
        return self.midichan
            
    def getWithMidi(self):
        if self.getMidiCtl() != None and CeciliaLib.getUseMidi():
            return True
        else:
            return False

    def setAutomationData(self, data, which=0):
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

        if len(self.automationData) < 2:
            self.automationData.append(temp)
        else:    
            self.automationData[which] = temp
            
    def getAutomationData(self, which=0):
        return [[x[0],x[1]] for x in self.automationData[which]]

    def getCeciliaText(self):
        orchtext = ''
        scotext = ''
        if self.rate == 'k':    
            orchtext += 'instr Cecilia_%s\n' % self.name
            orchtext += 'ksliderValuemin init %f\n' % self.getValue()[0]
            orchtext += 'ksliderValuemax init %f\n' % self.getValue()[1]
            orchtext += 'kgetValuemin init %f\n' % self.getValue()[0]
            orchtext += 'kgetValuemax init %f\n' % self.getValue()[1]

            if self.getWithMidi() and not self.getPlay():
                orchtext += 'kmidiValuemin init %f\n' % self.getValue()[0]
                orchtext += 'kmidiValuemax init %f\n' % self.getValue()[1]
                if not self.getLog():
                    init = (self.getValue()[0] - self.getMinValue()) / (self.getMaxValue() - self.getMinValue()) - (1./254)
                    if init <= 0:
                        orchtext += 'initc7 %d, %d, 0\n' % (self.getMidiChannel()[0], self.getMidiCtl()[0])
                    else:
                        orchtext += 'initc7 %d, %d, %f\n' % (self.getMidiChannel()[0], self.getMidiCtl()[0], init)
                    init = (self.getValue()[1] - self.getMinValue()) / (self.getMaxValue() - self.getMinValue()) - (1./254)
                    if init <= 0:
                        orchtext += 'initc7 %d, %d, 0\n' % (self.getMidiChannel()[1], self.getMidiCtl()[1])
                    else:
                        orchtext += 'initc7 %d, %d, %f\n' % (self.getMidiChannel()[1], self.getMidiCtl()[1], init)
                    orchtext += 'kmidiValuemin ctrl7 %d, %d, %f, %f\n' % (self.getMidiChannel()[0], self.getMidiCtl()[0], self.getMinValue(), self.getMaxValue())
                    orchtext += 'kmidiValuemax ctrl7 %d, %d, %f, %f\n' % (self.getMidiChannel()[1], self.getMidiCtl()[1], self.getMinValue(), self.getMaxValue())
                else:
                    init = math.log10(self.getValue()[0] / self.getMinValue()) / math.log10(self.getMaxValue() / self.getMinValue()) - (1./254)
                    if init <= 0:
                        orchtext += 'initc7 %d, %d, 0\n' % (self.getMidiChannel()[0], self.getMidiCtl()[0])
                    else:
                        orchtext += 'initc7 %d, %d, %f\n' % (self.getMidiChannel()[1], self.getMidiCtl()[0], init)
                    init = math.log10(self.getValue()[1] / self.getMinValue()) / math.log10(self.getMaxValue() / self.getMinValue()) - (1./254)
                    if init <= 0:
                        orchtext += 'initc7 %d, %d, 0\n' % (self.getMidiChannel()[1], self.getMidiCtl()[1])
                    else:
                        orchtext += 'initc7 %d, %d, %f\n' % (self.getMidiChannel()[1], self.getMidiCtl()[1], init)
                    orchtext += 'kmiditempmin ctrl7 %d, %d, 0, 1\n' % (self.getMidiChannel()[0], self.getMidiCtl()[0])
                    orchtext += 'kmiditempmax ctrl7 %d, %d, 0, 1\n' % (self.getMidiChannel()[1], self.getMidiCtl()[1])
                    orchtext += 'kmidiValuemin pow 10, kmiditempmin * %f + %f\n' % ((math.log10(self.getMaxValue()) - math.log10(self.getMinValue())), math.log10(self.getMinValue()))
                    orchtext += 'kmidiValuemax pow 10, kmiditempmax * %f + %f\n' % ((math.log10(self.getMaxValue()) - math.log10(self.getMinValue())), math.log10(self.getMinValue()))

            orchtext += 'kgetValuemin chnget "%s_value_min"\n' % self.name
            orchtext += 'kgetValuemax chnget "%s_value_max"\n' % self.name

            if self.getWithMidi() and not self.getPlay():
                orchtext += 'ksliderDown init 0\n'
                orchtext += 'ksliderDown chnget "%s_down"\n' % self.name
                orchtext += 'if ksliderDown == 1 then\n'
                orchtext += 'ksliderValuemin = kgetValuemin\n'
                orchtext += 'ksliderValuemax = kgetValuemax\n'
                orchtext += 'else\n'
                orchtext += 'ksliderValuemin = kmidiValuemin\n'
                orchtext += 'ksliderValuemax = kmidiValuemax\n'
                orchtext += 'endif\n\n'
                orchtext += 'gk%smin port ksliderValuemin, %f, %f\n' % (self.name, self.gliss, self.getValue()[0])
                orchtext += 'gk%smax port ksliderValuemax, %f, %f\n' % (self.name, self.gliss, self.getValue()[1])
                orchtext += 'chnset gk%smin, "%s_min"\n' % (self.name, self.name)                
                orchtext += 'chnset gk%smax, "%s_max"\n' % (self.name, self.name)                
            elif self.getPlay():
                orchtext += 'kreadValuemin init %f\n' % self.getValue()[0]
                orchtext += 'kreadValuemax init %f\n' % self.getValue()[1]
                orchtext += 'ksliderDown init 0\n'
                orchtext += 'ksliderDown chnget "%s_down"\n' % self.name
                orchtext += 'kphase phasor 1/p3\n'
                orchtext += 'kreadValuemin tablei kphase, %d, 1\n' % self.getTable()[0]
                orchtext += 'kreadValuemax tablei kphase, %d, 1\n' % self.getTable()[1]
                orchtext += 'if ksliderDown == 1 then\n'
                orchtext += 'gk%smin port kgetValuemin, %f, %f\n' % (self.name, self.gliss, self.getValue()[0])
                orchtext += 'gk%smax port kgetValuemax, %f, %f\n' % (self.name, self.gliss, self.getValue()[1])
                orchtext += 'else\n'
                orchtext += 'gk%smin = kreadValuemin\n' % self.name
                orchtext += 'gk%smax = kreadValuemax\n' % self.name
                orchtext += 'endif\n\n'
                orchtext += 'chnset gk%smin, "%s_min"\n' % (self.name, self.name)
                orchtext += 'chnset gk%smax, "%s_max"\n' % (self.name, self.name)
            else:
                orchtext += 'gk%smin port kgetValuemin, %f, %f\n' % (self.name, self.gliss, self.getValue()[0])   
                orchtext += 'gk%smax port kgetValuemax, %f, %f\n' % (self.name, self.gliss, self.getValue()[1])   

            if self.getRec():
                self.pathmin = os.path.join(AUTOMATION_SAVE_PATH, '%smin.auto' % self.name)
                self.pathmin = CeciliaLib.convertWindowsPath(self.pathmin)
                orchtext += 'dumpk gk%smin, "%s", 8, 4/kr\n\n' % (self.name, self.pathmin)    
                self.pathmax = os.path.join(AUTOMATION_SAVE_PATH, '%smax.auto' % self.name)
                self.pathmax = CeciliaLib.convertWindowsPath(self.pathmax)
                orchtext += 'dumpk gk%smax, "%s", 8, 4/kr\n\n' % (self.name, self.pathmax)  
                self.path = [self.pathmin, self.pathmax]  
            orchtext += 'endin\n\n'

            scotext += 'i "Cecilia_%s" 0 %f\n' % (self.name, CeciliaLib.getTotalTime())

        return orchtext, scotext

    def update(self, val):
        if not self.slider.HasCapture() and self.getPlay() == 1 or self.getWithMidi():
            self.setValue(val)
        
def buildHorizontalSlidersBox(parent, list):
    mainBox = wx.BoxSizer(wx.VERTICAL)
    box = wx.FlexGridSizer(24,4,2,5)
    sliders = []
    tableNum = CeciliaLib.getSliderTableNum()
    for widget in list:
        if widget['type'] in ['cslider', 'crange']:
            orient = widget.get('orient', 'h')
            mini = eval(widget.get('min', '0'))
            maxi = eval(widget.get('max', '1'))
            midictl = int(eval(widget.get('midictl', '-1')))
            if midictl == -1:
                midictl = None
            if widget['type'] == 'cslider':
                init = eval(widget.get('init', str(mini)))
            else:
                init = widget.get('init', '')
                if init == '':
                    init = [mini, maxi]
                else:
                    init = init.split(',')
                    init = [eval(i.strip()) for i in init]        
            unit = widget.get('unit', '')
            tooltip = widget.get('help', '')
            up = eval(widget.get('up', '0'))
            valtype = widget.get('res', 'float')
            if valtype not in ['int', 'float']:
                CeciliaLib.showErrorDialog('Error when building interface!', "-res option choices are 'int' or 'float'.")
            rate = widget.get('rate', 'k')
            if rate not in ['i', 'k']:
                CeciliaLib.showErrorDialog('Error when building interface!', "-rate option choices are 'i' or 'k'.")
            gliss = eval(widget.get('gliss', '.025'))
            if gliss < 0.0:
                CeciliaLib.showErrorDialog('Error when building interface!', "-gliss option must must be greater or equal than 0.")
            if up == 1:
                gliss = 0.0    
            linlog = widget.get('rel', 'lin')
            if linlog not in ['lin', 'log']:
                CeciliaLib.showErrorDialog('Error when building interface!', "-rel option choices are 'lin' or 'log'.")
            if linlog == 'log': log = True
            else: log = False
            if log and mini == 0 or maxi == 0:
                CeciliaLib.showErrorDialog('Error when building interface!', "-min or -max options can't be 0 for a logarithmic slider.")
            name = widget['name']
            if name.startswith('-'):
                CeciliaLib.showErrorDialog('Error when building interface!', "Missing name. First argument of cslider can't be %s." % widget['name'])
            label = widget.get('label', '')
            if label == '':
                CeciliaLib.showErrorDialog('Error when building interface!', "cslider %s has no -label option." % name)

            if widget['type'] == 'cslider':
                tableNum += 1 
                sl = CECSlider(parent, mini, maxi, init, label, unit, valtype, orient, log, name, tableNum, rate, gliss, midictl, tooltip, up)
            else:
                tableNums = []
                for i in range(2):
                    tableNum += 1
                    tableNums.append(tableNum)
                sl = CECRange(parent, mini, maxi, init, label, unit, valtype, orient, log, name, tableNums, rate, gliss, midictl, tooltip, up)                
            box.AddMany([(sl.label, 0, wx.LEFT, 5), (sl.buttons, 0, wx.LEFT, 0), 
                         (sl.slider, 0, wx.EXPAND), (sl.entryUnit, 0, wx.LEFT | wx.RIGHT, 5)])   
            sliders.append(sl)

    CeciliaLib.setSliderTableNum(tableNum+1)

    box.AddGrowableCol(2)
    mainBox.Add(box, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

    return mainBox, sliders
