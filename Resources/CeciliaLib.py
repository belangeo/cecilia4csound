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

import os, sys, wx, re, time, math, copy, codecs, ast
from types import UnicodeType, ListType, TupleType
from constants import *
import Variables as vars
from UDO import *
import unicodedata
from types import IntType
from subprocess import Popen

ceciliaEditor = None
csound = None
preferencePanel = None

DEFAULT_ENCODING = sys.getdefaultencoding()
ENCODING = sys.getfilesystemencoding()

def setSr(sr):
    vars.CeciliaVar['sr'] = sr

def getSr():
    return vars.CeciliaVar['sr']

def setKr(kr):
    vars.CeciliaVar['kr'] = kr

def getKsmps():
    return vars.CeciliaVar['ksmps']

def setKsmps(ksmps):
    vars.CeciliaVar['ksmps'] = ksmps

def getKr():
    return vars.CeciliaVar['kr']

def setNchnls(chnls):
    vars.CeciliaVar['nchnls'] = chnls
    updateNchnlsDevices()

def getNchnls():
    return vars.CeciliaVar['nchnls']

def setSampleSize(size):
    vars.CeciliaVar['sampSize'] = size

def getSampleSize():
    return vars.CeciliaVar['sampSize']

def setFileType(typ):   
    vars.CeciliaVar['audioFileType'] = typ

def getFileType():
    return vars.CeciliaVar['audioFileType']

def setOutputFile(f):   
    vars.CeciliaVar['outputFile'] = f

def getOutputFile():
    return vars.CeciliaVar['outputFile']

def setAudioOutput(x):   
    vars.CeciliaVar['audioOutput'] = x

def getAudioOutput():
    return vars.CeciliaVar['audioOutput']

def setEnableAudioInput(x):   
    vars.CeciliaVar['enableAudioInput'] = x

def getEnableAudioInput():
    return vars.CeciliaVar['enableAudioInput']

def setAudioInput(x):   
    vars.CeciliaVar['audioInput'] = x

def getAudioInput():
    return vars.CeciliaVar['audioInput']

def setAudioPort(port):   
    vars.CeciliaVar['audioPort'] = port

def getAudioPort():
    return vars.CeciliaVar['audioPort']

def setMidiPort(port):   
    vars.CeciliaVar['midiPort'] = port

def getMidiPort():
    return vars.CeciliaVar['midiPort']

def setSoftBuf(x):
    vars.CeciliaVar['softBuff'] = x

def getSoftBuf():
    return vars.CeciliaVar['softBuff']

def setHardBuf(x):
    vars.CeciliaVar['hardBuff'] = x

def getHardBuf():
    return vars.CeciliaVar['hardBuff']

def setMidiDeviceIn(dev):
    vars.CeciliaVar['midiDeviceIn'] = dev

def getMidiDeviceIn():
    return vars.CeciliaVar['midiDeviceIn']

def setMidiDeviceOut(dev):
    vars.CeciliaVar['midiDeviceOut'] = dev

def getMidiDeviceOut():
    return vars.CeciliaVar['midiDeviceOut']

def setMidiFileIn(f):
    vars.CeciliaVar['midiFileIn'] = f

def getMidiFileIn():
    return vars.CeciliaVar['midiFileIn']

def setMidiFileOut(f):
    vars.CeciliaVar['midiFileOut'] = f

def getMidiFileOut():
    return vars.CeciliaVar['midiFileOut']

def setScoreIn(sco):
    vars.CeciliaVar['scoreIn'] = sco

def getScoreIn():
    return vars.CeciliaVar['scoreIn']

def setJackParams(client = None, inPortName = None, outPortName = None):
    if not client==None:
        vars.CeciliaVar['jack']['client'] = client
    if not inPortName==None:
        vars.CeciliaVar['jack']['inPortName'] = inPortName
    if not outPortName==None:
        vars.CeciliaVar['jack']['outPortName'] = outPortName

def getJackParams():
    return vars.CeciliaVar['jack']

def setExtraOptions(opt):
    vars.CeciliaVar['extraOptions'].append(opt)

def getExtraOptions():
    return vars.CeciliaVar['extraOptions']

def insertTempo(pos, tempo):
    vars.CeciliaVar['tempo'].insert(pos, tempo)

def setTempo(tempo):
    vars.CeciliaVar['tempo'].append(tempo)

def getTempo():
    return vars.CeciliaVar['tempo']

def setOpenFilePath(path):
    vars.CeciliaVar['openFilePath'] = path

def getOpenFilePath():
    return ensureNFD(vars.CeciliaVar['openFilePath'])

def setSaveFilePath(path):
    vars.CeciliaVar['saveFilePath'] = path

def getSaveFilePath():
    return ensureNFD(vars.CeciliaVar['saveFilePath'])

def setOpenAudioFilePath(path):
    vars.CeciliaVar['openAudioFilePath'] = path
    
def getOpenAudioFilePath():
    return ensureNFD(vars.CeciliaVar['openAudioFilePath'])

def setSaveAudioFilePath(path):
    vars.CeciliaVar['saveAudioFilePath'] = path
    
def getSaveAudioFilePath():
    return ensureNFD(vars.CeciliaVar['saveAudioFilePath'])
    
def setCurrentCeciliaFile(path):
    vars.CeciliaVar['currentCeciliaFile'] = path

def getCurrentCeciliaFile():
    return ensureNFD(vars.CeciliaVar['currentCeciliaFile'])

def setIsModified(bool):
    if bool != vars.CeciliaVar['isModified']:
        ceciliaEditor.updateTitle(isModified=bool)
    vars.CeciliaVar['isModified'] = bool

def getIsModified():
    return vars.CeciliaVar['isModified']

def setTotalTime(time):
    vars.CeciliaVar['totalTime'] = time
    if getGrapher():
        getGrapher().setTotalTime(time)

def getTotalTime():
    return vars.CeciliaVar['totalTime']

def setDefaultTotalTime(time):
    vars.CeciliaVar['defaultTotalTime'] = time
    
def getDefaultTotalTime():
    return vars.CeciliaVar['defaultTotalTime']
        
def getUserInputs():
    return vars.CeciliaVar['userInputs']
    
def setUserInputs(x):
    vars.CeciliaVar['userInputs'] = x

def setCustomSupportedFormats(format):
    vars.CeciliaVar['supportedFormats']['Custom...'] = format

def getSupportedFormats():
    return vars.CeciliaVar['supportedFormats']

def getFaces():
    return vars.CeciliaVar['faces']

def getPlatform():
    return vars.CeciliaVar['systemPlatform']

def setAutoRenameFlag(a=True):
    vars.CeciliaVar['autoRename'] = a

def getAutoRenameFlag():
    return vars.CeciliaVar['autoRename']
    
def setAvailableAudioOutputs(x):
    vars.CeciliaVar['availableAudioOutputs'] = x
    
def getAvailableAudioOutputs():
    return vars.CeciliaVar['availableAudioOutputs']
    
def setAvailableAudioInputs(x):
    vars.CeciliaVar['availableAudioInputs'] = x
    
def getAvailableAudioInputs():
    return vars.CeciliaVar['availableAudioInputs']
    
def setAvailableMidiOutputs(x):
    vars.CeciliaVar['availableMidiOutputs'] = x
    
def getAvailableMidiOutputs():
    return vars.CeciliaVar['availableMidiOutputs']
    
def setAvailableMidiInputs(x):
    vars.CeciliaVar['availableMidiInputs'] = x
    
def getAvailableMidiInputs():
    return vars.CeciliaVar['availableMidiInputs']
   
def setSoundfilePlayerPath(path):
    vars.CeciliaVar['soundfilePlayer'] = path
    
def getSoundfilePlayerPath():
    return vars.CeciliaVar['soundfilePlayer']
    
def setSoundfileEditorPath(path):
    vars.CeciliaVar['soundfileEditor'] = path
    
def getSoundfileEditorPath():
    return vars.CeciliaVar['soundfileEditor']

def setPrefPath(path):
    vars.CeciliaVar['prefPath'] = path
    
def getPrefPath():
    return vars.CeciliaVar['prefPath']

def setDisplayTable(x):
    vars.CeciliaVar['displayTable'] = x

def getDisplayTable():
    return vars.CeciliaVar['displayTable']

def setShowPreview(x):
    vars.CeciliaVar['showPreview'] = x

def getShowPreview():
    return vars.CeciliaVar['showPreview']

def setUseMidi(x):
    vars.CeciliaVar['useMidi'] = x

def getUseMidi():
    return vars.CeciliaVar['useMidi']

def writeVarToDisk():
    vars.writeCeciliaPrefsToFile()

def setInterface(x):
    vars.CeciliaVar['interface'] = x

def getInterface():
    return vars.CeciliaVar['interface']
    
def getControlPanel():
    return vars.CeciliaVar['interface'].getControlPanel()

def getEditorSubTitleFont():
    return vars.CeciliaVar['editorSubTitleFont']

def getControlSliderFont():
    return vars.CeciliaVar['controlSliderFont']

def setGrapher(x):
    vars.CeciliaVar['grapher'] = x

def getGrapher():
    return vars.CeciliaVar['grapher']

def setInterfaceWidgets(list):
    vars.CeciliaVar['interfaceWidgets'] = list

def getInterfaceWidgets():
    return vars.CeciliaVar['interfaceWidgets']

def setSamplerSliders(list):
    vars.CeciliaVar['samplerSliders'] = list

def getSamplerSliders():
    return vars.CeciliaVar['samplerSliders']

def setUserSliders(x):
    vars.CeciliaVar['userSliders'] = x

def getUserSliders():
    return vars.CeciliaVar['userSliders']

def setUserTogglePopups(x):
    vars.CeciliaVar['userTogglePopups'] = x

def getUserTogglePopups():
    return vars.CeciliaVar['userTogglePopups']

def setSamplerTogglePopup(x):
    vars.CeciliaVar['samplerTogglePopup'] = x

def getSamplerTogglePopup():
    return vars.CeciliaVar['samplerTogglePopup']

def setUserSamplers(x):
    vars.CeciliaVar['userSamplers'] = x

def getUserSamplers():
    return vars.CeciliaVar['userSamplers']

def setGainSlider(x):
    vars.CeciliaVar['gainSlider'] = x

def getGainSlider():
    return vars.CeciliaVar['gainSlider']

def getPlugins():
    return vars.CeciliaVar['plugins']
    
def setPlugins(x, pos):
    vars.CeciliaVar['plugins'][pos] = x

def setSamplerTableNum(x):
    vars.CeciliaVar['samplerTableNum'] = x

def getSamplerTableNum():
    return vars.CeciliaVar['samplerTableNum']

def setSamplerSliderTableNum(x):
    vars.CeciliaVar['samplerSliderTableNum'] = x

def getSamplerSliderTableNum():
    return vars.CeciliaVar['samplerSliderTableNum']

def setSliderTableNum(x):
    vars.CeciliaVar['sliderTableNum'] = x

def getSliderTableNum():
    return vars.CeciliaVar['sliderTableNum']

def getTableNum():
    return vars.CeciliaVar['tableNum']
    
def setTableNum(x):
    vars.CeciliaVar['tableNum'] = x
        
def setPresets(presets):
    vars.CeciliaVar['presets'] = presets
    
def getPresets():
    return vars.CeciliaVar['presets']

def deletePreset(preset):
    del vars.CeciliaVar['presets'][preset]
    
def setPresetPanel(preset):
    vars.CeciliaVar['presetPanel'] = preset

def getPresetPanel():
    return vars.CeciliaVar['presetPanel']

def setBuiltinModule(x):
    vars.CeciliaVar['builtinModule'] = x

def getBuiltinModule():
    return vars.CeciliaVar['builtinModule']

def setRememberSound(x):
    vars.CeciliaVar['rememberedSound'] = x

def getRememberSound():
    return vars.CeciliaVar['rememberedSound']

def setInterfaceSize(x):
    vars.CeciliaVar['interfaceSize'] = x
    
def getInterfaceSize():
    return vars.CeciliaVar['interfaceSize']  

