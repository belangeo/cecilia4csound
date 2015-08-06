#!/usr/bin/env python
# encoding: utf-8
"""
Created by belangeo on 2010-05-31.

"""

import os

with open('CsoundKeywords.txt', 'r') as f:
    kwds = f.read().split()

syntax = {}

def filter(text):
    text = text.replace('class="synopsis">', '')
    text = text.replace('<span class="command">', '')
    text = text.replace('<strong>', '')
    text = text.replace('</strong>', '')
    text = text.replace('</span>', '')
    text = text.replace('</pre>', '')
    text = text.replace('\n', '')
    text = text.replace('\\', '')
    li = text.split(' ')
    text = ''
    for ele in li:
        if ele != '':
            text += ele + ' '
    return text
    
for key in kwds:
    manpage = 'html/%s.html' % key 
    if os.path.isfile(manpage):
        with open(manpage, 'r') as f:
            text = f.read()
        ind_s = text.find('class="synopsis"')
        if ind_s != -1:
            ind_e = text.find('</pre>', ind_s)
        text = filter(text[ind_s:ind_e])
        keypos = text.find(key)
        text = text[0:keypos] + '    ' + key + '    ' + text[keypos+len(key):]
        text = text.lstrip()
        syntax[key] = text
        
f = open('opcodes.py', 'w')
f.write('OPCODES_ARGS = ' + str(syntax) + '\n')
f.close()
