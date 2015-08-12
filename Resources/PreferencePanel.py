# -*- coding: utf-8 -*-
"""
Copyright 2009 iACT, universite de Montreal, Jean Piche, Olivier Belanger, 
Dominic Thibault

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

import wx, sys, os
import  wx.lib.scrolledpanel as scrolled
from constants import *
import CeciliaLib
from Widgets import *

PADDING = 10

class PreferenceFrame(wx.Frame):
    def __init__(self, parent):
        style = wx.CLIP_CHILDREN | wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED | wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, style = style)
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.parent = parent

        self.font = wx.Font(MENU_FONT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, face=FONT_FACE)

        self.SetClientSize((350, 355))

        panel = wx.Panel(self, -1)
        w, h = self.GetSize()
        panel.SetBackgroundColour(BACKGROUND_COLOUR)
        
        box = wx.BoxSizer(wx.VERTICAL)

        ### Title and Toolbar ###
        title = FrameLabel(panel, "Cecilia Preferences", size=(w-2, 24))
        box.Add(title, 0, wx.ALL, 1)

        headerSizer = wx.FlexGridSizer(1,2,5,5)
        headerSizer.AddGrowableCol(1, 1)
        self.panelTitles = ['  Paths', '  Audio', '   Midi', 'Csound', ' Cecilia']
        choice = PreferencesRadioToolBox(panel, size=(125,25), 
                                         outFunction=self.onPageChange)
        self.panelTitle = wx.StaticText(panel, -1, ' Paths')
        self.panelTitle.SetFont(self.font)
        headerSizer.AddMany([(choice, 0, wx.LEFT, 1), 
                             (self.panelTitle, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 90)
                            ])
                                        
        box.Add(headerSizer, 0, wx.ALL, 1)
        box.Add(wx.StaticLine(panel, -1, size=(346, 1)), 0, wx.LEFT, 2)
        box.AddSpacer(5)

        self.panelsBox = wx.BoxSizer(wx.HORIZONTAL)
        pathsPane = self.createPathsPanel(panel)
        audioPane = self.createAudioPanel(panel)
        audioPane.Hide()
        midiPane = self.createMidiPanel(panel)
        midiPane.Hide()
        csoundPane = self.createCsoundPanel(panel)
        csoundPane.Hide()
        ceciliaPane = self.createCeciliaPanel(panel)
        ceciliaPane.Hide()
        self.panels = [pathsPane, audioPane, midiPane, csoundPane, ceciliaPane]
        self.currentPane = 0
        self.panelsBox.Add(self.panels[self.currentPane], 1)
        box.Add(self.panelsBox, 0, wx.TOP, 10)
        
        box.AddSpacer(100)
        box.Add(Separator(panel), 0, wx.EXPAND | wx.BOTTOM, 10)
        closerBox = wx.BoxSizer(wx.HORIZONTAL)
        closer = CloseBox(panel, outFunction=self.onClose)
        closerBox.Add(closer, 0, wx.LEFT, 288)
        box.Add(closerBox)

        panel.SetSizerAndFit(box)

    def onClose(self, event=None):
        CeciliaLib.writeVarToDisk()
        self.Destroy()

    def onPageChange(self, index):
        self.panels[self.currentPane].Hide()    
        self.panels[index].Show()        
        self.panels[index].SetPosition(self.panelsBox.GetPosition())
        self.panelsBox.Replace(self.panels[self.currentPane], self.panels[index])
        self.currentPane = index
        self.panelTitle.SetLabel(self.panelTitles[self.currentPane])
        self.Refresh()
                    
    def createPathsPanel(self, panel):
        pathsPanel = wx.Panel(panel)
        pathsPanel.SetBackgroundColour(BACKGROUND_COLOUR)
        gridSizer = wx.FlexGridSizer(0,2,2,5)

        #Soundfile Player
        textSfPlayerLabel = wx.StaticText(pathsPanel, -1, 'Soundfile Player :')
        textSfPlayerLabel.SetFont(self.font)
        self.textSfPlayerPath = wx.TextCtrl(pathsPanel, -1, CeciliaLib.getSoundfilePlayerPath(), 
                                            size=(270,16), style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
        self.textSfPlayerPath.SetFont(self.font)       
        self.textSfPlayerPath.Bind(wx.EVT_TEXT_ENTER, self.handleSfPlayerPath)
        self.textSfPlayerPath.SetForegroundColour((50,50,50))
        self.textSfPlayerPath.SetBackgroundColour("#AAAAAA")
        buttonSfPlayerPath = CloseBox(pathsPanel, outFunction=self.changeSfPlayer, label='Set...')           

        #Soundfile Editor
        textSfEditorLabel = wx.StaticText(pathsPanel, -1, 'Soundfile Editor :')
        textSfEditorLabel.SetFont(self.font)       
        self.textSfEditorPath = wx.TextCtrl(pathsPanel, -1, CeciliaLib.getSoundfileEditorPath(), 
                                            size=(270,16), style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
        self.textSfEditorPath.SetFont(self.font)       
        self.textSfEditorPath.Bind(wx.EVT_TEXT_ENTER, self.handleSfEditorPath)
        self.textSfEditorPath.SetForegroundColour((50,50,50))
        self.textSfEditorPath.SetBackgroundColour("#AAAAAA")
        buttonSfEditorPath = CloseBox(pathsPanel, outFunction=self.changeSfEditor, label='Set...')           

        textPrefPathLabel = wx.StaticText(pathsPanel, -1, 'Preferred paths :')
        textPrefPathLabel.SetFont(self.font)       
        self.textPrefPath = wx.TextCtrl(pathsPanel, -1, CeciliaLib.getPrefPath(), 
                                        size=(270,16), style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
        self.textPrefPath.SetFont(self.font)       
        self.textPrefPath.Bind(wx.EVT_TEXT_ENTER, self.handleEditPrefPath)
        self.textPrefPath.SetForegroundColour((50,50,50))
        self.textPrefPath.SetBackgroundColour("#AAAAAA")
        buttonPrefPath = CloseBox(pathsPanel, outFunction=self.addPrefPath, label='Add...')           

        gridSizer.AddMany([ 
                            (textSfPlayerLabel, 0, wx.EXPAND | wx.LEFT, PADDING),
                            (wx.StaticText(pathsPanel), 0, wx.EXPAND | wx.RIGHT, 15),
                            (self.textSfPlayerPath, 0, wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (buttonSfPlayerPath, 0, wx.RIGHT, 15),
                            (textSfEditorLabel, 0, wx.EXPAND | wx.LEFT | wx.TOP, PADDING),
                            (wx.StaticText(pathsPanel, -1, ''), 0, wx.EXPAND | wx.RIGHT, 15),
                            (self.textSfEditorPath, 0, wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (buttonSfEditorPath, 0, wx.RIGHT, 15),
                            (textPrefPathLabel, 0, wx.EXPAND | wx.LEFT | wx.TOP, PADDING),
                            (wx.StaticText(pathsPanel, -1, ''), 0, wx.EXPAND | wx.RIGHT, 15),
                            (self.textPrefPath, 0,  wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (buttonPrefPath, 0, wx.RIGHT, 15),
                            ])
        gridSizer.AddGrowableCol(0, 1)
        
        self.textPrefPath.Navigate()
        panel.SetSizerAndFit(gridSizer)
        return pathsPanel

    def createCeciliaPanel(self, panel):
        ceciliaPanel = wx.Panel(panel)
        ceciliaPanel.SetBackgroundColour(BACKGROUND_COLOUR)
        gridSizer = wx.FlexGridSizer(3,3,10,3)

        textTotalTime = wx.StaticText(ceciliaPanel, 0, 'Total time default (sec) :')
        textTotalTime.SetFont(self.font)       
        self.choiceTotalTime = CustomMenu(ceciliaPanel, 
                                    choice= ["10.0", "30.0", "60.0", "120.0", "300.0", "600.0", "1200.0", "2400.0", "3600.0"], 
                                    init=str(CeciliaLib.getDefaultTotalTime()), outFunction=self.changeDefaultTotalTime)

        textUseTooltips = wx.StaticText(ceciliaPanel, 0, 'Use tooltips :')
        textUseTooltips.SetFont(self.font)       
        self.tooltipsToggle = Toggle(ceciliaPanel, CeciliaLib.getUseTooltips(), outFunction=self.enableTooltips)                              

        textgraphTexture = wx.StaticText(ceciliaPanel, 0, 'Use grapher texture :')
        textgraphTexture.SetFont(self.font)       
        self.textureToggle = Toggle(ceciliaPanel, CeciliaLib.getUseGraphTexture(), outFunction=self.enableGraphTexture)                              

        gridSizer.AddMany([ 
                            (textTotalTime, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(ceciliaPanel, -1, '', size=(86,-1)), 1, wx.EXPAND),
                            (self.choiceTotalTime, 0, wx.ALIGN_CENTER_VERTICAL),
                            (textUseTooltips, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(ceciliaPanel, -1, ''), 1, wx.EXPAND),
                            (self.tooltipsToggle, 0, wx.ALIGN_CENTER_VERTICAL),
                            (textgraphTexture, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(ceciliaPanel, -1, ''), 1, wx.EXPAND),
                            (self.textureToggle, 0, wx.ALIGN_CENTER_VERTICAL),
                         ])

        gridSizer.AddGrowableCol(1, 1)
        ceciliaPanel.SetSizerAndFit(gridSizer)
        return ceciliaPanel

    def createCsoundPanel(self, panel):
        csoundPanel = wx.Panel(panel)
        csoundPanel.SetBackgroundColour(BACKGROUND_COLOUR)
        gridSizer = wx.FlexGridSizer(3,3,10,3)

        textKsmps = wx.StaticText(csoundPanel, 0, 'ksmps :')
        textKsmps.SetFont(self.font)       
        self.choiceKsmps = CustomMenu(csoundPanel, choice= ["1", "2", "5", "10", "25", "50", "100"], 
                                      init=str(CeciliaLib.getKsmps()), outFunction=self.changeKsmps)

        textHardbuff = wx.StaticText(csoundPanel, 0, 'Hardware buffer :')
        textHardbuff.SetFont(self.font)       
        self.choiceHardBuff = CustomMenu(csoundPanel, choice=HARD_BUFF_SIZES, 
                                        init=str(CeciliaLib.getHardBuf()), outFunction=self.changeHardBuff)

        textSoftbuff = wx.StaticText(csoundPanel, 0, 'Software buffer :')
        textSoftbuff.SetFont(self.font)       
        self.choiceSoftBuff = CustomMenu(csoundPanel, choice=SOFT_BUFF_SIZES, 
                                        init=str(CeciliaLib.getSoftBuf()), outFunction=self.changeSoftBuff)

        gridSizer.AddMany([ 
                            (textKsmps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(csoundPanel, -1, '', size=(125,-1)), 1, wx.EXPAND),
                            (self.choiceKsmps, 0, wx.ALIGN_CENTER_VERTICAL),
                            (textHardbuff, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(csoundPanel, -1, ''), 1, wx.EXPAND),
                            (self.choiceHardBuff, 0, wx.ALIGN_CENTER_VERTICAL),
                            (textSoftbuff, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(csoundPanel, -1, ''), 1, wx.EXPAND),
                            (self.choiceSoftBuff, 0, wx.ALIGN_CENTER_VERTICAL),
                         ])

        gridSizer.AddGrowableCol(1, 1)
        csoundPanel.SetSizerAndFit(gridSizer)
        return csoundPanel

    def createMidiPanel(self, panel):        
        midiParamPanel = wx.Panel(panel)
        midiParamPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        box = wx.BoxSizer(wx.VERTICAL)

        # Audio driver
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        textInOutConfig = wx.StaticText(midiParamPanel, 0, 'Midi Driver :')
        textInOutConfig.SetFont(self.font)       
        self.midiDriverChoice = CustomMenu(midiParamPanel, choice=['PortMidi'], 
                                       init='PortMidi', outFunction=self.onMidiDriverPageChange)
        box1.Add(textInOutConfig, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING)
        box1.AddStretchSpacer()
        box1.Add(self.midiDriverChoice, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        self.midiDriverBox = wx.BoxSizer(wx.VERTICAL)
        self.midiDriverCurrentPane = self.midiDriverChoice.getIndex()
        self.midiDriverPanels = []
        portmidiPane = self.createPortmidiPane(midiParamPanel)
        if self.midiDriverCurrentPane != 0:
            portmidiPane.Hide()
        self.midiDriverPanels.append(portmidiPane)
        self.midiDriverBox.Add(self.midiDriverPanels[self.midiDriverCurrentPane])

        box.Add(box1, 0, wx.EXPAND)
        box.AddSpacer(20)
        box.Add(self.midiDriverBox)
        midiParamPanel.SetSizerAndFit(box)
        return midiParamPanel

    def createAudioPanel(self, panel):        
        audioParamPanel = wx.Panel(panel)
        audioParamPanel.SetBackgroundColour(BACKGROUND_COLOUR)
        
        box = wx.BoxSizer(wx.VERTICAL)

        # Audio driver
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        textInOutConfig = wx.StaticText(audioParamPanel, 0, 'Audio Driver :')
        textInOutConfig.SetFont(self.font)       
        self.driverChoice = CustomMenu(audioParamPanel, choice=AUDIO_DRIVERS, 
                                       init=CeciliaLib.getAudioPort(), 
                                       outFunction=self.onDriverPageChange)

        box1.Add(textInOutConfig, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING)
        box1.AddStretchSpacer()
        box1.Add(self.driverChoice, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Audio driver panels
        self.driverBox = wx.BoxSizer(wx.VERTICAL)
        self.driverCurrentPane = self.driverChoice.getLabel()
        self.driverPanels = {}
        coreaudioPane = self.createCoreaudioPane(audioParamPanel)
        portaudioPane = self.createPortaudioPane(audioParamPanel)
        jackPane = self.createJackPane(audioParamPanel)
        if self.driverCurrentPane != 'CoreAudio':
            coreaudioPane.Hide()
        if self.driverCurrentPane != 'PortAudio':    
            portaudioPane.Hide()
        if self.driverCurrentPane != 'Jack':
            jackPane.Hide()
        self.driverPanels['CoreAudio'] = coreaudioPane
        self.driverPanels['PortAudio'] = portaudioPane
        self.driverPanels['Jack'] = jackPane
        self.driverBox.Add(self.driverPanels[self.driverCurrentPane])
        
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # File Format
        textFileFormat = wx.StaticText(audioParamPanel, 0, 'File Format :')
        textFileFormat.SetFont(self.font)       
        self.choiceFileFormat = CustomMenu(audioParamPanel, choice=AUDIO_FILE_FORMATS, 
                                      init=CeciliaLib.getFileType(), outFunction=self.changeFileType)
        box2.Add(textFileFormat, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING)
        box2.AddStretchSpacer()
        box2.Add(self.choiceFileFormat, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Bit depth
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        textBD = wx.StaticText(audioParamPanel, 0, 'Bit Depth :')
        textBD.SetFont(self.font)       
        self.choiceBD = CustomMenu(audioParamPanel, choice=BIT_DEPTHS.keys(), outFunction=self.changeSampSize)
        box3.Add(textBD, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING)
        box3.AddStretchSpacer()
        box3.Add(self.choiceBD, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        for item in BIT_DEPTHS.items():
            if item[1]==CeciliaLib.getSampleSize():
                self.choiceBD.setStringSelection(item[0])
                        
        # Number of channels
        formats, selectedNCHNLS = self.defineFormatsList()
        
        box4 = wx.BoxSizer(wx.HORIZONTAL)
        textNCHNLS = wx.StaticText(audioParamPanel, 0, '# of channels :')
        textNCHNLS.SetFont(self.font)       
        self.choiceNCHNLS = CustomMenu(audioParamPanel, choice=formats, 
                            init=selectedNCHNLS, outFunction=self.changeNchnls)        
        box4.Add(textNCHNLS, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING)
        box4.AddStretchSpacer()
        box4.Add(self.choiceNCHNLS, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
 
        # Sampling rate
        box5 = wx.BoxSizer(wx.HORIZONTAL)
        textSR = wx.StaticText(audioParamPanel, 0, 'Sample Rate :')
        textSR.SetFont(self.font)       
        self.comboSR = CustomMenu(audioParamPanel, choice=SAMPLE_RATES, 
                            init=str(CeciliaLib.getSr()), outFunction=self.changeSr)        
        box5.Add(textSR, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING)
        box5.AddStretchSpacer()
        box5.Add(self.comboSR, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        box.Add(box1, 0, wx.EXPAND)
        box.AddSpacer(20)
        box.Add(self.driverBox)
        box.AddSpacer([60,30,20,60][['CoreAudio', 'PortAudio', 'Jack'].index(self.driverCurrentPane)])
        box.Add(box2, 0, wx.EXPAND)
        box.Add(box3, 0, wx.EXPAND | wx.TOP, 5)
        box.Add(box4, 0, wx.EXPAND | wx.TOP, 5)
        box.Add(box5, 0, wx.EXPAND | wx.TOP, 5)
        audioParamPanel.SetSizerAndFit(box)
        return audioParamPanel

    def createPortmidiPane(self, panel):
        portmidiPanel = wx.Panel(panel)
        portmidiPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        gridSizer = wx.FlexGridSizer(5, 3, 5, 5)
        # Input
        textIn = wx.StaticText(portmidiPanel, 0, 'Input Device :')
        textIn.SetFont(self.font)       
        availableMidiIns = []
        for d in CeciliaLib.getAvailableMidiInputs():
            availableMidiIns.append(CeciliaLib.ensureNFD(d))
        if availableMidiIns != [] and 'All' not in availableMidiIns:
            availableMidiIns.append('All')
        if CeciliaLib.getMidiDeviceIn() != '':
            try:
                initInput = availableMidiIns[int(CeciliaLib.getMidiDeviceIn())]
            except:
                initInput = 'dump'    
        else:
            initInput = 'dump'    
        self.midiChoiceInput = CustomMenu(portmidiPanel, choice=availableMidiIns, 
                                      init=initInput, size=(168,20), outFunction=self.changeMidiInput)

        gridSizer.AddMany([ 
                            (textIn, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                             (wx.StaticText(portmidiPanel, -1, '', size=(74,-1)), 1, wx.EXPAND),
                            (self.midiChoiceInput, 0, wx.ALIGN_CENTER_VERTICAL),
                            ])
                            
        gridSizer.AddGrowableCol(1, 1)
        portmidiPanel.SetSizerAndFit(gridSizer)
        return portmidiPanel

    def createPortaudioPane(self, panel):
        portaudioPanel = wx.Panel(panel)
        portaudioPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        gridSizer = wx.FlexGridSizer(5, 3, 5, 5)
        # Input
        textIn = wx.StaticText(portaudioPanel, 0, 'Input Device :')
        textIn.SetFont(self.font)       
        availableAudioIns = []
        for d in CeciliaLib.getAvailableAudioInputs():
            availableAudioIns.append(CeciliaLib.ensureNFD(d))
        if CeciliaLib.getAudioInput() != '':
            try:
                initInput = availableAudioIns[int(CeciliaLib.getAudioInput())]
            except:
                initInput = 'dump'
        else:
            initInput = 'dump'    
        self.choiceInput = CustomMenu(portaudioPanel, choice=availableAudioIns, 
                                      init=initInput, size=(168,20), 
                                      outFunction=self.changeAudioInput)
        if CeciliaLib.getAudioInput() == '' or CeciliaLib.getEnableAudioInput() == 0:
            initInputState = 0
        else:
            initInputState = 1
        self.inputToggle = Toggle(portaudioPanel, initInputState, 
                                  outFunction=self.enableAudioInput)                              
        
        # Output
        textOut = wx.StaticText(portaudioPanel, 0, 'Output Device :')
        textOut.SetFont(self.font)       
        availableAudioOuts = []
        for d in CeciliaLib.getAvailableAudioOutputs():
            availableAudioOuts.append(CeciliaLib.ensureNFD(d))
        try:
            initOutput = availableAudioOuts[int(CeciliaLib.getAudioOutput())]
        except:
            initOutput = availableAudioOuts[0]
        self.choiceOutput = CustomMenu(portaudioPanel, choice=availableAudioOuts, 
                                        init=initOutput, size=(168,20), outFunction=self.changeAudioOutput)
        
        gridSizer.AddMany([ 
                            (textIn, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (self.inputToggle, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 45),
                            (self.choiceInput, 0, wx.ALIGN_CENTER_VERTICAL),
                            (textOut, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(portaudioPanel, -1, '', size=(65,-1)), 1, wx.EXPAND),
                            (self.choiceOutput, 0, wx.ALIGN_CENTER_VERTICAL),
                            ])
        gridSizer.AddGrowableCol(1, 1)
        portaudioPanel.SetSizerAndFit(gridSizer)
        return portaudioPanel

    def createCoreaudioPane(self, panel):
        coreaudioPanel = wx.Panel(panel)
        coreaudioPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        box = wx.BoxSizer(wx.VERTICAL)

        self.openCoreaudioButton = CloseBox(coreaudioPanel, size=(200,20), 
                                    outFunction=self.openAudioMidiSetup, label='Open Audio MIDI Setup')
        box.Add(self.openCoreaudioButton, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 75)
        
        coreaudioPanel.SetSizerAndFit(box)
        return coreaudioPanel

    def createJackPane(self, panel):
        jackPanel = wx.Panel(panel)
        jackPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        gridSizer = wx.FlexGridSizer(3, 3, 5, 5)
        
        jackClientLabel = wx.StaticText(jackPanel, -1, 'Jack client :')
        jackClientLabel.SetFont(self.font)       
        self.jackClient = wx.TextCtrl(jackPanel, -1, CeciliaLib.getJackParams()['client'], size=(235,-1), style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
        self.jackClient.SetFont(self.font)       
        self.jackClient.Bind(wx.EVT_TEXT_ENTER, self.changeJackClient)
        self.jackClient.SetForegroundColour((50,50,50))
        self.jackClient.SetBackgroundColour("#999999")

        jackInPortLabel = wx.StaticText(jackPanel, -1, 'In Port :')
        jackInPortLabel.SetFont(self.font)       
        self.jackInPort = wx.TextCtrl(jackPanel, -1, CeciliaLib.getJackParams()['inPortName'], size=(235,-1), style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
        self.jackInPort.SetFont(self.font)       
        self.jackInPort.Bind(wx.EVT_TEXT_ENTER, self.changeJackInPort)
        self.jackInPort.SetForegroundColour((50,50,50))
        self.jackInPort.SetBackgroundColour("#999999")

        jackOutPortLabel = wx.StaticText(jackPanel, -1, 'Out Port :')
        jackOutPortLabel.SetFont(self.font)       
        self.jackOutPort = wx.TextCtrl(jackPanel, -1, CeciliaLib.getJackParams()['outPortName'], size=(235,-1), style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
        self.jackOutPort.SetFont(self.font)       
        self.jackOutPort.Bind(wx.EVT_TEXT_ENTER, self.changeJackOutPort)
        self.jackOutPort.SetForegroundColour((50,50,50))
        self.jackOutPort.SetBackgroundColour("#999999")

        gridSizer.AddMany([ 
                            (jackClientLabel, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(jackPanel, -1, '', size=(15,-1)), 1, wx.EXPAND),
                            (self.jackClient, 0, wx.ALIGN_CENTER_VERTICAL),
                            (jackInPortLabel, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(jackPanel, -1, ''), 1, wx.EXPAND),
                            (self.jackInPort, 0, wx.ALIGN_CENTER_VERTICAL),
                            (jackOutPortLabel, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, PADDING),
                            (wx.StaticText(jackPanel, -1, ''), 1, wx.EXPAND),
                            (self.jackOutPort, 0, wx.ALIGN_CENTER_VERTICAL),
                         ])
        
        gridSizer.AddGrowableCol(1, 1)
        jackPanel.SetSizerAndFit(gridSizer)
        return jackPanel

    def onDriverPageChange(self, index, label):
        CeciliaLib.setAudioPort(label)
        self.driverPanels[self.driverCurrentPane].Hide()    
        self.driverPanels[label].Show()        
        self.driverPanels[label].SetPosition(self.driverBox.GetPosition())
        self.driverBox.Replace(self.driverPanels[self.driverCurrentPane], self.driverPanels[label])
        self.driverCurrentPane = label
        self.Refresh()

    def onMidiDriverPageChange(self, index, label):
        pass
        
    def openAudioMidiSetup(self):
        os.system('open /Applications/Utilities/Audio\ MIDI\ Setup.app')

    def enableAudioInput(self, state):
        CeciliaLib.setEnableAudioInput(state)
        if state == 1:
            CeciliaLib.setAudioInput(str(self.choiceInput.getIndex()))
        else:
            CeciliaLib.setAudioInput('')

    def changeAudioInput(self, index, label):
        CeciliaLib.setAudioInput(index)

    def changeAudioOutput(self, index, label):
        CeciliaLib.setAudioOutput(index)

    def changeMidiInput(self, index, label):
        CeciliaLib.setMidiDeviceIn(index)

    def changeSfPlayer(self):
        if CeciliaLib.getPlatform() == 'win32':
            wildcard =  "Executable files (*.exe)|*.exe|"     \
                        "All files (*.*)|*.*"
        elif CeciliaLib.getPlatform() == 'darwin':
            wildcard =  "Application files (*.app)|*.app|"     \
                        "All files (*.*)|*.*"
        else:
            wildcard = "All files (*.*)|*.*"

        path = ''
        dlg = wx.FileDialog(self, message="Choose a soundfile player...",
                                 defaultDir=os.path.expanduser('~'),
                                 wildcard=wildcard,
                                 style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()   
        dlg.Destroy()

        if path:
            CeciliaLib.setSoundfilePlayerPath(path)
            self.textSfPlayerPath.SetValue(path)

    def changeSfEditor(self):
        if CeciliaLib.getPlatform() == 'win32':
            wildcard =  "Executable files (*.exe)|*.exe|"     \
                        "All files (*.*)|*.*"
        elif CeciliaLib.getPlatform() == 'darwin':
            wildcard =  "Application files (*.app)|*.app|"     \
                        "All files (*.*)|*.*"
        else:
            wildcard = "All files (*.*)|*.*"

        path = ''
        dlg = wx.FileDialog(self, message="Choose a soundfile editor...",
                                 defaultDir=os.path.expanduser('~'),
                                 wildcard=wildcard,
                                 style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()   
        dlg.Destroy() 

        if path:
            CeciliaLib.setSoundfileEditorPath(path)
            self.textSfEditorPath.SetLabel(path)

    def addPrefPath(self):
        currentPath = CeciliaLib.getPrefPath()

        path = ''
        dlg = wx.DirDialog(self, message="Choose a folder...",
                                 defaultPath=os.path.expanduser('~'))

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()   
        dlg.Destroy()

        if path and currentPath != '':
            path = currentPath + ';' + path
        elif not path:
            return

        CeciliaLib.setPrefPath(path)
        self.textPrefPath.SetValue(path)

    def handleSfPlayerPath(self, event):
        path = self.textSfPlayerPath.GetValue()
        CeciliaLib.setSoundfilePlayerPath(path)
        self.textSfPlayerPath.Navigate()

    def handleSfEditorPath(self, event):
        path = self.textSfEditorPath.GetValue()
        CeciliaLib.setSoundfileEditorPath(path)
        self.textSfEditorPath.Navigate()

    def handleEditPrefPath(self, event):
        path = self.textPrefPath.GetValue()
        CeciliaLib.setPrefPath(path)
        self.textPrefPath.Navigate()

    def changeFileType(self, index, label):
        CeciliaLib.setFileType(label)

    def changeSr(self, index, label):
        sr = int(label.strip())
        CeciliaLib.setSr(sr)
        ksmps = CeciliaLib.getKsmps()

        kr = sr/ksmps
        CeciliaLib.setKr(kr)

    def changeSampSize(self, index, label):
        CeciliaLib.setSampleSize(BIT_DEPTHS[label])

    def defineFormatsList(self):
        formats=[]
        self.formatDict=dict()
        selectedNCHNLS = ''
        for format in CeciliaLib.getSupportedFormats().items():
            if format[0]!='Custom...':
                self.formatDict[format[1]] = format[0]

        if self.formatDict.has_key(CeciliaLib.getNchnls()):
            selectedNCHNLS = self.formatDict[CeciliaLib.getNchnls()]
        else:
            selectedNCHNLS = 'Custom...'

        formatsNCHNLS=self.formatDict.keys()
        formatsNCHNLS.sort()
        for i in formatsNCHNLS:
            formats.append(self.formatDict[i])
        formats.append('Custom...')

        return formats, selectedNCHNLS

    def changeNchnls(self, index, choice):
        if choice == 'Custom...':
            nchnls = CeciliaLib.dialogSelectCustomNchnls(self)
            if nchnls==None:
                nchnls = CeciliaLib.getNchnls()
                if nchnls in self.formatDict.keys():
                    self.choiceNCHNLS.SetStringSelection(self.formatDict[nchnls])
                else:
                    self.choiceNCHNLS.SetStringSelection('Custom...')
                return

            if not nchnls in self.formatDict.keys():
                CeciliaLib.setCustomSupportedFormats(nchnls)
                self.choiceNCHNLS.SetStringSelection('Custom...')
            else:
                self.choiceNCHNLS.SetStringSelection(self.formatDict[nchnls])
        else:
            nchnls = CeciliaLib.getSupportedFormats()[choice]

        CeciliaLib.setNchnls(nchnls)

    def changeJackClient(self, event):
        CeciliaLib.setJackParams(client=event.GetString())

    def changeJackInPort(self, event):        
        CeciliaLib.setJackParams(inPortName=event.GetString())

    def changeJackOutPort(self, event):
        CeciliaLib.setJackParams(outPortName=event.GetString())

    def updateMidiIn(self):
        CeciliaLib.queryAudioMidiDrivers()

        inputs = CeciliaLib.getAvailableMidiInputs()

        if inputs == []:
            self.midiChoiceInput.setChoice([''])
        else:
            inputs.append('All')
            self.midiChoiceInput.setChoice(inputs)
            self.midiChoiceInput.setByIndex(int(CeciliaLib.getMidiDeviceIn()))
        
    def updateAudioInOut(self):
        CeciliaLib.queryAudioMidiDrivers()

        inputs = CeciliaLib.getAvailableAudioInputs()
        outputs = CeciliaLib.getAvailableAudioOutputs()

        if inputs == []:
            self.choiceInput.setChoice([''])
        else:
            self.choiceInput.setChoice(inputs)
            if CeciliaLib.getAudioInput()=='':
                self.inputToggle.setValue(0)
            else:
                self.inputToggle.setValue(1)
                self.choiceInput.setByIndex(int(CeciliaLib.getAudioInput()))

        if outputs == []:
            self.choiceOutput.setChoice([''])
        else:
            self.choiceOutput.setChoice(outputs)
            self.choiceOutput.setByIndex(int(CeciliaLib.getAudioOutput()))

    def changeKsmps(self, index, label):
        ksmps = int(self.choiceKsmps.getLabel().strip())
        CeciliaLib.setKsmps(ksmps)
        sr = CeciliaLib.getSr()

        kr = sr/ksmps
        CeciliaLib.setKr(kr)

    def changeHardBuff(self, index, label):
        hardBuff = int(self.choiceHardBuff.getLabel())

        if hardBuff < CeciliaLib.getSoftBuf():
            self.choiceHardBuff.setLabel(str(CeciliaLib.getHardBuf()))
        else:    
            CeciliaLib.setHardBuf(hardBuff)

    def changeSoftBuff(self, index, label):
        softBuff = int(self.choiceSoftBuff.getLabel())

        if softBuff > CeciliaLib.getHardBuf():
            self.choiceSoftBuff.setLabel(str(CeciliaLib.getSoftBuf()))
        else:    
            CeciliaLib.setSoftBuf(softBuff)

    def changeDefaultTotalTime(self, index, label):
        CeciliaLib.setDefaultTotalTime(float(self.choiceTotalTime.getLabel().strip()))

    def enableTooltips(self, state):
        CeciliaLib.setUseTooltips(state)

    def enableGraphTexture(self, state):
        CeciliaLib.setUseGraphTexture(state)
        if CeciliaLib.getGrapher() != None:
            CeciliaLib.getGrapher().plotter.draw()