def setInterfacePosition(x):
    vars.CeciliaVar['interfacePosition'] = x

def getInterfacePosition():
    return vars.CeciliaVar['interfacePosition']    

def setEditorSize(x):
    vars.CeciliaVar['editorSize'] = x

def getEditorSize():
    return vars.CeciliaVar['editorSize']  

def setEditorPosition(x):
    vars.CeciliaVar['editorPosition'] = x

def getEditorPosition():
    return vars.CeciliaVar['editorPosition']    

def setNumDisplays(x):
    vars.CeciliaVar['numDisplays'] = x
    
def getNumDisplays():
    return vars.CeciliaVar['numDisplays']
    
def setDisplaySize(x):
    vars.CeciliaVar['displaySize'] = x
    
def getDisplaySize():
    return vars.CeciliaVar['displaySize']

def setDisplayOffset(x):
    vars.CeciliaVar['displayOffset'] = x

def getDisplayOffset():
    return vars.CeciliaVar['displayOffset']

def setUseTooltips(x):
    vars.CeciliaVar['useTooltips'] = x

def getUseTooltips():
    return vars.CeciliaVar['useTooltips']

def setUseGraphTexture(x):
    vars.CeciliaVar['graphTexture'] = x
    
def getUseGraphTexture():
    return vars.CeciliaVar['graphTexture']
                
def setDayTime():
    vars.CeciliaVar['daytime'] = time.localtime()

def getDayTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S", vars.CeciliaVar['daytime'])

def setModuleDescription(x):
    vars.CeciliaVar['moduleDescription'] = x
    
def getModuleDescription():
    return vars.CeciliaVar['moduleDescription']
                 
#----------------------------------------------------------
#----------------------------------------------------------
 
def getCsoundFlags():
    
    flags = ''

    # Turn off display
    if not getDisplayTable():
        flags += '-d '
    
    # Sample size and File type
    flags += '--format=%s:%s ' % (getSampleSize(), getFileType())

    # Input output buffer size
    flags += '-b %s -B %s ' % (getSoftBuf(), getHardBuf())

    # Output
    if getOutputFile() == 'dac':
        if getAudioPort() == 'Jack':
            flags += '-o %s:%s -+rtaudio=%s ' % (getOutputFile(), getJackParams()['outPortName'], getAudioPort())            
        else:
            flags += '-o %s%s -+rtaudio=%s ' % (getOutputFile(), getAudioOutput(), getAudioPort())
    else:
        flags += '-o "%s" ' % getOutputFile()
    
    # Audio input
    if getAudioInput() != '' and getEnableAudioInput():
        if getAudioPort() == 'Jack':
            flags += '-iadc:%s ' % getJackParams()['inPortName']
        else:
            flags += '-iadc%s ' % getAudioInput()
    
    # MIDI
    if getUseMidi():
        if getMidiPort() != '':
            flags += '-+rtmidi=%s ' % getMidiPort()
        if getMidiDeviceIn() != '':
            if getMidiDeviceIn() >= len(getAvailableMidiInputs()):
                flags += '-Ma '
            else:    
                flags += '-M %s ' % getMidiDeviceIn()
        #if getMidiDeviceOut() != '':
        #    flags += '-Q %s ' % getMidiDeviceOut()
        #if getMidiFileIn() != '':
        #    flags += '-F "%s" ' % getMidiFileIn()
        #if getMidiFileOut() != '':
        #    flags += '--midioutfile= %s ' % getMidiFileOut()

    if getScoreIn() != '':
        flags += '-L %s ' % getScoreIn()
    
    # Jack
    if getAudioPort() == 'Jack':
        flags += '-+jack_client=%s' % getJackParams()['client']
    
    # Add extra options that Cecilia doesn't deal with
    for flag in getExtraOptions():
        flags += flag
        flags += ' '
    
    return flags

def getTempoLine():
    tempoText = ''
    if len(getTempo()) >= 2:
        tempoText = 't '
        for t in getTempo():
            tempoText += t[0]
            tempoText += t[1]
        tempoText += '\n'
    
    return tempoText

def openDirDialog(parent, path='/'):
 
    dirDialog = wx.DirDialog(parent, message='Choose folder', 
                                defaultPath=path, 
                                style=wx.DD_DEFAULT_STYLE)
                                    
    if dirDialog.ShowModal() == wx.ID_OK:
        dirPath = dirDialog.GetPath()
    else:
        dirPath = None
    
    dirDialog.Destroy()
    
    return dirPath

def openAudioFileDialog(parent, wildcard, type='open', defaultPath='/'):
        
    openDialog = wx.FileDialog(parent, message='Choose a file to %s' % type, 
                                defaultDir=defaultPath,
                                wildcard=wildcard, 
                                style=wx.FD_OPEN | wx.FD_PREVIEW)
                                    
    if openDialog.ShowModal() == wx.ID_OK:
        filePath = openDialog.GetPath()
    else:
        filePath = None
    
    openDialog.Destroy()
    
    return filePath

def saveFileDialog(parent, wildcard, type='Save'):
    if type == 'Save audio':
        defaultPath = getSaveAudioFilePath()
    else:
        defaultPath = getSaveFilePath()
    
    defaultFile = os.path.split(getCurrentCeciliaFile())[1]
    saveAsDialog = wx.FileDialog(parent, message="%s file as ..." % type,
                                 defaultDir=defaultPath,
                                 defaultFile=defaultFile,
                                 wildcard=wildcard,
                                 style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)
    
    if saveAsDialog.ShowModal() == wx.ID_OK:
        filePath = saveAsDialog.GetPath()
        if type == 'Save audio':
            setSaveAudioFilePath(os.path.split(filePath)[0])
        else:
            setSaveFilePath(os.path.split(filePath)[0])
    else:
        filePath = None
    
    saveAsDialog.Destroy()
    
    return filePath

def saveBeforeClose(parent):
    if getIsModified():
        saveBeforeCloseDialog = wx.MessageDialog(parent,
                        'This file has been modified since the last save point. \
                        Would you like to save the changes?',
                        'Save Changes?', wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT)
    else:
        return True
    
    answer = saveBeforeCloseDialog.ShowModal()
    if answer == wx.ID_YES:
        if saveCeciliaFile(parent, False):
            result =  True
        else:
            result =  False
    elif answer == wx.ID_NO:
        result =  True
    elif answer == wx.ID_CANCEL:
        result =  False

    saveBeforeCloseDialog.Destroy()
    return result

def showErrorDialog(title, msg):
    dlg = wx.MessageDialog(None, msg, title, wx.OK)
    dlg.ShowModal()
    dlg.Destroy()

def addHeaderToOrchestra(orchestraText):
    # Parse the text from the editor to see if sr, kr, ksmps and nchnls are present
    foundSR = False
    foundKR = False
    foundKSMPS = False
    foundNCHNLS = False

    if orchestraText.find('opcode') != -1:
        index = orchestraText.find('opcode')
    else:
        index = orchestraText.find('instr')
    orchHeader = orchestraText[0: index]

    ##### Sound tables loading #####
    numTables = orchHeader.count(' tables ')
    pos = 0
    tables_used = []
    
    for i in range(numTables):
        newpos = orchHeader.find(' tables ', pos)
        subpos = newpos
        chnls = 1
        while subpos != 0:
            try:
                unicodedata.name(orchHeader[subpos])
                if orchHeader[subpos] == ',': chnls += 1
                subpos += -1
            except:
                break
        lineFirstPos = subpos
        variables = orchHeader[lineFirstPos:newpos].split(',')
        subpos = newpos        
        while orchHeader[subpos] != ']':
            if orchHeader[subpos] == '[': openBracePos = subpos
            subpos += 1
        closeBracePos = subpos
        tableName = orchHeader[openBracePos+1:closeBracePos]
        tableLen = getUserInputs()[tableName]['gensize%s' % tableName]
        tableChnls = getUserInputs()[tableName]['nchnls%s' % tableName]
        newText = '\n'
        for i in range(chnls):
            num = getTableNum()
            if i >= tableChnls:
                chn = i % tableChnls
                newText += '%s = %s\n' % (variables[i].strip(), variables[chn].strip())
            else:    
                chn = (i % tableChnls) + 1
                newText += '%s ftgen %i, 0, %i, 1, [%s], 0, 0, %i\n' % (variables[i].strip(), num, tableLen, tableName, chn) 
                setTableNum(num+1)
        orchHeader = orchHeader[0:lineFirstPos] + newText + orchHeader[closeBracePos+1:]

    ##### Square brackets [key] replacement #####
    posOpenBracket = orchHeader.find('[')
    while posOpenBracket != -1:
        posCloseBracket = orchHeader.find(']', posOpenBracket)
        key = orchHeader[posOpenBracket+1:posCloseBracket]
        if key in getUserInputs().keys():
            new = '"' + convertWindowsPath(getUserInputs()[key]['path']) + '"'
            orchHeader = orchHeader[:posOpenBracket] + new + orchHeader[posCloseBracket+1:]
        else:
            for k in getUserInputs().keys():
                if 'off%s' % k == key or 'nchnls%s' % k == key or 'gensize%s' % k == key or 'sr%s' % k == key or 'dur%s' % k == key:
                    new = '%s' % getUserInputs()[k][key]
                    break
            orchHeader = orchHeader[:posOpenBracket] + new + orchHeader[posCloseBracket+1:]
        posOpenBracket = orchHeader.find('[')
 
    for line in orchestraText.splitlines(True):
        line = line.replace(' ','')
        if line.find('sr=') != -1:
            foundSR = True
        elif line.find('kr=') != -1:
            foundKR = True
        elif line.find('ksmps=') != -1:
            foundKSMPS = True
        elif line.find('nchnls=') != -1:
            foundNCHNLS = True
    
    # Build the header
    header = ''
    if not foundSR:
        header += 'sr = %d\n' % getSr()
    if not foundKSMPS and not foundKR:
        header += 'ksmps = %d\n' % getKsmps()
    if not foundNCHNLS:
        header += 'nchnls = %d\n' % getNchnls()
    if not foundSR or not foundKR or not foundNCHNLS:
        header += '\n\n'

    header += orchHeader + '\n'    
    return header

def presetsDictToText():
    text = ''
    for preset in getPresets():
        text += '***%s\n' % preset
        for data in getPresets()[preset]:
            text += '%s = %s\n' % (data, getPresets()[preset][data])
        text += '\n'            
    return text

def presetsTextToDict(linesList):
    presets = dict()
    preset = ''
    setPresets({})
    for line in linesList:
        if line[0:3] == '***':
            preset = ensureNFD(line[3:].strip('\n'))
            getPresets()[preset] = dict()
            continue
        
        lineSplit = line.split(' = ')
        if len(lineSplit) > 1:
            key = lineSplit[0]
            data = lineSplit[1].strip('\n')
            if preset != '':
                try:
                    getPresets()[preset][key] = ast.literal_eval(data)
                except:
                    getPresets()[preset][key] = data
    if getInterface():
        getPresetPanel().loadPresets()
            
