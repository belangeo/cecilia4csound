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

import wx, os
import CeciliaLib
from constants import *
from Sliders import buildHorizontalSlidersBox
from Grapher import getGrapher, buildGrapher
from TogglePopup import buildTogglePopupBox
import Control
import Preset
from menubar import InterfaceMenuBar

class CeciliaInterface(wx.Frame):
    def __init__(self, parent, id=-1, title='', editor=None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style= wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | \
                        wx.CLIP_CHILDREN | wx.WANTS_CHARS):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.ceciliaEditor = editor
        self.menubar = InterfaceMenuBar(self, self.ceciliaEditor)
        self.SetMenuBar(self.menubar)
        
        self.box = wx.GridBagSizer(0, 0)

        self.controlBox = wx.BoxSizer(wx.VERTICAL)

        self.controlPanel = Control.CECControl(self, -1)
        togglePopupPanel, objs, tpsize = self.createTogglePopupPanel()        
        slidersPanel, slPanelSize = self.createHorizontalSlidersPanel()
        self.grapher = getGrapher(self)
        presetPanel = Preset.CECPreset(self)
        CeciliaLib.setPresetPanel(presetPanel)

        self.controlBox.Add(self.controlPanel, 1, wx.EXPAND | wx.RIGHT, -1)
        self.controlBox.Add(presetPanel, 0, wx.EXPAND | wx.TOP | wx.RIGHT, -1)
        self.controlBox.Add(togglePopupPanel, 0, wx.EXPAND | wx.TOP | wx.RIGHT, -1)

        self.box.Add(self.controlBox, (0,0), span=(2,1), flag=wx.EXPAND)
        self.box.Add(self.grapher, (0,1), flag=wx.EXPAND)
        self.box.Add(slidersPanel, (1,1), flag=wx.EXPAND | wx.TOP, border=-1)
        
        self.box.AddGrowableCol(1, 1)
        self.box.AddGrowableRow(0, 1)

        pos, size = self.positionToClientArea(CeciliaLib.getInterfacePosition(), CeciliaLib.getInterfaceSize())

        self.SetSizer(self.box)        
        self.SetSize(size)

        self.Bind(wx.EVT_CLOSE, self.onClose)

        if pos == None:
            self.Center()
        else:
            self.SetPosition(pos)    

        wx.CallAfter(self.createGrapher)

    def positionToClientArea(self, pos, size):
        position = None
        screen = 0
        if pos != None:
            for i in range(CeciliaLib.getNumDisplays()):
                off = CeciliaLib.getDisplayOffset()[i]
                dispsize = CeciliaLib.getDisplaySize()[i]
                Xbounds = [off[0], dispsize[0]+off[0]]
                Ybounds = [off[1], dispsize[1]+off[1]]
                if pos[0] >= Xbounds[0] and pos[0] <= Xbounds[1] and pos[1] >= Ybounds[0] and pos[1] <= Ybounds[1]:
                    position = pos
                    screen = i
                    break
        dispsize = CeciliaLib.getDisplaySize()[screen]
        if size[0] <= dispsize[0] and size[1] <= dispsize[1]:
            newsize = size
        else:
            newsize = (dispsize[0]-50, dispsize[1]-50)
        return position, newsize        
                 
    def updateTitle(self, title):
        self.SetTitle(title)

    def createTogglePopupPanel(self):
        panel = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        panel.SetBackgroundColour(BACKGROUND_COLOUR)
        box, objs = buildTogglePopupBox(panel, CeciliaLib.getInterfaceWidgets())
        panel.SetSizerAndFit(box)
        CeciliaLib.setUserTogglePopups(objs)
        size = panel.GetSize()
        return panel, objs, size

    def createHorizontalSlidersPanel(self):
        panel = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        panel.SetBackgroundColour(BACKGROUND_COLOUR)
        box, sl = buildHorizontalSlidersBox(panel, CeciliaLib.getInterfaceWidgets())
        CeciliaLib.setUserSliders(sl)
        panel.SetSizerAndFit(box)
        size = panel.GetSize()
        return panel, size

    def onChangeSlidersPanelSize(self, evt):
        self.horizontalSlidersPanel.Layout()
        self.horizontalSlidersPanel.Refresh()
        
    def createGrapher(self):
        graph = buildGrapher(self.grapher, CeciliaLib.getInterfaceWidgets(), CeciliaLib.getTotalTime())
        CeciliaLib.setGrapher(graph)
        return graph

    def onClose(self, event):
        CeciliaLib.setInterfaceSize(self.GetSize())
        CeciliaLib.setInterfacePosition(self.GetPosition())
        CeciliaLib.resetWidgetVariables()
        try:
            self.Destroy()
        except:
            pass
        CeciliaLib.getCeciliaEditor().Show()
        
    def getControlPanel(self):
        return self.controlPanel

    def onUndo(self, evt):
        self.grapher.plotter.undoRedo(1)

    def onRedo(self, event):
        self.grapher.plotter.undoRedo(-1)

    def onCopy(self, event):
        self.grapher.plotter.onCopy()

    def onPaste(self, event):
        self.grapher.plotter.onPaste()
        
    def updateNchnls(self):
        self.controlPanel.updateNchnls()
