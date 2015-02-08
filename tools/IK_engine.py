'''
  Description: The Inverse Kinemtaic engine for calculating joint angles from tool points
      much thanks to Maquina_Pensante for helping me figure this out, TRIG FTW!

  PyPincher: A pose and sequence model of PhantomX Pincher arm from Trossen robotics
  Copyright (c) 2015 Philip Williammee.  All right reserved.

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
'''

import numpy as np
import math
np.seterr(divide='ignore', invalid='ignore')

JOINT = int(0)
IK = int(1)
TP = int(2)
SEGMENTS = int(4) #number of phantomX segments

class IK_engine(object):
    def __init__(self, type=TP, links=[0.0, 105.0, 105.0, 113.0]):
        self.type=type
        self.l12 = 0.0                                # hypotenuse belween a1 & a3
        self.a12 = 0.0                                #inscribed angle between hypotenuse, w 
        self.l = np.asarray(links) #98.0])# actual measurements of segment length in mm
        self.w = np.array([0.0]*SEGMENTS,dtype=float) #horizontal coordinate
        self.z = np.array([0.0]*SEGMENTS,dtype=float) #vertical coordinate
        self.x = np.array([0.0]*SEGMENTS,dtype=float) #x axis components 
        self.y = np.array([0.0]*SEGMENTS,dtype=float) #y axis components
        self.a = np.array([0.0]*SEGMENTS,dtype=float) #angle for the link, reference is previous link
        
    '''these functions convert slider variables to dynamixel and xyz coord'''   
    def sliders_to_var(self):#loads the variables needed to calculate pos.
        ##print self.sliders_val
        self.tx = self.sliders_val[0]
        self.ty = self.sliders_val[1]
        self.tz = self.sliders_val[2]
        self.gripper_angle = self.sliders_val[3]
        
    def calc_p2(self):#calculates position 2
        self.w[3] = self.tw
        self.z[3] = self.tz
        self.w[2] = self.tw-np.cos(self.gripper_angle)*self.l[3]
        self.z[2] = self.tz-np.sin(self.gripper_angle)*self.l[3]
        self.l12 = np.sqrt(np.square(self.w[2])+np.square(self.z[2])) 

    def calc_p1(self):#calculate position 1
        self.a12 = np.arctan2(self.z[2],self.w[2])#return the appropriate quadrant  
        
        if (2*self.l[1]*self.l12)==0 or np.square(self.l[1])+np.square(self.l12)-np.square(self.l[2]) ==0:
            self.a[1] = self.a12
        else:#@todo still gives error
            self.a[1] = np.arccos((np.square(self.l[1])+np.square(self.l12)-np.square(self.l[2])) 
                              /(2*self.l[1]*self.l12))+self.a12
                              
        self.w[1] = np.cos(self.a[1])*self.l[1]
        self.z[1] = np.sin(self.a[1])*self.l[1]
    
    def calc_angles(self): #calculate all of the motor angles see diagram
        #self.a[0] is set in calc positions  
        #self.a[1] is set in calc_p1
        #self.a[2] = np.arctan((self.z[2]-self.z[1])/(self.w[2]-self.w[1]))-self.a[1]
        if (self.w[2]-self.w[1]) ==0: 
            self.a[2] =-self.a[1]
        else:
            self.a[2] = np.arctan2((self.z[2]-self.z[1]),(self.w[2]-self.w[1]))-self.a[1]
        
        self.a[3]=(self.gripper_angle -self.a[1]-self.a[2])
    
    def calc_x_y(self):#calc x_y of servoscoordinates 
        for i in range(4):#fixed number of segments
            self.x[i] = self.w[i]*np.cos(self.a[0])
            self.y[i] = self.w[i]*np.sin(self.a[0])
             
    def calc_positions(self, t_x, t_y, t_z, g_a=0, style=TP ):
        #recieves in degrees, calculates in radians, returns in degrees 
        self.gripper_angle  = np.deg2rad(g_a)  
        error = False
        if style == TP:#recieved t_x
            if t_x == 0:
                t_x =  0.00001
            self.a[0] = np.arctan2(t_y , t_x )#radians
            self.tw = math.sqrt((t_x*t_x) + (t_y*t_y))
        else:
            self.a[0] = np.deg2rad(t_x)
            self.tw = t_y
        self.tz = t_z
        
        #self.sliders_to_var()
        self.calc_p2() 
        self.calc_p1() 
        self.calc_angles()    
        self.calc_x_y()
        
        if self.l12 > (self.l[1]+self.l)[2]:
            #print "target position can not be reached"
            error = True
            
        if None in self.a:
            #print "angles return an empty list", self.a
            error = True
        a_list = np.rad2deg(self.a).tolist()
        mod_a = [a%360 for a in a_list]
        return  error, mod_a
        
    def get_pos(self):
        #convert arrays to lists
        xs = np.array(self.x).tolist()
        ys = np.array(self.y).tolist()
        zs = np.array(self.z).tolist()
        return (xs, ys, zs)
           
    def angles_2_IK(self, deg_angles):  
        mod_angles = [a%360 for a in deg_angles]
        angles = np.deg2rad(mod_angles) 
        
        error= False 
        gripper_angle = (angles[1]+angles[2]+angles[3])
        
        l12 = np.sqrt((self.l[1]*self.l[1])+(self.l[2]*self.l[2])
                      -(2*self.l[1]*self.l[2]*np.cos(np.pi-angles[2])))
        #law of cosines to find second angle sigma
        sigma = np.arccos(((self.l[1]*self.l[1])+(l12*l12)
                           -(self.l[2]*self.l[2])) / (2*self.l[1]*l12))
        a12 = angles[1]-sigma
        w2 = l12*np.cos(a12)
        z2 = l12*np.sin(a12)
        wt = (self.l[3]*np.cos(gripper_angle))+w2
        zt = (self.l[3]*np.sin(gripper_angle))+z2
        ik = [np.rad2deg(angles[0]), wt, zt, np.rad2deg(gripper_angle ) ]
        if np.isnan(ik).any():
            error = True
        return error, ik
    
    def angles_2_TP(self, deg_angles):
        mod_angles = [a%360 for a in deg_angles]
        angles = np.deg2rad(mod_angles) 
        error = False
        gripper_angle = (angles[1]+angles[2]+angles[3])
        #print "gripper angle", gripper_angle, "=",angles[1],angles[2],angles[3]
        l12 = np.sqrt((self.l[1]*self.l[1])+(self.l[2]*self.l[2])
                      -(2*self.l[1]*self.l[2]*np.cos(np.pi-angles[2])))
        #law of cosines to find second angle sigma
        sigma = np.arccos(((self.l[1]*self.l[1])+(l12*l12)
                           -(self.l[2]*self.l[2])) / (2*self.l[1]*l12))
        a12 = angles[1]-sigma
        w2 = l12*np.cos(a12)
        z2 = l12*np.sin(a12)
        wt = (self.l[3]*np.cos(gripper_angle))+w2
        zt = (self.l[3]*np.sin(gripper_angle))+z2
        xt = wt*np.cos(angles[0])
        yt = wt*np.sin(angles[0])
        tp = [xt,yt, zt, (np.rad2deg(gripper_angle)%360) ]
        if np.isnan(tp).any():
            error = True
        return error, tp
    
NAME = "SKIP"
STATUS = "Trig stuff..."