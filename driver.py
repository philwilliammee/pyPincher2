#!/usr/bin/env python

""" 
  PyPose: Serial driver for connection to arbotiX board or USBDynamixel.
  Copyright (c) 2008,2009 Michael E. Ferguson.  All right reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import serial
import time
import sys
from binascii import b2a_hex
from ax12 import *

class Driver:
    """ Class to open a serial port and control AX-12 servos 
    through an arbotiX board or USBDynamixel. """
    #def __init__(self, port="/dev/ttyUSB0",baud=38400, interpolation=False, direct=False):
    def __init__(self, port="COM7",baud=38400, interpolation=False, direct=False):
        """ This may throw errors up the line -- that's a good thing. """
        self.ser = serial.Serial()
        self.ser.baudrate = baud
        self.ser.port = port
        self.ser.timeout = 0.5
        self.ser.open()
        self.error = 0
        self.hasInterpolation = interpolation
        self.direct = direct

    def execute(self, index, ins, params):
        """ Send an instruction to a device. """
        #print "Driver executing instruction "
        #print ("index = " + str(index))
        #print ("ins = " + str(ins))
        #print ("params = " + str(params))
        self.ser.flushInput()
        length = 2 + len(params)
        checksum = 255 - ((index + length + ins + sum(params))%256)
        self.ser.write(chr(0xFF)+chr(0xFF)+chr(index)+chr(length)+chr(ins))
        for val in params:
            self.ser.write(chr(val))
        self.ser.write(chr(checksum))
        return self.getPacket(0)

    def setReg(self, index, regstart, values):
        """ Set the value of registers. Should be called as such:
        ax12.setReg(1,1,(0x01,0x05)) """ 
        self.execute(index, AX_WRITE_DATA, [regstart] + values)
        return self.error     

    def getPacket(self, mode, id=-1, leng=-1, error=-1, params = None):
        """ Read a return packet, iterative attempt """
        # need a positive byte
        d = self.ser.read()
        if d == '': 
            print "Fail Read"
            return None

        # now process our byte
        if mode == 0:           # get our first 0xFF
            if ord(d) == 0xff:   
                return self.getPacket(1)
            else:
                return self.getPacket(0)
        elif mode == 1:         # get our second 0xFF
            if ord(d) == 0xff:
                return self.getPacket(2)
            else:
                return self.getPacket(0)
        elif mode == 2:         # get id
            if d != 0xff:
                return self.getPacket(3, ord(d))
            else:              
                return self.getPacket(0)
        elif mode == 3:         # get length
            return self.getPacket(4, id, ord(d))
        elif mode == 4:         # read error    
            self.error = ord(d)
            if leng == 2:
                return self.getPacket(6, id, leng, ord(d), list())
            else:
                return self.getPacket(5, id, leng, ord(d), list())
        elif mode == 5:         # read params
            params.append(ord(d))
            if len(params) + 2 == leng:
                return self.getPacket(6, id, leng, error, params)
            else:
                return self.getPacket(5, id, leng, error, params)
        elif mode == 6:         # read checksum
            checksum = id + leng + error + sum(params) + ord(d)
            if checksum % 256 != 255:
                print "Checksum ERROR"
                return None
            return params
        # fail
        return None

    def getReg(self, index, regstart, rlength):
        return self.execute(index, AX_READ_DATA, [regstart, rlength])

    def syncWrite(self, regstart, vals):#sync write is not implemented in arbitix
        """ Set the value of registers. Should be called as such:
        ax12.syncWrite(reg, ((id1, val1, val2), (id2, val1, val2))) 
        
        Setting thefollowing positionsand velocities for 4 Dynamixel actuators
Dynamixel actuator with anID of 0: to position 0X010 witha speed of 0X150 
Dynamixel actuator with anID of 1: to position 0X220 witha speed of 0X360 
Dynamixel actuator with anID of 2: to position 0X030 witha speed of 0X170 
Dynamixel actuator with anID of 0: to position 0X220 witha speed of 0X380 
Instruction Packet : 0XFF 0XFF BroadcastID(0XFE) length(0X18) sync_write(0X83) 
startingaddress(0X1E) dataLength(0X04) ax_ID(0X00) position_L(0X10) pos_H(0X00) 
speed_L(0X50) speed_H(0X01) 0X01 0X20 0X02 0X60 0X03 0X02 0X30 0X00 0X70 0X01 
0X03 0X20 0X02 0X80 0X03 checksum(0X12) """ 

        self.ser.flushInput()
        length = 4
        valsum = 0
        for i in vals:
            length = length + len(i)    
            valsum = valsum + sum(i)
        checksum = 255 - ((254 + length + AX_SYNC_WRITE + regstart + len(vals[0]) - 1 + valsum)%256)
        # packet: FF FF ID LENGTH INS(0x03) PARAM .. CHECKSUM
        self.ser.write(chr(0xFF)+chr(0xFF)+chr(0xFE)+chr(length)+chr(AX_SYNC_WRITE)+chr(regstart)+chr(len(vals[0])-1))
        print ("doing sync write of values")
        for servo in vals:
            for value in servo:
                print hex(value)
                self.ser.write(chr(value))
        self.ser.write(chr(checksum))
        # no return info...

        '''#some sync write work I have done:
                    dynamixel_ids = project.extract([1,2,3,4,5])
                    dynamixel_speeds = project.extract([50,50,50,50,50])
                    dynamixels = project.extract(self.dynamixels)
                    
                    
                    sync = [None]*(len(self.dynamixels)+len(dynamixel_speeds)+len(dynamixel_ids))
                    sync[::3] = dynamixel_ids
                    sync[1::3] = self.dynamixels
                    sync[2::3] = dynamixel_speeds
                    
                    sync = [None]*(len(dynamixel_ids))
                    
                    for i in range(len(dynamixel_ids)):
                        sync[i] = [(dynamixel_ids[i], dynamixels[i],dynamixel_speeds[i])]
                    print ("sync = " + str(sync))
                    self.port.syncWrite(P_GOAL_POSITION_L, sync)
                    
                    curPose = list() #TODO: should we use a syncWrite here?
                    for i in range(len(self.dynamixels)):
                        pos = self.dynamixels[i]
                        #self.port.setReg(servo+1, P_GOAL_POSITION_L, [pos%256, pos>>8])
                        #self.parent.project.poses[self.curpose][servo] = self.servos[servo].position.GetValue()                 
                        #pos = self.servos[servo].position.get()
                        curPose.append( (i+1, pos%256, pos>>8) )
                    print ("vals curpose = " + str(curPose))
                    self.port.syncWrite(P_GOAL_POSITION_L, curPose)
        '''
        '''
                if self.go_live and self.port != None and self.delay == False:   # live update 
                    
                    #self.delay = True
                    #start = time.time()
                    #self.setPose()
                    #print("setpose time : " + str( time.time()-start))
                    #self.t1 = wx.Timer(self)
                    #self.t1.Start(self.deltaT-100)
                    #print self.deltaT
                    
                    self.delay = True
                    print ("id =" +str(id))
                    if id ==1:
                        speeds = [100, 30, 23, 23, 100]#W extension
                    elif id ==2:
                        speeds = [100, 17, 41, 38, 100]#z height
                    else: 
                        speeds = [100, 25, 30, 38, 100]
                    for i in range(len(self.dynamixels)):
                        self.port.setReg(i+1, P_GOAL_SPEED_L, [speeds[i]%256,speeds[i]>>8]) 
                    
                    #loads all the servo values
                    for i, pos in enumerate(self.dynamixels):
            
                        self.port.setReg(i+1, P_GOAL_POSITION_L, [pos%256,pos>>8])
                        #print ("goal speed_L is " + str(self.port.getReg(i+1, P_GOAL_SPEED_L, 1)))
                        #print ("goal speed_H is " + str(self.port.getReg(i+1, P_GOAL_SPEED_H, 1)))
                else:
                     self.delay = False  
        '''
