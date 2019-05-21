
'''
This script is used for Prarde TT41701 getting Cm and Cp raw data.
Usage
--tt4R --test.txt
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
def tt4SusScan():
    susCommand=[0x04,0x00,0x05,0x00,0x2F,0x00,0x03]
    success=0x2F
    #tt4.i2cw(TT4Addr,susCommand)
    tt4.delayMs(1)
    while success!=0x1F:
        tt4.i2cw(TT4Addr,susCommand)
        try:
            #tt4.i2cw(TT4Addr,susCommand)
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=300) 
            result=tt4.i2cr(TT4Addr,5)
            success=result[2]
            print 'suspend scan response {0}'.format(result)
        except KeyboardInterrupt:
            tt4.ldoPowerOff()  
            GPIO.cleanup()

def tt4GetSysInf():            
    sysInfCmd=[0x04,0x00,0x05,0x00,0x2F,0x00,0x02]
    dataleng=0x0000
    while dataleng!=0x3300:
        tt4.i2cw(TT4Addr,sysInfCmd)
        try:
            #tt4.i2cw(TT4Addr,sysInfCmd)
            #tt4.delayMs(1.5)
            #if GPIO.input(bInt)==0:
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=300) 
            data=tt4.i2cr(TT4Addr,3)
            dataleng=(data[0]<<8)+data[1]
            if dataleng==0x3300:
                data=tt4.i2cr(TT4Addr,data[0]) 
                fwVer=(data[9]<<8)+data[10]
                fwRev=(data[11]<<16)+(data[12]<<8)+data[13]
                cfgVer=(data[14]<<8)+data[15]
                xNum=data[33]
                yNum=data[34]
                print 'fwVer :0x%04x'%fwVer
                print 'fwRev :0x%06x'%fwRev
                print 'cfgVer:0x%04x'%cfgVer
                print 'rxNum:0x%02x'%xNum
                print 'txNum:0x%02x'%yNum
                trNum=[xNum,yNum]
                return trNum
        except KeyboardInterrupt:
            tt4.ldoPowerOff()  
            GPIO.cleanup() 
            
def tt4GetRawData(txNum,rxNum):
    cmSelfTestCmd=[0x04,0x00,0x06,0x00,0x2F,0x00,0x26,0x05]
    cmGetRepCmd=[0x04,0x00,0x0A,0x00,0x2F,0x00,0x27,0x00,0x00,0xFF,0xFF,0x05]
    cpSelfTestCmd=[0x04,0x00,0x06,0x00,0x2F,0x00,0x26,0x06]
    cpGetRepCmd=[0x04,0x00,0x0A,0x00,0x2F,0x00,0x27,0x00,0x00,0xFF,0xFF,0x06]
    totalByte=(txNum*rxNum*2)+2    
    cmRawData=np.zeros((1,totalByte/2))
    #icpRawData=np.zeros((1,txNum+rxNum+2))
    cpRawData=np.zeros((1,(txNum*2+rxNum*2)))
    
    # start to do Cm Self test
    print 'start to do Cm Self test'
    statusResult=0xFFFF
    while statusResult!=0x0000:
        tt4.i2cw(TT4Addr,cmSelfTestCmd)
        try:        
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=300) 
            result=tt4.i2cr(TT4Addr,7)
            statusResult=(result[5]<<8)+result[6]
            print result
            if statusResult==0x0000:            
                print 'Cm Self Test Status+Result:0x%04x' %statusResult
            elif result[5]==0xff:
                print 'not support Cm self test ID 0x05'
                GPIO.cleanup()
                sys.exit()
            elif result[6]==0x01:
                print 'Cm self test Fail'
                GPIO.cleanup()
                sys.exit()               
        except KeyboardInterrupt:
            tt4.ldoPowerOff()  
            GPIO.cleanup()
    
    countByte=0
    index=0
    executeCmd=1
    while countByte<totalByte: # read Cm self test raw data;
        if executeCmd==1:
            tt4.i2cw(TT4Addr,cmGetRepCmd)
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
                cmGetRepCmd[7]=countByte&0x00FF      # offset value         
                cmGetRepCmd[8]=(countByte>>8)&0xFF   # offset value
                count=0         
                while count<(thisSensByte):
                    cmRawData[0][index]=int((result[count+11]<<8)+result[count+10]) #fF/10
                    count=count+2
                    index=index+1
                tt4.delayMs(1)
                executeCmd=1
            else:
                tt4.delayMs(2)
                executeCmd=0                
        except KeyboardInterrupt:
            tt4.ldoPowerOff()
            GPIO.clearnup()
    #Send Cp Self test start     
    statusResult=0xFFFF     
    tt4.i2cw(TT4Addr,cpSelfTestCmd)     
    try:
        while statusResult==0xFFFF:
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=300) 
            result=tt4.i2cr(TT4Addr,7)
            statusResult=(result[5]<<8)+result[6]
            print result
            if statusResult==0x0000:            
                print 'Cp Self Test Status+Result:0x%04x' %statusResult
            elif result[5]==0xFF:
                print 'not support Cp self test ID 0x06'
                GPIO.cleanup()
                sys.exit()
            elif result[6]==0x01:
                print 'not support Cp self test fail'
                tt4.ldoPowerOff()
                GPIO.cleanup()
                sys.exit()           
    except KeyboardInterrupt:
        tt4.ldoPowerOff()
        GPIO.cleanup()
    index=0
    countByte=0
    executeCmd=1
    while countByte<(txNum+rxNum)*4:
        index=0
        #countByte=0
        tt4.i2cw(TT4Addr,cpGetRepCmd)
        try:
            #GPIO.wait_for_edge(bInt,GPIO.FALLING)
            if GPIO.input(bInt)==0:
                result=tt4.i2cr(TT4Addr,2)
                packetLength=(result[1]<<8)+result[0]
                result=tt4.i2cr(TT4Addr,packetLength)
                thisSensByte=(result[8]<<8)+result[7]
                countByte=countByte+thisSensByte
                print 'Cp countByte:{0}'.format(countByte)
                print 'Cp PacketLength:{0}'.format(packetLength)
                cpGetRepCmd[7]=countByte&0x00FF            
                cpGetRepCmd[8]=(countByte>>8)&0xFF 
                count=0          
                while count<(thisSensByte):
                    cpRawData[0][index]=int((result[count+11]<<8)+result[count+10]) #fF/10
                    count=count+2
                    index=index+1
                tt4.delayMs(1)
                executeCmd=1
            else:
                executeCmd=0
                tt4.delayMs(2)                
        except KeyboardInterrupt:
            tt4.ldoPowerOff() 
            GPIO.cleanup()
    return cmRawData,cpRawData    
     
def tt4R():
    fprint=0
    if len(sys.argv)<2 or len(sys.argv)>4:
        print 'no tx or rx number arguments or wrong arguments'
        GPIO.cleanup()
        sys.exit()
#    elif len(sys.argv)==3:
#        Print 'start to get the system information'
#        sysinf=int(sys.argv[2][2:])
#        if sysinf=='sysInf':
#            tt4GetSysInf()
#    elif len(sys.argv)==4:
#        print 'no save to file arguments'
#        txNum=int(sys.argv[2][2:])
#        rxNum=int(sys.argv[3][2:])
#        print 'txNum:{0},rxNum{1}'.format(txNum,rxNum)
#        fprint=0
    elif len(sys.argv)==3:
        print 'with save to file arguments'
        #txNum=int(sys.argv[2][2:])
        #rxNum=int(sys.argv[3][2:])
        filename=sys.argv[2][2:]
        print 'fileName:{0}'.format(filename)          
        fo = open(filename, "w")
        fprint=1
    
    tt4.TT4Init()
    tt4.delayMs(10)
    tt4SusScan()
    tt4.delayMs(10)
    [txNum,rxNum]=tt4GetSysInf()

    totalByte=txNum*rxNum*2+2      
    cmRawData=np.zeros((1,totalByte/2))
    cpRawData=np.zeros((1,(txNum+rxNum)*2))    

    while True:
        print 'Initial get:%s' %time.time()      
        index=0
        indexTx=0
        
        try:
            tt4.delayMs(1)
            cmRawData,cpRawData=tt4GetRawData(txNum,rxNum)
            while index<(totalByte/2):
                print '{0},'.format(cmRawData[0][index]),
                if fprint==1:
                    fo.write('{0},'.format(cmRawData[0][index]))                      
                index=index+1
                if index%rxNum==0:
                    print '{0},'.format(cpRawData[0][indexTx]),
                    print ''
                    if fprint==1:
                        fo.write('{0}\n'.format(cpRawData[0][indexTx]))
                        indexTx=indexTx+1
                        
            for i in range(txNum*2,txNum*2+rxNum-1):
                print '{0},'.format(cpRawData[0][i]),
                if fprint==1:
                    fo.write('{0},'.format(cpRawData[0][i]))
            print ''
            if fprint==1:
                fo.write('\n')
                fo.write('page start \n')
        except KeyboardInterrupt:
            print 'exit :%s' %time.time()
            tt4.ldoPowerOff()            
            GPIO.cleanup()
            if fprint==1:
                fo.close()
            break
