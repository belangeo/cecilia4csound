#!/usr/bin/env python
# encoding: utf-8
"""
Created by Olivier Bélanger on 2011-02-15.
"""
import os
from subprocess import Popen, PIPE

path = "/Users/olivier/svn/cecilia4/Cecilia4_OSX/Cecilia.app/Contents/Frameworks/CsoundLib64.framework/Versions/5.2/Resources/Opcodes64"
files = os.listdir(path)
libs = ["/usr/local/lib/libsndfile.1.dylib", "/usr/local/lib/liblo.0.dylib", "libmpadec.dylib", "/usr/local/lib/libpng12.0.dylib", "/usr/local/lib/libfluidsynth.1.dylib", "/Users/victor/src/portmidi/Release/libportmidi.dylib", "/usr/local/lib/libportaudio.2.dylib"]

print "number of files : ", len(files)

outfile = open("/Users/olivier/Desktop/repareLinks.txt", "w")

for j, f in enumerate(files):
    output = Popen(["otool", "-L", os.path.join(path, f)], stdout=PIPE).communicate()[0]
    lines = output.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("/Users/olivier") and i != 0:
            break
        if i == 1 and not line.startswith("@executable_path"):
            outfile.write("install_name_tool -id @executable_path/../Frameworks/CsoundLib64.framework/Versions/5.2/Resources/Opcodes64/%s %s\n" % (f, f))
        if i >= 2:
            for lib in libs:
                if lib in line and not line.startswith("@executable_path/"):
                    libname = lib.split("/")[-1]
                    outfile.write("install_name_tool -change %s @executable_path/../Frameworks/%s %s\n" % (lib, libname, f))
        if "/Library/Frameworks/Jackmp.framework/Versions/A/Jackmp" in line:
            outfile.write("install_name_tool -change /Library/Frameworks/Jackmp.framework/Versions/A/Jackmp @executable_path/../Frameworks/Jackmp.framework/Versions/A/Jackmp %s\n" % f)
            
outfile.close()
