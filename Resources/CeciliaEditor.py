#! /usr/bin/env python
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

import wx
import wx.richtext as rt
from wx.lib.splitter import MultiSplitterWindow
import wx.stc  as  stc
import os, sys, math, re, string, time, keyword, webbrowser, codecs
import wx.html
from constants import *
import CeciliaLib
import PreferencePanel 
from menubar import CeciliaMenuBar
import CeciliaInterface
from opcodes import *
from Widgets import *
from scoreInterpreter import scoreFormat
from types import DictType, IntType

statusBar = None

class CeciliaEditor(wx.Frame):
    def __init__(self, parent, id, title = '', pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE|wx.WANTS_CHARS):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        
        global statusBar
        
        self.menubar = CeciliaMenuBar(self, self)
        self.SetMenuBar(self.menubar)

        self.updateTitle()

        self.prefs = None
        self.time = 0
        self.interfacePosition = wx.DefaultPosition
        self.interfaceSize = wx.DefaultSize
        self.anchor1 = self.anchor2 = 0
       
        self.sash_props = [.2, .6]
      
        activeOrchestra = "Stereo"
        for key, val in CeciliaLib.getSupportedFormats().items():
            if val == CeciliaLib.getNchnls():
                activeOrchestra = key
        self.activeOrchestra = activeOrchestra
        self.activeScore = "Csound"

        self.orchestraPanels = {}
        self.scorePanels = {}

        vbox = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Transport panel
        trPanel = wx.Panel(self, -1, style=wx.EXPAND)
        trPanel.SetBackgroundColour(TITLE_BACK_COLOUR)
        trBox = wx.FlexGridSizer(1,3,5,0)
        self.transportButtons = Transport(trPanel, 
                                          outPlayFunction=self.onPlayStop,
                                          outRecordFunction=self.onRec,
                                          backgroundColour=TITLE_BACK_COLOUR, 
                                          borderColour=WIDGET_BORDER_COLOUR)
        self.clocker = Clocker(trPanel, backgroundColour=TITLE_BACK_COLOUR, 
                               borderColour=WIDGET_BORDER_COLOUR)
        fakePanel = wx.Panel(trPanel, -1, size=((trPanel.GetSize()[0], 36)))
        fakePanel.SetBackgroundColour(TITLE_BACK_COLOUR)  
        trBox.Add(self.transportButtons, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        trBox.Add(fakePanel, 0, wx.RIGHT, 20)
        trBox.Add(self.clocker, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        trBox.AddGrowableCol(1)
        trPanel.SetSizer(trBox)
        sizer.Add(trPanel, 0, wx.EXPAND)
        
        # Sets the status bar
        statusBar = self.CreateStatusBar(style=wx.NO_BORDER)
        statusBar.SetToolTip(CECTooltip(TT_OPCODE_HELP))

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(EDITOR_BACK_COLOUR)
        
        # Generates the MultiSplitterWindow
        self.multiSplitter = MultiSplitterWindow(
                                        panel, 
                                        style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH
                                        )
        self.multiSplitter.SetOrientation(wx.VERTICAL)
        self.multiSplitter.SetMinimumPaneSize(SASH_SIZE)
        self.multiSplitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, 
                                self.OnSashChanging)
        vbox.Add(self.multiSplitter, 1, wx.EXPAND)
        panel.SetSizer(vbox)
        sizer.Add(panel, 1, wx.EXPAND)

        # Sets the interface editor
        self.interface = InterfacePanel(self.multiSplitter, "INTERFACE")
        self.multiSplitter.AppendWindow(self.interface)

        # Sets the Orchestra editors
        for format in CeciliaLib.getSupportedFormats():
            self.orchestraPanels[format] = OrchestraPanel(self.multiSplitter, 
                                                          "ORCHESTRA", format)
            if format == self.activeOrchestra:
                self.multiSplitter.AppendWindow(self.orchestraPanels[format])
            else:
                self.orchestraPanels[format].Hide()

        # Sets the Score editors
        for format in SCORE_TYPES:
            self.scorePanels[format] = ScorePanel(self.multiSplitter, 
                                                  "SCORE", format)
            if format == self.activeScore:
                self.multiSplitter.AppendWindow(self.scorePanels[format])
            else:
                self.scorePanels[format].Hide()

        self.SetSizer(sizer)

        self.findFlag = 1
#        self.Bind(wx.EVT_FIND, self.onFindEvent)
#        self.Bind(wx.EVT_FIND_NEXT, self.onFindEvent)
#        self.Bind(wx.EVT_FIND_REPLACE, self.onFindEvent)
#        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.onFindEvent)
#        self.Bind(wx.EVT_FIND_CLOSE, self.onFindClose)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.orchestraPanels[self.activeOrchestra].SetFocus()

        wx.CallAfter(self.moveSashPosition)

    def getActiveScore(self):
        return self.activeScore

    def onFlipFrontWindow(self, event):
        modified = CeciliaLib.getIsModified()
        if not CeciliaLib.getInterface():
            self.Show()
            self.Raise()
        else:
            if self.FindFocus() != None:
                if self == self.FindFocus().GetTopLevelParent(): 
                    CeciliaLib.getInterface().Raise()
                else:
                    self.Show()
                    self.Raise()
            else:
                self.Show()
                self.Raise()
        CeciliaLib.setIsModified(modified)

    def setTime(self,curTime=0):
        self.time = curTime
        self.clocker.setTime(curTime)

    def changeOrchestraPanel(self, label):
        if type(label) == IntType:
            nchnls = label
        else:
            nchnls = CeciliaLib.getSupportedFormats()[label]
        if nchnls is None:
            nchnls = CeciliaLib.dialogSelectCustomNchnls(self)
            if nchnls is not None:
                CeciliaLib.setNchnls(nchnls)
        else:
            CeciliaLib.setNchnls(nchnls)
        self.setOrchestraPanel()
        if CeciliaLib.getInterface():        
            CeciliaLib.getControlPanel().updateOutputFormat()

    def setOrchestraPanel(self):
        oldOrchestra = self.activeOrchestra
        nchnls = CeciliaLib.getNchnls()
        newOrchestra = 'Custom...'
        for label, chnls in CeciliaLib.getSupportedFormats().items():
            if chnls == nchnls:
                newOrchestra = label
        
        self.orchestraPanels[oldOrchestra].orchestraChoice.setLabel(oldOrchestra)

        if oldOrchestra == newOrchestra:
            return
        
        self.multiSplitter.ReplaceWindow(self.orchestraPanels[oldOrchestra], 
                                         self.orchestraPanels[newOrchestra])
        self.orchestraPanels[oldOrchestra].Hide()

        self.activeOrchestra = newOrchestra

    def changeScorePanel(self, label):
        oldScore = self.activeScore

        self.scorePanels[oldScore].scoreChoice.setLabel(oldScore)
        if oldScore == label:
            return
        
        self.multiSplitter.ReplaceWindow(self.scorePanels[oldScore], 
                                         self.scorePanels[label])
        self.scorePanels[oldScorePanel].Hide()

        self.activeScore = label
     
    def updateTitle(self, isModified=False):
        title = os.path.split(CeciliaLib.getCurrentCeciliaFile())[1]    
        if CeciliaLib.getBuiltinModule():
            file = title
        else:
            file = CeciliaLib.getCurrentCeciliaFile()
        if not isModified:
            self.SetTitle('Editor - ' + file)
            if CeciliaLib.getInterface():
                CeciliaLib.getInterface().updateTitle('Interface - ' + title)
        else:
            self.SetTitle('*** Editor - ' + file + ' ***')
            if CeciliaLib.getInterface():
                title = '*** Interface - ' + title + ' ***'
                CeciliaLib.getInterface().updateTitle(title)

    def OnResize(self, event):
        self.moveSashPosition()
        event.Skip()

    def OnSashChanging(self, event):
        inter = self.interface.isMaximized
        orch = self.orchestraPanels[self.activeOrchestra].isMaximized
        sco = self.scorePanels[self.activeScore].isMaximized    
        msize = self.multiSplitter.GetSize()[1] - SASH_SIZE
        sash0 = self.multiSplitter.GetSashPosition(0)
        sash1 = self.multiSplitter.GetSashPosition(1)
        if inter and orch:            
            self.sash_props[0] = (sash0-14) / float(msize)
        if orch and sco:                
            self.sash_props[1] = (sash1-14) / float(msize)  
        ssum = sum(self.sash_props[0:2])
        if ssum > 1.0:
            half = (ssum - 1.0) * 0.5
            self.sash_props[0] -= half
            self.sash_props[1] -= half

    def moveSashPosition(self):
        inter = self.interface.isMaximized
        orch = self.orchestraPanels[self.activeOrchestra].isMaximized
        sco = self.scorePanels[self.activeScore].isMaximized    
        msize = self.multiSplitter.GetSize()[1]
        if inter and orch and sco:
            first = int(msize*self.sash_props[0])
            second = int(msize*self.sash_props[1])
        elif inter and not orch and not sco:
            first = (msize-(SASH_SIZE*2)-14)
            second = SASH_SIZE
        elif inter and orch and not sco:
            first = int((msize-(SASH_SIZE*2))*self.sash_props[0]+8)
            second = int((msize-(SASH_SIZE*2))*(1-self.sash_props[0])+8)
        elif inter and not orch and sco:
            first = int((msize-(SASH_SIZE*2))*self.sash_props[0])
            second = SASH_SIZE
        elif not inter and orch and sco:
            first = SASH_SIZE
            second = int((msize-SASH_SIZE)*self.sash_props[1])
        elif not inter and not orch and sco:
            first = SASH_SIZE
            second = SASH_SIZE
        elif not inter and orch and not sco:
            first = SASH_SIZE
            second = (msize-(SASH_SIZE*2)-14)

        if first < SASH_SIZE: 
            first = SASH_SIZE
        elif first > (msize-SASH_SIZE*2):
            first = msize-SASH_SIZE*2-14    
        self.multiSplitter.SetSashPosition(0, first)
        
        if (first + second) > (msize-SASH_SIZE*2):
            second = msize-first-SASH_SIZE-14
        elif (second) < SASH_SIZE:   
            second = SASH_SIZE 
        self.multiSplitter.SetSashPosition(1, second)
       
    def getEditorFocus(self):
        return self.FindFocus()

    def onShortPlayStop(self, event):
        if CeciliaLib.getCsound().isCsoundRunning():
            self.onPlayStop(0)
        else:
            self.onPlayStop(1)
                
    def onPlayStop(self, value):
        if value:
            CeciliaLib.setOutputFile('dac')
            CeciliaLib.startCeciliaSound()
            if CeciliaLib.getInterface():
                CeciliaLib.getControlPanel().transportButtons.setPlay(True)      
        else:
            CeciliaLib.stopCeciliaSound()
        
    def onRec(self, value):
        if value:
            filename = self.onSelectOutputFilename()
            if filename == None:
                CeciliaLib.stopCeciliaSound()
                if CeciliaLib.getInterface():
                    CeciliaLib.getControlPanel().transportButtons.setRecord(False)      
                    CeciliaLib.getControlPanel().transportButtons.setPlay(False)      
                return
            CeciliaLib.setOutputFile(filename)
            CeciliaLib.startCeciliaSound()  
            if CeciliaLib.getInterface():
                CeciliaLib.getControlPanel().transportButtons.setRecord(True)      
                CeciliaLib.getControlPanel().transportButtons.setPlay(True)      
        else:
            CeciliaLib.stopCeciliaSound()

    def onSelectOutputFilename(self):
        if CeciliaLib.getFileType() == 'wav':
            wc = "Wave file|*.wav;*.wave;*.WAV;*.WAVE;*.Wav;*.Wave|" \
                 "All files|*.*"
        elif CeciliaLib.getFileType() == 'aiff':
            wc = "AIFF file|*.aif;*.aiff;*.aifc;*.AIF;*.AIFF;*.Aif;*.Aiff|" \
                 "All files|*.*"
        file = CeciliaLib.saveFileDialog(self, wc, type='Save audio')
        if file is not None:
            CeciliaLib.setSaveAudioFilePath(os.path.split(file)[0])
        return file
                    
    def onStartCsound(self, event):
        if not CeciliaLib.getCsound().isCsoundRunning():
            if CeciliaLib.getInterface():
                CeciliaLib.getControlPanel().resetMeter()
            CeciliaLib.startCeciliaSound()
        else:
            CeciliaLib.stopCeciliaSound()

    def closeInterface(self):
        if CeciliaLib.getInterface():
            self.interfaceSize = CeciliaLib.getInterface().GetSize()
            self.interfacePosition = CeciliaLib.getInterface().GetPosition()
            CeciliaLib.getInterface().onClose(None)
            CeciliaLib.setInterface(None)

    def onNew(self, event):
        CeciliaLib.closeCeciliaFile(self)
        self.changeScorePanel('Csound')
        self.updateTitle()
        self.Show()

    def newRecent(self, file):
        filename = CeciliaLib.ensureNFD(os.path.join(TMP_PATH,'.recent.txt'))
        try:
            f = codecs.open(filename, "r", encoding="utf-8")
            lines = [line.replace("\n", "") for line in f.readlines()]
            f.close()
        except:
            lines = []
        if not file in lines and not 'Resources/modules/' in file:
            f = codecs.open(filename, "w", encoding="utf-8")
            lines.insert(0, file)
            if len(lines) > 20:
                lines = lines[0:20]
            for line in lines:
                f.write(line + '\n')
            f.close()
        subId2 = ID_OPEN_RECENT
        if lines != []:
            for item in self.menubar.openRecentMenu.GetMenuItems():
                self.menubar.openRecentMenu.DeleteItem(item)
            for file in lines:
                self.menubar.openRecentMenu.Append(subId2, CeciliaLib.toSysEncoding(file))
                subId2 += 1
        if subId2 > ID_OPEN_RECENT:
            for i in range(ID_OPEN_RECENT,subId2):
                self.Bind(wx.EVT_MENU, self.openRecent, id=i) 

    def resetEditorSpacing(self):
        for format in CeciliaLib.getSupportedFormats():
            self.orchestraPanels[format].editor.maxSpace = 8
            self.orchestraPanels[format].editor.maxOpcodeLen = 1

    def onOpen(self, event):
        if isinstance(event, wx.CommandEvent):
            CeciliaLib.openCeciliaFile(self)
        elif os.path.isfile(event):
            self.resetEditorSpacing()
            CeciliaLib.openCeciliaFile(self, event)
        self.updateTitle()

    def openRecent(self, event):
        menu = self.GetMenuBar()
        id = event.GetId()
        file = menu.FindItemById(id).GetLabel()
        self.resetEditorSpacing()
        CeciliaLib.openCeciliaFile(self, file)
        self.updateTitle()
        
    def onOpenBuiltin(self, event):
        menu = self.GetMenuBar()
        item = menu.FindItemById(event.GetId())
        filename = item.GetLabel()
        filedict = self.GetMenuBar().getBuiltinFiles()
        for key in filedict.keys():
            if filename in filedict[key]:
                dirname = key
                break
        name = os.path.join(MODULES_PATH, dirname, filename)
        self.resetEditorSpacing()
        CeciliaLib.openCeciliaFile(self, name, True)
        self.updateTitle()

    def onOpenPrefModule(self, event):
        menu = self.GetMenuBar()
        item = menu.FindItemById(event.GetId())
        filename = item.GetLabel()
        filedir = item.GetMenu().GetTitle()
        prefPath = CeciliaLib.getPrefPath()
        prefPaths = prefPath.split(';')
        prefBaseNames = [os.path.basename(path) for path in prefPaths]
        dirname = prefPaths[prefBaseNames.index(filedir)]
        if dirname:
            name = os.path.join(dirname, filename)
            self.resetEditorSpacing()
            CeciliaLib.openCeciliaFile(self, name)
            self.updateTitle()

    def onClose(self, event):
        self.Hide()
        
    def onSave(self, event):
        CeciliaLib.saveCeciliaFile(self, showDialog=False)
        self.updateTitle()

    def onSaveAs(self, event):
        CeciliaLib.saveCeciliaFile(self)
        self.updateTitle()

    def onPreferences(self, event):
        self.prefs = PreferencePanel.PreferenceFrame(self)
        self.prefs.Show()
        self.prefs.Center()

    def onRememberInputSound(self, event):
        state = bool(event.GetInt())
        self.menubar.editMenu.FindItemById(ID_REMEMBER).Check(state)
        if CeciliaLib.getInterface():
            win = CeciliaLib.getInterface()
            win.menubar.editMenu.FindItemById(ID_REMEMBER).Check(state)
        CeciliaLib.setRememberSound(state)

    def checkForUdoWidgets(self):
        text = []
        udoDone = []
        orchText =  self.orchestraPanels[self.activeOrchestra].editor.GetText()
        orchText = orchText.replace('\t', ' ').splitlines()
        udoslist = [udo for udo in os.listdir(UDO_PATH) if not udo.startswith('.')]
        for udo in udoslist:
            for line in orchText:
                line = line.strip()
                # TODO: This may not work with the new syntax
                # Is it possible to call an UDO with the functional syntax?
                if line.find(' ' + udo + ' ') != -1 and \
                        not line.startswith(';') and not udo in udoDone:
                    f = open(os.path.join(UDO_PATH, udo), 'r')
                    udotext = f.read().split('opcode')[0].replace(';', '')
                    f.close()
                    text.extend(udotext.splitlines())
                    udoDone.append(udo)
        return text

    def onUpdateInterface(self, event):
        if event != None:
            snds = []
            if CeciliaLib.getRememberSound():
                for key in CeciliaLib.getUserInputs().keys():
                    if CeciliaLib.getUserInputs()[key]['path'] != '':
                        snds.append(CeciliaLib.getUserInputs()[key]['path'])
        self.closeInterface()
        if CeciliaLib.getCsound().isCsoundRunning():
            CeciliaLib.stopCeciliaSound()
        udosInterfaceLines = self.checkForUdoWidgets()
        intertext = self.interface.editor.GetText()
        CeciliaLib.parseInterfaceText(intertext, udosInterfaceLines)
        title = os.path.split(CeciliaLib.getCurrentCeciliaFile())[1]
        try:
            ceciliaInterface = CeciliaInterface.CeciliaInterface(
                                                None, 
                                                title='Interface - %s' % title, 
                                                editor=self
                                                )
        except:
            e = sys.exc_info()[0]
            e1 = sys.exc_info()[1]
            CeciliaLib.resetWidgetVariables()
            CeciliaLib.showErrorDialog("Failed to build the interface.", 
                                       "Review syntax in the Interface panel\n\n%s\n%s\n." % (e, e1))
            self.Show()
            self.Raise()
            return  
        ceciliaInterface.SetSize(self.interfaceSize)
        ceciliaInterface.SetPosition(self.interfacePosition)
        ceciliaInterface.Show(True)
        CeciliaLib.setInterface(ceciliaInterface)
        if CeciliaLib.getInterface():
            if CeciliaLib.getPresets() != {}:
                CeciliaLib.getPresetPanel().loadPresets()
            if event != None:
                panel = CeciliaLib.getControlPanel()
                for i, cfilein in enumerate(panel.getCfileinList()):
                    if i >= len(snds):
                        break
                    cfilein.onLoadFile(snds[i])

    def getWordUnderCaret(self):
        editor = self.orchestraPanels[self.activeOrchestra].editor
        caretPos = editor.GetCurrentPos()
        startpos = editor.WordStartPosition(caretPos, True)
        endpos = editor.WordEndPosition(caretPos, True)
        currentword = editor.GetTextRangeUTF8(startpos, endpos)
        return currentword
            
    def onShowManual(self, event):
        if isinstance(self.FindFocus(), OrchestraSTC):
            text = self.orchestraPanels[self.activeOrchestra].editor.GetSelectedText()
            if text == "":
                text = self.getWordUnderCaret()
            with open(os.path.join(RESOURCES_PATH, 'CsoundKeywords.txt'), "r") as f:
                opcodes = f.read()
            if text in opcodes and text != '':
                page = text + '.html'
                webbrowser.open_new_tab(os.path.join(HTML_PATH, page))
        elif isinstance(self.FindFocus(), InterfaceSTC):
            text = self.interface.editor.GetSelectedText()
            objects = ['cfilein','csampler','cgraph','cslider','ctoggle',
                       'cpopup','cbutton','cpoly','crange','cgen']
            if text in objects and text != '':
                page = text + '.html'
                webbrowser.open_new_tab(os.path.join(CEC_MAN_PATH, page))

    def openCsdFile(self, event):
        with open(os.path.join(TMP_PATH, 'temp.csd'), "r") as f:
            msg = f.read()
        self.csdView = LogPage(self, "Csound file", (20,20), (500,500), msg)

    def openManUseCecilia(self, event):
        page = os.path.join(CEC_MAN_PATH, "usingCecilia.html")
        self.manView = ManualPage(self, page=page)
        self.manView.Show()
 
    def openManBuildCecilia(self, event):
        page = os.path.join(CEC_MAN_PATH, "buildInterface.html")
        self.manView = ManualPage(self, page=page)
        self.manView.Show()
             
    def openLogFile(self, event):
        logPath = os.path.join(TMP_PATH, 'csoundLog.txt')
        if os.path.isfile(logPath) and CeciliaLib.getDayTime() != None:
            f = open(logPath, "r")
            msg = f.read()
            f.close()
            self.logView = LogPage(self, 
                                   "Csound Log - %s" % CeciliaLib.getDayTime(), 
                                   pos=(20,20), size=(500,500), msg=msg)
        else:
            CeciliaLib.showErrorDialog("Opening file error.", 
                                       "Log file doesn't exist.")
            
    def onQuit(self, event):
        if not CeciliaLib.closeCeciliaFile(self):
            return
            
        CeciliaLib.setEditorSize(self.GetSize())
        CeciliaLib.setEditorPosition(self.GetPosition())

        try:
            self.prefs.onClose(event)
        except:
            pass
 
        CeciliaLib.getCsound().stopCsound()
        self.closeInterface()
        CeciliaLib.writeVarToDisk()
        self.Destroy()
        sys.exit()

    def onUndo(self, event):
        f = self.getEditorFocus()
        if f:
            f.Undo()
        
    def onRedo(self, event):
        f = self.getEditorFocus()
        if f:
            f.Redo()
        
    def onCut(self, event):
        f = self.getEditorFocus()
        if f:
            f.Cut()
        
    def onCopy(self, event):
        f = self.getEditorFocus()
        if f:
            f.Copy()
        
    def onPaste(self, event):
        f = self.getEditorFocus()
        if f:
            f.Paste()
        
    def onSelectAll(self, event):
        f = self.getEditorFocus()
        if f:
            f.SelectAll()

    def onFindReplace(self, event):
        self.editorFocused = self.getEditorFocus()
        if self.editorFocused == None:
            return
        
        self.data = wx.FindReplaceData()
        self.data.SetFindString(self.editorFocused.GetSelectedText())
        
        title = 'Find Replace in %s' % self.editorFocused.parent.tag
        findDialog = wx.FindReplaceDialog(self, self.data, title, wx.FR_REPLACEDIALOG | wx.FR_NOUPDOWN)
        findDialog.Bind(wx.EVT_FIND, self.OnFindEvent)
        findDialog.Bind(wx.EVT_FIND_NEXT, self.OnFindEvent)
        findDialog.Bind(wx.EVT_FIND_REPLACE, self.OnFindEvent)
        findDialog.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFindEvent)
        findDialog.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        findDialog.Show(True)

    def OnFindClose(self, evt):
        evt.GetDialog().Destroy()

    def OnFindEvent(self, evt):
        map = { wx.wxEVT_COMMAND_FIND : "FIND",
                wx.wxEVT_COMMAND_FIND_NEXT : "FIND_NEXT",
                wx.wxEVT_COMMAND_FIND_REPLACE : "REPLACE",
                wx.wxEVT_COMMAND_FIND_REPLACE_ALL : "REPLACE_ALL" }
        evtType = evt.GetEventType()
        findTxt = evt.GetFindString()
        newTxt = evt.GetReplaceString()
        findStrLen = len(findTxt)
        newStrLen = len(newTxt)
        diffLen = newStrLen - findStrLen

        editor = self.editorFocused
        selection = editor.GetSelection()
        if selection[0] == selection[1]:
            selection = (0, editor.GetLength())

        if map[evtType] == 'FIND':
            startpos = editor.FindText(selection[0], selection[1], findTxt, evt.GetFlags())
            endpos = startpos+len(findTxt)
            self.anchor1 = endpos
            self.anchor2 = selection[1]
            editor.SetSelection(startpos, endpos)
        elif map[evtType] == 'FIND_NEXT':
            startpos = editor.FindText(self.anchor1, self.anchor2, findTxt, evt.GetFlags())
            endpos = startpos+len(findTxt)
            self.anchor1 = endpos
            editor.SetSelection(startpos, endpos)
        elif map[evtType] == 'REPLACE':
            startpos = editor.FindText(selection[0], selection[1], findTxt, evt.GetFlags())
            if startpos != -1:
                endpos = startpos+len(findTxt)
                editor.SetSelection(startpos, endpos)
                editor.ReplaceSelection(newTxt)
                self.anchor1 = startpos + newStrLen + 1
                self.anchor2 += diffLen
        elif map[evtType] == 'REPLACE_ALL':
            self.anchor1 = startpos = selection[0]
            self.anchor2 = selection[1]
            while startpos != -1:
                startpos = editor.FindText(self.anchor1, self.anchor2, findTxt, evt.GetFlags())
                if startpos != -1:
                    endpos = startpos+len(findTxt)
                    editor.SetSelection(startpos, endpos)
                    editor.ReplaceSelection(newTxt)
                    self.anchor1 = startpos + newStrLen + 1
                    self.anchor2 += diffLen
        line = editor.GetCurrentLine()
        halfNumLinesOnScreen = editor.LinesOnScreen() / 2
        editor.ScrollToLine(line - halfNumLinesOnScreen)
        
    def onComment(self, event):
        f = self.getEditorFocus()
        if f:
            f.commentLines()

    def onInsertPath(self, event):
        f = self.getEditorFocus()
        if f:
            f.onInsertPath()

    def onAutoCompOpcode(self, event):
        f = self.getEditorFocus()
        if f:
            f.showAutoComp()

    def onIndent(self, event):
        if event.GetId() == ID_INDENT_ORC:
            self.orchestraPanels[self.activeOrchestra].editor.indentText()
        elif event.GetId() == ID_TAB_SCORE:
            if self.activeScore == 'Csound':
                self.scorePanels[self.activeScore].editor.indentText()

    def onPower2(self, event):
        editor = self.getEditorFocus()
        selection =  editor.GetSelectedText()
        start = editor.GetSelectionStart()
        pos = editor.GetCurrentPos()
        if selection != '':
            try: 
                value = eval(selection)
            except:
                return
            if event.GetId() == ID_UPPER_POWER2:
                for i in range(25):
                    p2 = int(math.pow(2,(i)))
                    if p2 > value:
                        break   
            else:
                for i in range(25):
                    p2 = int(math.pow(2,(24-i)))
                    if p2 < value:
                        break  
            newstr = str(p2)
            editor.ReplaceSelection(newstr)
            editor.SetSelection(start, start+len(newstr)) 

    def onDisplayTable(self, event):
        CeciliaLib.setDisplayTable(event.GetInt())

    def onShowPreview(self, event):
        CeciliaLib.setShowPreview(event.GetInt())

    def onUseMidi(self, event):
        CeciliaLib.setUseMidi(event.GetInt())

    def onHelpAbout(self, evt):
        Y = CeciliaLib.getDisplaySize()[0][1]
        about = AboutPopupFrame(self, Y/5)
        about.Show()

