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

import wx, os, codecs
from constants import *
import CeciliaLib

def buildFileTree():
    root = MODULES_PATH
    directories = []
    files = {}
    for dir in os.listdir(MODULES_PATH):
        if not dir.startswith('.'):
            directories.append(dir)
            files[dir] = []
            for f in os.listdir(os.path.join(root, dir)):
                if not f.startswith('.'):
                    files[dir].append(f)
    return root, directories, files

class MainMenuBar(wx.MenuBar):
    def __init__(self, frame, ceciliaEditor):
        wx.MenuBar.__init__(self, wx.MB_DOCKABLE)
        self.frame = frame
        self.ceciliaEditor = ceciliaEditor

        self.root, self.directories, self.files = buildFileTree()

    def getBuiltinFiles(self):
        return self.files

    def buildFileMenu(self):
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(wx.ID_NEW, 'New...\tCtrl+N', 
                            'Start a new Cecilia project (Modules)')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onNew, id=wx.ID_NEW)
        self.fileMenu.Append(wx.ID_OPEN, 'Open...\tCtrl+O', 
                            'Open a previously saved Cecilia project')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onOpen, id=wx.ID_OPEN)

        ######## Implement the Open builtin menu #########
        self.openBuiltinMenu = wx.Menu()
        subId1 = ID_OPEN_BUILTIN
        for dir in self.directories:
            menu = wx.Menu()
            self.openBuiltinMenu.AppendMenu(-1, dir, menu)
            for f in self.files[dir]:
                menu.Append(subId1, f)
                self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onOpenBuiltin, 
                                id=subId1)
                subId1 += 1
                
        prefPath = CeciliaLib.getPrefPath()
        if prefPath:
            for path in prefPath.split(';'):
                if not os.path.isdir(path):
                    continue     
                menu = wx.Menu(os.path.split(path)[1])
                self.openBuiltinMenu.AppendMenu(-1, os.path.split(path)[1], 
                                                menu)
                files = os.listdir(path)
                for file in files:
                    if os.path.isfile(os.path.join(path, file)):
                        ok = False
                        try:
                            ext = file.rsplit('.')[1]
                            if ext == 'cec':
                                ok = True
                        except:
                            ok = False 
                        if ok:
                            menu.Append(subId1, file)
                            self.frame.Bind(wx.EVT_MENU, 
                                            self.ceciliaEditor.onOpenPrefModule, 
                                            id=subId1)
                            subId1 += 1
                
        self.fileMenu.AppendMenu(-1, 'Modules', self.openBuiltinMenu)

        self.openRecentMenu = wx.Menu()
        subId2 = ID_OPEN_RECENT
        recentFiles = []
        filename = CeciliaLib.ensureNFD(os.path.join(TMP_PATH,'.recent.txt'))
        if os.path.isfile(filename):
            f = codecs.open(filename, "r", encoding="utf-8")
            for line in f.readlines():
                recentFiles.append(line.replace("\n", ""))
            f.close()
        if recentFiles:
            for file in recentFiles:
                self.openRecentMenu.Append(subId2, file)
                subId2 += 1
        if subId2 > ID_OPEN_RECENT:
            for i in range(ID_OPEN_RECENT,subId2):
                self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.openRecent, id=i) 

        self.fileMenu.AppendMenu(-1,'Open Recent', self.openRecentMenu, 
                                'Access previously opened files in Cecilia')
        self.fileMenu.Append(wx.ID_CLOSE, 'Close\tCtrl+W', 
                            'Close the current Interface window')
        self.frame.Bind(wx.EVT_MENU, self.frame.onClose, id=wx.ID_CLOSE)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(wx.ID_SAVE, 'Save\tCtrl+S', 
                            'Save changes made on the current module')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onSave, id=wx.ID_SAVE)
        self.fileMenu.Append(wx.ID_SAVEAS, 'Save as...\tShift+Ctrl+s', 
                            'Save the current module as... (.cec file)')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onSaveAs, id=wx.ID_SAVEAS)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(ID_UPDATE_INTERFACE, 'Reset Interface\tCtrl+R', 
                            'Generate the interface')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onUpdateInterface, 
                        id=ID_UPDATE_INTERFACE)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(ID_OPEN_CSD, "Show computed .csd file\tCtrl+T", 
                            "Shows the .csd file generated by Cecilia")
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.openCsdFile, 
                        id=ID_OPEN_CSD)
        self.fileMenu.Append(ID_OPEN_LOG, "Show Csound log file\tShift+Ctrl+T", 
                            "Shows the Csound log file")
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.openLogFile, 
                        id=ID_OPEN_LOG)
        pref_item = self.fileMenu.Append(wx.ID_PREFERENCES, 
                                        'Preferences...\tCtrl+;', 
                                        'Open Cecilia preferences pane')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onPreferences, 
                        id=wx.ID_PREFERENCES)
        self.fileMenu.AppendSeparator()
        quit_item = self.fileMenu.Append(wx.ID_EXIT, 'Quit\tCtrl+Q', 
                                        'Quit Cecilia')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onQuit, id=wx.ID_EXIT)

        if wx.Platform=="__WXMAC__":
            wx.App.SetMacExitMenuItemId(quit_item.GetId())
            wx.App.SetMacPreferencesMenuItemId(pref_item.GetId())

    def buildEditMenu(self):
        self.editMenu = wx.Menu()
        self.editMenu.Append(wx.ID_UNDO, 'Undo\tCtrl+Z', 
                            'Undo the last change')
        self.frame.Bind(wx.EVT_MENU, self.frame.onUndo, id=wx.ID_UNDO)
        self.editMenu.Append(wx.ID_REDO, 'Redo\tShift+Ctrl+Z', 
                            'Redo the last change')
        self.frame.Bind(wx.EVT_MENU, self.frame.onRedo, id=wx.ID_REDO)
        self.editMenu.AppendSeparator()
        self.editMenu.Append(wx.ID_COPY, 'Copy\tCtrl+C', 
                            'Copy the text selected in the clipboard')
        self.frame.Bind(wx.EVT_MENU, self.frame.onCopy, id=wx.ID_COPY)
        self.editMenu.Append(wx.ID_PASTE, 'Paste\tCtrl+V', 
                            'Paste the text in the clipboard')
        self.frame.Bind(wx.EVT_MENU, self.frame.onPaste, id=wx.ID_PASTE)
        if self.isEditor:
            self.editMenu.Append(wx.ID_CUT, 'Cut\tCtrl+X', 
                                'Cut the text selected in the clipboard')
            self.frame.Bind(wx.EVT_MENU, self.frame.onCut, id=wx.ID_CUT)
            self.editMenu.Append(wx.ID_SELECTALL, 'Select All\tCtrl+A', 
                                'Select all text')
            self.frame.Bind(wx.EVT_MENU, self.frame.onSelectAll, 
                            id=wx.ID_SELECTALL)
            self.editMenu.AppendSeparator()
            self.editMenu.Append(ID_FIND_REPLACE, 'Find Replace...\tCtrl+F', 
                                'Find an expression in the text and replace it')
            self.frame.Bind(wx.EVT_MENU, self.frame.onFindReplace, 
                            id=ID_FIND_REPLACE)
        self.editMenu.AppendSeparator()
        self.editMenu.Append(ID_REMEMBER, 'Remember input sound', 
                            'Remember the selected soundfile on module switch',
                            kind=wx.ITEM_CHECK)
        self.editMenu.FindItemById(ID_REMEMBER).Check(CeciliaLib.getRememberSound())
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onRememberInputSound, 
                        id=ID_REMEMBER)

    def buildFormatMenu(self):
        self.formatMenu = wx.Menu()
        self.formatMenu.Append(ID_COMMENT, 'Un/Comment line(s)\tCtrl+J', 
                              'Comment or uncomment selected (or current) lines')
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onComment, 
                                id=ID_COMMENT)
        self.formatMenu.Append(ID_INSERT_PATH, "Insert file path...\tCtrl+L", 
                              "Opens standard dialog and insert chosen file path at the current position")
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onInsertPath, 
                                id=ID_INSERT_PATH)
        self.ceciliaEditor.autoCompleteMenu = wx.Menu()
        self.formatMenu.Append(ID_AUTOCOMP_OPCODE, "AutoComplete Opcode\tCtrl+K", 
                              "Checks for autoCompletion possibilities and opens popup menu")
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onAutoCompOpcode, 
                                id=ID_AUTOCOMP_OPCODE)        
        self.formatMenu.AppendSeparator()
        self.formatMenu.Append(ID_INDENT_ORC, 'Indent Orchestra\tCtrl+I', 
                              'Set the indentation of the orchestra editor')
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onIndent, 
                                id=ID_INDENT_ORC)
        self.formatMenu.Append(ID_TAB_SCORE, 'Tabulate Score\tShift+Ctrl+I', 
                              'Tabulate the score editor')
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onIndent, 
                                id=ID_TAB_SCORE)
        self.formatMenu.AppendSeparator()
        self.formatMenu.Append(ID_UPPER_POWER2, 'Higher power of 2\tCtrl+UP', 
                              'Replaces selected number by the next power of 2')
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onPower2, 
                                id=ID_UPPER_POWER2)
        self.formatMenu.Append(ID_LOWER_POWER2, 'Lower power of 2\tCtrl+DOWN', 
                              'Replaces selected number by the previous power of 2')
        self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onPower2, 
                                id=ID_LOWER_POWER2)

    def buildCsoundMenu(self):
        self.csoundMenu = wx.Menu()
        self.csoundMenu.Append(ID_PLAY_STOP, 'Play / Stop\tCtrl+.', 
                              'Start and stop Csound performance')
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onShortPlayStop, 
                        id=ID_PLAY_STOP)
        self.csoundMenu.AppendSeparator()
        self.csoundMenu.Append(ID_SHOW_PREVIEW, 'Preview command', 
                        'Allow the visualization and modification of the csound command line before it is lauched', 
                        kind=wx.ITEM_CHECK)
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onShowPreview, 
                        id=ID_SHOW_PREVIEW)
        self.csoundMenu.Append(ID_USE_MIDI, 'Use MIDI', 
                              'Allow Csound to use a midi device.', 
                              kind=wx.ITEM_CHECK)
        if CeciliaLib.getUseMidi() == 1: midiCheck = True
        else: midiCheck = False
        self.csoundMenu.FindItemById(ID_USE_MIDI).Check(midiCheck)
        self.csoundMenu.FindItemById(ID_USE_MIDI).Enable(False)
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onUseMidi, id=ID_USE_MIDI)
        if self.isEditor:
            self.csoundMenu.AppendSeparator()        
            self.csoundMenu.Append(2012, 'Help with selected opcode\tCtrl+U', 
                                  'Show the manual page for the selected opcode')
            self.ceciliaEditor.Bind(wx.EVT_MENU, self.ceciliaEditor.onShowManual, 
                                    id=2012)

    def buildWindowMenu(self):
        self.windowMenu = wx.Menu()
        self.windowMenu.Append(3001, 'Flip Editor / Interface\tCtrl+E', 
                              kind=wx.ITEM_CHECK)
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onFlipFrontWindow, id=3001)
        if not self.isEditor:
            self.csoundMenu.AppendSeparator()        
            self.windowMenu.Append(3002, 'Eh Oh Mario!\tShift+Ctrl+E',
                                   kind=wx.ITEM_CHECK)
            self.frame.Bind(wx.EVT_MENU, self.marioSwitch, id=3002)

    def buildHelpMenu(self):
        self.helpMenu = wx.Menu()        
        helpItem = self.helpMenu.Append(-1, '&About %s %s' % (APP_NAME, APP_VERSION), 
                                        'wxPython RULES!!!')
        wx.App.SetMacAboutMenuItemId(helpItem.GetId())
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.onHelpAbout, helpItem)
        manUseItem = self.helpMenu.Append(-1, "Using Cecilia's Interface")
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.openManUseCecilia, manUseItem)
        manBuildItem = self.helpMenu.Append(-1, "Building Cecilia's Interface")
        self.frame.Bind(wx.EVT_MENU, self.ceciliaEditor.openManBuildCecilia, manBuildItem)

    def buildMenuBar(self):
        self.Append(self.fileMenu, '&File')
        self.Append(self.editMenu, '&Edit')
        if self.isEditor:
            self.Append(self.formatMenu, '&Format')
        self.Append(self.csoundMenu, '&Csound')
        self.Append(self.windowMenu, '&Window')
        self.Append(self.helpMenu, '&Help')

