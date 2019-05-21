#!/usr/bin/python
import sys
import time
import numpy as np
import RPi.GPIO as GPIO
import time
import lib.tt4Lib as tt4
from smbus2 import SMBusWrapper, i2c_msg
bInt=37
TT4Addr=0x24
"""
tt4I V1 
 
"""
def tt4I(): 
    if len(sys.argv)>3:
        print 'Wring argument number'
        
    tt4.TT4Init()
    [xNum,yNum]=tt4.tt4GetSysInf()
    tPre=time.time()
    tt4.tt4SusScan()
    tNow=time.time()
    tDiff=(tNow-tPre)*1000
    print 'Suspend scan execute time:{0}' .format(tDiff)
    tPre=tNow
    
    try:    
        while True:
            print 'measure suspend current'
            time.sleep(2)
            
    except KeyboardInterrupt:
        tNow=time.time()
        tDiff=(tNow-tPre)*1000
        print 'Measure time :{0}' .format(tDiff)
        tt4.ldoPowerOff()               
        GPIO.cleanup()
        