class EditorPanel(wx.Panel):
    def __init__(self, parent, tag):
        wx.Panel.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
      
        self.isMaximized = True
        self.tag = tag
        self.parent = parent
        self.SetBackgroundColour(TITLE_BACK_COLOUR)

        self.hbox = wx.FlexGridSizer(1, 4, 0, 0)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Sets the title of the panel
        self.title = wx.StaticText(self, -1, label = ('  ' + self.tag + '  '))
        font = wx.Font(CeciliaLib.getEditorSubTitleFont(), wx.NORMAL, 
                       wx.NORMAL, wx.NORMAL, face=FONT_FACE)
        self.title.SetFont(font)
        self.title.SetForegroundColour(WHITE_COLOUR)
        self.hbox.Add(self.title, 0, wx.ALIGN_CENTER_VERTICAL)

        # Sets the toggle button to maximize or minimize the editor
        self.minMaxToggle = MinMaxToggle(self, False, outFunction=self.minMaxText)
        self.hbox.Add(self.minMaxToggle, 0, wx.ALIGN_CENTER_VERTICAL)

        # Sets an empty panel to fill extra space
        fakePanel = wx.Panel(self, -1, size=(10, self.GetSize()[1]))
        fakePanel.SetBackgroundColour(TITLE_BACK_COLOUR)
        self.hbox.Add(fakePanel, 0, wx.EXPAND | wx.RIGHT, 20)

        self.hbox.AddGrowableCol(2)
        self.mainSizer.Add(self.hbox, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 3)
        self.SetSizer(self.mainSizer)

    def minMaxText(self, value):
        if value:
            self.isMaximized = False
        else:
            self.isMaximized = True
        self.GetParent().GetParent().GetParent().moveSashPosition()

