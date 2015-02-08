#!/usr/bin/env python2.7

'''
  Description: Knobs have functions for creating the knob pannels 
also helper for converting between JOINT, TP, and IK positioning 

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
import wx
import wx.lib.agw.knobctrl as KC
from IK_engine import IK_engine
import math
import numpy as np
from wx_obj_canvas import do_collision_chec#(spheres, gl_angles, unpack_angles=True):
#from Pose_Editor import servo_2_angle_offset,ax_2_deg, deg_2_ax, angle_2_servo_offset

JOINT=0
IK=1
TP=2     

def get_distance(p1,p2):
    p1=p1[:3] #this should be removed
    p2=p2[:3] #this should be removed
    x,y,z = [list(a) for a in zip(p1, p2)]
    xd = x[1]-x[0]
    yd = y[1]-y[0]
    zd = z[1]-z[0]
    distance = math.sqrt(xd*xd + yd*yd + zd*zd)
    return distance

def get_vector_steps(p1, p2, distance, resolution=3):
    #calculates the vector between two points and segments it into iterations in mm
    p1=p1[:3]
    p2=p2[:3]
    x,y,z = [list(a) for a in zip(p1, p2)]
    vector = np.arange(0, distance, resolution)
    xs, ys, zs=[],[],[]
    for v in vector:
        scale = v/(distance*1.0)
        xs.append( x[0] + scale*(x[1]-x[0]))
        ys.append( y[0] + scale*(y[1]-y[0]))
        zs.append( z[0] + scale*(z[1]-z[0]))
    
    xs.append(x[1])
    ys.append(y[1])
    zs.append(z[1])
    return xs,ys,zs

#@ TODO Move this to apropriate folder
class run_sequence():
    def __init__(self, parent, tranbox_items, proj_poses, start_pos=None, loop=True, iter=3 ):
        #@todo this needs clean up and speed improvements
        #@todo implement smooth transitions between wrist angles it just blips from one to next
        
        #@todo TP speeds are calculated but nothing is checked for joint speeds 
        self.res_step = iter#iteration interval
        self.move_seq, self.time_seq = seq_2_key(tranbox_items)
        self.total_dist=0
        self.tran_time_list = []
        self.home_pos = [0,65,35,0]
        self.parent = parent
        if loop == True:
            self.move_seq.append(self.move_seq[0])
            self.time_seq.append(self.time_seq[0])
            
            
        self.proj_poses = proj_poses
        self.IK_canvas=[]
        self.moving = False
        self.counter = 0
        self.draw_sequence = True
        
        if start_pos == None:
            start_deg = self.get_pos_deg(self.move_seq[0])
            e, self.start_TP = gl_2_TP(start_deg)
            del self.move_seq[0]
            
        else:
            e, self.start_TP = gl_2_TP(start_pos)
            
        self.griper_tran_angle = self.start_TP[3]
        
        self.xs=[]
        self.ys=[]
        self.zs=[]

        #generate the list
        self.do_seq()
        
    def get_seq(self):
        return list(self.IK_canvas)
    
    def get_line_points(self):
        return list(self.xs), list(self.ys), list(self.zs)
    
    def get_pos_deg(self, seq_pos):
        #recieves the pose position in the list
        #@todo deal with key errors
        curpose = self.proj_poses[seq_pos]
        #@todo this should include grippers open position
        deg_position = [ax_2_deg(ax) for ax in (curpose[:-1])] + [curpose[4]]
        return deg_position


    def do_seq(self):
        distance = 0
        self.total_dist = 0
        for seq, time in zip(self.move_seq, self.time_seq):  
            #load the next saved project position
            finish_deg = self.get_pos_deg(seq)
            
            #convert it to tp so we can calculate distance
            e, next_TP = gl_2_TP(finish_deg)        
            if e is not True:           
                #use tp to get distance
                distance = get_distance(self.start_TP, next_TP) 
                             
                self.total_dist += distance 
                #get the number of iterations
                xs,ys,zs = get_vector_steps(self.start_TP, next_TP, distance, self.res_step)  
                print "next tp angle is ", next_TP[3]   
                for x,y,z in zip(xs,ys,zs):
                    #do a smooth transition of grippers
                    if int(next_TP[3]) > int(self.griper_tran_angle):
                        self.griper_tran_angle = (self.griper_tran_angle + 1)
                    elif int(next_TP[3]) < int(self.griper_tran_angle):
                        self.griper_tran_angle = (self.griper_tran_angle - 1)                       
                    gripper_angle = self.griper_tran_angle
                    
                    coord = IK_engine(TP)
                    e, angle = coord.calc_positions(x, y, z, gripper_angle, TP)
                    
                    if e is not True:
                        #@todo make sure this is the gripper position
                        gl_a = angle_2_servo_offset(angle + [finish_deg[4]]) 
                        
                        '''
                        @todo implement this
                        #test here for collision
                        if self.parent.collision_detect is True:
                            collision = do_collision_chec(self.parent.spheres, gl_a, unpack_angles=True)
                            if collision is True:
                                #do evasive manuevers
                                continue
                        '''
                                
                        self.IK_canvas.append(gl_a)  
                        self.tran_time_list.append(time) 
                        #could add a test to ignore distances greater the min_draw distance
                        self.xs.append(x)
                        self.ys.append(y) 
                        self.zs.append(z)   
                    else:
                        self.total_dist -= distance/(len(xs)*1.0)#remove the unused distance
                        #@todo auto griper level with search through all gripper angles
                        #print "found error gripper angles may need adjustment"
                        
                self.start_TP = list(next_TP)
                
    def __del__(self):
        print "run_seq deleted"

              
class knob_sizer(wx.StaticBox):#parent should be a panel parent whose parent is a fram
    def __init__(self, parent, ID=-1, label=wx.EmptyString, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=wx.StaticBoxNameStr, knob_type=JOINT):       
        wx.StaticBox.__init__(self, parent, ID, label, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=name)
        self.box_sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.Lower()
        self.knobtracker = wx.StaticText(self.Parent, -1, "0")
        self.knob = knob(self.Parent, wx.ID_ANY, size=(95, 95), type=knob_type) 
        self.box_sizer.Add(self.knobtracker, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.box_sizer.Add(self.knob, 1, 0, 0)

    def set_label(self, value):
        self.knobtracker.SetLabel(value)
        self.knobtracker.Refresh()
               
class knob(KC.KnobCtrl):
    #knobs should be able to return a list of axis angles in degrees, axis points, and dynamixels motor values
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=(100,100), type=JOINT):
        KC.KnobCtrl.__init__(self, parent, ID, pos, size)
        self.SetSecondGradientColour(wx.RED)
        self.SetBoundingColour(wx.BLACK)
        self.SetBackgroundColour([211,211,211])
        self.SetAngularRange(-45, 225)
        self.type = type
        #an offset is needed because knob widgets do not return negatives
        self.offset = 0
            
    def get_value(self):
        return self.GetValue()-self.offset
    
    def set_value(self, val):
        self.SetValue(val+self.offset)

class knobs_helper():
    def __init__(self, style=JOINT, knobs_box=[knob_sizer]*5 ):
        self.style = style
        self.knobs_box = knobs_box
        self.knobs = [k.knob for k in knobs_box]
        self.pos_knobs = self.knobs[:4]
        self.gripper = self.knobs[4]
        self.converter = IK_engine(style)
        self.set_style(style)
            
    def get_knobs(self):
        #accesses the knobs and returns a new list of their values
        return [knob.get_value() for knob in self.knobs]
    
    def get_pos_knobs(self):
        return [knob.get_value() for knob in self.pos_knobs]
        
    def get_joint_angles(self):
        error = False
        if self.style == JOINT:
            val = self.get_knobs()
            ret = [ax_2_deg(v) for v in val[:-1]]+[val[4]]
            #print ret, "knob joints to degrees"
            return error, ret
        error, angle = self.converter.calc_positions(*self.get_pos_knobs(), style=self.style)
        angle.append(self.gripper.get_value())
        return error, angle
    
    def get_TP(self):
        xs, ys, zs = self.converter.get_pos()
        return [xs[3],ys[3],zs[3]]
    
    def get_joints(self):
        return self.converter.get_pos()

    def set_style(self, style=JOINT):
        #sets the knob style and offset for appropriate range
        style_list =  [
                (JOINT,JOINT,JOINT,JOINT,JOINT),
                (IK,TP,TP,IK,JOINT),
                (TP,TP,TP,IK,JOINT)]
        
        for i, key in enumerate(style_list[style]):
            if key == IK:
                #print "seting style to IK"
                #self.knobs[i].SetAngularRange(-45, 225)
                self.knobs[i].SetTags(range(0, 361, 36))
                self.knobs[i].offset=0
            elif key == TP:
                #print "seting style to TP"
                #self.knobs[i].SetAngularRange(-44, 224)
                self.knobs[i].SetTags(range(0,561, 56)) 
                self.knobs[i].offset = 280
            else:#joint
                #print "seting style to Joint"
                #self.knobs[i].SetAngularRange(-46, 226)
                self.knobs[i].SetTags(range(0, 1228, 128))
                self.knobs[i].SetValue(512)
                self.knobs[i].offset = 0
                
    def get_servo_angles(self):
        #returns the servo angles *note gripper is always a servo position
        error, servo_angles = self.get_joint_angles()
        #print "IK servo angles =",servo_angles
        #apply the offset to convert from IK to AX and GL
        if self.style == JOINT:
            return error, servo_angles
        
        return error, angle_2_servo_offset(servo_angles)
                
    def set_values(self, values):  
        #2todo does this set the aproprite value
        for i, value in enumerate(values):
            #print i, value
            self.knobs[i].set_value(value) 
            self.knobs_box[i].set_label(str(int(round(value,0))))#+self.knobs[i].offset))
            
    def update_text(self): 
        #update all of the knob boxes texts with offset recieved from get function
        for knob_box in self.knobs_box:
            knob_box.set_label(str(int(round(knob_box.knob.get_value(),0))))
              
    def angle_2_knob(self, gl_ang):
        #print "angle 2 knobs recieved", gl_ang
        knob_val = []
        error = False
        grippers = gl_ang[4]
        #print "angles to knob val recieved", gl_ang
        #apply offset
        kin_angle = servo_2_angle_offset(gl_ang)
        #print "servo to angle offset returns ", kin_angle
        if self.style == IK:
            error, knob_val = self.converter.angles_2_IK(kin_angle[:-1])
        elif self.style == TP:
            error, knob_val = self.converter.angles_2_TP(kin_angle[:-1])
        else:
            return error, ([deg_2_ax(deg) for deg in gl_ang[:-1]]+[grippers])
        
        knob_val[3]=knob_val[3]%360
        return error, knob_val+[grippers]
    
def seq_2_key(seq_items):
        ss = [i_s.split(',') for i_s in seq_items]
        keys= [(item) for sublist in ss for item in sublist][::2]
        tran_time = map(int, [(item) for (sublist) in ss for item in sublist][1::2])
        return keys, tran_time

def ax_2_deg(ax):
    return ((ax) * 0.29296875)+30

def deg_2_ax(deg):
    return (deg-30)/ 0.29296875

def ard_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_2_gl(value):      
        if value>512:
            val = ard_map(value, 512, 1024, 0, 17)
        else:
            val = ard_map(value, 512, 0, 0, 17)
        return val
    
def IK_2_servo(ax_list):
    #convert a list of servos to degrees
    return [ax_2_deg(ax) for ax in ax_list]

def gl_2_TP(gl_angle):
    coord = IK_engine(TP)
    kin_angle = servo_2_angle_offset(gl_angle)
    e, tp = coord.angles_2_TP(kin_angle[:-1]) 
    #xt,yt, zt, g_a = tp 
    return e,tp
  
def angle_2_servo_offset(coord_ang): #adjust servo angles to match starting position
    #This is needed because the calculations for the IK engine give the angles in a different direction
    #and the starting values are different the gl graphics are set to mid point of servos
    #@todo these should unpack the angles from origin to previous axis and then apply offset
    new_angle = [0.0]*5
    new_angle[0] = (coord_ang[0]-90)%360
    new_angle[1] = (-coord_ang[1]-90)%360
    new_angle[2] = (-coord_ang[2]-180)%360
    new_angle[3] = (-coord_ang[3]-180)%360
    new_angle[4] = coord_ang[4]
    return new_angle

def servo_2_angle_offset(coord_ang): #adjust servo angles to match starting position
    #This is needed because the calculations for the IK engine give the angles in a different direction
    #and the starting values are different the gl graphics are set to mid point of servos
    new_angle = [0.0]*5
    new_angle[0] = (coord_ang[0]+90)%360
    new_angle[1] = (-coord_ang[1]-90)%360
    new_angle[2] = (-coord_ang[2]-180)%360
    new_angle[3] = (-coord_ang[3]-180)%360
    new_angle[4] = coord_ang[4]
    return new_angle
    
NAME = "SKIP"
STATUS = "Pose_Editor dialog..."