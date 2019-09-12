# Cecilia4Csound #

Cecilia4Csound is an audio signal processing environment that lets you create 
your own GUI (grapher, sliders, toggles, popup menus) using a simple syntax. 
Cecilia4Csound comes with many original built-in modules, written with Csound, 
for sound effects and synthesis.

Previously written with Tcl/Tk, Cecilia4Csound was entirely rewritten with 
Python/wxPython and uses the Csound API for the communication between the 
interface and the audio engine. 

# Running Cecilia4Csound from sources #

**To run Cecilia4Csound from sources, the following softwares must be installed on the system:**

- [Python 2.7](https://www.python.org/downloads/release/python-2716/)

- [wxPython 3.0.2.0](https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/)

- [pyo 1.0.0](http://ajaxsoundstudio.com/software/pyo/)

- [numpy](https://numpy.org/)

- [Csound6 6](https://csound.com/)

Then, download and extract sources for cecilia4csound and run in a terminal 
(or command prompt on Windows):

    cd path/to/folder/cecilia4csound/
    python Cecilia4Csound.py