class InterfacePanel(EditorPanel):
    def __init__(self, parent, tag):
        EditorPanel.__init__(self, parent, tag)

        self.editor = InterfaceSTC(self, -1)
        self.mainSizer.Add(self.editor, 1, wx.EXPAND | wx.BOTTOM, -2)

class OrchestraPanel(EditorPanel):
    def __init__(self, parent, tag, activeOrchestra):
        EditorPanel.__init__(self, parent, tag)
        
        self.activeOrchestra = activeOrchestra
                
        # Sets the available orchestras in a wx.Choice box
        formats, selectedNCHNLS = self.defineFormatsList()
        self.orchestraChoice = CustomMenu(self, choice=formats, init=self.activeOrchestra, 
                                          outFunction=self.changeOrchestra)
        self.orchestraChoice.setBackgroundColour(TITLE_BACK_COLOUR)
        self.orchestraChoice.SetToolTip(CECTooltip(TT_EDITOR_CHANNELS))
        self.hbox.Add(self.orchestraChoice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 1)
        
        # Sets the STC Editor
        self.editor = OrchestraSTC(self, -1)

        self.mainSizer.Add(self.editor, 1, wx.EXPAND | wx.BOTTOM, -2)

    def changeOrchestra(self, ind, label):
        self.GetParent().GetParent().GetParent().changeOrchestraPanel(label)
        
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

