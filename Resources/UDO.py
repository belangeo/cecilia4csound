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

LINKER = {
'out': 'globalOut1',
'outs': 'globalOut2',
'outq': 'globalOut4',
'outh': 'globalOut6',
'outo': 'globalOut8',
'outx': 'globalOut16',
'out32': 'globalOut32',
'outc': ''}

UDO = {
        'globalOut1':
"""
opcode globalOut1, 0, a
a0 xin
gaGlobalOut0 = gaGlobalOut0 + a0
endop

""",
        'globalOut2':
"""
opcode globalOut2, 0, aa
a0, a1 xin
gaGlobalOut0 = gaGlobalOut0 + a0
gaGlobalOut1 = gaGlobalOut1 + a1
endop

""",
        'globalOut4':
"""
opcode globalOut4, 0, aaaa
a0, a1, a2, a3 xin
gaGlobalOut0 = gaGlobalOut0 + a0
gaGlobalOut1 = gaGlobalOut1 + a1
gaGlobalOut2 = gaGlobalOut2 + a2
gaGlobalOut3 = gaGlobalOut3 + a3
endop

""",
        'globalOut6':
"""
opcode globalOut6, 0, aaaaaa
a0, a1, a2, a3, a4, a5 xin
gaGlobalOut0 = gaGlobalOut0 + a0
gaGlobalOut1 = gaGlobalOut1 + a1
gaGlobalOut2 = gaGlobalOut2 + a2
gaGlobalOut3 = gaGlobalOut3 + a3
gaGlobalOut4 = gaGlobalOut4 + a4
gaGlobalOut5 = gaGlobalOut5 + a5
endop

""",
        'globalOut8':
"""
opcode globalOut8, 0, aaaaaaaa
a0, a1, a2, a3, a4, a5, a6, a7 xin
gaGlobalOut0 = gaGlobalOut0 + a0
gaGlobalOut1 = gaGlobalOut1 + a1
gaGlobalOut2 = gaGlobalOut2 + a2
gaGlobalOut3 = gaGlobalOut3 + a3
gaGlobalOut4 = gaGlobalOut4 + a4
gaGlobalOut5 = gaGlobalOut5 + a5
gaGlobalOut6 = gaGlobalOut6 + a6
gaGlobalOut7 = gaGlobalOut7 + a7
endop

""",
        'globalOut16':
"""
opcode globalOut16, 0, aaaaaaaaaaaaaaaa
a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15 xin
gaGlobalOut0 = gaGlobalOut0 + a0
gaGlobalOut1 = gaGlobalOut1 + a1
gaGlobalOut2 = gaGlobalOut2 + a2
gaGlobalOut3 = gaGlobalOut3 + a3
gaGlobalOut4 = gaGlobalOut4 + a4
gaGlobalOut5 = gaGlobalOut5 + a5
gaGlobalOut6 = gaGlobalOut6 + a6
gaGlobalOut7 = gaGlobalOut7 + a7
gaGlobalOut8 = gaGlobalOut8 + a8
gaGlobalOut9 = gaGlobalOut9 + a9
gaGlobalOut10 = gaGlobalOut10 + a10
gaGlobalOut11 = gaGlobalOut11 + a11
gaGlobalOut12 = gaGlobalOut12 + a12
gaGlobalOut13 = gaGlobalOut13 + a13
gaGlobalOut14 = gaGlobalOut14 + a14
gaGlobalOut15 = gaGlobalOut15 + a15
endop

""",
        'globalOut32':
"""
opcode globalOut32, 0, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, a22, a23, a24, a25, a26, a27, a28, a29, a30, a31 xin
gaGlobalOut0 = gaGlobalOut0 + a0
gaGlobalOut1 = gaGlobalOut1 + a1
gaGlobalOut2 = gaGlobalOut2 + a2
gaGlobalOut3 = gaGlobalOut3 + a3
gaGlobalOut4 = gaGlobalOut4 + a4
gaGlobalOut5 = gaGlobalOut5 + a5
gaGlobalOut6 = gaGlobalOut6 + a6
gaGlobalOut7 = gaGlobalOut7 + a7
gaGlobalOut8 = gaGlobalOut8 + a8
gaGlobalOut9 = gaGlobalOut9 + a9
gaGlobalOut10 = gaGlobalOut10 + a10
gaGlobalOut11 = gaGlobalOut11 + a11
gaGlobalOut12 = gaGlobalOut12 + a12
gaGlobalOut13 = gaGlobalOut13 + a13
gaGlobalOut14 = gaGlobalOut14 + a14
gaGlobalOut15 = gaGlobalOut15 + a15
gaGlobalOut16 = gaGlobalOut16 + a16
gaGlobalOut17 = gaGlobalOut17 + a17
gaGlobalOut18 = gaGlobalOut18 + a18
gaGlobalOut19 = gaGlobalOut19 + a19
gaGlobalOut20 = gaGlobalOut20 + a20
gaGlobalOut21 = gaGlobalOut21 + a21
gaGlobalOut22 = gaGlobalOut22 + a22
gaGlobalOut23 = gaGlobalOut23 + a23
gaGlobalOut24 = gaGlobalOut24 + a24
gaGlobalOut25 = gaGlobalOut25 + a25
gaGlobalOut26 = gaGlobalOut26 + a26
gaGlobalOut27 = gaGlobalOut27 + a27
gaGlobalOut28 = gaGlobalOut28 + a28
gaGlobalOut29 = gaGlobalOut29 + a29
gaGlobalOut30 = gaGlobalOut30 + a30
gaGlobalOut31 = gaGlobalOut31 + a31
endop
"""
}