class CeciliaMenuBar(MainMenuBar):
    def __init__(self, frame, ceciliaEditor):
        MainMenuBar.__init__(self, frame, ceciliaEditor)
        self.isEditor = True
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, wx.WXK_UP, ID_UPPER_POWER2),
                                         (wx.ACCEL_CTRL, wx.WXK_DOWN, ID_LOWER_POWER2),
                                         (wx.ACCEL_CTRL,  ord('L'), ID_INSERT_PATH),
                                         (wx.ACCEL_CTRL,  ord('T'), ID_OPEN_CSD),
                                         (wx.ACCEL_CTRL|wx.ACCEL_SHIFT,  ord('T'), ID_OPEN_LOG),
                                         (wx.ACCEL_CTRL,  ord('U'), 2012)])
        self.ceciliaEditor.SetAcceleratorTable(accel_tbl)

        self.buildFileMenu()
        self.buildEditMenu()
        self.buildFormatMenu()
        self.buildCsoundMenu()
        self.buildWindowMenu()
        self.buildHelpMenu()
        self.buildMenuBar()

class InterfaceMenuBar(MainMenuBar):
    def __init__(self, frame, ceciliaEditor):
        MainMenuBar.__init__(self, frame, ceciliaEditor)
        self.isEditor = False

        self.buildFileMenu()
        self.buildEditMenu()
        self.buildCsoundMenu()
        self.buildWindowMenu()
        self.buildHelpMenu()
        self.buildMenuBar()

    def marioSwitch(self, evt):
        if evt.GetInt() == 1:
            self.FindItemById(3002).Check(1)
            for slider in CeciliaLib.getUserSliders():
                slider.slider.useMario = True
                slider.slider.Refresh()
        else:
            self.FindItemById(3002).Check(0)
            for slider in CeciliaLib.getUserSliders():
                slider.slider.useMario = False 
                slider.slider.Refresh()
               