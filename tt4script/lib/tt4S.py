
'''
This script is used for Prarde TT41701 getting Mutual/Self raw or diffcount.
Usage
python tt4Main.py --tt4S --xx --test.txt
xx
0: mutual/self Raw
1: mutual/self baseline
2: mutual/self diffcount
test.txt : raw data file name 
'''
import sys
import numpy as np
import RPi.GPIO as GPIO
import time
import lib.tt4Lib as tt4
from smbus2 import SMBusWrapper, i2c_msg
bInt=37
TT4Addr=0x24
def twos_comp(val,bits):
    if (val&(1<<(bits-1)))!=0:
        val=val-(1<<bits)
    return val

def tt4PanlScan():
    scanCmd=[0x04,0x00,0x05,0x00,0x2F,0x00,0x2A]
    result=0xFFFF
    print 'start to do the panel scan'
    while result!=0x1F00:
        tt4.i2cw(TT4Addr,scanCmd)
        try:
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=500)
            data=tt4.i2cr(TT4Addr,6)
            result=(data[2]<<8)+data[5]
            if result==0x1F00:
               print 'Scan success:0x%04x'%result
            else:
               print 'Scan Fail :0x%04x'%result          
        except KeyboardInterrupt:
            tt4.ldoPowerOff()
            GPIO.cleanup()
            
            
def tt4GetScan(txNum,rxNum,cmdNum):
    cmdNumM=cmdNum
    cmdNumS=cmdNum+3
    retriveScanDataM=[0x04,0x00,0x0A,0x00,0x2F,0x00,0x2B,0x00,0x00,0xFF,0xFF,cmdNumM]
    retriveScanDataS=[0x04,0x00,0x0A,0x00,0x2F,0x00,0x2B,0x00,0x00,0xFF,0xFF,cmdNumS]    
    totalByte=(txNum*rxNum)    
    mutual=np.zeros((1,totalByte*2))
    self=np.zeros((1,(txNum+rxNum)*2))
    
    # start to retrive data
    tt4PanlScan()
    
    print 'Start to retrive Data'    
    countByte=0
    index=0
    executeCmd=1
    while countByte<totalByte: # read Mutal data
        if executeCmd==1:
            tt4.i2cw(TT4Addr,retriveScanDataM)
        else:
           executeCmd=0
        try:
            #GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=500)            
            if GPIO.input(bInt)==0:
                result=tt4.i2cr(TT4Addr,2)
                print result
                packetLength=(result[1]<<8)+result[0]
                result=tt4.i2cr(TT4Addr,packetLength)
                thisSensByte=(result[8]<<8)+result[7]
                countByte=countByte+thisSensByte
                print 'countByte byte:{0}' .format(countByte)
                print 'This sense total byte:{0}'.format(packetLength)
                retriveScanDataM[7]=countByte&0x00FF      # offset value         
                retriveScanDataM[8]=(countByte>>8)&0xFF   # offset value
                count=0         
                while count<(thisSensByte*2):
                    val=int((result[count+11]<<8)+result[count+10])
                    if cmdNum==2:
                        val=twos_comp(val,16)
                    else: 
                        val=val
                    mutual[0][index]=val 
                    count=count+2
                    index=index+1
                tt4.delayMs(0.5)
                executeCmd=1
            else:
                tt4.delayMs(1)
                executeCmd=0                
        except KeyboardInterrupt:
            tt4.ldoPowerOff() 
            GPIO.cleanup()
# start to retrive Self data
    tt4PanlScan()    
    print 'Start to retvie self data'
    index=0
    countByte=0
    executeCmd=1
    while countByte<(txNum+rxNum):
        if executeCmd==1:
            tt4.i2cw(TT4Addr,retriveScanDataS)
        try:
            #GPIO.wait_for_edge(bInt,GPIO.FALLING)
            if GPIO.input(bInt)==0:
                result=tt4.i2cr(TT4Addr,2)
                packetLength=(result[1]<<8)+result[0]
                result=tt4.i2cr(TT4Addr,packetLength)
                thisSensByte=(result[8]<<8)+result[7]
                countByte=countByte+thisSensByte
                print 'countByte:{0}'.format(countByte)
                print 'PacketLength:{0}'.format(packetLength)
                retriveScanDataS[7]=countByte&0x00FF            
                retriveScanDataS[8]=(countByte>>8)&0xFF 
                count=0          
                while count<(thisSensByte*2):
                    val=int((result[count+11]<<8)+result[count+10])
                    if cmdNum==2:
                        val=twos_comp(val,16)
                    self[0][index]=val 
                    count=count+2
                    index=index+1
                tt4.delayMs(0.5)
                executeCmd=1
            else:
                tt4.delayMs(1)
                executeCmd=0                
        except KeyboardInterrupt:
            tt4.ldoPowerOff()
            GPIO.cleanup()
    return mutual,self    
     
def tt4S():
    fprint=0
    if len(sys.argv)<3 or len(sys.argv)>5:
        print 'wrong argument'
        GPIO.cleanup()
        sys.exit()
    elif len(sys.argv)==3 and sys.argv[2].startswith('--'):
        print 'Without sav to file arguments'
        cmdNum=int(sys.argv[2][2:])
        print 'Command Number is: 0x%02x' %cmdNum
    elif len(sys.argv)==4 and sys.argv[3].startswith('--'):
        print 'with save to file arguments'
        cmdNum=int(sys.argv[2][2:])
        print 'Command Number is: 0x%02x' %cmdNum
        filename=sys.argv[3][2:]
        print 'fileName:{0}'.format(filename)          
        fo = open(filename, "w")
        fprint=1
    else:
        print 'wrong argument'
        
    tt4.TT4Init()
    tt4.delayMs(1)
    tt4.tt4SusScan()
    tt4.delayMs(1)
    [xNum,yNum]=tt4.tt4GetSysInf() #rx=x; tx=y
    totalByte=xNum*yNum*2      
    mutual=np.zeros((1,totalByte/2))
    self=np.zeros((1,(yNum+xNum)))    
    try:
        while True:
            print 'Initial get:%s' %time.time()      
            index=0
            indexTx=0        
            tt4.delayMs(2)           
            mutual,self=tt4GetScan(yNum,xNum,cmdNum)
            while index<(totalByte/2):
                print '{0},'.format(mutual[0][index]),
                if fprint==1:
                    fo.write('{0},'.format(mutual[0][index]))                      
                    index=index+1
                if index%xNum==0:
                    print '{0},'.format(self[0][indexTx+xNum]),
                    print ''
                    if fprint==1:
                        fo.write('{0}\n'.format(self[0][indexTx+xNum]))
                        indexTx=indexTx+1
                            
            for i in range(0,xNum):
                print '{0},'.format(self[0][i]),
                if fprint==1:
                    fo.write('{0},'.format(self[0][i]))
            print ''
            if fprint==1:
                fo.write('\n')
                fo.write('Page Start\n')
    except KeyboardInterrupt:
        print 'exit :%s' %time.time() 
        tt4.ldoPowerOff()  
        GPIO.cleanup()
        if fprint==1:
            fo.close()
