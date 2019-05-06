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
tt4P V2 
revise the timestamp to RPI internal timer Tdiff 
"""
def tt4P(): 
    if len(sys.argv)<3:
        print 'no print to file argument'
        fprint=0
    elif sys.argv[2].startswith('--'):
        filename=sys.argv[2][2:] 
        print filename
        fo = open(filename, "w")
        fprint=1
        
    tt4.TT4Init()
    count=0
    tPre=time.time()
    while True:    
        try:
            tt4.delayMs(0.02)
            #print 'before Falling'
            if GPIO.input(bInt)==0:
                #print 'time:%s INT Low'%time.time()
                count=count+1
                tNow=time.time()
                diff=tNow-tPre
                tPre=tNow
                data1=tt4.readFgData(TT4Addr,3,10)
                a,b=tt4.TT4resolve(data1)
                count1=0
                #print a[0][4],a[0][3]
                if a[0][4]==0:
                    if a[0][3]==1:
                        print 'LO:{0}, large Object Detected' .format(a[0][3])
                    else:   
                        print 'RID:{0}, liftoff' .format(a[0][1])
                else:
                    while count1<a[0][4]:
                        print 'RID:{0},TDF:{1},LO:{2},NE:{3},TIP:{4},EID:{5},TID:{6},{7},{8},{9},{10},{11},{12},'\
                        .format(a[0][1],diff,a[0][3],a[0][6],b[count1][1],\
                        b[count1][2],b[count1][3],b[count1][4],b[count1][5],\
                        b[count1][6],b[count1][7],b[count1][8],b[count1][9]) 
                        if fprint==1:
                            if count1==0:
                                fo.write('RID:{0},TDF:{1},LO:{2},NE:{3},'\
                                .format(a[0][1],diff,a[0][3],a[0][6]))
                                fo.write('Type:{0},TIP:{1},EID:{2},TID:{3},{4},{5},{6},{7},{8},{9},'\
                                .format(b[count1][0],b[count1][1],b[count1][2],b[count1][3],\
                                b[count1][4],b[count1][5],b[count1][6],b[count1][7],\
                                b[count1][8],b[count1][9])) 
                            else:
                                fo.write('Type:{0},TIP:{1},EID:{2},TID:{3},{4},{5},{6},{7},{8},{9},'\
                                .format(b[count1][0],b[count1][1],b[count1][2],b[count1][3],\
                                b[count1][4],b[count1][5],b[count1][6],b[count1][7],\
                                b[count1][8],b[count1][9])) 
            
                        count1=count1+1                   

                if fprint==1:                
                    fo.write('\n')
                tt4.delayMs(0.5)
            else:
                tt4.delayMs(1)
        except KeyboardInterrupt:
            print 'exit check :%s' %time.time()
            tt4.ldoPowerOff()               
            GPIO.cleanup()
            if fprint==1:
                fo.close()
            break
