<CeciliaInterface>
csampler snd -label Audio
cgraph env -label Envelope -unit x -rel lin -min 0 -max 1 -col red -func 0 0 .000001 1 .99 1 1 0 
cslider freqsup -unit Hz -label green -rel log -min 20 -max 20000 -init 5000 -col green
cslider freq1 -label  forestgreen -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  forestgreen
cslider freq2 -label  olivegreen -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  olivegreen
cslider freq3 -label  lightgreen -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  lightgreen

cslider freqsup2 -unit Hz -label blue -rel log -min 20 -max 20000 -init 5000 -col blue
cslider freq4 -label  marineblue -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  marineblue
cslider freq5 -label  royalblue -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  royalblue
cslider freq6 -label  lightblue -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  lightblue

cslider freq7 -label  red -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  red
cslider freq8 -label  orange -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  orange
cslider freq9 -label  khaki -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  khaki
cslider freq10 -label  tan -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  tan

cslider freq11 -label  brightred -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  brightred
cslider freq12 -label  brightblue -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  brightblue
cslider freq13 -label  brightgreen -unit Hz -rel log -min 20 -max 20000 -init 1000 -col  brightgreen


cslider num -label Number of Layers -rate k -res int -min 1 -max 20 -init 5 -gliss 0 -up 1
ctoggle bal -label Restore Amp -init 0 -col green
</CeciliaInterface>

<5.1>

</5.1>

<Custom...>

</Custom...>

<Mono>

opcode mfilter, a, akki


ain, kfreqs, kfreqi, inum xin 


if kfreqs <= kfreqi then

kfreqs          =           kfreqi

endif

afilt           tonex       ain, kfreqs, inum

afilt           atonex      afilt, kfreqi, inum

                xout        afilt

endop 



                instr 1 


aOri1     sampler     [snd]


ktrig           changed     gknum
if ktrig = 1 then
                reinit      pass
endif

pass:


aProc1 mfilter aOri1, gkfreqsup, gkfreqinf, i(gknum)

rireturn



if gkbal = 1 then
    aProc1          balance     aProc1, aOri1
endif

aProc1          chorus      aProc1,gkchor,gkmodu 


aGauche         =           aProc1*gkenv

aGauche         dcblock2    aGauche


                out        aGauche*gkgain



                endin
</Mono>

<Octo>

</Octo>

<Quad>

</Quad>

<Stereo>
opcode mfilter, a, akki


ain, kfreqs, kfreqi, inum xin 


if kfreqs <= kfreqi then

kfreqs          =           kfreqi

endif

afilt           tonex       ain, kfreqs, inum

afilt           atonex      afilt, kfreqi, inum

                xout        afilt

endop 



                instr 1 


aOri1,aOri2     sampler     [snd]


ktrig           changed     gknum
if ktrig = 1 then
                reinit      pass
endif

pass:


aProc1 mfilter aOri1, gkfreqsup, gkfreqinf, i(gknum)
aProc2 mfilter aOri2, gkfreqsup, gkfreqinf, i(gknum)

rireturn



if gkbal = 1 then
aProc1          balance     aProc1, aOri1
aProc2          balance     aProc2, aOri2
endif

aProc1          chorus      aProc1,gkchor,gkmodu 
aProc2          chorus      aProc2,gkchor,gkmodu 

aProc1          varfilter      aProc1,gkchor,gkmodu 
aProc1          compresseur      aProc1,gkchor,gkmodu 


aGauche         =           aProc1*gkenv
aDroite         =           aProc2*gkenv

aGauche         dcblock2    aGauche
aDroite         dcblock2    aDroite


                outs        aDroite*gkgain, aGauche*gkgain



                endin
</Stereo>


<CsoundScore>
;#   p1   p2   p3              
i    1    0    [total_time]    
</CsoundScore>


<PythonScore>

</PythonScore>


<CeciliaOpen>
scoreType=Csound

</CeciliaOpen>

<CeciliaData>
</CeciliaData>