def loadPresetFromDict(preset):
    if getPresets().has_key(preset):
        for data in getPresets()[preset]:                
            if data == 'nchnls':
                setNchnls(getPresets()[preset][data])
                
            elif data == 'duration':
                setTotalTime(getPresets()[preset][data])
                getControlPanel().updateDurationSlider()
                
            elif data == 'activeScore':
                ceciliaEditor.changeScorePanel(getPresets()[preset][data])
     
            elif data == 'userInputs':
                if getPresets()[preset][data] == {}:
                    continue
                ok = True
                prekeys = getPresets()[preset][data].keys()
                for key in prekeys:
                    if not os.path.isfile(getPresets()[preset][data][key]['path']):
                        ok = False
                        break
                if not getRememberSound():
                    if ok:
                        setUserInputs(copy.deepcopy(getPresets()[preset][data]))
                        updateInputsFromDict()
                    else:
                        for input in getUserInputs():
                            cfilein = getControlPanel().getCfileinFromName(input)
                            cfilein.reset()
                else:
                    if ok:
                        setUserInputs(copy.deepcopy(getPresets()[preset][data]))
                        updateInputsFromDict()
                    else:
                        pass
                                       
            elif data == 'userSliders':
                slidersDict = getPresets()[preset][data]
                for slider in getUserSliders():
                    if slider.getName() in slidersDict:
                        slider.setState(slidersDict[slider.getName()])
                del slidersDict
            
            elif data == 'plugins':
                pluginsDict = getPresets()[preset][data]
                getControlPanel().setPlugins(pluginsDict)
                del pluginsDict
                    
            elif data == 'userTogglePopups':
                togDict = getPresets()[preset][data]
                for widget in getUserTogglePopups():
                    if widget.getName() in togDict:
                        widget.setValue(togDict[widget.getName()], True)
                del togDict
            
            if getPresets()[preset].has_key('userGraph'):    
                graphDict = getPresets()[preset]['userGraph']
                ends = ['min', 'max']
                for line in graphDict:
                    for i, graphLine in enumerate(getGrapher().getPlotter().getData()):
                        if line == graphLine.getName():
                            graphLine.setLineState(copy.deepcopy(graphDict[line]))
                            break    
                        else:        
                            for end in ends: 
                                if graphLine.getLabel().endswith(end) and line.endswith(end) and line.startswith(graphLine.getName()):
                                    graphLine.setLineState(copy.deepcopy(graphDict[line]))
                                    break
                del graphDict
                
        getPresetPanel().setLabel(preset)
        getGrapher().getPlotter().draw()
                
def savePresetToDict(presetName):
    presetDict = dict()
    
    presetDict['nchnls'] = getNchnls()
    presetDict['duration'] = getTotalTime()
    presetDict['activeScore'] = ceciliaEditor.getActiveScore()
    
    if getInterface():            
        presetDict['userInputs'] = completeUserInputsDict()
        
        sliderDict = dict()
        for slider in getUserSliders():
            sliderDict[slider.getName()] = slider.getState()
        presetDict['userSliders'] = sliderDict
        del sliderDict

        widgetDict = dict()
        plugins = getPlugins()
        for i, plugin in enumerate(plugins):
            if plugin == None:
                widgetDict[i] = ['None', [0,0,0,0],[[0,0,None],[0,0,None],[0,0,None]]]
            else:    
                widgetDict[i] = [plugin.getName(), plugin.getParams(), plugin.getStates()]
        presetDict['plugins'] = widgetDict
        del widgetDict
                
        widgetDict = dict()
        for widget in getUserTogglePopups():
            widgetDict[widget.getName()] = widget.getValue()
        presetDict['userTogglePopups'] = widgetDict
        del widgetDict

        graphDict = dict()
        ends = ['min', 'max']
        for line in getGrapher().getPlotter().getData():
            if line.slider == None:
                graphDict[line.getName()] = line.getLineState()
            else:        
                outvalue = line.slider.getValue()
                if type(outvalue) not in [ListType, TupleType]:
                    graphDict[line.getName()] = line.getLineState()
                else:
                    for i in range(len(outvalue)): 
                        if line.getLabel().endswith(ends[i]):
                            graphDict[line.getName()+ends[i]] = line.getLineState()
                            break
        presetDict['userGraph'] = graphDict
        del graphDict
            
    getPresets()[presetName] = presetDict
    setIsModified(True)
    
def saveCeciliaFile(parent, showDialog=True):
    if getCurrentCeciliaFile() == '' or getBuiltinModule():
        showDialog = True

    if showDialog:
        wildcard = "Cecilia file (*.cec)|*.cec|"     \
                   "All files (*.*)|*.*"
        
        fileToSave = saveFileDialog(parent, wildcard, 'Save')
        if not fileToSave:
            return False
        else:
            if not fileToSave.endswith('.cec'):
                fileToSave = fileToSave + '.cec'    
    else:
        fileToSave = getCurrentCeciliaFile()
    
    try:
        file = open(fileToSave, 'wt')
    except IOError:
        dlg = wx.MessageDialog(parent, 'Please verify permissions and write access on the file and try again.',
                            '"%s" could not be opened for writing' % (fileToSave), 
                            wx.OK | wx.ICON_EXCLAMATION)
        if dlg.ShowModal()==wx.ID_OK:
            dlg.Destroy()
            return
    
    # Write CeciliaInterface to the text file
    ceciliaInterface = '<CeciliaInterface>\n'
    a = parent.interface.editor.GetText()
    if a[len(a)-1:]=='\n':
        ceciliaInterface += a
    else:
        ceciliaInterface += a + '\n'
    ceciliaInterface+= '</CeciliaInterface>\n\n'
    file.write(ceciliaInterface)

    formats = [key for key in getSupportedFormats().keys()]
    for format in sorted(formats):
        ceciliaOrc = '<%s>\n' % format
        a = parent.orchestraPanels[format].editor.GetText()
        if a[len(a)-1:]=='\n':
            ceciliaOrc+= a
        else:
            ceciliaOrc+= a + '\n'
        ceciliaOrc+= '</%s>\n\n' % format
        file.write(ceciliaOrc)
    
    scoreTypes = SCORE_TYPES
    for scoreType in scoreTypes:
        ceciliaScore = '\n<%sScore>\n' % scoreType
        a = parent.scorePanels[scoreType].editor.GetText()
        if a[len(a)-1:]=='\n':
            ceciliaScore+= a
        else:
            ceciliaScore+= a + '\n'
        ceciliaScore+= '</%sScore>\n\n' % scoreType
        file.write(ceciliaScore)
    
    ceciliaOpen = '\n<CeciliaOpen>\n'
    ceciliaOpen += 'scoreType=%s\n' % getCeciliaEditor().activeScore 
    if getInterface():
        ceciliaOpen += 'totalTime=%f\n' % getTotalTime()
        ceciliaOpen += 'masterVolume=%f\n' % getGainSlider().GetValue()
    ceciliaOpen += '\n</CeciliaOpen>\n'
    file.write(ceciliaOpen)
    
    ceciliaData = '\n<CeciliaData>\n'
        
    ceciliaData += presetsDictToText()
    
    ceciliaData += '</CeciliaData>\n'
    file.write(ceciliaData)

    file.close()

    setBuiltinModule(False)
    setCurrentCeciliaFile(fileToSave)

    setIsModified(False)
    
    return True

def openCeciliaFile(parent, openfile=None, builtin=False):    
    if not openfile:
        wildcard = "Cecilia file (*.cec)|*.cec|"     \
                   "Csound unified orchestra (*.csd)|*.csd|"     \
                   "All files (*.*)|*.*"

        defaultPath = getOpenFilePath()
            
        openDialog = wx.FileDialog(parent, message='Choose a file to %s' % type, 
                                    defaultDir=defaultPath,
                                    wildcard=wildcard, 
                                    style=wx.OPEN)
                                        
        if openDialog.ShowModal() == wx.ID_OK:
            cecFilePath = openDialog.GetPath()
            setOpenFilePath(os.path.split(cecFilePath)[0])
        else:
            cecFilePath = None
        
        openDialog.Destroy()

        if cecFilePath == None:
            return

    else:
        cecFilePath = openfile

    ext = cecFilePath.rsplit('.', 1)[1]

    if ext == 'csd':
        importCsdFile(parent, cecFilePath)
        return
    elif ext == 'orc':
        importOrcFile(parent, cecFilePath)
        return
    elif ext == 'sco':
        importScoFile(parent, cecFilePath)
        return

    snds = []
    if getRememberSound():
        for key in getUserInputs().keys():
            if getUserInputs()[key]['path'] != '':
                snds.append(getUserInputs()[key]['path'])

    if not closeCeciliaFile(parent):
        return

    getCeciliaEditor().Hide()
    
    # Build a dictionary to store all the parts of the text file
    separatedText = {'interface':[], 'Mono':[], 'Stereo':[], 'Open': [],
                'Quad':[], '5.1':[], 'Octo':[], 'Custom...':[], 'data':[], 'score':[], 'Csound':[], 'Python':[]}
    section = ''

    try:
        file = open(cecFilePath, 'rt')
    except IOError:
        print 'Unable to read the selected text file'
    
    # Write the different sections of the text file in the good section of the dictionary
    for line in file.readlines():
        if line.find('<CeciliaInterface>') != -1:
            section = 'interface'
        elif line.find('<CeciliaData>') != -1:
            section = 'data'
        elif line.find('<CeciliaOpen>') != -1:
            section = 'Open'
        elif line.find('<Mono>') != -1:
            section = 'Mono'
        elif line.find('<Stereo>') != -1:
            section = 'Stereo'
        elif line.find('<Quad>') != -1:
            section = 'Quad'
        elif line.find('<5.1>') != -1:
            section = '5.1'
        elif line.find('<Octo>') != -1:
            section = 'Octo'
        elif line.find('<Custom...>') != -1:
            section = 'Custom...'
        elif line.find('<CeciliaScore>') != -1:
            section = 'Csound'
        elif line.find('<CsoundScore>') != -1:
            section = 'Csound'
        elif line.find('<PythonScore>') != -1:
            section = 'Python'
        elif line.find('</') !=-1:
            section = ''
        else:
            if section != '':
                separatedText[section].append(line)
    
    file.close()

    if builtin:
        setBuiltinModule(True)
    else:
        setBuiltinModule(False)
    setCurrentCeciliaFile(cecFilePath)
    parent.newRecent(cecFilePath)
    after = wx.CallLater(200, setIsModified, False)
    
    # Write text to the editors
    showInterface = False
    for line in separatedText['interface']:
        line = line.replace('\t', '    ')
        if line != '\n':
            showInterface = True
            parent.interface.editor.AppendText(line)
    for format in getSupportedFormats():
        for line in separatedText[format]:
            line = line.replace('\t', '    ')
            parent.orchestraPanels[format].editor.AppendText(line)
    for scoreType in SCORE_TYPES:
        for line in separatedText[scoreType]:
            line = line.replace('\t', '    ')
            parent.scorePanels[scoreType].editor.AppendText(line)
    moduleInfo = ''

    parent.changeOrchestraPanel(getNchnls())
    parent.interface.editor.EmptyUndoBuffer()
    for format in getSupportedFormats():
        parent.orchestraPanels[format].editor.EmptyUndoBuffer()
    for scoreType in SCORE_TYPES:
        parent.scorePanels[scoreType].editor.EmptyUndoBuffer()

    setIsModified(False)
    
    presetsTextToDict(separatedText['data'])
         
    scoreType = '' 
    if separatedText['Open'] != []:
        for line in separatedText['Open']:
            if 'scoreType' in line:
                scoreType = line.strip().replace('scoreType=', '')
                break
    if scoreType:
        parent.changeScorePanel(scoreType)
    else:                         
        parent.changeScorePanel('Csound')

    if showInterface:
        getCeciliaEditor().onUpdateInterface(None)
        if separatedText['Open'] != []:
            for line in separatedText['Open']:
                if 'totalTime' in line:
                    setTotalTime(float(line.strip().replace('totalTime=', '')))
                    getControlPanel().durationSlider.SetValue(float(line.strip().replace('totalTime=', '')))
                if 'masterVolume' in line:
                    getGainSlider().SetValue(float(line.strip().replace('masterVolume=', '')))
        wx.CallAfter(getCeciliaEditor().Hide)
        wx.CallAfter(getInterface().Raise)
    else:    
        getCeciliaEditor().Show()
        
    if getInterface():
        for i, cfilein in enumerate(getControlPanel().getCfileinList()):
            if i >= len(snds):
                break
            cfilein.onLoadFile(snds[i])

def closeCeciliaFile(parent):
    if not saveBeforeClose(parent):
        return False
    getCeciliaEditor().closeInterface()
    parent.interface.editor.ClearAll()
    for format in getSupportedFormats():
        parent.orchestraPanels[format].editor.ClearAll()
    for scoreType in SCORE_TYPES:
        parent.scorePanels[scoreType].editor.ClearAll()
    
    setCurrentCeciliaFile('')
    if getInterface():
        getInterface().onClose(wx.EVT_CLOSE)
        setInterface(None)
        setPresets({})

    wx.CallLater(200, setIsModified, False)
    return True

