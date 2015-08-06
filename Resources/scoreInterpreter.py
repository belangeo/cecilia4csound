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

import os
from types import ListType, StringType
from constants import *
from Drunk import *
import CeciliaLib

csoundText = ''
instrumentNumber = 1
champs = True
pnum = 3

def scoreFormat():
    global champs, pnum, csoundText

    csoundText = ''
    reset()

    execfile(os.path.join(TMP_PATH, 'pythonScore.py'), var)

    if var['p2'] != None:
        write()

    return csoundText
        
def write():
    global csoundText, champs, pnum

    if type(var['p2']) != ListType:
        var['p2'] = [var['p2']]

    while champs == True:
        if var['p%d' % pnum] != None:
            if type(var['p%d' % pnum]) != ListType:
                var['p%d' % pnum] = [var['p%d' % pnum]]
        if var['p%d' % (pnum+1)] == None:
            champs = False
        else:
            pnum += 1

    length = len(var['p2'])
    for i in range(length):
        csoundText += 'i%d ' % instrumentNumber
        for j in range(2, pnum+1):
            csoundText += str(var['p%d' % j][i%len(var['p%d' % j])]) + ' '
        csoundText += '\n'
    reset()

def addLine(x):
    global csoundText
    csoundText += x + '\n'

def forInst(x):
    global instrumentNumber, champs, pnum
    global p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20

    if var['p2'] != None:
        write()

    instrumentNumber = x
    reset()

def createTable(tableNum, initTime, tableSize, gen, *args):
    global csoundText
    arglist = []
    for arg in args:
        if type(arg) == StringType and '[' not in arg:
            arg = '"%s"' % arg
        arglist.append(arg)
    csoundText += 'f%d %f %s %d ' % (tableNum, initTime, tableSize, gen) + ' '.join([str(x) for x in arglist]) + '\n'

def getUserValue(str):
    if str == 'total_time':
        return CeciliaLib.getTotalTime()
    elif str in CeciliaLib.getUserInputs().keys():
        return CeciliaLib.getUserInputs()[str]['path']
    elif str in [slider.getName() for slider in CeciliaLib.getUserSliders()]:
        for slider in CeciliaLib.getUserSliders():
            if str == slider.getName():
                return slider.getValue()
    elif str in [obj.getName() for obj in CeciliaLib.getUserTogglePopups()]:
        for obj in CeciliaLib.getUserTogglePopups():
            if str == obj.getName():
                return obj.getValue()
    else:
        for k in CeciliaLib.getUserInputs().keys():
            if 'off%s' % k == str or 'nchnls%s' % k == str or 'gensize%s' % k == str or 'sr%s' % k == str or 'dur%s' % k == str:
                return CeciliaLib.getUserInputs()[k][str]

def midiToHertz(pitch):
    """Converts a midi pitch to frequency.
    
pitch = midi_pitch

return frequency in hertz

--- PARAMETERS ---

pitch : midi pitch to be converted in Hertz (cycle per second)
"""
    return 8.175798 * pow(1.0594633, pitch)

def midiToTranspo(pitch, centralkey=60):
    """Converts a midi pitch to a transposition factor.
    
pitch = midi_pitch
centralkey = 60

return transpo value

--- PARAMETERS ---

pitch : midi pitch to be converted in transposition factor
centralkey : midi pitch used as nominal value (midiToTranspo(60) returns 1.)
"""

    return pow(1.059463, pitch - centralkey)    

def drunk(mini=0, maxi=127):
    """Creates a drunk generator objet. Outputs integer values between mini and maxi.
    
mini = 0
maxi = 127 

return a drunk objet

--- PARAMETERS ---

mini : Minimum generated value.
maxi : Maximum generated value.

drunk performs a random walk generation.
"""
    return Drunk(mini, maxi)

def droneAndJump(mini=0, maxi=127):
    """Creates a droneAndJump generator objet. Outputs integer values between mini and maxi.
    
mini = 0
maxi = 127

return a droneAndJump objet

--- PARAMETERS ---

mini : Minimum generated value.
maxi : Maximum generated value.

droneAndJump outputs systematically a single note, but sometimes jumps to another note and returns to the first one.
"""
    return DroneAndJump(mini, maxi)

def repeater(mini=0, maxi=127):
    """Creates a repeater generator objet. Outputs integer values between mini and maxi.
    
mini = 0
maxi = 127

return a repeater objet

--- PARAMETERS ---

mini : Minimum generated value.
maxi : Maximum generated value.

repeater outputs many times a note before switching to another one.
"""
    return Repeater(mini, maxi)

def loopseg(mini=0, maxi=127):
    """Creates a loop segments generator objet. Outputs integer values between mini and maxi.
    
mini = 0
maxi = 127

return a loopseg objet

--- PARAMETERS ---

mini : Minimum generated value.
maxi : Maximum generated value.

loopseg generates cycle of notes and loop them a couple of times before switching.
"""
    return Loopseg(mini, maxi)

def reset():
    global p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20
    global champs, pnum

    p2 = p3 = p4 = p5 = p6 = p7 = p8 = p9 = p10 = p11 = p12 = p13 = p14 = p15 = p16 = p17 = p18 = p19 = p20 = None
    for i in range(2, 21):
        var['p%d' % i] = None
    champs = True
    pnum = 3

p2 = p3 = p4 = p5 = p6 = p7 = p8 = p9 = p10 = p11 = p12 = p13 = p14 = p15 = p16 = p17 = p18 = p19 = p20 = None
var = {'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5, 'p6': p6, 'p7': p7, 'p8': p8, 'p9': p9, 'p10': p10,
       'p11': p11, 'p12': p12, 'p13': p13, 'p14': p14, 'p15': p15, 'p16': p16, 'p17': p17, 'p18': p18, 'p19': p19, 'p20': p20,
       'forInst': forInst, 'addLine': addLine, 'write': write, 'createTable': createTable, 'midiToHertz': midiToHertz,
       'midiToTranspo': midiToTranspo, 'drunk': drunk, 'droneAndJump': droneAndJump, 'repeater': repeater, 'loopseg': loopseg,
       'getUserValue': getUserValue}