class ScorePanel(EditorPanel):
    def __init__(self, parent, tag, activeScore):
        EditorPanel.__init__(self, parent, tag)
        
        self.activeScore = activeScore
                
        # Sets the available orchestras in a wx.Choice box
        scoreTypes = SCORE_TYPES
        self.scoreChoice = CustomMenu(self, choice=scoreTypes, init=self.activeScore, 
                                          outFunction=self.changeScore)
        self.scoreChoice.SetToolTip(CECTooltip(TT_EDITOR_SCORE))                                  
        self.scoreChoice.setBackgroundColour(TITLE_BACK_COLOUR)
        self.hbox.Add(self.scoreChoice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 1)

        # Sets the STC Editor
        if activeScore == 'Csound':
            self.editor = ScoreSTC(self, -1)
        elif activeScore == 'Python':
            self.editor = PythonSTC(self, -1)

        self.mainSizer.Add(self.editor, 1, wx.EXPAND | wx.BOTTOM, -2)

    def changeScore(self, ind, label):
        self.GetParent().GetParent().GetParent().changeScorePanel(label)
        
class CsoundSTC(stc.StyledTextCtrl):
    style = wx.RAISED_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE | wx.WANTS_CHARS
    def __init__(self, parent, id, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=style):
        stc.StyledTextCtrl.__init__(self, parent, id, pos, size, style)

        self.parent = parent

        self.alphaStr = string.lowercase + string.uppercase + '0123456789'

        dt = MyFileDropTarget(self.GetTopLevelParent())
        self.SetDropTarget(dt)

        self.oldText = ''
        self.maxSpace = 1
        self.maxOpcodeLen = 1

        self.SetLexer(stc.STC_LEX_CSOUND) 

        self.SetMargins(0,0)

        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 25)
        self.SetMarginMask(1, 0)
        self.SetMarginSensitive(1, False)
        self.SetMarginLeft(5)

        self.SetCaretForeground("BLACK")
        self.SetCaretWidth(1)
        self.SetUseHorizontalScrollBar(False)
        self.SetViewWhiteSpace(False)
        self.SetUseAntiAliasing(True)
        self.SetIndent(4)
        self.SetBackSpaceUnIndents(True)
        self.SetTabIndents(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.AutoCompSetChooseSingle(True)
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetPasteConvertEndings(True)
        self.SetControlCharSymbol(32)
        self.SetLayoutCache(True)        

        self.SetModEventMask(stc.STC_PERFORMED_USER)

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
                          "face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#A5A5A5,face:%(helv)s,size:%(size2)d" % CeciliaLib.getFaces())
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % CeciliaLib.getFaces())
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#000000,back:#888BFF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF2222,bold")
        
        self.EmptyUndoBuffer()
        
        ################### STYLES FOR THE CSOUND LEXER #####################
        # stc.STC_CSOUND_DEFAULT = 0
        # stc.STC_CSOUND_COMMENT = 1
        # stc.STC_CSOUND_NUMBER = 2
        # stc.STC_CSOUND_OPERATOR = 3
        # stc.STC_CSOUND_INSTR = 4
        # stc.STC_CSOUND_IDENTIFIER = 5
        # stc.STC_CSOUND_OPCODE = 6
        # stc.STC_CSOUND_HEADERSTMT = 7
        # stc.STC_CSOUND_USERKEYWORD = 8
        # stc.STC_CSOUND_COMMENTBLOCK = 9
        # stc.STC_CSOUND_PARAM = 10
        # stc.STC_CSOUND_ARATE_VAR = 11
        # stc.STC_CSOUND_KRATE_VAR = 12
        # stc.STC_CSOUND_IRATE_VAR = 13
        # stc.STC_CSOUND_GLOBAL_VAR = 14
        # stc.STC_CSOUND_STRINGEOL = 15
        #####################################################################
        
        # Default
        self.StyleSetSpec(stc.STC_CSOUND_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        # Comments
        self.StyleSetSpec(stc.STC_CSOUND_COMMENT, "fore:%(comments)s,face:%(other)s,size:%(size)d" % (CeciliaLib.getFaces()))
        
        # Set the different keywords for each subclasses
        self.setKeywords()
        # Set the other styles (opcodes, userkeywords). Dependent of the subclass
        self.setKeywordsColor()
        # Shortcuts
        self.defineShortcuts()
        
        # Useful for strings highlighting
        self.openQuote = False
        self.quotePos = -1

    def defineShortcuts(self):
        # Remove some key bindings
        self.CmdKeyClear(ord('Y'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('D'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('L'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('T'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('L'), stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT)

        # Zoom in zoom out
        self.CmdKeyAssign(ord("="), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord("-"), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)
        
        # Move caret around
        self.CmdKeyAssign(stc.STC_KEY_HOME, 0, stc.STC_CMD_HOME)
        self.CmdKeyAssign(stc.STC_KEY_END, 0, stc.STC_CMD_LINEEND)
        self.CmdKeyAssign(stc.STC_KEY_NEXT, 0, stc.STC_CMD_PAGEDOWN)
        self.CmdKeyAssign(stc.STC_KEY_PRIOR, 0, stc.STC_CMD_PAGEUP)
        self.CmdKeyAssign(stc.STC_KEY_LEFT, stc.STC_SCMOD_ALT, stc.STC_CMD_WORDLEFT)
        self.CmdKeyAssign(stc.STC_KEY_RIGHT, stc.STC_SCMOD_ALT, stc.STC_CMD_WORDRIGHT)
        
        # Insert/Overtype
        self.CmdKeyAssign(stc.STC_KEY_INSERT, 0, stc.STC_CMD_EDITTOGGLEOVERTYPE)
        
        # Selections
        self.CmdKeyAssign(stc.STC_KEY_LEFT, stc.STC_SCMOD_ALT | stc.STC_SCMOD_SHIFT, stc.STC_CMD_WORDLEFTEXTEND)
        self.CmdKeyAssign(stc.STC_KEY_RIGHT, stc.STC_SCMOD_ALT | stc.STC_SCMOD_SHIFT, stc.STC_CMD_WORDRIGHTEXTEND)
        self.CmdKeyAssign(stc.STC_KEY_LEFT, stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT, stc.STC_CMD_HOMEEXTEND)
        self.CmdKeyAssign(stc.STC_KEY_RIGHT, stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT, stc.STC_CMD_LINEENDEXTEND)
        
        # Undo, Redo
        self.CmdKeyAssign(ord('Z'), stc.STC_SCMOD_CTRL, stc.STC_CMD_UNDO)
        self.CmdKeyAssign(ord('Z'), stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT, stc.STC_CMD_REDO)

    def commentLines(self):
        selStartPos, selEndPos = self.GetSelection()
        self.firstLine = self.LineFromPosition(selStartPos)
        self.endLine = self.LineFromPosition(selEndPos)

        commentStr = ';'

        for i in range(self.firstLine, self.endLine):
            lineLen = len(self.GetLine(i))
            pos = self.PositionFromLine(i)
            while self.GetTextRange(pos,pos+1) == ' ':
                pos += 1
            if self.GetTextRange(pos,pos+1) not in [commentStr, '\n'] and lineLen > 2:
                self.InsertText(pos, commentStr)
            elif self.GetTextRange(pos, pos+3) == commentStr*3:
                pass    
            elif self.GetTextRange(pos,pos+1) == commentStr:
                self.GotoPos(pos+1)
                self.DelWordLeft()

    def onInsertPath(self):
        dlg = wx.FileDialog(self, message="Choose a file", 
                            defaultDir=os.getcwd(), defaultFile="", style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetPath()
            self.ReplaceSelection('"' + text + '"')
        dlg.Destroy()    

    def checkModified(self):
        text = self.GetText()
        if text != self.oldText:
            CeciliaLib.setIsModified(True)
        self.oldText = text
        
    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_CSOUND_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_CSOUND_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

        wstart = self.WordStartPosition(caretPos, True)
        wend = self.WordEndPosition(caretPos, True)
        currentWord = self.GetTextRange(wstart, wend)
        if currentWord in self.wordlist:
            try:
                statusBar.SetStatusText(OPCODES_ARGS[currentWord], 0)
            except:
                try:
                    statusBar.SetStatusText(INTERFACE_ARGS[currentWord], 0)
                except:
                    pass
        self.checkModified()
    
    def ConvertEndOfLines(self):
        self.ConvertEOLs(stc.STC_EOL_LF)
        
class InterfaceSTC(CsoundSTC):
    def __init__(self, parent, id):
        CsoundSTC.__init__(self, parent, id)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)

    def setKeywords(self):
        self.wordlist = [word for word in CECILIA_INTERFACE_KEYWORDS]
        self.SetKeyWords(0, " ".join(self.wordlist))
        
    def setKeywordsColor(self):
        self.StyleSetSpec(stc.STC_CSOUND_OPCODE, "fore:%(interfaceKeywords)s,bold,size:%(size)d" % CeciliaLib.getFaces())

    def OnRightClick(self, evt):
        self.PopupMenu(InsertInterfaceMenu(self), evt.GetPosition())
               
class OrchestraSTC(CsoundSTC):
    def __init__(self, parent, id):
        CsoundSTC.__init__(self, parent, id)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        
    def setKeywords(self):
        keywordfile = open(os.path.join(RESOURCES_PATH, "CsoundKeywords.txt"), "rt")
        keywordlist = []

        for line in keywordfile.readlines():
            for word in line.split():
                keywordlist.append(word)
        keywordfile.close()

        keywordlist.extend(['dcblock2', 'then', '=', 'pan2'])
        keywordlist.remove('opcode')
        keywordlist.remove('endop')
        
        udoslist = [udo for udo in os.listdir(UDO_PATH) if not udo.startswith('.')]

        self.wordlist = keywordlist + udoslist + ['sampler', 'tables']

        # SetKeyWords uses a mysterious value (first argument) to define a set of keywords
        # Meaning that you can define many sets of keywords that Scintilla will style differently
        # You still need to define the style using self.StyleSetSpec
        # Here are the differents sets of keywords that can be defined: 
        # OPCODE = 0
        # HEADERSTMT = 1
        # USERKEYWORD = 2
        # PARAM = 3
        
        # Define the OPCODE keywords
        self.SetKeyWords(0, " ".join(self.wordlist))
        # Define the HEADERSTMT keywords
        self.SetKeyWords(1, 'sr kr ksmps nchnls')
        # Define the USERKEYWORD keywords
        self.SetKeyWords(2, 'instr endin opcode endop')
               
    def setKeywordsColor(self):
        self.StyleSetSpec(stc.STC_CSOUND_OPCODE, "fore:%s,bold,size:%d" % (CeciliaLib.getFaces()['csoundKeywords'], CeciliaLib.getFaces()['size']))
        self.StyleSetSpec(stc.STC_CSOUND_USERKEYWORD, "fore:%s,bold,size:%d" % (CeciliaLib.getFaces()['instrKeywords'], CeciliaLib.getFaces()['size']))
        self.StyleSetSpec(stc.STC_CSOUND_HEADERSTMT, "fore:%s,bold,size:%d" % (CeciliaLib.getFaces()['headerKeywords'], CeciliaLib.getFaces()['size']))

    def OnRightClick(self, evt):
        self.PopupMenu(InsertOpcodeMenu(self), evt.GetPosition())
        
    def findMaxSpace(self):
        self.maxSpace = 1
        self.maxOpcodeLen = 1
        lineCount = self.GetLineCount()
        for lineNum in range(lineCount):
            text = self.GetLine(lineNum)
            text = text.strip()
            wlist = text.split(' ')
            for w in wlist:
                if w in ['if', 'elseif', 'else', 'then', 'endif', 'goto', 'i', 'k', 'a', 'xin']:
                    continue
                if w in self.wordlist:
                    space = len(text[:text.find(w)].rstrip()) + 2
                    if space > self.maxSpace:
                        self.maxSpace = space
                    space = len(w) + 2
                    if space > self.maxOpcodeLen:
                        self.maxOpcodeLen = space 
        # make sure markers are on tab column 
        for i in range(16):
            if (i*4) > self.maxSpace:
                self.maxSpace = i*4
                break             
        for i in range(16):
            if (i*4) > self.maxOpcodeLen:
                self.maxOpcodeLen = i*4
                break             
        
    def indentText(self):   
        self.unindentText()
        lineCount = self.GetLineCount()
        currentLine = self.GetCurrentLine()
        firstVisibleLine = self.GetFirstVisibleLine()
        
        self.findMaxSpace()
        
        for lineNum in range(lineCount):
            self.SetLineIndentation(lineNum, 0)
            line = self.GetLine(lineNum)
            if line.strip() == '':
                continue

            if 'instr ' in line or 'endin' in line:
                self.SetLineIndentation(lineNum, self.maxSpace)
            elif 'if ' in line:    
                self.SetLineIndentation(lineNum, 0)
            elif 'elseif ' in line:    
                self.SetLineIndentation(lineNum, 0)
            elif 'else ' in line:    
                self.SetLineIndentation(lineNum, 0)
            elif 'endif ' in line:    
                self.SetLineIndentation(lineNum, 0)
            elif 'goto ' in line:    
                self.SetLineIndentation(lineNum, 0)
            elif ' xin' in line:    
                self.SetLineIndentation(lineNum, 0)
            else:
                wlist = line.split(' ')
                for w in wlist:
                    if w in self.wordlist and w not in ['i', 'k', 'a', 'x', 'in']:
                        pos = line.find(w) 
                        while line[pos-1] not in [' ', '\n']:
                            pos = line.find(w, pos+1)
                        off = self.maxSpace - pos
                        self.InsertText(self.PositionFromLine(lineNum)+pos, ' '*off)
                        off2 = self.maxOpcodeLen - len(w)
                        self.SetCurrentPos(self.PositionFromLine(lineNum)+pos+off+len(w))
                        a1 = self.GetCurrentPos() + off2
                        self.WordRight()
                        a2 = self.GetCurrentPos()
                        if a2 > a1:
                            for i in range(a2-a1):
                                self.DeleteBack()
                        else:        
                            self.InsertText(a1-off2, ' '*(a1-a2))
        self.SetCurrentPos(self.PositionFromLine(firstVisibleLine))
        self.SetSelection(self.GetCurrentPos(), self.GetCurrentPos())
        self.SetCurrentPos(self.PositionFromLine(currentLine))
        self.SetSelection(self.GetCurrentPos(), self.GetCurrentPos())
              
    def unindentText(self):
        text = self.GetText()
        li = text.split(' ')
        text = ''
        for ele in li:
            if ele != '':
                text += ele + ' '
        self.SetText(text)
              
    def showAutoComp(self):
        charBefore = None
        caretPos = self.GetCurrentPos()
        
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)

        startpos = self.WordStartPosition(caretPos, True)
        endpos = self.WordEndPosition(caretPos, True)
        currentword = self.GetTextRange(startpos, endpos)
                
        if chr(charBefore) in self.alphaStr:
            list = ''
            for word in self.wordlist:
                if word.startswith(currentword) and word != currentword:
                    list = list + word + ' ' 
            if list:
                self.AutoCompShow(len(currentword), list)
            
class ScoreSTC(CsoundSTC):
    def setKeywords(self):
        self.wordlist = ['a', 'b', 'e', 'f', 'i', 'm', 'n', 'q', 'r', 's', 't', 'v', 'x', '{', '}']
        self.SetKeyWords(0, " ".join(self.wordlist))
        
    def setKeywordsColor(self):
        self.StyleSetSpec(stc.STC_CSOUND_OPCODE, "fore:%(scoreKeywords)s,bold,size:%(size)d" % CeciliaLib.getFaces())

    def indentText(self):
        maxParams = 0
        maxLine = self.GetLineCount()
        scoreLines = dict()
        removedLine = -1
        curLine = self.GetCurrentLine()
        firstVisibleLine = self.GetFirstVisibleLine()
        
        for lineNum in range(maxLine):
            line = {'statement':'', 'parameters':[], 'comment':''}
            
            lineText = self.GetLine(lineNum).strip('\r\n').lstrip()
            
            # Avoid writing a second time the first comment line
            if lineText.find(';#') != -1:
                removedLine = lineNum
                continue
            
            # Extract comments
            if lineText.find(';') != -1:
                line['comment'] = lineText[lineText.find(';'):]
                lineText = lineText[0:lineText.find(';')]
            
            
            if len(lineText) > 0:
                # Extract the line statement (first character)
                line['statement'] = lineText[0:1] + '    '
                lineText = lineText[1:]
                
                # Extract the parameters and suppress the empty entries
                params = lineText.split(' ')
                for p in params:
                    if p != '':
                        line['parameters'].append(p)
                del params
                
            if len(line['parameters']) > maxParams:
                maxParams = len(line['parameters'])
            
            scoreLines[lineNum] = line
        
        # Create a first line (comment) that states what are the Csound parameters
        # this line start with ';#' this is how it is recognized
        scoreLines['firstLine'] = ';#   '
        
        # Pad the parameters and realize the first line
        for paramNum in range(maxParams):
            maxChar = 0
            for lineNum in range(maxLine):
                if lineNum == removedLine:
                    continue
                if len(scoreLines[lineNum]['parameters']) > paramNum:
                    if len(scoreLines[lineNum]['parameters'][paramNum])>maxChar:
                        maxChar = len(scoreLines[lineNum]['parameters'][paramNum])
            
            for lineNum in range(maxLine):
                if lineNum == removedLine:
                    continue
                if len(scoreLines[lineNum]['parameters']) > paramNum:
                    pad = '    '
                    for i in range(maxChar - len(scoreLines[lineNum]['parameters'][paramNum])):
                        pad += ' '
                    scoreLines[lineNum]['parameters'][paramNum] += pad
            
            pField = 'p%d' % (paramNum+1)
            pad = ''
            for i in range((maxChar+4)-len(pField)):
                pad += ' '
            scoreLines['firstLine'] += pField
            scoreLines['firstLine'] += pad
        
        self.ClearAll()
        self.AddText(scoreLines['firstLine']+'\r\n')
        
        
        for lineNum in range(maxLine):
            if lineNum == removedLine:
                continue
            line = scoreLines[lineNum]['statement']
            for p in scoreLines[lineNum]['parameters']:
                line += p
            line += scoreLines[lineNum]['comment']
            if lineNum < maxLine-1:
                line += '\r\n'
            self.AddText(line)

        self.SetCurrentPos(self.PositionFromLine(firstVisibleLine))
        self.SetSelection(self.GetCurrentPos(), self.GetCurrentPos())
        self.SetCurrentPos(self.PositionFromLine(curLine))
        self.SetSelection(self.GetCurrentPos(), self.GetCurrentPos())
        
    def unindentText(self):
        text = self.GetText().splitlines(True)
        self.ClearAll()
        
        for line in text:
            newLine = ''
            prevChar = ''
            for char in line:
                if char == ' ' and prevChar == ' ':
                    continue
                else:
                    newLine = newLine + char
                prevChar = char
            self.AddText(newLine)
  
    def GetCsoundText(self):
        return self.GetText()

class PythonSTC(stc.StyledTextCtrl):
    def __init__(self, parent, ID,
                 pos=wx.DefaultPosition, size=wx.Size(-1,-1),
                 style=wx.RAISED_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE |
                 wx.WANTS_CHARS):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.parent = parent

        self.alphaStr = string.lowercase + string.uppercase + '0123456789'

        dt = MyFileDropTarget(self.GetTopLevelParent())
        self.SetDropTarget(dt)

        self.oldText = ''

        self.SetLexer(stc.STC_LEX_PYTHON)
        p = ['p%d' % i for i in range(2,21)]
        func = ['write', 'forInst', 'addLine', 'createTable', 'midiToHertz', 'midiToTranspo', 'drunk',
                'droneAndJump', 'repeater', 'loopseg', 'getUserValue', 'next']
        self.SetKeyWords(0, " ".join(keyword.kwlist) + " None True False " + " ".join(func) + " " + " ".join(p))

        self.SetProperty("fold", "1")

        self.SetMargins(0,0)
        self.SetViewWhiteSpace(False)
        self.SetUseAntiAliasing(True)
        self.SetCaretWidth(1)
        self.SetUseHorizontalScrollBar(False)        
        self.SetUseTabs(False)
        self.SetIndent(4)
        self.SetTabWidth(4)
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetPasteConvertEndings(True)
        self.SetControlCharSymbol(32)
        self.SetLayoutCache(True)

        # Setup the margins to hold fold markers
        self.SetFoldFlags(16)
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 25)
        self.SetMarginLeft(5)

        self.SetModEventMask(stc.STC_PERFORMED_USER)

        # Bind all the event that are gonna be useful
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#A5A5A5,face:%(helv)s,size:%(size2)d" % CeciliaLib.getFaces())
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % CeciliaLib.getFaces())
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#000000,back:#888BFF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#888BFF,bold")
        self.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, "fore:#303030,back:#FFFFFF")
        
        self.EmptyUndoBuffer()
        
        # Default
        self.StyleSetSpec(stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        # Comments
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:%(comment)s,face:%(other)s,italic,size:%(size)d" % CeciliaLib.getFaces())
        # Number
        self.StyleSetSpec(stc.STC_P_NUMBER, "fore:%(number)s,bold,size:%(size)d" % CeciliaLib.getFaces())
        # String
        self.StyleSetSpec(stc.STC_P_STRING, "fore:%(string)s,face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        # Single quoted string
        self.StyleSetSpec(stc.STC_P_CHARACTER, "fore:%(string)s,face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        # Keyword
        self.StyleSetSpec(stc.STC_P_WORD, "fore:%(keyword)s,bold,size:%(size)d" % CeciliaLib.getFaces())
        # Triple quotes
        self.StyleSetSpec(stc.STC_P_TRIPLE, "fore:%(triple)s,size:%(size)d" % CeciliaLib.getFaces())
        # Triple double quotes
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:%(triple)s,size:%(size)d" % CeciliaLib.getFaces())
        # Class name definition
        self.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:%(class)s,bold,size:%(size)d" % CeciliaLib.getFaces())
        # Function or method name definition
        self.StyleSetSpec(stc.STC_P_DEFNAME, "fore:%(function)s,bold,size:%(size)d" % CeciliaLib.getFaces())
        # Operators
        self.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % CeciliaLib.getFaces())
        # Identifiers
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % CeciliaLib.getFaces())
        # Comment-blocks
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:%(commentblock)s,italic,size:%(size)d" % CeciliaLib.getFaces())
        
        self.SetCaretForeground("BLACK")

        # Shortcuts
        self.defineShortcuts()
        
        # Useful for strings highlighting
        self.openQuote = False
        self.quotePos = -1

    def defineShortcuts(self):
        # Remove some key bindings
        self.CmdKeyClear(ord('Y'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('D'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('L'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('T'), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('L'), stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT)

        # Zoom in zoom out
        self.CmdKeyAssign(ord("="), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord("-"), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)
        
        # Move caret around
        self.CmdKeyAssign(stc.STC_KEY_HOME, 0, stc.STC_CMD_HOME)
        self.CmdKeyAssign(stc.STC_KEY_END, 0, stc.STC_CMD_LINEEND)
        self.CmdKeyAssign(stc.STC_KEY_NEXT, 0, stc.STC_CMD_PAGEDOWN)
        self.CmdKeyAssign(stc.STC_KEY_PRIOR, 0, stc.STC_CMD_PAGEUP)
        self.CmdKeyAssign(stc.STC_KEY_LEFT, stc.STC_SCMOD_ALT, stc.STC_CMD_WORDLEFT)
        self.CmdKeyAssign(stc.STC_KEY_RIGHT, stc.STC_SCMOD_ALT, stc.STC_CMD_WORDRIGHT)
        
        # Insert/Overtype
        self.CmdKeyAssign(stc.STC_KEY_INSERT, 0, stc.STC_CMD_EDITTOGGLEOVERTYPE)
        
        # Selections
        self.CmdKeyAssign(stc.STC_KEY_LEFT, stc.STC_SCMOD_ALT | stc.STC_SCMOD_SHIFT, stc.STC_CMD_WORDLEFTEXTEND)
        self.CmdKeyAssign(stc.STC_KEY_RIGHT, stc.STC_SCMOD_ALT | stc.STC_SCMOD_SHIFT, stc.STC_CMD_WORDRIGHTEXTEND)
        self.CmdKeyAssign(stc.STC_KEY_LEFT, stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT, stc.STC_CMD_HOMEEXTEND)
        self.CmdKeyAssign(stc.STC_KEY_RIGHT, stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT, stc.STC_CMD_LINEENDEXTEND)
        
        # Undo, Redo
        self.CmdKeyAssign(ord('Z'), stc.STC_SCMOD_CTRL, stc.STC_CMD_UNDO)
        self.CmdKeyAssign(ord('Z'), stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT, stc.STC_CMD_REDO)

    def commentLines(self):
        selStartPos, selEndPos = self.GetSelection()
        self.firstLine = self.LineFromPosition(selStartPos)
        self.endLine = self.LineFromPosition(selEndPos)

        commentStr = '#'

        for i in range(self.firstLine, self.endLine):
            lineLen = len(self.GetLine(i))
            pos = self.PositionFromLine(i)
            if self.GetTextRange(pos,pos+1) != commentStr and lineLen > 2:
                self.InsertText(pos, commentStr)
            elif self.GetTextRange(pos,pos+1) == commentStr:
                self.GotoPos(pos+1)
                self.DelWordLeft()

    def onInsertPath(self):
        dlg = wx.FileDialog(self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetPath()
            self.ReplaceSelection('"' + text + '"')
        dlg.Destroy()    

    def checkModified(self):
        text = self.GetText()
        if text != self.oldText:
            CeciliaLib.setIsModified(True)
        self.oldText = text
        
    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_CSOUND_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_CSOUND_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

        self.checkModified()

    def GetCsoundText(self):
        return self.interpretedText(self.GetText())

    def interpretedText(self, text):
        with open(os.path.join(TMP_PATH, 'pythonScore.py'), 'w') as f:
            f.write(text)
        return scoreFormat()
        
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for file in filenames:
            if os.path.isfile(file):    
                CeciliaLib.openCeciliaFile(self.window, file)
            else:
                pass

class LogPage(wx.Frame):
    def __init__(self, parent, title, pos, size, msg):
        wx.Frame.__init__(self, parent, -1, title, pos=pos, size=size)        

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(1, "Save...\tCtrl-S", "Save...")
        self.Bind(wx.EVT_MENU, self.saveas, id=1)
        menu.Append(2, "Close\tCtrl-W", "Close this window")
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=2)
        menuBar.Append(menu, "&File")            
        self.SetMenuBar(menuBar)

        self.msg = msg
        self.text = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.SUNKEN_BORDER)
        self.text.Freeze()
        self.text.WriteText(msg)
        self.text.Thaw()

        self.Show()
        self.SetFocus()
     
    def OnTimeToClose(self, evt):
        self.Destroy()

    def saveas(self, event):
        dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", style=wx.SAVE)
        dlg.SetFilterIndex(0)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            f = open(path, 'w')
            f.write(self.msg)
            f.close()
        dlg.Destroy()

class InsertOpcodeMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.parent = parent

        with open(RESOURCES_PATH + '/opcodestree.py', 'r') as f:
            opdict = eval(f.read())
        
        for key in sorted(opdict.keys()):
            keymenu = wx.Menu()
            self.buildMenu(keymenu, opdict[key])
            self.AppendMenu(wx.NewId(), key, keymenu)

    def buildMenu(self, menu, dict):
        if type(dict) == DictType:
            for key in sorted(dict.keys()):
                keymenu = wx.Menu()
                self.buildMenu(keymenu, dict[key])
                if key == "":
                    key = "---"
                menu.AppendMenu(wx.NewId(), key, keymenu)
        else:
            for op in dict:
                if op != "&":
                    item = wx.MenuItem(menu, wx.NewId(), op)
                    menu.AppendItem(item)
                    menu.Bind(wx.EVT_MENU, self.onInsertOpcode, id=item.GetId())
            
    def onInsertOpcode(self, event):
        id = event.GetId()
        item = self.FindItemById(id)
        opcode = item.GetLabel()
        line = self.parent.GetCurrentLine()
        if opcode in self.parent.wordlist:
            try:
                self.parent.InsertText(self.parent.GetCurrentPos(), 
                                       OPCODES_ARGS[opcode]+'\n')
                self.parent.GotoLine(line+1)
            except:
                CeciliaLib.showErrorDialog("Missing opcode syntax!", 
                                           "Cecilia can't find opcode syntax in its database.")   

class InsertInterfaceMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.parent = parent

        self.opdict = {
                    'filein': 'cfilein snd -label Audio\n',
                    'sampler': 'csampler snd -label Audio\n',
                    'graph (k-rate)': 'cgraph env -label Envelope -unit x -rel lin -min 0 -max 1 -func 0 0 .01 1 .99 1 1 0\n',
                    'graph (table)': 'cgraph env -label Envelope -unit x -rel lin -gen 1 -size 8192 -min 0 -max 1 -func 0 0 .01 1 .99 1 1 0\n',
                    'slider (i-rate)': 'cslider slide -label X -min 0 -max 1 -init 0 -unit x -res float -rate i -rel lin\n',
                    'slider (k-rate)': 'cslider slide -label X -min 0 -max 1 -init 0 -unit x -res float -rate k -rel lin -gliss 0.025\n',
                    'slider (freq)': 'cslider freq -label Freq -min 20 -max 20000 -init 1000 -unit Hz -res float -rate k -rel log -gliss 0.025\n',
                    'slider (mouse up)': 'cslider slide -label X -min 0 -max 1 -init 0 -unit x -res float -rate k -rel lin -up 1\n',
                    'range (k-rate)': 'crange range -label X -min 0 -max 1 -init 0,1 -unit x -res float -rate k -rel lin -gliss 0.025\n',
                    'range (freq)': 'crange freq -label Freq -min 20 -max 20000 -init 1000,5000 -unit Hz -res float -rate k -rel log -gliss 0.025\n',
                    'toggle': 'ctoggle tog -label MyTog -init 1 -rate k\n',
                    'popup': 'cpopup pop -label MyPop -value 0 1 2 3 4 5 -init 0 -rate k\n',
                    'button': 'cbutton but -label MyBut -trig 0\n',
                    'poly': 'cpoly poly -label voices -min 1 -max 10 -init 1\n',
                    'gen': 'cgen wave -label Waveform -gen 10 -size 8192 -init 1,.3,.2,.1,.05' 
        }

        for key in sorted(self.opdict.keys()):
            item = wx.MenuItem(self, wx.NewId(), key)
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.onInsertObject, id=item.GetId())

    def onInsertObject(self, event):
        id = event.GetId()
        item = self.FindItemById(id)
        obj = item.GetLabel()
        line = self.parent.GetCurrentLine()
        self.parent.InsertText(self.parent.GetCurrentPos(), self.opdict[obj])
        self.parent.GotoLine(line+1)

class ManualPage(wx.Frame):
    def __init__(self, parent, page, size=(1000, 600)):
        wx.Frame.__init__(self, parent, size=size)
        self.page = page
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(1, "Close\tCtrl-W", "Close this window")
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=1)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.html1 = wx.html.HtmlWindow(self, -1, size=size)
        self.html1.LoadPage(page)
        self.SetFocus()

    def openPage(self, page):
        self.page = page
        self.html1.LoadPage(page + '.html')

    def OnTimeToClose(self, evt):
        self.Destroy()