def importOrcFile(parent, csdFilePath):
    try:
        file = open(csdFilePath, 'rt')
    except IOError:
        print 'Unable to read the selected text file'

    text = file.read()
    file.close()

    text = text.replace('\t', '    ')
    parent.orchestraPanels[parent.activeOrchestra].editor.SetText(text)
    parent.orchestraPanels[parent.activeOrchestra].editor.ConvertEndOfLines()
    
    setIsModified(True)

def importScoFile(parent, csdFilePath):
    try:
        file = open(csdFilePath, 'rt')
    except IOError:
        print 'Unable to read the selected text file'

    text = file.read()
    file.close()

    text = text.replace('\t', '    ')
    parent.scorePanels['Csound'].editor.SetText(text) 
    parent.scorePanels['Csound'].editor.ConvertEndOfLines()
    parent.changeScorePanel('Csound')
    
    setIsModified(True)
    
def importCsdFile(parent, csdFilePath):
    if not closeCeciliaFile(parent):
        return

    separatedText = {'CsoundSynthesizer':[], 'CsOptions':[], 'CsInstruments':[], 'CsScore':[],
                'CsFileB':[], 'CsVersion':[], 'CsLicense':[]}
    section = ''
    
    try:
        file = open(csdFilePath, 'rt')
    except IOError:
        print 'Unable to read the selected text file'
    
    for line in file.readlines():
        if line.find('<CsoundSynthesizer>') != -1:
            section = 'CsoundSynthesizer'
        elif line.find('<CsOptions>') != -1:
            section = 'CsOptions'
        elif line.find('<CsInstruments>') != -1:
            section = 'CsInstruments'
        elif line.find('<CsScore>') != -1:
            section = 'CsScore'
        elif line.find('<CsFileB>') != -1:
            section = 'CsFileB'
        elif line.find('<CsVersion>') != -1:
            section = 'CsVersion'
        elif line.find('<CsLicense>') != -1:
            section = 'CsLicense'
        elif line.find('</') !=-1:
            section = ''
        else:
            if section != '':
                separatedText[section].append(line)
            
    file.close()
        
    moduleInfo = ''
    for line in separatedText['CsoundSynthesizer']:
        moduleInfo += line + '\n'
    
    orchestra = []

    # Scan the Csound instruments for sr, kr, ksmps or nchnls first
    for line in separatedText['CsInstruments']:
        tmp = line
        if tmp.replace(' ', '').find('kr=') != -1:
            setKr(int(re.findall(r'\d+', tmp)[0]))
        elif tmp.replace(' ', '').find('sr=') != -1:
            setSr(int(re.findall(r'\d+', tmp)[0].strip()))
        elif tmp.replace(' ', '').find('nchnls=') != -1:
            setNchnls(int(re.findall(r'\d+', tmp)[0]))
        else:
            orchestra.append(line)
            
    parent.setOrchestraPanel()

    for line in orchestra:
        line = line.replace('\t', '    ')
        parent.orchestraPanels[parent.activeOrchestra].editor.AppendText(line)
    parent.orchestraPanels[parent.activeOrchestra].editor.ConvertEndOfLines()
        
    for line in separatedText['CsScore']:
        if line.find('t ') != -1:
            tmpList = re.findall(r'\d+', line)
            for i in range (0, len(tmpList)/2):
                t = int(tmpList[2*i]), int(tmpList[2*i+1])
                setTempo(t)
        line = line.replace('\t', '    ')
        parent.scorePanels['Csound'].editor.AppendText(line)        
    parent.scorePanels['Csound'].editor.ConvertEndOfLines()
    
    # Parse Csound option flags after the <CsInstruments> because they overwrite it
    ################## Still to implement : --format=type (support all types) #######################
    ### lots of weird stuff here... need a cleanup. ex: -o dac (not working) -odac (working)
    for line in separatedText['CsOptions']:
        # Don't take commented lines in consideration
        if line.lstrip(' ')[0]== ';':
            continue

        # Deal with file types:
        if line.find('-A ')!=-1 or line.find('--aiff')!=-1 or line.find('--format=aiff')!=-1:
            setFileType('aiff')
        if line.find('-a ')!=-1 or line.find('--format=alaw')!=-1:
            setFileType('alaw')
        if line.find('-J ')!=-1 or line.find('--ircam')!=-1 or line.find('--format=ircam')!=-1:
            setFileType('ircam')
        if line.find('-u ')!=-1 or line.find('--format=ulaw')!=-1:
            setFileType('ulaw')
        if line.find('-W ')!=-1 or line.find('--wave')!=-1 or line.find('--format=wave')!=-1:
            setFileType('wav')

        # Deal with sample size:
        if line.find('-3 ')!=-1 or line.find('--format=24bit')!=-1:
            setSampleSize('24bit')
        if line.find('-8 ')!=-1 or line.find('--format=uchar')!=-1:
            setSampleSize('uchar')
        if line.find('-c ')!=-1 or line.find('--format=schar')!=-1:
            setSampleSize('schar')
        if line.find('-f ')!=-1 or line.find('--format=float')!=-1:
            setSampleSize('float')
        if line.find('-l ')!=-1 or line.find('--format=long')!=-1:
            setSampleSize('long')
        if line.find('-s ')!=-1 or line.find('--format=short')!=-1:
            setSampleSize('short')
            
        #Deal with input and output
        if line.find('-i ')!=-1:
            startIdx = (line.find('-i ')+3)
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setAudioInput(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--input=')!=-1:
            startIdx = (line.find('--input=')+8)
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setAudioInput(line[startIdx: line.find(endChar,startIdx)])
        if line.find('-o ')!=-1:
            startIdx = (line.find('-o ')+3)
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setAudioOutput(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--output=')!=-1:
            startIdx = (line.find('--output=')+9)
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setAudioOutput(line[startIdx: line.find(endChar,startIdx)])

        # Deal with other audio options
        if line.find('-h ')!=-1 or line.find('--noheader')!=-1:
            setExtraOptions('--noheader')
        if line.find('-K ')!=-1 or line.find('--nopeaks')!=-1:
            setExtraOptions('--nopeaks')
        if line.find('-n ')!=-1 or line.find('--nosound')!=-1:
            setExtraOptions('--nosound')
        if line.find('-R ')!=-1 or line.find('--rewrite')!=-1:
            setExtraOptions('--rewrite')
        if line.find('-Z ')!=-1 or line.find('--dither')!=-1:
            setExtraOptions('--dither')

        # Deal with real time audio
        if line.find('-+rtaudio=') != -1:
            startIdx = (line.find('-+rtaudio=')+len('-+rtaudio='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setAudioPort(line[startIdx: line.find(endChar,startIdx)])
        if line.find('-+jack_client=') != -1:
            startIdx = (line.find('-+jack_client=')+len('-+jack_client='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setJackParams(client = line[startIdx: line.find(endChar,startIdx)])
        if line.find('-+jack_inportname=') != -1:
            startIdx = (line.find('-+jack_inportname=')+len('-+jack_inportname='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setJackParams(inPortName = line[startIdx: line.find(endChar,startIdx)])
        if line.find('-+jack_outportname=') != -1:
            startIdx = (line.find('-+jack_outportname=')+len('-+jack_outportname='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setJackParams(outPortName = line[startIdx: line.find(endChar,startIdx)])

        # Deal with the midi file flags
        if line.find('--midifile=') != -1:
            startIdx = (line.find('--midifile=')+len('--midifile='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiFileIn(line[startIdx: line.find(endChar,startIdx)])
        if line.find('-F ') != -1:
            startIdx = (line.find('-F ')+len('-F '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiFileIn(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--midioutfile=') != -1:
            startIdx = (line.find('--midioutfile=')+len('--midioutfile='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiFileOut(line[startIdx: line.find(endChar,startIdx)])
        if line.find('-+mute_tracks=') != -1:
            startIdx = line.find('-+mute_tracks=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-+raw_controller_mode=') != -1:
            startIdx = line.find('-+raw_controller_mode=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-+skip_seconds=') != -1:
            startIdx = line.find('-+skip_seconds=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-T ')!=-1 or line.find('--terminate-on-midi')!=-1:
            setExtraOptions('--terminate-on-midi')
            
        # Deal with real time MIDI
        if line.find('-M ') != -1:
            startIdx = (line.find('-M ')+len('-M '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiDeviceIn(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--midi-device=') != -1:
            startIdx = (line.find('--midi-device=')+len('--midi-device='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiDeviceIn(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--midi-key=') != -1:
            startIdx = line.find('--midi-key=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--midi-key-cps=') != -1:
            startIdx = line.find('--midi-key-cps=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--midi-key-oct=') != -1:
            startIdx = line.find('--midi-key-oct=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--midi-key-pch=') != -1:
            startIdx = line.find('--midi-key-pch=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--midi-velocity=') != -1:
            startIdx = line.find('--midi-key-pch=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--midi-velocity-amp=') != -1:
            startIdx = line.find('--midi-velocity-amp=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-+rtmidi=') != -1:
            startIdx = (line.find('-+rtmidi=')+len('-+rtmidi='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiPort(line[startIdx: line.find(endChar,startIdx)])
        if line.find('-Q ') != -1:
            startIdx = (line.find('-Q ')+len('-Q '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setMidiDeviceOut(line[startIdx: line.find(endChar,startIdx)])
        
        # Deal with Performance Configuration and Control
        if line.find('-B ') != -1:
            startIdx = (line.find('-B ')+len('-B '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setHardBuf(int(line[startIdx: line.find(endChar,startIdx)]))
        if line.find('--hardwarebufsamps=') != -1:
            startIdx = (line.find('--hardwarebufsamps=')+len('--hardwarebufsamps='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setHardBuf(int(line[startIdx: line.find(endChar,startIdx)]))
        if line.find('-b ') != -1:
            startIdx = (line.find('-b ')+len('-b '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setSoftBuf(int(line[startIdx: line.find(endChar,startIdx)]))
        if line.find('--iobufsamps=') != -1:
            startIdx = (line.find('--iobufsamps=')+len('--iobufsamps='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setSoftBuf(int(line[startIdx: line.find(endChar,startIdx)]))
        if line.find('-k ') != -1:
            startIdx = (line.find('-k ')+len('-k '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setKr(int(line[startIdx: line.find(endChar,startIdx)]))
        if line.find('--control-rate=') != -1:
            startIdx = (line.find('--control-rate=')+len('--control-rate='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setKr(int(line[startIdx: line.find(endChar,startIdx)]))
        if line.find('-L ') != -1:
            startIdx = (line.find('-L ')+len('-L '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setScoreIn(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--score-in=') != -1:
            startIdx = (line.find('--score-in=')+len('--score-in='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setScoreIn(line[startIdx: line.find(endChar,startIdx)])
        if line.find('--omacro:') != -1:
            startIdx = line.find('--omacro:')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-r ') != -1:
            startIdx = (line.find('-r ')+len('-r '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setSr(int(line[startIdx: line.find(endChar,startIdx)].strip()))
        if line.find('--sample-rate=') != -1:
            startIdx = (line.find('--sample-rate=')+len('--sample-rate='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            setSr(int(line[startIdx: line.find(endChar,startIdx)].strip()))
        if line.find('--smacro:') != -1:
            startIdx = line.find('--smacro:')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--strset') != -1:
            startIdx = line.find('--strset')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-+skip_seconds=') != -1:
            startIdx = line.find('-+skip_seconds=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-t ') != -1:
            startIdx = (line.find('-t ')+len('-t '))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            insertTempo(0, (0, int(line[startIdx: line.find(endChar,startIdx)])))
        if line.find('--tempo=') != -1:
            startIdx = (line.find('--tempo=')+len('--tempo='))
            endChar = ' -'
            if line.find(endChar,startIdx) == -1:
                endChar = '\n'
            insertTempo(0, (0, int(line[startIdx: line.find(endChar,startIdx)])))
            
        # Deal with miscellaneous flags
        if line.find('-@ ') != -1:
            startIdx = line.find('-@ ')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-C ')!=-1 or line.find('--cscore')!=-1:
            setExtraOptions('--cscore')
        if line.find('--default-paths')!=-1:
            setExtraOptions('--default-paths')
        if line.find('-D ')!=-1 or line.find('--defer-gen1')!=-1:
            setExtraOptions('--defer-gen1')
        if line.find('--env:') != -1:
            startIdx = line.find('-@')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--expression-opt')!=-1:
            setExtraOptions('--expression-opt')
        if line.find('-I ')!=-1 or line.find('--i-only')!=-1:
            setExtraOptions('--i-only')
        if line.find('-+ignore_csopts=') != -1:
            startIdx = line.find('-+ignore_csopts=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-+max_str_len=') != -1:
            startIdx = line.find('-+max_str_len=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-N ')!=-1 or line.find('--notify')!=-1:
            setExtraOptions('--notify')
        if line.find('--no-default-paths')!=-1:
            setExtraOptions('--no-default-paths')
        if line.find('--no-expression-opt')!=-1:
            setExtraOptions('--no-expression-opt')
        if line.find('-O ') != -1:
            startIdx = line.find('-O ')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--logfile=') != -1:
            startIdx = line.find('--logfile=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--syntax-check-only')!=-1:
            setExtraOptions('--syntax-check-only')
        if line.find('-t0 ')!=-1 or line.find('--keep-sorted-score')!=-1:
            setExtraOptions('--keep-sorted-score')
        if line.find('-U ') != -1:
            startIdx = line.find('-U ')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--utility=') != -1:
            startIdx = line.find('--utility=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('-x ') != -1:
            startIdx = line.find('-x ')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        if line.find('--extract-score=') != -1:
            startIdx = line.find('--extract-score=')
            endIdx = line.find(' -', start)
            if endIdx == -1:
                endIdx = line.find('\n', start)-1
            setExtraOptions((line[startIdx:endIdx]))
        
        setIsModified(True)

    parent.interface.editor.EmptyUndoBuffer()
    for format in getSupportedFormats():
        parent.orchestraPanels[format].editor.EmptyUndoBuffer()
    for scoreType in SCORE_TYPES:
        parent.scorePanels[scoreType].editor.EmptyUndoBuffer()
        
def parseUserOrchestra(orchText, forCecilia=True, scoreText=''):   
    # look for setting p3 from the orchestra
    tmp_orch_lines = orchText.splitlines()
    tmp_sco_lines = scoreText.splitlines()
    which = None
    if getInterface():
        masterDuration = getTotalTime()
    else:
        masterDuration = 0.0    
    for line in tmp_orch_lines:
        line = line.replace(' ', '')
        if line.startswith('instr'):
            if ',' in line:
                which = int(line.replace('instr', '').split(',')[0])
            else:
                which = int(line.replace('instr', ''))
        if 'p3=' in line and which != None:
            for scoline in tmp_sco_lines:
                li = scoline.split()
                if len(li) >= 4:
                    if li[0] == 'i' and li[1] == str(which):
                        notedur = float(li[3])
                        line = line.replace('p3=', '')
                        if 'p3' in line:
                            line = line.replace('p3', str(notedur))
                            if 'i(gk' in line:
                                line = line.replace('i(gk', '').replace(')', '', 1)
                                for slider in getUserSliders():
                                    if slider.getName() in line:
                                        line = line.replace(slider.getName(), str(slider.getValue()))
                            if 'i(k' in line:
                                line = line.replace('i(', '').replace(')', '', 1)
                                for slider in getUserSliders():
                                    if slider.getName() in line:
                                        line = line.replace(slider.getName(), str(slider.getValue()))
                            elif 'gi' in line:
                                line = line.replace('gi', '', 1)
                                for slider in getUserSliders():
                                    if slider.getName() in line:
                                        line = line.replace(slider.getName(), str(slider.getValue()))
                            newdur = eval(line)
                        else:
                            newdur = eval(line.strip())  
                        if newdur > masterDuration:
                            masterDuration = newdur

             
    if orchText.find('opcode') != -1:
        index = orchText.find('opcode')
    else:
        index = orchText.find('instr')
    orchText = orchText[index: -1]

    numSamplers = orchText.count(' sampler ')
    pos = 0
    samplers_used = []
    
    for i in range(numSamplers):
        newpos = orchText.find(' sampler ', pos)
        subpos = newpos
        chnls = 1
        while subpos != 0:
            try:
                unicodedata.name(orchText[subpos])
                if orchText[subpos] == ',': chnls += 1
                subpos += -1
            except:
                break
        subpos = newpos
        while orchText[subpos] != ']':
            if orchText[subpos] == '[': openBracePos = subpos
            subpos += 1
        closeBracePos = subpos
        gainAndTrans = []
        while orchText[subpos] != '\n':
            if orchText[subpos] == ',':
                subpos += 1
                string = ''
                while orchText[subpos] not in [',', '\r', '\n']:
                    if orchText[subpos] != ' ': string += orchText[subpos]
                    subpos += 1
                else:
                    gainAndTrans.append(string)
            else:
                subpos += 1   
        
        samplerName = orchText[openBracePos+1:closeBracePos]
        if samplerName not in samplers_used:
            samplers_used.append(samplerName)
        else:
            showErrorDialog('Multiple references to a csampler object!',
                            'Csampler "%s" is refered more than once in the orchestra. \
                            Put it in a global variable to be able to use it many times.' % samplerName) 
            stopCeciliaSound()
            return '', '', ''
                               
        getUserSamplers()[i].setOutputChnls(chnls)
        getUserSamplers()[i].setGainAndTrans(gainAndTrans)   
        orchText = orchText.replace('sampler', 'Sampler_'+samplerName, 1)
        pos = newpos
    
    ##### Square brackets [key] replacement #####
    posOpenBracket = orchText.find('[')
    while posOpenBracket != -1:
        posCloseBracket = orchText.find(']', posOpenBracket)
        key = orchText[posOpenBracket+1:posCloseBracket]

        if key in getUserInputs().keys():
            path = convertWindowsPath(getUserInputs()[key]['path'])
            new = '"' + path + '"'
            orchText = orchText[:posOpenBracket] + new.decode('utf-8') + orchText[posCloseBracket+1:]
        else:
            for k in getUserInputs().keys():
                if 'off%s' % k == key or 'nchnls%s' % k == key or 'gensize%s' % k == key or 'sr%s' % k == key or 'dur%s' % k == key:
                    new = '%s' % getUserInputs()[k][key]
                    break
            orchText = orchText[:posOpenBracket] + new + orchText[posCloseBracket+1:]
        posOpenBracket = orchText.find('[')
    
    ##### Replace various out opcodes by UDO #####
    udoToCreate = []
    header = ''
        
    for outType in LINKER.keys():
        outFound = orchText.find(' '+outType+' ')
        if outFound==-1:
            outFound = orchText.find('\n'+outType+' ')
        while outFound != -1:
            if outType == 'outc':
                new_udo = "opcode globalOut%d, 0, " % getNchnls() + "a"*getNchnls() + "\n"
                new_udo += ", ".join(["a%d" % i for i in range(getNchnls())]) + " xin\n"
                for i in range(getNchnls()):
                    new_udo += "gaGlobalOut%d = gaGlobalOut%d + a%d\n" % (i, i, i)
                new_udo += "endop\n\n"
                orchText = orchText[:outFound] + '\n' + 'globalOut%d' % getNchnls() + orchText[outFound+len(outType)+1:]     
            else:    
                orchText = orchText[:outFound] + '\n' + LINKER[outType] + orchText[outFound+len(outType)+1:]
            
            outFound = orchText.find(' '+outType+' ')
            if outFound==-1:
                outFound = orchText.find('\n'+outType+' ')
            
            if outType == 'outc':
                if 'globalOut%d' % getNchnls() not in udoToCreate:
                    udoToCreate.append('globalOut%d' % getNchnls())
            else:    
                if LINKER[outType] not in udoToCreate:
                    udoToCreate.append(LINKER[outType])

    for i in range(getNchnls()):
        header += 'gaGlobalOut%d init 0\n' % i
    header += '\n'
    
    for udo in udoToCreate:
        if UDO.has_key(udo):
            header += UDO[udo]
        else:
            header += new_udo
            
    # UDOs bank
    udoslist = [udo for udo in os.listdir(UDO_PATH) if not udo.startswith('.')]
    for udo in udoslist:
        if orchText.find(' ' + udo + ' ') != -1:
            f = open(os.path.join(UDO_PATH, udo), 'r')
            header += f.read()
            header += '\n\n'
            f.close()

    loadTables = ''
    for sampler in getUserSamplers():
        udoText, loadTableText = sampler.getText()
        header += udoText
        loadTables += loadTableText
     
    if masterDuration == 0.0:
        masterDuration = None    
    return header, orchText, loadTables, masterDuration

def removeExtraSpace(text):
    li = text.split(' ')
    text = ''
    for ele in li:
        if ele != '':
            text += ele + ' '
    return text
        
def parseUserScore(scoText, forCecilia=True):
    scoText = removeExtraSpace(scoText)

    ##### Square brackets [key] replacement #####
    posOpenBracket = scoText.find('[')
    
    while posOpenBracket != -1:
        posCloseBracket = scoText.find(']', posOpenBracket)
        key = scoText[posOpenBracket+1:posCloseBracket]
        if key == 'total_time':
            new = str(getTotalTime())
            scoText = scoText[:posOpenBracket] + new + scoText[posCloseBracket+1:]
        elif key in getUserInputs().keys():
            path = convertWindowsPath(getUserInputs()[key]['path'])
            new = '"' + path + '"'
            scoText = scoText[:posOpenBracket] + new + scoText[posCloseBracket+1:]
        elif key in [slider.getName() for slider in getUserSliders()]:
            for slider in getUserSliders():
                if key == slider.getName():
                    new = '%s' % slider.getValue()
                    break
            scoText = scoText[:posOpenBracket] + new + scoText[posCloseBracket+1:]
        elif key in [obj.getName() for obj in getUserTogglePopups()]:
            for obj in getUserTogglePopups():
                if key == obj.getName():
                    new = '%s' % obj.getValue()
                    break
            scoText = scoText[:posOpenBracket] + new + scoText[posCloseBracket+1:]
        else:
            for k in getUserInputs().keys():
                if 'off%s' % k == key or 'nchnls%s' % k == key or 'gensize%s' % k == key or 'sr%s' % k == key or 'dur%s' % k == key:
                    new = '%s' % getUserInputs()[k][key]
                    break
            scoText = scoText[:posOpenBracket] + new + scoText[posCloseBracket+1:]

        posOpenBracket = scoText.find('[')
   
    temp = scoText.split('\n')
    for line in temp:
        if line.strip() == 'e': temp.remove(line)
    scoText = '\n'.join(temp)
     
    return scoText

def createGlobalVariables(): 
    header = ''
    if  getInterface():
        header += 'gicomb0 ftgen 0,0,64,-2,-1009,-1103,-1123,-1281,-1289,-1307,-1361,-1409,-1429,-1543,-1583,-1601,-1613,-1709,-1801,-1949,-2003,-2111,-2203,-2341,-2411,-2591,-2609,-2749,-2801,-2903,-3001,-3109,-3203,-3301,-3407,-3539,0.82,0.81,0.8,0.79,0.78,0.77,0.76,0.75,0.74,0.73,0.72,0.71,0.7,0.69,0.68,0.67,0.66,0.65,0.64,0.63,0.62,0.61,0.6,0.59,0.58,0.57,0.56,0.55,0.54,0.53,0.52,0.51\n'
        header += 'gicomb1 ftgen 0,0,64,-2,-1013,-1033,-1151,-1193,-1213,-1237,-1327,-1337,-1423,-1487,-1523,-1553,-1687,-1721,-1841,-1907,-2053,-2161,-2239,-2311,-2473,-2521,-2687,-2711,-2803,-2927,-3011,-3119,-3209,-3307,-3413,-3517,0.82,0.81,0.8,0.79,0.78,0.77,0.76,0.75,0.74,0.73,0.72,0.71,0.7,0.69,0.68,0.67,0.66,0.65,0.64,0.63,0.62,0.61,0.6,0.59,0.58,0.57,0.56,0.55,0.54,0.53,0.52,0.51\n'
        header += 'gicomb2 ftgen 0,0,64,-2,-953,-1049,-1093,-1129,-1163,-1249,-1277,-1367,-1381,-1451,-1483,-1567,-1637,-1759,-1871,-1973,-2063,-2153,-2251,-2357,-2467,-2557,-2663,-2749,-2857,-2963,-3061,-3181,-3257,-3343,-3467,-3547,0.82,0.81,0.8,0.79,0.78,0.77,0.76,0.75,0.74,0.73,0.72,0.71,0.7,0.69,0.68,0.67,0.66,0.65,0.64,0.63,0.62,0.61,0.6,0.59,0.58,0.57,0.56,0.55,0.54,0.53,0.52,0.51\n'
        header += 'gicomb3 ftgen 0,0,64,-2,-1061,-1181,-1259,-1321,-1373,-1453,-1459,-1571,-1579,-1657,-1663,-1777,-1783,-1873,-1877,-1987,-2081,-2179,-2269,-2377,-2477,-2591,-2677,-2767,-2879,-2971,-3079,-3191,-3271,-3359,-3491,-3559,0.82,0.81,0.8,0.79,0.78,0.77,0.76,0.75,0.74,0.73,0.72,0.71,0.7,0.69,0.68,0.67,0.66,0.65,0.64,0.63,0.62,0.61,0.6,0.59,0.58,0.57,0.56,0.55,0.54,0.53,0.52,0.51\n'
        header += 'giallp0 ftgen 0,0,16,-2,-179,-223,-233,-311,-347,-409,-433,-509,0.76,0.74,0.72,0.7,0.68,0.64,0.62,0.6\n'
        header += 'giallp1 ftgen 0,0,16,-2,-199,-241,-313,-379,-419,-439,-521,-557,0.76,0.74,0.72,0.7,0.68,0.64,0.62,0.6\n'
        header += 'giallp2 ftgen 0,0,16,-2,-173,-257,-269,-353,-379,-457,-569,-509,0.76,0.74,0.72,0.7,0.68,0.64,0.62,0.6\n'
        header += 'giallp3 ftgen 0,0,16,-2,-191,-281,-337,-373,-431,-479,-587,-557,0.76,0.74,0.72,0.7,0.68,0.64,0.62,0.6\n'

    if getSamplerSliders():
        for slider in getSamplerSliders():
            header += 'gk%s init %f\n' % (slider.getCName(), slider.getValue())
    if getUserSliders():
        for slider in getUserSliders():
            if slider.getRate() == 'k':
                if type(slider.getValue()) in [ListType, TupleType]:
                    header += 'gk%smin init %f\n' % (slider.getName(), slider.getValue()[0])
                    header += 'gk%smax init %f\n' % (slider.getName(), slider.getValue()[1])                    
                else:    
                    header += 'gk%s init %f\n' % (slider.getName(), slider.getValue())
            else:
                if type(slider.getValue()) in [ListType, TupleType]:
                    header += 'gi%smin init %f\n' % (slider.getName(), slider.getValue()[0])
                    header += 'gi%smax init %f\n' % (slider.getName(), slider.getValue()[1])                    
                else:    
                    header += 'gi%s init %f\n' % (slider.getName(), slider.getValue())
    if getSamplerTogglePopup():
        for obj in getSamplerTogglePopup():
            header += 'gi%s init %s\n' % (obj.getName(), obj.getValue())
    if getUserTogglePopups():
        for obj in getUserTogglePopups():
            if obj.getRate() == 'table':
                header += obj.getCeciliaText()
            elif obj.getRate() == 'k':
                header += 'gk%s init %s\n' % (obj.getName(), obj.getValue())
            else:
                header += 'gi%s init %s\n' % (obj.getName(), obj.getValue())
    header += '\n'
    return header

def checkForFileInPath(text):
    for key in getUserInputs().keys():
        if text.find('['+key+']') != -1:
            if not os.path.isfile(getUserInputs()[key]['path']):
                getUserInputs()[key]['path'] = ''
            if getUserInputs()[key]['path'] == '':
                return False
    return True
   
def filterOutComments(text):
    filteredText = ''
    lines = [line.rstrip('\r') for line in text.split('\n')]
    for line in lines:
        length = len(line)
        pos = 0
        for i in range(length):
            if line[pos] == ';':
                break
            pos += 1
        filteredText += line[:pos]
        filteredText += '\n'
        
    return filteredText
       
def generateCSD(forCecilia=True, flagsLine=''):

    userOrchText = ceciliaEditor.orchestraPanels[ceciliaEditor.activeOrchestra].editor.GetText()
    userOrchText = filterOutComments(userOrchText)
    userScoText = ceciliaEditor.scorePanels[ceciliaEditor.activeScore].editor.GetCsoundText()
    userScoText = filterOutComments(userScoText)
    # Check if soundfile is loaded
    if not checkForFileInPath(userOrchText) or not checkForFileInPath(userScoText):
        showErrorDialog('No input sound file!', 'Please load one...')
        for key in getUserInputs().keys():
            if not os.path.isfile(getUserInputs()[key]['path']):
                getControlPanel().getCfileinFromName(key).onLoadFile()
        stopCeciliaSound()
        return None

    headerText = ''
    orchText = ''
    scoreText = ''

    headerText += addHeaderToOrchestra(userOrchText)

    headerText += createGlobalVariables()

    scoreText += getTempoLine()

    if forCecilia:
        samplerSlidersDone = []
        if getGrapher():
            for line in getGrapher().plotter.getData():
                orc, sco = createGrapherInst(line)
                orchText += orc
                scoreText += sco
        for slider in getSamplerSliders():
            samplerSlidersDone.append(slider)
            orc, sco = slider.getCeciliaText()
            orchText += orc
            scoreText += sco
        for slider in getUserSliders():
            if slider not in samplerSlidersDone:
                orc, sco = slider.getCeciliaText()
                orchText += orc
                scoreText += sco
        for obj in getUserTogglePopups():
            if obj.getRate() != 'table':
                orc, sco = obj.getCeciliaText()
                orchText += orc
                scoreText += sco
        plugins = getPlugins()
        used_udos = []
        plugin_udo_head = ''
        for plug in plugins:
            if plug != None:
                orc, sco = plug.getParamsText()
                head, udo = plug.getUdoText()
                if udo not in used_udos:
                    plugin_udo_head += head
                    used_udos.append(udo)
                orchText += orc
                scoreText += sco

    scoreText += parseUserScore(userScoText, forCecilia)
    head, orc, loadTables, masterDuration = parseUserOrchestra(userOrchText, forCecilia, scoreText)
    if head == '' and orc == '' and loadTables == '':
        return None
    headerText += loadTables.decode('utf-8')
    headerText += head
    headerText += plugin_udo_head
    orchText += orc

    if forCecilia:
        orc = createCeciliaInstr()
        orchText += orc
        scoreText += createCeciliaScore(scoreText, masterDuration)

    # Build the CSD
    csdText = '<CsoundSynthesizer>\n'
     
    # Csound flags
    csdText += '<CsOptions>\n'
    csdText += flagsLine
    csdText += '\n</CsOptions>\n'
    
    # Csound Orchestra
    csdText += '<CsInstruments>\n'
    csdText += headerText
    csdText += orchText
    csdText += '\n</CsInstruments>\n'
    
    # Csound Score
    csdText += '<CsScore>\n'
    csdText += scoreText
    csdText += '\n</CsScore>\n'
    
    csdText += '</CsoundSynthesizer>'
    
    return csdText

def interpolate(lines, size, listlen):
    scale = size / lines[-1][0]
    templist = []
    for i in range(listlen-1):
        t = lines[i+1][0] - lines[i][0]
        num = int(round(t * scale))
        if num == 0:
            pass
        else:
            step = (lines[i+1][1] - lines[i][1]) / num
            for j in range(num):
                templist.append(lines[i][1] + (step*j))
    return templist               

def removeDuplicates(seq): 
   result = []
   for item in seq:
       if item in result: continue
       result.append(item)
   return result

def interpolateCurved(lines, size, listlen):
    lines = removeDuplicates(lines)
    scale = size / float(len(lines))
    depth = int(round(scale))
    off = int(1. / (scale - depth))
    templist = []
    for i in range(len(lines)-1):
        num = depth
        if (i%off) == 0: num = depth + 1
        step = (lines[i+1][1] - lines[i][1]) / num
        for j in range(num):
            templist.append(lines[i][1] + (step*j))
    return templist

def interpolateLog(lines, size, listlen, yrange):
    scale = size / lines[-1][0]
    templist = []
    for i in range(listlen-1):
        t = lines[i+1][0] - lines[i][0]
        num = int(round(t * scale))
        if num == 0:
            pass
        else:
            step = (lines[i+1][1] - lines[i][1]) / num
            for j in range(num):
                templist.append(lines[i][1] + (step*j))
    list = []
    if yrange[0] == 0: yoffrange = .00001
    else: yoffrange = yrange[0] 
    totalRange = yrange[1] - yoffrange
    currentTotalRange = math.log10(yrange[1]/yrange[0])
    currentMin = math.log10(yrange[0])
    for p in templist:
        if p == 0: p = .00001
        ratio = (p - yoffrange) / totalRange
        list.append(math.pow(10, ratio * currentTotalRange + currentMin))
    return list

def convertWindowsPath(path):
    if getPlatform() == 'win32':
        return path.replace('\\', '/')
    else:
        return path

def createGrapherInst(line):
    data = line.getData()
    name = line.getName()
    log = line.getLog()
    yrange = line.getYrange()
    curved = line.getCurved()
    csoundPoints = line.getCsoundPoints()
    lines = line.getLines()
    types = line.getTypes()
    suffix = line.getSuffix()
    gen = line.getGen()
    size = line.getSize()
    orchtext = ''
    scotext = ''
    if gen != None and not curved:
        if len(data) > 50:
            filename = os.path.join(TMP_PATH, "table_%s%s" % (name,suffix))
            f = open(filename, "w")
            f.write(' '.join([str(p) for p in interpolate(data, size, len(data))]))
            f.close()
            filename = convertWindowsPath(filename)
            scotext = 'f%d 0 %d -23 "%s"\n' % (gen, size, filename)
        else:
            templist = []
            for p in data:
                templist.append(int(p[0] / data[-1][0] * size))
                templist.append(p[1])
            if log:
                scotext = 'f%d 0 %d -25 ' % (gen, size) + ' '.join(str(x) for x in templist) + '\n'
            else:
                scotext = 'f%d 0 %d -27 ' % (gen, size) + ' '.join(str(x) for x in templist) + '\n'

    elif gen != None and curved:
        filename = os.path.join(TMP_PATH, "table_%s%s" % (name,suffix))
        f = open(filename, "w")
        f.write(' '.join([str(p) for p in interpolateCurved(lines, size, len(lines))]))
        f.close()
        filename = convertWindowsPath(filename)
        scotext = 'f%d 0 %d -23 "%s"\n' % (gen, size, filename)

    elif curved:
        tableNum = getSliderTableNum()
        filename = os.path.join(TMP_PATH, "table_%s%s" % (name,suffix))
        f = open(filename, "w")
        f.write(' '.join([str(p) for p in interpolateCurved(lines, 8192, len(lines))]))
        f.close()
        filename = convertWindowsPath(filename)
        scotext = 'f%d 0 %d -23 "%s"\n' % (tableNum, 8192, filename)

        orchtext = 'instr Cecilia_%s\n' % name
        orchtext += 'kphase phasor 1/p3\n'            
        orchtext += 'gk%s ' % name + 'tablei kphase, %d, 1\n' % tableNum
        orchtext += 'endin\n\n'
        scotext += 'i "Cecilia_%s" 0 %f\n' % (name, getGrapher().plotter.getTotalTime())
        setSliderTableNum(tableNum+1)

    elif not log:
        if len(data) > 50:
            tableNum = getSliderTableNum()
            filename = os.path.join(TMP_PATH, "table_%s%s" % (name,suffix))
            f = open(filename, "w")
            f.write(' '.join([str(p) for p in interpolate(data, 8192, len(data))]))
            f.close()
            filename = convertWindowsPath(filename)
            scotext = 'f%d 0 %d -23 "%s"\n' % (tableNum, 8192, filename)
    
            orchtext = 'instr Cecilia_%s\n' % name
            orchtext += 'kphase phasor 1/p3\n'            
            orchtext += 'gk%s ' % name + 'tablei kphase, %d, 1\n' % tableNum
            orchtext += 'endin\n\n'
            scotext += 'i "Cecilia_%s" 0 %f\n' % (name, getGrapher().plotter.getTotalTime())
            setSliderTableNum(tableNum+1)
        else:
            args = [data[0][1]]
            for i in range(len(data)-1):
                args.append(data[i+1][0] - data[i][0])
                args.append(data[i+1][1])
            if args[1] == 0: args[1] = 0.00001
            orchtext = 'instr Cecilia_%s\n' % name
            orchtext += 'gk%s ' % name + 'linseg ' + ', '.join([str(x) for x in args]) + '\n'
            orchtext += 'endin\n\n'
            scotext = 'i "Cecilia_%s" 0 %f\n' % (name, getGrapher().plotter.getTotalTime())

    else:
        tableNum = getSliderTableNum()
        filename = os.path.join(TMP_PATH, "table_%s%s" % (name,suffix))
        f = open(filename, "w")
        f.write(' '.join([str(p) for p in interpolateLog(data, 8192, len(data), yrange)]))
        f.close()
        filename = convertWindowsPath(filename)
        scotext = 'f%d 0 %d -23 "%s"\n' % (tableNum, 8192, filename)

        orchtext = 'instr Cecilia_%s\n' % name
        orchtext += 'kphase phasor 1/p3\n'            
        orchtext += 'gk%s ' % name + 'tablei kphase, %d, 1\n' % tableNum
        orchtext += 'endin\n\n'
        scotext += 'i "Cecilia_%s" 0 %f\n' % (name, getGrapher().plotter.getTotalTime())
        setSliderTableNum(tableNum+1)

    return orchtext, scotext

def createCeciliaInstr(): 
    ceciliaInstr = '\n'
    
    ##### Cecilia Monitor Instrument ######
    ceciliaInstr += '\ninstr +CeciliaMonitor\n'
        
    ceciliaInstr += 'ktime times\n\n'
    #ceciliaInstr += 'printk .25, ktime\n\n'
    
    if  getInterface():
        for i in range(getNchnls()):
            ceciliaInstr += 'kRMS%d init 0\n' % i

    globalOuts =['gaGlobalOut%d' % i for i in range(getNchnls())]
    outs =['aOut%d' % i for i in range(getNchnls())]

    if getGainSlider():
        masterVolumeInit = getGainSlider().GetValue()
        ceciliaInstr += 'kmasterVolume init %f\n' % masterVolumeInit
        ceciliaInstr += 'kmasterVolume chnget "masterVolume"\n'
        ceciliaInstr += 'kVolume = ampdb(90 + kmasterVolume) / 32768.\n'

        plugins = getPlugins()
        for plug in plugins:
            if plug != None:
                ceciliaInstr += plug.getText()
                
        for i in range(getNchnls()):
            ceciliaInstr += '%s = %s * kVolume\n' % (outs[i], globalOuts[i])
    else:
        for i in range(getNchnls()):
            ceciliaInstr += '%s = %s\n' % (outs[i], globalOuts[i])

    ceciliaInstr += 'outc ' + ', '.join(outs) + '\n\n'

    if  getInterface():
        for i in range(getNchnls()):
            ceciliaInstr += 'krms%d downsamp aOut%d\n' % (i, i)
            ceciliaInstr += 'if krms%d > kRMS%d then\n' % (i, i)
            ceciliaInstr += 'kRMS%d = krms%d\nendif\n' % (i, i)
        
        ceciliaInstr += 'ktrig metro 20\n'    
        ceciliaInstr += 'if ktrig == 1 then\n'
        for i in range(getNchnls()):    
            ceciliaInstr += 'chnset dbamp(kRMS%d), "rms%i"\n' % (i, i)
            ceciliaInstr += 'kRMS%d = 0\n' % i
        ceciliaInstr += 'endif\n'    

    ceciliaInstr += 'chnset ktime, "time"\n'

    for x in globalOuts:
        ceciliaInstr += '%s = 0\n' % x

    ceciliaInstr += 'chnset 1, "ready"\n'
    ceciliaInstr += 'endin\n\n'
    
    ceciliaInstr += '\ninstr +CeciliaStop\n'
    ceciliaInstr += 'chnset 1, "stop"\n'
    ceciliaInstr += 'turnoff\n'
    ceciliaInstr += 'endin\n'     
         
    return ceciliaInstr

def createCeciliaScore(scoreText, masterDuration=None):
    ceciliaScore = ''
    ceciliaScore += '\ni "CeciliaMonitor" 0 -1\n'
    if getInterface():
        if masterDuration == None:
            masterDuration = getTotalTime()
        ceciliaScore += 'i "CeciliaStop" %f .05\n' % masterDuration
    else:
        lines = scoreText.split('\n') 
        lines = [line for line in lines if line.strip() != ""]
        # remove possible spaces in "p1"
        for line in lines:
            if len(line.split()[0]) == 1:
                sp = line.split()
                newline = sp[0] + sp[1] + " " + " ".join(p for p in sp[2:])
                lines[lines.index(line)] = newline
                
        # handle possible shortcuts in score lines
        starts = {}
        durs = {}
        ends = []
        for i in range(len(lines)):
            l = lines[i]
            if l.strip().startswith('i'):
                instr = l.split()[0][1:]
                if not starts.has_key(instr):
                    starts[instr] = []
                    durs[instr] = []
                start = l.split()[1]
                dur = l.split()[2]
                if start == '+':
                    start = starts[instr][-1] + durs[instr][-1]
                elif start == '.':
                    start = starts[instr][-1]
                if dur == '.':
                    dur = durs[instr][-1]    

                starts[instr].append(float(start))
                durs[instr].append(float(dur)) 
                ends.append(float(start) + float(dur))
        dur = max(ends) 
        if masterDuration != None:
            dur = max([dur, masterDuration])  
        ceciliaScore += 'i "CeciliaStop" %f .05\n' % dur
    return ceciliaScore

def start(flagsLine):
    csdText = generateCSD(flagsLine=flagsLine)
    if not csdText: return

    csdPath = os.path.join(TMP_PATH, 'temp.csd')

    try:
        if getPlatform() == 'win32':
            #file = codecs.open(csdPath, 'wt', 'cp1252')
            file = open(csdPath, 'wt')
        else:    
            file = codecs.open(csdPath, 'wt', 'utf-8')
    except:
        print "Cecilia can't write files in the tmp directory, please check authorizations"
        return

    file.write(csdText)
    file.close()

    csound.startCsound(csdPath)

def cancel():
    stopCeciliaSound()

def startCeciliaSound():
    if getInterface():
        getControlPanel().resetMeter()
    flagsLine = getCsoundFlags()
    if getShowPreview():
        from Widgets import CmdLinePreviewPopupFrame 
        dlg = CmdLinePreviewPopupFrame(wx.GetTopLevelWindows()[0], flagsLine, start, cancel)
    else:
        start(flagsLine)
                
def stopCeciliaSound():
    csound.stopCsound()

    time.sleep(.25)
    setSamplerTableNum(3000)
    setSamplerSliderTableNum(6000)
    #setSliderTableNum(10000)
    getCeciliaEditor().transportButtons.setPlay(False)
    getCeciliaEditor().transportButtons.setRecord(False)
    if getInterface():
        getControlPanel().transportButtons.setPlay(False)
        getControlPanel().transportButtons.setRecord(False)
        if getGrapher():
            getGrapher().checkForAutomation()
        wx.CallAfter(getControlPanel().vuMeter.reset)
    
def csoundIsRunning(state):
    if state == 1:
        if getInterface():
            getControlPanel().transportButtons.setPlay(True)
        getCeciliaEditor().transportButtons.setPlay(True)

def setCeciliaEditor(editor):
    global ceciliaEditor
    ceciliaEditor = editor
    
def getCeciliaEditor():
    return ceciliaEditor

def setCsound(csnd):
    global csound
    csound = csnd
    vars.CeciliaVar['csound'] = csnd
    
def getCsound():
    return vars.CeciliaVar['csound']

def setPreferencePanel(prefs):
    global preferencePanel
    preferencePanel = prefs

def getPreferencePanel():
    return preferencePanel

def queryAudioMidiDrivers():
    inputs, selectedInput, outputs, selectedOutput, midiInputs, selectedMidiInput = csound.getAvailableAudioMidiDrivers()

    setAvailableAudioOutputs(outputs)
    if getAudioOutput() != '':
        if getAudioOutput() < len(outputs):
            setAudioOutput(getAudioOutput())
        else:    
            setAudioOutput(outputs.index(selectedOutput))
    else:
        setAudioOutput(outputs.index(selectedOutput))
                
    setAvailableAudioInputs(inputs)
    if getAudioInput() != '':
        if getAudioInput() < len(inputs):
            setAudioInput(getAudioInput())
        else:    
            setAudioInput(inputs.index(selectedInput))
    else:    
        setAudioInput(inputs.index(selectedInput))

    if midiInputs == []:
        setUseMidi(0)
    else:
        setUseMidi(1)    
    setAvailableMidiInputs(midiInputs)
    if getMidiDeviceIn() != '':
        if getMidiDeviceIn() <= len(midiInputs):
            setMidiDeviceIn(getMidiDeviceIn())
        else:
            setMidiDeviceIn(midiInputs.index(selectedMidiInput))
    else:            
        setMidiDeviceIn(midiInputs.index(selectedMidiInput))

def dialogSelectCustomNchnls(parent, msg = 'Set the numbers of channels for your orchestra',
                           tag = 'nchnls = ', title = 'Custom channels', value=None,
                           min=1, max=128):
        
    if value == None:
        value = getNchnls()
            
    # Show the dialog
    dlg = wx.NumberEntryDialog(parent, msg, tag, title, value, min, max)
    if dlg.ShowModal() == wx.ID_OK:
        nchnls = dlg.GetValue()
        if not nchnls in getSupportedFormats().values():
            setCustomSupportedFormats(nchnls)
    else:
        nchnls = None
    dlg.Destroy()
    
    return nchnls

def loadPlayerEditor(app_type):
    if getPlatform() == 'win32':
        wildcard =  "Executable files (*.exe)|*.exe|"     \
                    "All files (*.*)|*.*"
    elif getPlatform() == 'darwin':
        wildcard =  "Application files (*.app)|*.app|"     \
                    "All files (*.*)|*.*"
    else:
        wildcard = "All files (*.*)|*.*"
    
    path = ''
    dlg = wx.FileDialog(None, message="Choose a soundfile %s..." % app_type,
                             defaultDir=os.path.expanduser('~'),
                             wildcard=wildcard,
                             style=wx.OPEN)

    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()   
    dlg.Destroy()

    if path:
        if app_type == 'player':
            setSoundfilePlayerPath(path)
        elif app_type == 'editor':
            setSoundfileEditorPath(path)

def listenSoundfile(filename):
    if getSoundfilePlayerPath() == '':
        showErrorDialog("Preferences not set", "Choose a soundfile player first.")
        loadPlayerEditor('player')
    if os.path.isfile(filename):
        name = ''
        if getPlatform() == 'darwin':
            name = getSoundfilePlayerPath()
            cmd = 'open -a ' + slashifyText(name) + ' ' + slashifyText(filename)
            Popen(cmd, shell=True)
        elif getPlatform() == 'win32':
            app = getSoundfilePlayerPath()
            cmd = '"' + os.path.join(app) + '" "' + slashifyText(filename) + '"'
            try:
                Popen(cmd, shell=True)
            except OSError, OSError2:
                print 'Unable to open desired software:\t' + app
        else:
            app = getSoundfilePlayerPath()
            cmd = slashifyText(app) + ' ' + slashifyText(filename)
            try:
                Popen(cmd, shell=True)
            except OSError, OSError2:
                print 'Unable to open desired software:\t' + app

def editSoundfile(filename):
    if getSoundfileEditorPath() == '':
        showErrorDialog("Preferences not set", "Choose a soundfile editor first.")
        loadPlayerEditor('editor')
    if os.path.isfile(filename):
        name = ''
        if getPlatform() == 'darwin':
            name = getSoundfileEditorPath()
            cmd = 'open -a ' + slashifyText(name) + ' ' + slashifyText(filename)
            Popen(cmd, shell=True)
        elif getPlatform() == 'win32':
            app = getSoundfileEditorPath()
            cmd = '"' + os.path.join(app) + '" "' + slashifyText(filename) + '"'
            try:
                Popen(cmd, shell=True)
            except OSError, OSError2:
                print 'Unable to open desired software:\t' + app
        else:
            app = getSoundfileEditorPath()
            cmd = slashifyText(app) + ' ' + slashifyText(filename)
            try:
                Popen(cmd, shell=True)
            except OSError, OSError2:
                print 'Unable to open desired software:\t' + app

def resetWidgetVariables():
    setGainSlider(None)
    setUserInputs({})
    setUserSliders([])
    setUserSamplers([])
    setUserTogglePopups([])
    setSamplerSliders([])
    setTableNum(13000)
    setSliderTableNum(10000)
    setSamplerTableNum(3000)
    setGrapher(None)
    setPresetPanel(None)
   
def parseInterfaceText(text, udolines=[]):
    # Parse each line separatly to create the interface widgets List
    setModuleDescription('')
    text = removeExtraSpace(text)
    widgetsList=[]
    tmplines = text.splitlines()
    if udolines != []:
        tmplines.extend(udolines)
    lines = []    
    skip = False
    multiline = ''
    for i in range(len(tmplines)):
        if not skip:
            if tmplines[i].rstrip().endswith('\\'):
                multiline = tmplines[i].replace('\\', '').replace('\n', '')
                skip = True
            else:
                lines.append(tmplines[i])
                skip = False
        else:
            if tmplines[i].rstrip().endswith('\\'):
                multiline += tmplines[i].replace('\\', '').replace('\n', '')
            else:
                multiline += tmplines[i].replace('\\', '')
                lines.append(multiline)
                skip = False         
            
    for line in lines:
        # Remove leading spaces
        line = line.lstrip(' ')
        line = line.replace('\t', ' ')

        line = ' '.join([x.strip() for x in line.split(' ')])
        
        #Make sure the first word is a keyword
        if line[0:line.find(' ')] in CECILIA_INTERFACE_KEYWORDS:
            widget = {}
            
            #Get the type and maybe the name of the widget first
            for i in range(2):
                endPos = line.find(' ')
                if endPos != -1:
                    if i == 0:
                        widget['type'] = line[0:endPos]
                        line = line[endPos+1:]
                    elif i == 1:
                        widget['name'] = line[0:endPos]
                        line = line[endPos:]
                else:
                    if i == 0:
                        widget['type'] = line[0:]
                        line = ''
                        break
                    elif i == 1:
                        widget['name'] = line[0:]
                        line = ''
                        break
                                    
            # Go over each flag and create an entry in the dictionary
            while line != '':
                commentPos = line.find(';')
                sepPos = line.find(' -')
                
                if sepPos == -1 or (commentPos!=-1 and commentPos < sepPos):
                    break
                
                else:
                    line = line[sepPos+2:]
                    spacePos = line.find(' ')
                    if spacePos != -1:
                        key = line[0:spacePos]
                        line = line[spacePos+1:]
                        commentPos = line.find(';')
                        nextSepPos = line.find(' -')
                        if nextSepPos != -1 and key != 'func':
                            if commentPos != -1 and commentPos < nextSepPos:
                                value = line[0:commentPos]
                                line = ''
                            else:
                                value = line[0:nextSepPos]
                                line = line[nextSepPos:]
                        else:
                            if commentPos != -1:
                                value = line[0:commentPos]
                            else:
                                value = line[0:]
                            line = ''
                           
                        value = value.strip() 
                        widget[key] = value
            
            widgetsList.append(widget)

    for widget in widgetsList:
        if widget['type'] == 'cmodule':
            setModuleDescription(widget['label'])
            break
            
    setInterfaceWidgets(widgetsList)
    
    return widgetsList

def slashifyText(text):
    charsToSlashify = [' ', '(', ')']
    newText = ''
    for i in range(len(text)):
        char = text[i]
        if char in charsToSlashify:
            char = '\\' + char
        newText += char
        
    return newText

def autoRename(path, index=0, wrap=False):
    if os.path.exists(path):
        file = ensureNFD(os.path.split(path)[1])
        if wrap:
            name = ensureNFD(file.rsplit('.', 1)[0])[:-4]
        else:    
            name = ensureNFD(file.rsplit('.', 1)[0])
        ext = file.rsplit('.', 1)[1]

        if len(name) >= 5:
            try:
                if name[-4] == '_' and type(eval(name[-3:])) == IntType:
                    name = name[:-4]
            except:
                pass
                
        root = os.path.split(path)[0]
        filelist = os.listdir(root)
        num = index
        for f in filelist:
            f = ensureNFD(f)
            if name in f and ext in f:
                num += 1
        newName = name + '_%03d' % num + '.' + ext      
        newPath = os.path.join(root, newName)
        return autoRename(newPath, index+1, True)
    else:
        newPath = path
    
    return newPath
    
def updateNchnlsDevices():
    interface = getInterface()
    editor = getCeciliaEditor()
    
    try:
        interface.updateNchnls()
    except:
        pass
    try:
        editor.setOrchestraPanel()
    except:
        pass
    
def shortenName(name,maxChar):
    if len(name)>maxChar:
        shortenChar = '...'
        addSpace = 0
        charSpace = (maxChar-len(shortenChar)) / 2
        if (maxChar-5) % 2 != 0:
            addSpace = 1
            
        name = name[:charSpace+addSpace] + shortenChar + name[len(name)-charSpace:]
    return name

def completeUserInputsDict():
    for i in getUserInputs():
        if getUserInputs()[i]['type'] == 'csampler':
            cfilein = getControlPanel().getCfileinFromName(i)
            getUserInputs()[i]['off'+cfilein.getName()] = cfilein.getOffset()
            getUserInputs()[i]['loopMode'] = cfilein.getSamplerInfo()['loopMode']
            getUserInputs()[i]['startFromLoop'] = cfilein.getSamplerInfo()['startFromLoop']
            getUserInputs()[i]['loopX'] = cfilein.getSamplerInfo()['loopX']
            getUserInputs()[i]['loopIn'] = cfilein.getSamplerInfo()['loopIn']
            getUserInputs()[i]['loopOut'] = cfilein.getSamplerInfo()['loopOut']
            getUserInputs()[i]['gain'] = cfilein.getSamplerInfo()['gain']
            getUserInputs()[i]['transp'] = cfilein.getSamplerInfo()['transp']
        elif getUserInputs()[i]['type'] == 'cfilein':
            cfilein = getControlPanel().getCfileinFromName(i)
            getUserInputs()[i]['off'+cfilein.getName()] = cfilein.getOffset()

    return copy.deepcopy(getUserInputs())

def updateInputsFromDict():
    for input in getUserInputs():
        cfilein = getControlPanel().getCfileinFromName(input)
        if cfilein and os.path.isfile(getUserInputs()[input]['path']):
            inputDict = getUserInputs()[input]
            cfilein.updateMenuFromPath(inputDict['path'])
            for k in inputDict:
                if k == 'loopMode':
                    cfilein.getSamplerFrame().setLoopMode(inputDict[k])
                elif k == 'loopX':
                    cfilein.getSamplerFrame().setLoopX(inputDict[k])
                elif k == 'loopIn':
                    cfilein.getSamplerFrame().setLoopIn(inputDict[k])
                elif k == 'loopOut':
                    cfilein.getSamplerFrame().setLoopOut(inputDict[k])
                elif k == 'gain':
                    cfilein.getSamplerFrame().setGain(inputDict[k])
                elif k == 'transp':
                    cfilein.getSamplerFrame().setTransp(inputDict[k])
                elif k == 'startFromLoop':
                    cfilein.getSamplerFrame().setStartFromLoop(inputDict[k])
                elif k == ('off'+input):
                    cfilein.setOffset(inputDict[k])
                elif k == 'path':
                    pass

def ensureNFD(unistr):
    if getPlatform() in ['linux2', 'win32']:
        encodings = [DEFAULT_ENCODING, ENCODING,
                     'cp1252', 'iso-8859-1', 'utf-16']
        format = 'NFC'
    else:
        encodings = [DEFAULT_ENCODING, ENCODING,
                     'macroman', 'iso-8859-1', 'utf-16']
        format = 'NFC'
    decstr = unistr
    if type(decstr) != UnicodeType:
        for encoding in encodings:
            try:
                decstr = decstr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
            except:
                decstr = "UnableToDecodeString"
                print "Unicode encoding not in a recognized format..."
                break
    if decstr == "UnableToDecodeString":
        return unistr
    else:
        return unicodedata.normalize(format, decstr)

def toSysEncoding(unistr):
    try:
        if getPlatform() == "win32":
            unistr = unistr.encode(ENCODING)
        else:
            unistr = unicode(unistr)
    except:
        pass
    return unistr

def chooseColour(i, numlines):
    def clip(x):
        val = int(x*255)
        if val < 0: val = 0
        elif val > 255: val = 255
        else: val = val
        return val

    def colour(i, numlines, sat, bright):
        hue = (i / float(numlines)) * 315
        segment = math.floor(hue / 60) % 6
        fraction = hue / 60 - segment
        t1 = bright * (1 - sat)
        t2 = bright * (1 - (sat * fraction))
        t3 = bright * (1 - (sat * (1 - fraction)))
        if segment == 0:
            r, g, b = bright, t3, t1
        elif segment == 1:
            r, g, b = t2, bright, t1
        elif segment == 2:
            r, g, b = t1, bright, t3
        elif segment == 3:
            r, g, b = t1, t2, bright
        elif segment == 4:
            r, g, b = t3, t1, bright
        elif segment == 5:
            r, g, b = bright, t1, t2
        return wx.Colour(clip(r),clip(g),clip(b))

    lineColour = colour(i, numlines, 1, 1)
    midColour = colour(i, numlines, .5, .5)
    knobColour = colour(i, numlines, .8, .5)
    sliderColour = colour(i, numlines, .5, .75)

    return [lineColour, midColour, knobColour, sliderColour]

def chooseColourFromName(name):
    def clip(x):
        val = int(x*255)
        if val < 0: val = 0
        elif val > 255: val = 255
        else: val = val
        return val

    def colour(name):
        vals = COLOUR_CLASSES[name]
        hue = vals[0]
        bright = vals[1]
        sat = vals[2]
        segment = int(math.floor(hue / 60))
        fraction = hue / 60 - segment
        t1 = bright * (1 - sat)
        t2 = bright * (1 - (sat * fraction))
        t3 = bright * (1 - (sat * (1 - fraction)))
        if segment == 0:
            r, g, b = bright, t3, t1
        elif segment == 1:
            r, g, b = t2, bright, t1
        elif segment == 2:
            r, g, b = t1, bright, t3
        elif segment == 3:
            r, g, b = t1, t2, bright
        elif segment == 4:
            r, g, b = t3, t1, bright
        elif segment == 5:
            r, g, b = bright, t1, t2
        return wx.Colour(clip(r),clip(g),clip(b))

    lineColour = colour(name)
    midColour = colour(name)
    knobColour = colour(name)
    sliderColour = colour(name)

    return [lineColour, midColour, knobColour, sliderColour]
