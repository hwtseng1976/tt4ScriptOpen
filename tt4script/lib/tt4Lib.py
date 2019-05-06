#!/usr/bin/python
import sys
import numpy as np
import RPi.GPIO as GPIO
import time
from smbus2 import SMBusWrapper, i2c_msg

#Use phsical pin numbers GPIO.setmode(GPIO.BOARD) not GPIO.BCM!!
#pin number setup
ene=12
ent=16
en18=18
oeb=7
bRst=33
bInt=37
TT4Addr=0x24
TT4RHidDes=[0x01,0x00]
TT4AppInit=[0x04,0x00,0x0B,0x00,0x40,0x00,0x01,0x3B,0x00,0x00,0x20,0xC7,0x17]

#functions 
class switch(object):
    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))    
        
   
def i2crw(addr,cmd,dataNum):
    with SMBusWrapper(1) as bus:
        msg=i2c_msg.write(addr,cmd)
        data=i2c_msg.read(addr,dataNum)
        bus.i2c_rdwr(msg,data)
    data=list(data)
    return data
def i2cr(addr,dataNum):
    with SMBusWrapper(1) as bus:
        data=i2c_msg.read(addr,dataNum)
        bus.i2c_rdwr(data)
    data=list(data)
    return data
def i2cw(addr,cmd):
    with SMBusWrapper(1) as bus:
        msg=i2c_msg.write(addr,cmd)
        bus.i2c_rdwr(msg)
    data=list(msg)
    return data    
def readFgData(addr,cmdNum,TNum):
    data=i2cr(addr,cmdNum)
    data=list(data)
    totalNum=(data[1]<<8)+data[0]
    RID=data[2]
    count=0
    n=0
    #:wprint totalNum,RID
    #while count<totalNum:
    data=i2cr(addr,totalNum)
    data=list(data)
    #print data[n]
    result=data
    return result

def millis():
    return time.time()*1000

def delayMs(howLong):
    start=millis()
    while((start+howLong)>millis()):
        pass
def powerOnRst(powerOnWait,rstWidth):
    #GPIO.output((en1,bRst),(GPIO.HIGH,GPIO.HIGH))
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.HIGH,GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.HIGH))
    delayMs(powerOnWait)
    #GPIO.output((en1,bRst),(GPIO.HIGH,GPIO.LOW))
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.HIGH,GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
    delayMs(rstWidth)
    #GPIO.output((en1,bRst),(GPIO.HIGH,GPIO.HIGH))
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.HIGH,GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.HIGH))

def ldoPowerOff():
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.LOW,GPIO.LOW,GPIO.LOW,GPIO.LOW,GPIO.LOW))    
    
def TT4resolve(fingerList):
    length=(fingerList[1]<<8)+fingerList[0]
    rId=fingerList[2]
    timeStamp=(fingerList[4]<<8)+fingerList[3]
    lo=(fingerList[5]>>5)&0b1
    numRec=fingerList[5]&0b11111
    reportCount=(fingerList[6]>>6)
    noiseEffect=fingerList[6]&0b111
    fInf=np.zeros((1,7))
    fInf=[[length,rId,timeStamp,lo,numRec,reportCount,noiseEffect]]
    frec=np.zeros((1,10))
    count=0
    while count<numRec:
        touchType=fingerList[10*(count)+7]&0b111
        tip=(fingerList[10*(count)+8]>>7)&0b1
        eventId=(fingerList[10*(count)+8]>>5)& 0b11
        touchId=fingerList[10*(count)+8]&0b11111        
        fX=(fingerList[10*(count)+10]<<8)+fingerList[10*(count)+9]
        fY=(fingerList[10*(count)+12]<<8)+fingerList[10*(count)+11]
        pressure=fingerList[10*(count)+13]
        majorAxis=fingerList[10*(count)+14]
        minorAxis=fingerList[10*(count)+15]
        orientation=fingerList[10*(count)+16]
        if count==0:
            frec=[[touchType,tip,eventId,touchId,fX,fY,pressure,majorAxis\
            ,minorAxis,orientation]]
        else:
            frec=np.append(frec,[[touchType,tip,eventId,touchId,fX,fY\
            ,pressure,majorAxis,minorAxis,orientation]],axis=0)
        count=count+1
    return fInf,frec    
def TT4Init():    
    GPIO.setmode(GPIO.BOARD)
    #Power on Reset for the ParadeIC
    print "Setup Pin12,16,18,7 GPIO18 as output"
    GPIO.setup(ene,GPIO.OUT)
    GPIO.setup(ent,GPIO.OUT)
    GPIO.setup(en18,GPIO.OUT)
    GPIO.setup(oeb,GPIO.OUT)
    GPIO.setup(bRst,GPIO.OUT)
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.LOW,GPIO.HIGH,GPIO.LOW,GPIO.HIGH,GPIO.LOW))
    delayMs(0.01)
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
    delayMs(0.01)
    GPIO.output((ene,ent,en18,oeb,bRst),(GPIO.HIGH,GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
    print "Setup pin37 GPIO26 as input"
    GPIO.setup(bInt,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    print "Start: %s"%time.time()
    powerOnRst(2,0.1)
    print "End: %s"%time.time()
    print "Wait for INT Pull Down"
    print "Start: %s"%time.time()
    try:
        result=0xffff
        while result!=0x0000:
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=10)
            print"falling edge start to  readRstSent"    
            data=i2cr(TT4Addr,5)
            print data
            result=(data[1]<<8)+data[0]
            if result==0:
                print 'start to send appInit data=0x%04x' % result
            else:
                print 'start to send appInit data fail data=0x%04x' % result
                powerOnRst(2,0.01)
        result=0x00
        while result!=0xFF:        
            data1=i2cw(TT4Addr,TT4RHidDes)
            print 'Send RHidDes'
            print ','.join('%02x'%x for x in data1)
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=10)
            data1=i2cr(TT4Addr,32)
            print data1
            result=data1[2]
            if result==0xff:
                print 'Bootload check ok data2=0x%02x' % result
            else:
               print 'Bootload check fail data2=0x%02x' %result
    except KeyboardInterrupt:
        GPIO.cleanup()   
    print"End:%s"%time.time()
    data1=i2cw(TT4Addr,TT4AppInit)
    print " ," .join('%02x'%x for x in data1)
    try:
        result=0xffff
        while result!=0x0000:
            GPIO.wait_for_edge(bInt,GPIO.FALLING,timeout=30)
            data1=i2cr(TT4Addr,2)
            result=(data[1]<<8)+data[0]
            print "receive:0x%04x" %result
    except KeyboardInterrupt:
        GPIO.cleanup() 
