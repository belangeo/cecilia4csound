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

import sys, os, wx, time
from constants import * 

CeciliaVar = dict()
CeciliaVar['systemPlatform'] = sys.platform

CeciliaVar['numDisplays'] = 1
CeciliaVar['displaySize'] = []
CeciliaVar['displayOffset'] = []

CeciliaVar['editorSize'] = None
CeciliaVar['editorPosition'] = (20,20)

# Path of the currently opened file
CeciliaVar['currentCeciliaFile'] = ''
CeciliaVar['builtinModule'] = False

# Save path for the various dialogs that pops
CeciliaVar['openFilePath'] = os.path.expanduser('~')
CeciliaVar['saveFilePath'] = os.path.expanduser('~')
CeciliaVar['openAudioFilePath'] = os.path.expanduser('~')
CeciliaVar['saveAudioFilePath'] = os.path.expanduser('~')

# Preferences file
CeciliaVar['prefsFile'] = os.path.join(TMP_PATH, 'ceciliaPrefs.txt')

# Boolean that says if file was modified since last save
CeciliaVar['isModified'] = False

# Rename output file if it already exists
CeciliaVar['autoRename'] = True

# Available formats in Cecilia
CeciliaVar['supportedFormats'] = {'Mono': 1, 'Stereo': 2, 'Quad': 4, '5.1': 6, 'Octo': 8, 'Custom...': None}

CeciliaVar['availableAudioOutputs'] = []
CeciliaVar['availableAudioInputs'] = []
CeciliaVar['availableMidiOutputs'] = []
CeciliaVar['availableMidiInputs'] = []

CeciliaVar['soundfilePlayer'] = ''
CeciliaVar['soundfileEditor'] = ''
CeciliaVar['prefPath'] = ''

CeciliaVar['showPreview'] = 0
CeciliaVar['displayTable'] = 0

CeciliaVar['rememberedSound'] = True
CeciliaVar['useTooltips'] = 1
CeciliaVar['graphTexture'] = 1
CeciliaVar['moduleDescription'] = ''

# interface is a list of dictionaries.
# each entry is a dictionary defining a widget.
# the key is the name of the widget
# It is a list. not a dictionary.
# this way, we keep the user entries in order.
CeciliaVar['interfaceWidgets'] = []
CeciliaVar['interface'] = None
CeciliaVar['interfaceSize'] = (1000, 600)
CeciliaVar['interfacePosition'] = None
CeciliaVar['grapher'] = None
CeciliaVar['gainSlider'] = None
CeciliaVar['plugins'] = [None, None, None]
CeciliaVar['userSliders'] = []
CeciliaVar['userTogglePopups'] = []
CeciliaVar['userSamplers'] = []
CeciliaVar['userInputs'] = dict()
CeciliaVar['samplerSliders'] = []
CeciliaVar['samplerTogglePopup'] = []
CeciliaVar['samplerTableNum'] = 3000
CeciliaVar['samplerSliderTableNum'] = 6000
CeciliaVar['sliderTableNum'] = 10000
CeciliaVar['tableNum'] = 13000

CeciliaVar['presets'] = dict()
CeciliaVar['presetPanel'] = None

##################   Variables for Csound   ######################

CeciliaVar['outputFile'] = 'dac'
CeciliaVar['totalTime'] = 30.0
CeciliaVar['defaultTotalTime'] = 30.0

CeciliaVar['csound'] = None

# Csound Flags
CeciliaVar['sr'] = 44100
CeciliaVar['kr'] = 4410
CeciliaVar['ksmps'] = 10
CeciliaVar['nchnls'] = 2
CeciliaVar['sampSize'] = 'short' # 24bit, uchar, schar, float, long or short(=16bit)
CeciliaVar['audioFileType'] = 'aiff' # aiff, wav, 
if sys.platform == "win32":
    CeciliaVar['hardBuff'] = 4096
    CeciliaVar['softBuff'] = 2048
else:
    CeciliaVar['hardBuff'] = 2048
    CeciliaVar['softBuff'] = 1024
# Tempo is a list of tuples (time, tempo_in_bpm)
CeciliaVar['tempo'] = list()
CeciliaVar['audioPort'] = 'PortAudio'
CeciliaVar['audioOutput'] = 0
CeciliaVar['audioInput'] = ''
CeciliaVar['enableAudioInput'] = 0
CeciliaVar['useMidi'] = 0
CeciliaVar['midiPort'] = 'PortMidi'
CeciliaVar['midiDeviceIn'] = 0
CeciliaVar['scoreIn'] = ''
CeciliaVar['jack'] = {'client':'cecilia4', 'inPortName':'system:capture_', 'outPortName':'system:playback_'}
CeciliaVar['daytime'] = time.localtime()

#Extra options to control Csound
CeciliaVar['extraOptions'] = []
 
if wx.Platform == '__WXMSW__':
    CeciliaVar['faces'] = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'Courier',
              'size' : 8,
              'size2': 6,
              'interfaceKeywords': '#22B022',
              'csoundKeywords': '#2222B0',
              'scoreKeywords': 'STEEL BLUE',
              'instrKeywords': 'RED',
              'comments': 'MEDIUM FOREST GREEN',
              'strings': 'PINK',
              'headerKeywords': 'FIREBRICK',
              'default': '#000000',
              'number': '#367800',
              'comment': '#007F7F',
              'string': '#7F007F',
              'keyword': '#00007F',
              'triple': '#7F0000',
              'class': '#0000FF',
              'function': '#007F7F',
              'identifier': 'FOREST GREEN',
              'commentblock': '#7F7F7F'
             }
    CeciliaVar['editorSubTitleFont'] = 10
    CeciliaVar['controlSliderFont'] = 8
