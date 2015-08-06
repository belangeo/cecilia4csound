<CsoundSynthesizer>

<CsOptions>
-odac -d -Ma
</CsOptions>

<CsInstruments>
sr        =  44100
ksmps     =  10
nchnls    =  1

massign         0, 130  ; make sure that all channels
pgmassign       0, 130  ; and programs are assigned to test instr

instr   130

knotelength    init    0
knoteontime    init    0

kstatus, kchan, kdata1, kdata2 midiin

if (kstatus == 176) then
printks "kstatus= %d, kchan = %d, \\t CC = %d, value = %d \\tControl Change\\n", 0, kstatus, kchan, kdata1, kdata2
chnset kdata1, "midictrl"
chnset kchan, "midichannel"
endif

endin

</CsInstruments>

<CsScore>
i130 0 10
e
</CsScore>

</CsoundSynthesizer> 