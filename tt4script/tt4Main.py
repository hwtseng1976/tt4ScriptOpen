#!/usr/bin/python
import sys
import numpy as np
import RPi.GPIO as GPIO
import time
import lib.tt4PrintRep as tt4P
from smbus2 import SMBusWrapper, i2c_msg
"""
This Python code is for Parade TT41701 IC get report 
usage 
Case1 to print the coordinate data
python tt4Main.py --tt4P --filename.txt

Case 2

Case 3

"""

def main():
    if len(sys.argv) < 2: 
        print 'no argument'
        sys.exit()
    elif sys.argv[1].startswith('--'):
        n=sys.argv[1][2:]
        print n
        
    while tt4P.switch(n):
        if tt4P.case('tt4P'):
            print "Start to do the tt4P test."
            tt4P.tt4PrintRep()
            break
        if tt4P.case('tt4A'):
            print "Start to do the tt4N test."
            break
        if tt4P.case('tt4L'):
            print "Start to do the tt4L test."
            break
        if tt4P.case('tt4N'):
            print "Start to do the tt4N test."
            break
        if tt4P.case('tt4X'):
            print "Start to do the tt4X test."
            break
        print "No argument is not allowded."
        break        
       

if __name__== "__main__":
    main()  