elif wx.Platform == '__WXMAC__':
    CeciliaVar['faces'] = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Courier',
              'other': 'Courier',
              'size' : 14,
              'size2': 11,
              'interfaceKeywords': 'GOLD',
              'csoundKeywords': '#2222B0',
              'scoreKeywords': 'STEEL BLUE',
              'instrKeywords': 'RED',
              'comments': 'MEDIUM FOREST GREEN',
              'strings': 'PINK',
              'headerKeywords': 'FIREBRICK',
              'default': '#000000',
              'number': '#367800',
              'comment': '#007F7F',
              'string': '#7F007F',
              'keyword': '#00007F',
              'triple': '#7F0000',
              'class': '#0000FF',
              'function': '#007F7F',
              'identifier': 'FOREST GREEN',
              'commentblock': '#7F7F7F'
             }
    CeciliaVar['editorSubTitleFont'] = 14
    CeciliaVar['controlSliderFont'] = 9
else:
    CeciliaVar['faces'] = { 'times': 'Times',
              'mono' : 'Monospace',
              'helv' : 'Monospace',
              'other': 'Monospace',
              'size' : 10,
              'size2': 8,
              'interfaceKeywords': '#229055',
              'csoundKeywords': '#2222B0',
              'scoreKeywords': 'STEEL BLUE',
              'instrKeywords': 'RED',
              'comments': 'MEDIUM FOREST GREEN',
              'strings': 'PINK',
              'headerKeywords': 'FIREBRICK',
              'default': '#000000',
              'number': '#367800',
              'comment': '#007F7F',
              'string': '#7F007F',
              'keyword': '#00007F',
              'triple': '#7F0000',
              'class': '#0000FF',
              'function': '#007F7F',
              'identifier': 'FOREST GREEN',
              'commentblock': '#7F7F7F'
             }
    CeciliaVar['editorSubTitleFont'] = 10
    CeciliaVar['controlSliderFont'] = 8

def readCeciliaPrefsFromFile():
    if os.path.isfile(PREFERENCES_FILE):
        try:
            file = open(PREFERENCES_FILE, 'rt')
        except IOError:
            print('Unable to open the preferences file.')
            return
        
        print('Loading Cecilia Preferences...')
        
        #### Some special cases ####
        convertToInt = ['sr', 'kr', 'ksmps', 'nchnls', 'audioOutput', 'audioInput',
                        'midiDeviceIn', 'useTooltips', 'enableAudioInput', 'graphTexture']  
        convertToFloat = ['totalTime', 'defaultTotalTime']                      
        convertToTuple = ['interfaceSize', 'interfacePosition', 'editorSize', 'editorPosition']
        jackPrefs = ['client', 'inPortName', 'outPortName']
        
        # Go thru the text file to assign values to the variables
        for i, line in enumerate(file.readlines()):
            if i == 0:
                if not line.startswith("version"):
                    print('preferences file from an older version not used. New preferences will be created.')
                    return
                else:
                    if line.strip(' \n').split('=')[1] != APP_VERSION:
                        print('preferences file from an older version not used. New preferences will be created.')
                        return
                    else:
                        continue

            pref = line.strip(' \n').split('=')
            
            if pref[1]!='':
                if pref[0] in convertToInt:
                    CeciliaVar[pref[0]] = int(pref[1])
                elif pref[0] in convertToFloat:
                    CeciliaVar[pref[0]] = float(pref[1])
                elif pref[0] in convertToTuple:
                    CeciliaVar[pref[0]] = eval(pref[1])        
                elif pref[0] in jackPrefs:
                    CeciliaVar['jack'][pref[0]] = pref[1]
                else:
                    CeciliaVar[pref[0]] = pref[1]  
        file.close()
        
    else:
        print('Preferences file not found')

def writeCeciliaPrefsToFile():
    # Variables that need to be saved
    varsToSave = ['interfaceSize', 'interfacePosition', 'useTooltips', 'enableAudioInput',
                  'editorSize', 'editorPosition', 'sr', 'kr', 'ksmps', 'nchnls', 'sampSize', 
                  'audioFileType', 'hardBuff', 'softBuff', 'audioPort', 'audioOutput',
                  'audioInput', 'midiPort', 'midiDeviceIn',
                  'client', 'inPortName', 'graphTexture',
                  'outPortName', 'soundfilePlayer', 'soundfileEditor', 'prefPath',
                  'openFilePath', 'saveFilePath', 'saveAudioFilePath', 
                  'openAudioFilePath', 'totalTime', 'defaultTotalTime']
    
    print('Writing Cecilia preferences...')
    
    #Open preferences file for writing
    try:
        file = open(PREFERENCES_FILE,'wt')
    except IOError:
        print('Unable to open the preferences file.')
        return
    
    # Write variables
    file.write("version=%s\n" % APP_VERSION)
    for key in CeciliaVar:
        if key in varsToSave:
            line = '%s=%s\n' % (key, CeciliaVar[key])
            file.write(line)
        elif key=='jack':
            line = '%s=%s\n' % ('client', CeciliaVar[key]['client'])
            line += '%s=%s\n' % ('inPortName', CeciliaVar[key]['inPortName'])
            line += '%s=%s\n' % ('outPortName', CeciliaVar[key]['outPortName'])
            file.write(line)
    
    file.close()

readCeciliaPrefsFromFile()
    
