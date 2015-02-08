#!/usr/bin/env python2.7

'''
  Description: The wxCanvas for displaying the model the angles values can be
      directly converted to servo positions. 

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
import time
from wx import glcanvas
#from IK_engine import IK_engine
import numpy as np
import math as m

# The Python OpenGL package can be found at
# http://PyOpenGL.sourceforge.net/
from OpenGL.GL import * #@UnusedWildImport
from OpenGL.GLU import * #@UnusedWildImport
print GL_VERSION #7938 = OpenGL 1.1

# IMPORT OBJECT LOADER
from objloader import OBJ

class MyCanvasBase(glcanvas.GLCanvas):

    def __init__(self, parent):
        self.seg_breaks = list()
        glcanvas.GLCanvas.__init__(self, parent, -1)
        #define variables here
        #self.angle_dict = self.Parent.Parent.parent.project.poses
        self.panel = parent #this isnt panel its gl_canvas
        self.parent = self.panel.Parent
        self.frame = self.Parent.Parent.parent
        self.init = False
        self.start_time = time.time()
        
        self.context = glcanvas.GLContext(self)#added for 3.0
        
        self.angle = [180, 180, 180, 180, 0]#starting position of knobs
        self.starting_angle = list([-168.5, -162, 45, -152, 0])#[-168.5, -162, 45, -152, 0])#list([11.5,18,225,28,0])#list([11.5,108,45,28,0])

        # initial mouse position
        self.rx, self.ry = self.last_rx,self.last_ry = (0,0)
        self.tx, self.ty = self.last_tx, self.last_ty = (0,0)
        self.size = None
        self.zpos = -600
        
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
                
    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.
    
    def OnSize(self, event=None):
        wx.CallAfter(self.DoSetViewport)
        if event != None: event.Skip()

    def DoSetViewport(self):#added in v3.0
        w,h = self.size = self.GetClientSize()
        self.SetCurrent(self.context) #added for 3.0
        w = max(w, 1.0)
        h = max(h, 1.0)
        self.xScale = 180.0 / w
        self.yScale = 180.0 / h
        if self.init == True:
            glViewport(0, 0, w, h)
        self.Refresh(False)  

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()
        
    #key events
    def on_key_up(self, event):
        self.key=None
        event.Skip()
     
    def on_key_down(self, event):
        key = event.GetKeyCode()
        #print "you pressed a key", key
        if key == ord("H"):
            self.tx=0
            self.ty=0
            self.rx=0
            self.ry=0
            self.Refresh(False) 
        else:
            self.key = key
            
        event.Skip()
        
    key =None    
    #mouse events   
    def OnScroll(self, event):
        if event.GetWheelRotation() > 0:
            self.zpos += 10
        else:
            self.zpos -= 10
        self.Refresh(True)
        
    def OnLMouseDown(self, evt):
        self.SetFocus()
        self.CaptureMouse()
        self.last_rx, self.last_ry = evt.GetPosition()

    def OnLMouseUp(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse() 
            
    def OnRMouseDown(self, evt):
        self.SetFocus()
        self.CaptureMouse()
        self.last_tx, self.last_ty = evt.GetPosition()

    def OnRMouseUp(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse() 

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            i,j= evt.GetPosition()
            self.rx += i-self.last_rx
            if self.key == wx.WXK_ALT:
                self.ry += j-self.last_ry
            self.last_rx,self.last_ry= (i,j)
            self.Refresh(False)
        elif evt.Dragging() and evt.RightIsDown():
            i,j= evt.GetPosition()
            self.tx += i-self.last_tx
            self.ty -= j-self.last_ty
            self.last_tx,self.last_ty= (i,j)
            self.Refresh(False)

class GL_Canvas(MyCanvasBase):    
    def InitGL(self):
        
        self.safe_angle = list(self.angle)      #the last angle ran
        self.detect_col = True                  #collision 
        self.port_locked = False                #serial port lock
        self.project = self.frame.project       #main project

        #light 0
        glLightfv(GL_LIGHT0, GL_POSITION,  (-100, 500,  0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (.1, .1, .1, .1))
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glEnable(GL_LIGHT0)
       
        #Light 1
        glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.0, 0.0, 0.0, 1.0]) # R G B A
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  [.85, .85, .85, 1]) # R G B A
        glLightfv(GL_LIGHT1, GL_POSITION, [300, 550, 300, 0.0]) # x y z w y = height, z = distance
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glEnable(GL_LIGHT1)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded
        
        glEnable(GL_BLEND)#allow blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        #load object files after init
        
        #@todo these values should come from project?
        self.base = OBJ("base_bm.obj")
        self.shoulder = OBJ("shoulder_b.obj")
        self.bicep = OBJ("bicep_b.obj")
        self.bicep001 = OBJ("bicep001_b.obj")
        self.wrist = OBJ("wrist_wrail.obj")
        self.gripper = OBJ("gripper_b.obj")
        self.gripper001 = OBJ("gripper001_b.obj")
        self.room_T_B_B = OBJ('room_T_B.obj', swapyz=False, my_texture = True, use_mat = False)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        if self.size:
            width, height = self.size
        else: 
            print"no size"
            width, height = 800, 600
        gluPerspective(45, width/float(height), 1, 2000.0)
        
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_COLOR_MATERIAL)
    
    #object rendering done here          
    def OnDraw(self):
        #do calculations
        now = time.time()
        if now != self.start_time:
            self.Parent.Parent.label_5.SetLabel("%.2f" % (1/(now-self.start_time)))
        self.start_time = now
        rx = float(self.rx*self.xScale)
        ry = float(self.ry*self.yScale)
        tx = self.tx*self.xScale
        ty = self.ty*self.yScale
        
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        #update camera
        glTranslate(tx-80, ty-175, self.zpos)
        glRotatef(rx, 0.0, 1.0, 0.0)#x is left right, y is up down
        glRotatef(ry, 1.0, 0.0, 0.0)
        #render room
        # save start up atributes
        glCallList(self.room_T_B_B.gl_list)
        
        glRotatef(-90, 1.0, 0.0, 0.0)
        
        glEnable(GL_COLOR_MATERIAL)
        glPushAttrib(GL_CURRENT_BIT)
        glPushAttrib(GL_LIGHTING_BIT)
        set_specular(self.frame.robot_color.get_value())
        
        #render robot
        glCallList(self.base.gl_list)
        
        glPushMatrix()
        
        if self.parent.enable_limits == True:
            #lim = {'shoulder_right': 975, 'wrist_left': 837, 'base_left': 49, 'wrist_right': 171, 'elbow_right': 1016, 'base_right': 991, 'elbow_left': 51, 'shoulder_left': 105}
            axs = [deg_2_ax(a) for a in self.angle[:-1]]
            #@todo just pass gripper open as an angle so it is more consistent 
            axs.append(self.angle[4])
            #count = 0
            for ax, limit in zip(axs, self.frame.project.safety_limits):
                hi = limit[0]
                low = limit[1]
                if ax > hi or ax < low:
                    #self.angle[count]=self.safe_angle[count]
                    self.angle = list(self.safe_angle)
                    self.parent.log("safety limits exceeded")
                    break
                #count+=1
                    
        if self.parent.collision_detect == True:
            col = do_collision_chec(self.parent.spheres, self.angle)
            if col is True:
                self.angle = self.safe_angle
                self.parent.log("collision detected")
                
        self.shoulder_rot(self.angle[0]+self.starting_angle[0])#this rotates backwards
        self.bicep_rot(self.angle[1]+self.starting_angle[1])
        self.bicep001_rot(self.angle[2]+self.starting_angle[2])
        self.wrist_rot(self.angle[3]+self.starting_angle[3])
        self.gripper_mov(self.angle[4])
    
        glPopMatrix()  
        glPopAttrib() 
        glPopAttrib()
        
        self.old_as = list(self.angle)
        self.SwapBuffers()
        
        #@ todo to many if checks this work well though
        #@ todo adjust speed depending on distance 
        #     so all motors reach end position at the same time
        #@todo should this check if the ax values have changed ie 
        #    just a screen refresh or resize no change in motors
        self.live_updating = True 
        if self.parent.running_seq == False and self.port_locked == False:       
            self.set_reg()
        self.safe_angle = list(self.angle)
        
    def set_reg(self):
        if self.live_updating is not False and self.parent.button_10.GetValue() and self.parent.port:
            axs = [deg_2_ax(a) for a in self.angle[:-1]]
            axs.append(self.angle[4])
            for i, servo in enumerate(axs): 
                # @todo should this be done in safety enable?
                # why not have safties enabled all the time and just adjust settings
                # then model cant reach some positions and its not as pretty for presentation
                if servo < 1 or servo > 1023:
                    continue
                servo = int(round(servo,0))
                #setting speed could be removed
                vals = self.parent.port.getReg((i+1), 36, 2)
                if vals: 
                    if len(vals) > 1:
                        cur_pos = vals[0] + (vals[1]<<8)
                        speed = int(abs(cur_pos-axs[i])+self.parent.servo_speed)
                        if speed > 115: speed = 115
                        self.parent.port.setReg(i+1, 32, [speed%256,speed>>8])
                self.parent.port.setReg(i+1, 30, [servo%256,servo>>8])
        
    def set_reg_thread(self):
        self.port_locked = True
        while (self.parent.button_10.GetValue() and self.parent.port and 
               self.parent.running_seq is not False):
            self.set_reg()
        self.port_locked = False
        wx.CallAfter(self.parent.btn10_event)
                

    '''functions to rotate robot joints'''
    def shoulder_rot(self, a=0):   
        
        if self.parent.show_tool_path is True:      
            self.draw_line()                        #draws the tool path
                 
        glTranslate(99, 131.75, 87.4) 
        
        if self.parent.show_force_fields is True:
            glTranslate(0, 0, -((self.parent.spheres["base"].position_offset)))
            gluSphere(*self.parent.spheres["base"].get_glu())
            glTranslate(0, 0, (self.parent.spheres["base"].position_offset))
        
        glRotatef(a, 0.0, 0, 1)    
        glTranslate(-99, -131.75, -87.4)   
        glCallList(self.shoulder.gl_list)
        
    def bicep_rot(self, a=0):
        glTranslate(99, 131.75, 128.9)
        
        glRotatef(a, .98052, -0.1964, 0)
        
        if self.parent.show_force_fields is True:
            glTranslate(0, 0, ((self.parent.spheres["shoulder"].position_offset)))
            gluSphere(*self.parent.spheres["shoulder"].get_glu()) 
            glTranslate(0, 0, ((self.parent.spheres["shoulder"].position_offset)))
        
        glTranslate(-99, -131.75, -128.9) 
        glCallList(self.bicep.gl_list)

        
    def bicep001_rot(self, a=0):
        glTranslate(105.11, 162.26, 230.96)
        glRotatef(a, .98052,-0.1964, 0)
        if self.parent.show_force_fields is True:         
            gluSphere(*self.parent.spheres["elbow"].get_glu())
        glTranslate(-105.11, -162.26, -230.96) 
        glCallList(self.bicep001.gl_list)
        
    def wrist_rot(self, a=0):#86.6, 180.29, 70.3
        glTranslate(86.6, 70.3, 180.29)
        glRotatef(a, .98052,  -0.1964, 0)
        if self.parent.show_force_fields is True:
            gluSphere(*self.parent.spheres["wrist"].get_glu())  
        glTranslate(-20, -self.parent.spheres["gripper"].position, 0)
        if self.parent.show_force_fields is True:
            gluSphere(*self.parent.spheres["gripper"].get_glu())
        glTranslate(20, self.parent.spheres["gripper"].position, 0)
        glTranslate(-86.6, -70.3, -180.29)        
        glCallList(self.wrist.gl_list)
        
    def gripper_mov(self, a=0):
        a = servo_2_gl(a)#this needs adjusting grippers overlap
        glTranslate(a*.9805, a*-0.1964, 0)
        glCallList(self.gripper.gl_list)
        glTranslate(-a*1.961,  a*0.3928, 0)
        glCallList(self.gripper001.gl_list)
        
    def draw_line(self):
        # this should be called before shoulder rotate 
        # or translate must be modified
        if self.parent.line_list == None:
            return
        glPushAttrib(GL_CURRENT_BIT)
        glPushAttrib(GL_LIGHTING_BIT)
        glColor(0, 0, 1.0)
        glTranslate(99, 131.75, 128.9)          # move the line to origin
        glCallList(self.parent.line_list)       #draw the toolpath
        glTranslate(-99, -131.75, -128.9)
        glPopAttrib() 
        glPopAttrib()

def ard_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def servo_2_gl(value):      
        if value>512:
            val = ard_map(value, 512, 1024, 0, 17)
        else:
            val = ard_map(value, 512, 0, 0, 17)
        return val        
        
def set_specular(my_color):
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT)
    glColor(.2, .2, .2)
    glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
    glColor(my_color) 
    glColorMaterial(GL_FRONT_AND_BACK, GL_SPECULAR)
    glColor(.75,.75,.75)
    glColorMaterial(GL_FRONT_AND_BACK, GL_EMISSION)
    glColor(.1,.1,.1)
    glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, 128 )

#clear lighting to initial values   
def clear_specular():
    glColorMaterial(GL_FRONT, GL_SPECULAR)
    glColor(.0,.0,.0)
    glColorMaterial(GL_FRONT, GL_EMISSION)
    glColor(.0,.0,.0)
    glMaterial(GL_FRONT, GL_SHININESS, 128 )
           
'''------------------- --------------------------------------------------
    -----------------   H E L P E R   C L A S S E S   -------------------
    -------------------------------------------------------------------'''
class coordinate():  
    # x y z coordinates
    def __init__(self, x, y, z): 
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def set_coord(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def get_coord(self):
        return [self.x, self.y, self.z]
    
class sphere(): 
    # objects used to calculate collisions
    def __init__(self, position, name="", coord=[0,0,0], radius=30):
        self.coord = coordinate(*coord)
        self.quad = gluNewQuadric()
        self.radius = radius
        self.name = name
        self.slices = 32
        self.stacks = 32
        self.position = position
        self.position_offset = 0 #this is where it is drawn

    def get_glu(self):
            return self.quad, self.radius, self.slices, self.stacks

'''----------------------   H E L P E R    F U N C T I O N S   ---------------''' 
       
''' ---- the main function for testing for collisions --------'''
def do_collision_chec(spheres, gl_angles, unpack_angles=True):
    #make a copy of the angles
    angles = list(gl_angles)
    #remove the rotation and gripper
    del angles[0]
    del angles[3]
    #add base angles and tool point
    angles.insert(0, 180)
    angles.insert(0, 180)
    #condition and load the angles into the spheres
    set_spheres_coord(spheres, angles)
    #do the collision test
    col=test_spheres(spheres)
    return col
 
def pointdistance(p1,p2):
    #reurns the distance between two (x,y,z)points
    #print "p1,p2",p1,p2
    p1=p1[:3]
    p2=p2[:3]
    x,y,z = [list(a) for a in zip(p1, p2)]
    xd = x[1]-x[0]
    yd = y[1]-y[0]
    zd = z[1]-z[0]
    distance = m.sqrt((xd*xd) + (yd*yd) + (zd*zd))
    return distance
      
def simp_sphere(c1,r1,c2,r2,):
    #a test two see if two spheres are overlapping
    dist=pointdistance(c1, c2)
    if dist <= (r1+r2): return True
    else: return False 
    
def get_w_z(ws, ang): 
    #x and y of a circle on the coordinate plane
    a = np.deg2rad(ang)
    wp = (ws*np.cos(a))
    zp = (ws*np.sin(a))
    return wp,zp
 
def set_spheres_coord(spheres, angles):
    #get the x,y,z coord of the speres points
    #the - in sphere position rotates it upside from 180 so values are positive
    names = ["base", "shoulder", "elbow", "wrist", "gripper"]
    links = [-spheres[name].position for name in names]
    spheres[names[0]].coord.set_coord(0.0, 0.0, 0.0)#base
    im, rr=0, 0
    offset = 180
    last_a = 180
    for n, l, ca in zip(names, links, angles):
        #assemble point with angles relative to the origin
        adj_a = ca - offset
        a = adj_a + last_a      
        ra = m.radians(a)
        rr += l*m.cos(ra)
        im += l*m.sin(ra)
        spheres[n].coord.set_coord(0,rr,im)#x,y,z
        #print "rr, IM, angle, adj", rr, im,ca, a
        last_a = a
 
def test_spheres(spheres):
    #probably should get the sphere names from sphere class but this is ok
    names = ["base", "shoulder", "elbow", "wrist", "gripper"]
    col = False
    for name in names[2:]:
        spheres[name]
        for name2 in names:
            if name != name2:
                col = simp_sphere(spheres[name].coord.get_coord(), spheres[name].radius,
                                  spheres[name2].coord.get_coord(), spheres[name2].radius )
                if col==True:
                    print name, name2,"sphere colided dist ="
                    return col
    return col

def deg_2_ax(deg):
    return (deg-30)/ 0.29296875      
