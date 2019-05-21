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
tt4Sy
"""
def tt4Sy(): 
    if len(sys.argv)<3 or len(sys.argv)>4:
        print 'wrong number of argument number'
        sys.exit()       
    elif len(sys.argv)==3 and sys.argv[2].startswith('--'):
        susTime=int(sys.argv[2][2:])
        fprint=0
        print 'suspend waiting time={0} sec' .format(susTime)        
    elif len(sys.argv)==4 and sys.argv[3].startswith('--'):
        susTime=int(sys.argv[2][2:]) # in sec
        filename=sys.argv[3][2:] 
        print filename
        fo = open(filename, "w")
        fprint=1
        print 'suspend waiting time={0} sec' .format(susTime)
    else:
        print 'wrong argument inputed'
        sys.exit()
       
    tt4.TT4Init()
    count=0
    tPalmon=0
    tInit=time.time()
    tPre=tInit
    print 'please put you palm on the screen.'
    print 'Please swipe the palm till suspend show finish'
    try:
        while True:
            if GPIO.input(bInt)==0 and tPalmon<=5000:
                #print 'time:%s INT Low'%time.time()
                count=count+1
                tNow=time.time()
                diff=(tNow-tPre)*1000
                tPalmon=(tNow-tInit)*1000
                tPre=tNow
                data1=tt4.readFgData(TT4Addr,3,10)
                a,b=tt4.TT4resolve(data1)
                count1=0
                #print a[0][4],a[0][3]
                if a[0][4]==0:
                    if a[0][3]==1:
                        print 'LO:{0}, large Object Detected' .format(a[0][3])
                        if fprint==1:
                            fo.write('RID:{0},TDF:{1},LO:{2},NE:{3},LargeObj\n'\
                            .format(a[0][1],diff,a[0][3],a[0][6]))
                    else:
                         print 'RID:{0}, liftoff' .format(a[0][1])
                         if fprint==1:
                            fo.write('RID:{0},TDF:{1},LO:{2},NE:{3},liftoff\n'\
                            .format(a[0][1],diff,a[0][3],a[0][6]))                                           
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
            elif tPalmon<=5000 and GPIO.input(bInt)==1:
                tcal=time.time()
                tPalmon=(tcal-tInit)*1000
                tt4.delayMs(1)            
            elif tPalmon>5000 and GPIO.input(bInt)==1:  # supend start
                tt4.tt4SusScan()
                print 'Scan susped start. Please swip the palm or finger on the screen'
                if fprint==1:
                    fo.write('Scan suspend start\n')
                tt4.delayMs(susTime*1000)               
                print 'Scan resume start. Please liftoff the palm and finger'
                tt4.tt4Resume()
                tInit=time.time()
                if fprint==1:
                    fo.write('Scan resumed\n')
                tPalmon=0
    except KeyboardInterrupt:
        print 'exit check :%s' %time.time()
        tt4.ldoPowerOff()               
        GPIO.cleanup()
        if fprint==1:
            fo.close()
