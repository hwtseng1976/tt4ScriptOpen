#!/usr/bin/python
import sys
import numpy as np
import RPi.GPIO as GPIO
import time
import lib.tt4P as tt4P
import lib.tt4I as tt4I
import lib.tt4Sy as tt4Sy
import lib.tt4R as tt4R
import lib.tt4S as tt4S
import lib.tt4Lib as tt4
from smbus2 import SMBusWrapper, i2c_msg
"""
This Python code is for Parade TT41701 IC get report 
usage 
Case1 to print the coordinate data
python tt4Main.py --tt4P --filename.txt (print the result to file)
python tt4Main.py --tt4P (do not print to file)

Case 2 get tt4 system information and suspend the IC
python tt4Main.py --tt4I

Case 3 to simulate EMR inRang sync function.
python tt4Main.py --tt4Sy --xx --log.txt
xx : suspend time
log.txt: log the coordinate the time for the touch

Case 4 to get the Cm and Cp self test data
python tt4Main.py --tt4R --filename.txt

Case 5 to get the mutual/self data
python tt4Main.py --tt4S --xx --test.txt
xx
0: mutual/self Raw
1: mutual/self baseline
2: mutual/self diffcount
test.txt : raw data file name 
V1
initial release
V2
1. add tt4S : scan raw data function
V3 
1. improve the tt4P time diff accuracy
2. poweroff before leave each test case
V4
1. add the get Information and EMR sync simulation case
"""

def main():
    if len(sys.argv) < 2: 
        print 'no argument'
        sys.exit()
    elif sys.argv[1].startswith('--'):
        n=sys.argv[1][2:]
        print n
    else: 
        print "wrog argument"
        sys.exit()
        
    while tt4.switch(n):
        if tt4.case('tt4P'):
            print "Start to do the tt4P Print the TP coordinate data."
            tt4P.tt4P()
            break
        if tt4.case('tt4I'):
            print "Start to do the tt4I get sys inf and suspend the IC."
            tt4I.tt4I()
            break
        if tt4.case('tt4Sy'):
            print "Start to do the tt4Sy EMR Sync function simulation test."
            tt4Sy.tt4Sy()
            break
        if tt4.case('tt4R'):
            print "Start to do the tt4R Read Cm and Cp test."
            tt4R.tt4R()
            break
        if tt4.case('tt4S'):
            print "Start to do the tt4S Scan and get the raw diff count data."
            tt4S.tt4S()
            break
        print "No argument is not allowded."
        break        
       

if __name__== "__main__":
    main()  
