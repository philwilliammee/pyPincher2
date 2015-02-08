#!/usr/bin/env python2.7

'''
  Description: The Editor panel contains wx events for everything
    except the robot canvas 

  PyPincher: A graphical model of phantomX pincher arm from Trossen robotics
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

import sys, time, os, wx, project
from wx.lib.masked import NumCtrl
from wx_obj_canvas import GL_Canvas, sphere
from OpenGL.GL import * #@UnusedWildImport
from OpenGL.GLU import * #@UnusedWildImport 

from driver import *
from ax12 import *
from ToolPane import *
#import numpy as np
#import math
#import wx.lib.agw.shapedbutton
from wx.lib.agw.shapedbutton import SBitmapButton, SBitmapToggleButton#,SButton, SBitmapTextToggleButton
#from operator import add, sub
from eq_dialog import eq_dialog
from posebox_dblclick_dialog import posebox_dblclick_dialog
from IK_engine import IK_engine
from knobs import *#knob_sizer, KC, knobs_helper
import thread

KNOB_COUNT = 5 
JOINT = 0
IK = 1
TP = 2
BITMAP_DIR = "resources\\"
   
class Pose_Editor(ToolPane):
    wx_id1 = wx.NewId()             #the panel ID
    
    def __init__(self, parent, port=None):  #parent = frame
        ToolPane.__init__(self, parent, port)
        #@todo give all values names with meaning or create consistent system for naming
        self.seq_timer = wx.Timer(self, wx.ID_ANY)
        self.panel_1 = wx.Panel(self, self.wx_id1)
        self.posebox = wx.ListBox(self.panel_1, wx.ID_ANY, choices=self.parent.project.poses.keys())
        self.button_1 = wx.Button(self.panel_1, wx.ID_ANY, _("Add"))
        self.button_2 = wx.Button(self.panel_1, wx.ID_ANY, _("Remove"))
        self.button_3 = wx.Button(self.panel_1, wx.ID_ANY, _("Rename"))
        self.sizer_2_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("Pose Editor"))
        
        self.radio_box_1 = wx.RadioBox(self.panel_1, wx.ID_ANY, _("Motion Options"), 
                                       choices=[_("Joint(AX)"), _("World(IK)"), _("Tool(TP)")],
                                       majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        #build the knob panels
        self.knobs_box = [[] for _x in xrange(3)]
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)
        knob_names = ["M1","M2","M3","M4", "Pincher"]
        for i in range(KNOB_COUNT):
            self.knobs_box[JOINT].append(knob_sizer(self.panel_2, i, _(knob_names[i]), JOINT))
        self.sizer_12_staticbox = wx.StaticBox(self.panel_2, wx.ID_ANY, _("JOINT_panel_2"))
          
        self.panel_3 = wx.Panel(self.panel_1, wx.ID_ANY)
        knob_names = ["A0","W","Z","Tool Angle", "Pincher"]
        for i in range(5):
            self.knobs_box[IK].append(knob_sizer(self.panel_3, i, _(knob_names[i]), IK))
        self.sizer_13_staticbox = wx.StaticBox(self.panel_3, wx.ID_ANY, _("IK_panel_3"))
        
        self.panel_4 = wx.Panel(self.panel_1, wx.ID_ANY)
        knob_names = ["X","Y","Z","Tool Angle", "Pincher"]
        for i in range(5):
            self.knobs_box[TP].append(knob_sizer(self.panel_4, i, _(knob_names[i]), TP))
            
        self.sizer_14_staticbox = wx.StaticBox(self.panel_4, wx.ID_ANY, _("TP_panel_4"))
        self.tranbox = wx.ListBox(self.panel_1, wx.ID_ANY, choices=[])
        self.label_1 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" Pose:"))
        self.tranPose = wx.ComboBox(self.panel_1, wx.ID_ANY, choices=self.parent.project.poses.keys(), style=wx.CB_DROPDOWN | wx.CB_DROPDOWN)
        self.servo_speedButton = wx.StaticText(self.panel_1, wx.ID_ANY, _(" Delta_T"))
        self.tranTime = wx.SpinCtrl(self.panel_1, wx.ID_ANY, '50', min=1, max=1024)
        self.button_21 = wx.Button(self.panel_1, wx.ID_ANY, _("Move_Up"))
        self.button_22 = wx.Button(self.panel_1, wx.ID_ANY, _("Move_Down"))
        self.button_19 = wx.Button(self.panel_1, wx.ID_ANY, _("New"))
        self.button_20 = wx.Button(self.panel_1, wx.ID_ANY, _("Delete"))
        self.label_4 = wx.StaticText(self.panel_1, wx.ID_ANY, _("FPS:"))
        self.label_5 = wx.StaticText(self.panel_1, wx.ID_ANY, _("0.0"))
        
        self.sizer_21_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("Transition Editor"))
        self.sizer_20_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("Sequence Controls"))
        self.sizer_5_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("Motor Controls")) 
        self.button_4 = wx.Button(self.panel_1, wx.ID_ANY, _("Aux_10"))
        self.toggle_relax = wx.ToggleButton(self.panel_1, wx.ID_ANY, _("Torque"))
        self.button_6 = wx.Button(self.panel_1, wx.ID_ANY, _("Capture"))
        self.button_7 = wx.Button(self.panel_1, wx.ID_ANY, _("AX_Speed"))
        self.button_8 = wx.Button(self.panel_1, wx.ID_ANY, _("Aux_8"))
        self.button_9 = wx.Button(self.panel_1, wx.ID_ANY, _("Aux_9"))
        self.button_10 = wx.ToggleButton(self.panel_1, wx.ID_ANY, _("Live"))
        self.button_11 = wx.Button(self.panel_1, wx.ID_ANY, _("Aux_7"))
        self.button_12 = wx.Button(self.panel_1, wx.ID_ANY, _("Clear"))
        self.sizer_4_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("aux functions"))
        self.seqbox = wx.ListBox(self.panel_1, wx.ID_ANY, choices=self.parent.project.sequences.keys())
        self.button_13 = wx.Button(self.panel_1, wx.ID_ANY, _("Add"))
        self.button_14 = wx.Button(self.panel_1, wx.ID_ANY, _("Remove"))
        self.button_15 = wx.Button(self.panel_1, wx.ID_ANY, _("Update"))
        self.button_16 = wx.Button(self.panel_1, wx.ID_ANY, _("EQ_editor"))
        self.button_17 = wx.Button(self.panel_1, wx.ID_ANY, _("Import_OBJ"))
        
        self.gripper_angle_label = wx.StaticText(self.panel_1, wx.ID_ANY, _("Gripper_angle: "), style=wx.ALIGN_CENTRE)
        self.gripper_angle_combo_box = wx.ComboBox(self.panel_1, wx.ID_ANY, choices=[_("auto"),
                                             _("0"), _("315"), _("270"), _("45"), _("90")], style=wx.CB_DROPDOWN)# | wx.CB_READONLY)
        self.label_6 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" Calculated_time:"))
        self.label_7 = wx.StaticText(self.panel_1, wx.ID_ANY, _("0.0"))
        self.label_8 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" Actual_Time:"))
        self.label_9 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" 0.0"))
        self.label_10 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" Distance:"))
        self.label_11 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" 0.0"))
        self.label_12 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" Iterations:"))
        self.label_13 = wx.StaticText(self.panel_1, wx.ID_ANY, _(" 0.0"))
        self.vecto_label = wx.StaticText(self.panel_1, wx.ID_ANY, _("Max Vector Length:"))
        self.vector_length = NumCtrl(self.panel_1, wx.ID_ANY, "3")
        
        self.sizer_7_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("sequences"))

        self.__set_properties()
        self.__do_layout()

        '''------------- BIND EVENTS -----------------------------------'''
        self.Bind(wx.EVT_BUTTON, self.addPose, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.remPose, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.renamePose, self.button_3)
        
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.knobs_event)#, self.knobs_box[0].knob)
        self.Bind(wx.EVT_RADIOBOX, self.radio_box_event, self.radio_box_1)
        #self.Bind(wx.EVT_BUTTON, self.setPose, self.button_4)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.relaxServo, self.toggle_relax)
        self.Bind(wx.EVT_BUTTON, self.capturePose, self.button_6)
        self.Bind(wx.EVT_BUTTON, self.set_servo_speed, self.button_7)
        self.Bind(wx.EVT_BUTTON, self.btn8_event, self.button_8)
        self.Bind(wx.EVT_BUTTON, self.btn9_event, self.button_9)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.btn10_event, self.button_10)
        self.Bind(wx.EVT_BUTTON, self.btn11_event, self.button_11)
        self.Bind(wx.EVT_BUTTON, self.btn12_event, self.button_12)
        self.Bind(wx.EVT_BUTTON, self.update_tran, self.button_15)
        self.Bind(wx.EVT_BUTTON, self.btn16_event, self.button_16)
        self.Bind(wx.EVT_BUTTON, self.btn17_event, self.button_17)
        
        self.Bind(wx.EVT_LISTBOX, self.doPose, self.posebox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.dbl_click_pose_box, self.posebox)
        
        self.Bind(wx.EVT_BUTTON,  self.addSeq, self.button_13)
        self.Bind(wx.EVT_BUTTON, self.remSeq, self.button_14)
        self.Bind(wx.EVT_BUTTON, self.moveUp, self.button_21)
        self.Bind(wx.EVT_BUTTON, self.moveDn, self.button_22)
        self.Bind(wx.EVT_BUTTON, self.addTran, self.button_19)
        self.Bind(wx.EVT_BUTTON, self.remTran, self.button_20)
        
        self.Bind(wx.EVT_LISTBOX, self.doTran, self.tranbox)
        self.Bind(wx.EVT_LISTBOX, self.doSeq, self.seqbox)
        self.Bind(wx.EVT_COMBOBOX, self.updateTran , self.tranPose)
        self.Bind(wx.EVT_SPINCTRL, self.updateTran, self.tranTime)
        self.Bind(wx.EVT_TIMER, self.on_seq_timer, self.seq_timer)
        
        self.Bind(wx.EVT_TEXT, self.on_gripper_angle, self.gripper_angle_combo_box)
        self.init_variables()
        #define variables
        # end wxGlade

    def __set_properties(self):
        w,h = wx.GetDisplaySize()
        self.panel_1.SetMinSize((w,h))
        self.radio_box_1.SetSelection(JOINT)
        self.button_10.SetBackgroundColour('RED')
        self.gripper_angle_combo_box.SetValue("0")
        self.panel_3.Hide()
        self.panel_4.Hide()
        self.canvas = GL_Canvas(self.panel_1)
    
    '''---------------------------------------------------------------------
        --------------------   L A Y O U T   -------------------------------
        -----------------------------------------------------------------'''
    def __do_layout(self):
        # @ todo rebuild this with fewer sizers
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 3, 3, 3)
        
        self.sizer_7_staticbox.Lower()
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.VERTICAL)       
        grid_sizer_24 = wx.FlexGridSizer(2, 1, 0, 0)     
        grid_sizer_3 = wx.GridSizer(1, 4, 0, 0)
        
        self.sizer_4_staticbox.Lower()
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
        grid_sizer_2 = wx.GridSizer(3, 3, 3, 3)
        
        self.sizer_5_staticbox.Lower()
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
        
        self.sizer_14_staticbox.Lower()
        sizer_14 = wx.StaticBoxSizer(self.sizer_14_staticbox, wx.HORIZONTAL)
        
        self.sizer_13_staticbox.Lower()
        sizer_13 = wx.StaticBoxSizer(self.sizer_13_staticbox, wx.HORIZONTAL)
        
        self.sizer_12_staticbox.Lower()
        sizer_12 = wx.StaticBoxSizer(self.sizer_12_staticbox, wx.HORIZONTAL)
        
        grid_sizer_4 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_18 = wx.FlexGridSizer(2, 1, 0, 0)
        self.sizer_20_staticbox.Lower()
        sizer_20 = wx.StaticBoxSizer(self.sizer_20_staticbox, wx.HORIZONTAL)
        grid_sizer_19 = wx.GridSizer(1, 4, 0, 0)
        grid_sizer_19.SetMinSize((150,50))
        self.sizer_21_staticbox.Lower()
        sizer_21 = wx.StaticBoxSizer(self.sizer_21_staticbox, wx.HORIZONTAL)
        grid_sizer_20 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_sizer_21 = wx.GridSizer(1, 2, 0, 0)
        sizer_22 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_22 = wx.FlexGridSizer(9, 2, 0, 0)
        sizer_24 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_23 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizer_2_staticbox.Lower()
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        
        #sequence
        grid_sizer_13 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_sizer_14 = wx.GridSizer(1, 3, 0, 0)
        
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        self.canvas.SetSizer(sizer_18)
        grid_sizer_1.Add(self.canvas, 1, wx.EXPAND, 0)
        
        grid_sizer_13.Add(self.posebox, 1, wx.EXPAND | wx.ALIGN_RIGHT, 0)
        grid_sizer_14.Add(self.button_1, 0, wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM, 2)
        grid_sizer_14.Add(self.button_2, 0, wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM, 2)
        grid_sizer_14.Add(self.button_3, 0, wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM, 2)
        grid_sizer_13.Add(grid_sizer_14, 0, wx.EXPAND, 0)
        grid_sizer_13.AddGrowableRow(0)
        sizer_2.Add(grid_sizer_13, 2, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        
        sizer_3.Add(self.label_4, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 3)
        sizer_3.Add(self.label_5, 0,  wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 3)
        grid_sizer_4.Add(sizer_3, 1, wx.EXPAND, 0)
        grid_sizer_4.Add(self.radio_box_1, 0, wx.TOP | wx.ALIGN_BOTTOM, 10)
        sizer_5.Add(grid_sizer_4, 0, wx.EXPAND, 0)
        
        grid_sizer_20.Add(self.tranbox, 0, wx.EXPAND, 0)
        sizer_23.Add(self.label_1, 0, wx.ALIGN_BOTTOM, 0)
        
        sizer_23.Add(self.tranPose, 1, wx.ALIGN_BOTTOM, 0)
        sizer_22.Add(sizer_23, 1, wx.EXPAND, 0)
        sizer_24.Add(self.servo_speedButton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_24.Add(self.tranTime, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_22.Add(sizer_24, 1, wx.EXPAND, 0)
        grid_sizer_22.Add(self.button_21, 0, wx.ALL, 2)#move up
        grid_sizer_22.Add(self.button_22, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.button_15, 0, wx.ALL, 2)#eqeditor
        grid_sizer_22.Add(self.button_16, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.button_17, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add((20, 20), 0, wx.EXPAND, 0)#move down
        
        grid_sizer_22.Add(self.gripper_angle_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 2)#move down
        grid_sizer_22.Add(self.gripper_angle_combo_box, 0, wx.ALL, 2)#move down        
        
        grid_sizer_22.Add(self.label_6, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.label_7, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 2)#move down
        grid_sizer_22.Add(self.label_8, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.label_9, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 2)#move down
        grid_sizer_22.Add(self.label_10, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.label_11, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 2)#move down
        grid_sizer_22.Add(self.label_12, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.label_13, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 2)#move down
        grid_sizer_22.Add(self.vecto_label, 0, wx.ALL, 2)#move down
        grid_sizer_22.Add(self.vector_length, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 2)#move down

        sizer_22.Add(grid_sizer_22, 0, wx.EXPAND, 0)
        sizer_22.Add((20, 20), 0, wx.EXPAND, 0)
        sizer_22.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_20.Add(sizer_22, 1, wx.EXPAND, 0)
        grid_sizer_21.Add(self.button_19, 0, wx.ALL, 2)
        grid_sizer_21.Add(self.button_20, 0, wx.ALL, 2)
        grid_sizer_20.Add(grid_sizer_21, 1, wx.EXPAND, 0)
        grid_sizer_20.Add((20, 20), 0, 0, 0)
        
        grid_sizer_20.AddGrowableRow(0)
        sizer_21.Add(grid_sizer_20, 1, wx.EXPAND, 0)
        grid_sizer_18.Add(sizer_21, 1, wx.EXPAND, 0)
        
        #grid_sizer_19.Add((5, 20),  1, wx.EXPAND, 0)
        self.build_shapped_btns(grid_sizer_19)
        sizer_20.Add(grid_sizer_19, 1, wx.EXPAND, 0)
        grid_sizer_18.Add(sizer_20, 1, wx.EXPAND, 0)
        grid_sizer_18.AddGrowableRow(0)
        sizer_19.Add(grid_sizer_18, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_19, 1, wx.EXPAND, 0)
        #end of sequence
        
        sizer_5.Add((5, 5), 0, 0, 0)
        #add knobsizers to motor control sizer
        for knob in self.knobs_box[JOINT]:
            sizer_12.Add(knob.box_sizer, 1, wx.EXPAND, 0)
        self.panel_2.SetSizer(sizer_12)
        sizer_5.Add(self.panel_2, 1, wx.EXPAND, 0)
        
        for knob in self.knobs_box[IK]:
            sizer_13.Add(knob.box_sizer, 1, wx.EXPAND, 0)
        self.panel_3.SetSizer(sizer_13)
        sizer_5.Add(self.panel_3, 1, wx.EXPAND, 0)
        
        for knob in self.knobs_box[TP]:
            sizer_14.Add(knob.box_sizer, 1, wx.EXPAND, 0)
        self.panel_4.SetSizer(sizer_14)
        sizer_5.Add(self.panel_4, 1, wx.EXPAND, 0)
        
        sizer_5.Add((5, 5), 0, 0, 0)
        
        grid_sizer_1.Add(sizer_5, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.button_10, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.toggle_relax, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.button_6, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.button_7, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.button_11, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.button_12, 0, wx.ALL | wx.EXPAND, 1)
        
        grid_sizer_2.Add(self.button_8, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.button_9, 0, wx.ALL | wx.EXPAND, 1)
        grid_sizer_2.Add(self.button_4, 0, wx.ALL | wx.EXPAND, 1)
        
        sizer_4.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_4, 1, wx.EXPAND, 0)

        #sequence
        grid_sizer_24.Add(self.seqbox, 0, wx.EXPAND, 0)
        grid_sizer_24.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        grid_sizer_24.AddGrowableRow(0)
        #grid_sizer_24.AddGrowableRow(1)
        #grid_sizer_24.AddGrowableCol(0)
        sizer_7.Add(grid_sizer_24, 1, wx.EXPAND, 0)
        grid_sizer_3.Add((20, 20), 0, 0, 0)
        grid_sizer_3.Add(self.button_13, 0, wx.ALL, 2)
        grid_sizer_3.Add(self.button_14, 0, wx.ALL, 2)
        grid_sizer_3.Add((20, 20), 0, 0, 0)
        
        grid_sizer_1.Add(sizer_7, 1, wx.EXPAND, 0)
        #end sequence
        self.panel_1.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(0) #caused resize bug
        grid_sizer_1.AddGrowableCol(0)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 10)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.panel_1.Layout()
        # end wxGlade
        
    '''-----------------------------------------------------------------------
        -----------------   S H A P E D   B U T T O N S    -------------------
        -------------------------------------------------------------------'''
    def build_shapped_btns(self, sizer):   
        size = (48,48)
        # The Play Button Is A Toggle Bitmap Button (SBitmapToggleButton)
        upbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "play.png"), wx.BITMAP_TYPE_PNG)
        disbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "playdisabled.png"), wx.BITMAP_TYPE_PNG)
        self.play = SBitmapToggleButton(self.panel_1, 0, upbmp, size)
        self.play.SetUseFocusIndicator(False)
        self.play.SetBitmapDisabled(disbmp)
        self.Bind(wx.EVT_BUTTON, self.OnPlay, self.play)             
        sizer.Add(self.play, 0, wx.EXPAND, 0)
        
        # The Pause Button Is A Toggle Bitmap Button (SBitmapToggleButton)
        upbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "pause.png"), wx.BITMAP_TYPE_PNG)
        disbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "pausedisabled.png"), wx.BITMAP_TYPE_PNG)
        self.pause = SBitmapToggleButton(self.panel_1, -1, upbmp, size)
        self.pause.SetUseFocusIndicator(False)
        self.pause.SetBitmapDisabled(disbmp)
        self.pause.Enable(False)
        sizer.Add(self.pause, 0,wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.OnPause, self.pause)

        # The Stop Button Is A Simple Bitmap Button (SBitmapButton)
        upbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "stop.png"), wx.BITMAP_TYPE_PNG)
        disbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "stopdisabled.png"), wx.BITMAP_TYPE_PNG)
        self.stop = SBitmapButton(self.panel_1, -1, upbmp, size)
        self.stop.SetUseFocusIndicator(False)
        self.stop.SetBitmapDisabled(disbmp)
        self.stop.Enable(False)
        sizer.Add(self.stop, 0,wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop) 
                
        # The FFWD Button Is A Simple Bitmap Button (SBitmapButton)
        upbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "ffwd.png"), wx.BITMAP_TYPE_PNG)
        disbmp = wx.Bitmap(os.path.join(BITMAP_DIR, "ffwddisabled.png"), wx.BITMAP_TYPE_PNG)
        self.ffwd = SBitmapButton(self.panel_1, -1, upbmp, size)
        self.ffwd.SetUseFocusIndicator(False)
        self.ffwd.SetBitmapDisabled(disbmp)
        sizer.Add(self.ffwd,0, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.OnFFWD, self.ffwd) 
        
    '''-----------------------------------------------------------------------
        -------------   I N I T I A L I Z E   V A R I A B L E S --------------
        -------------------------------------------------------------------'''
    def init_variables(self):
        self.curpose = ""                           #the name of the pose being edited
        self.curseq = ""                            #the current sequence from a list in seqbox
        self.curtran = -1                           #current transition
        self.tranTime_list = []
        self.collision_detect = False               #updated by frame collision detect enable
        self.show_force_fields=False                #canvas display force fields
        self.show_tool_path = False                 #canvas show tool path
        #@todo add a button for this
        #self.iteration_dist = 3                 #the number of vector iterations in mm steps virtual robot
        self.xs, self.ys, self.zs = [], [], []      #an array of x,y,z values to draw tool path
        self.line_list = None                       #a gl list to draw the tool path
        #@todo this keys and limits should be saved to project
        self.pose_key = 1                            #a unique value for poses
        self.seq_key = 1
        #@todo this should be updated by frame
        #self.limits = self.parent.project.safety_limits
        
        self.file = str(self.parent.filename)       #saved file location 
        self.dir = str(self.parent.dirname)         #saved path
        self.loop = False                           #continous sequence
        self.running_seq = False                    #continous run thread enabler
        
        for box in self.knobs_box:                  #disable the knobs until a pose is selcted
            for widget in box:
                widget.knob.Disable()
                
        #an array of knobs
        self.knobs = [knobs_helper(i, box) for i,box in enumerate(self.knobs_box )]
        
        #@delta t needs to be fixed speed needs to be sent to ports as soon as they open
        #self.iteration_interval = 31
        self.servo_speed = 50                       #set max speeds for all servos this should be calculated!!
        self.saveReq = False
        #self.live = self.parent.live.IsChecked()
        #self.live = False
        self.style = JOINT                          #starting style of knobs
        #@todo put this value in gripper angle box at start its blank now
        self.seq_gripper_angle = 0
        self.enable_limits = False                  #safety limits are off at start
        
        #make some spheres for collision detection
        sphere_names = ["base", "shoulder", "elbow", "wrist", "gripper"]
        #these are link lengths + a offset position for base
        #@todo the drawn sphere may not match these positions need to verify and these should be retrieved from project
        sphere_pos = [0, 105, 105, 105, 95]
        self.spheres = {}                           #a dictionary of spheres
        for pos, name in zip(sphere_pos, sphere_names ):
            self.spheres[name] = sphere( position=pos, name=name)
            gluQuadricNormals(self.spheres[name].quad, GLU_SMOOTH) # // Create Smooth Normals
        self.spheres["base"].position_offset =75   #zero position for link calculations and canvas    

    '''-------------------  UPDATE CANVAS and save angles ---------------------'''      
    def IK_2_canvas(self, angles):
        self.canvas.angle = list(angles)            #make a copy of the angles
        self.canvas.Refresh(False)                  #Render object with new angles

    '''-------------------------------------------------------------------------
        -------------   E V E N T S    S T A R T   -----------------------------
        ---------------------------------------------------------------------'''
    #@todo call events directly this comes with naming conventions        
    def addTran(self, e=None):       
        """ create a new transtion in this sequence. """
        if self.curseq != "":
            if self.curtran != -1:
                self.tranbox.Insert("none,"+str(self.tranTime.GetValue()),self.curtran+1)
            else:
                self.tranbox.Append("none,"+str(self.tranTime.GetValue()))
            self.parent.project.save = True

    def knobs_event(self, event=None):  # wxGlade: MyFrame.<event_handler>
        self.knobs[self.style].update_text()  
        self.updatePose(event)
        event.Skip()

    def btn8_event(self, event):  # wxGlade: MyFrame.<event_handler>
        print "Event handler 'btn8_event' not implemented!"
        event.Skip()

    def btn9_event(self, event):  # wxGlade: MyFrame.<event_handler>
        print "Event handler 'btn9_event' not implemented!"
        event.Skip()

    def btn10_event(self, event=None):  # wxGlade: MyFrame.<event_handler>
        if self.button_10.GetValue():
            if self.port:
                self.button_10.SetBackgroundColour('GREEN')
                # a new thread should only be started by a sequence otherwise to hard on CPU
                self.log( "live enabled")
            else: 
                self.log("Configure a COM port")
                self.button_10.SetValue(False)   
        else:
            self.button_10.SetBackgroundColour('RED')
            self.log( "live disabled")


    def btn11_event(self, event):  # wxGlade: MyFrame.<event_handler>
        """ Adjust iteration interval  """
        '''
        dlg = wx.TextEntryDialog(self,'Enter time in mS:', 'Adjust Iteration interval')
        dlg.SetValue(str(self.iteration_interval))
        if dlg.ShowModal() == wx.ID_OK:
            self.iteration_interval = int(dlg.GetValue())
        dlg.Destroy()
        '''
        print "Aux 7 not implemented"
        event.Skip()

    def btn12_event(self, event):  # wxGlade: MyFrame.<event_handler>
        dialog = wx.MessageDialog(self, "Do you really want to DELETE all poses?", caption="Clear Poses?", style=wx.OK|wx.CANCEL|wx.CENTRE)
        if dialog.ShowModal()==wx.ID_OK:
            self.tranbox.Clear()
            self.posebox.Clear()
            #clear the poses
            self.parent.project.poses.clear()
            self.update_tran()
            self.counter = 0
        event.Skip()

    def update_tran(self, event=None):  # wxGlade: MyFrame.<event_handler>
        #updates the tranpose box with new poses
        self.tranPose.Clear()
        self.tranPose.AppendItems(self.parent.project.poses.keys())
    
    def btn16_event(self, event):  # wxGlade: MyFrame.<event_handler>
        #equation editor
        #@todo deal with errors and constants needs more testing
    
        dlg = eq_dialog(self, wx.ID_ANY, "Equation Editor")      
        if dlg.ShowModal() == wx.ID_OK:   
           
            print "returned from dialog"
            try:
                error, gl_angles = self.real_TP_2_gl_angle(self.xs,self.ys,self.zs, g_a=self.seq_gripper_angle)
                self.save_glangles_2_proj(gl_angles, True)
            except Exception as e:
                self.log("Equation error: "+str(e))
                print e
            
        dlg.Destroy()
            
    def btn17_event(self, event):  # wxGlade: MyFrame.<event_handler>    
        #@todo keytags need testing
        vertices = []
        
        """ Loads a object file """ 
        dlg = wx.FileDialog(self, "Choose a file", self.dir, "", "Object files (*.obj; *.OBJ)|*.obj;*.OBJ|" \
         "All files (*.*)|*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.file = dlg.GetPath()
            self.dir = dlg.GetDirectory()       
            dlg.Destroy()
            self.parent.sb.SetStatusText('opened ' + self.file)

        for line in open(self.file, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                vertices.append(v)
        rvertices = reversed(vertices)
        xs, ys, zs=[], [], []  
        for v in rvertices:
            xs.append(v[0])
            ys.append(v[1])
            zs.append(v[2])

        error, myangles = self.real_TP_2_gl_angle(xs,ys,zs)   
        self.save_glangles_2_proj(myangles, True)

        event.Skip()
        
    def radio_box_event(self, event):  # wxGlade: MyFrame.<event_handler>
        style_select = self.radio_box_1.GetSelection()
        if style_select == JOINT:  
            self.panel_3.Hide()
            self.panel_4.Hide()
            self.panel_2.Show(True) 
            self.panel_1.Layout()
        
        if style_select == IK:
            self.panel_2.Hide()
            self.panel_4.Hide()
            self.panel_3.Show(True)
            self.panel_1.Layout()
            
        if style_select == TP: 
            self.panel_2.Hide()
            self.panel_3.Hide()
            self.panel_4.Show(True) 
            self.panel_1.Layout()
            
        self.style = style_select
        self.loadPose(self.curpose, True)
        event.Skip()
    
    def on_gripper_angle(self, event):
        val = self.gripper_angle_combo_box.GetValue()
        if val != "": self.seq_gripper_angle = int(val)
        else: self.seq_gripper_angle = 0    
        print "combo box val =",self.gripper_angle_combo_box.GetValue()
        event.Skip()
    
    def save_glangles_2_proj(self, gl_angles, do_tran = False):
        for i, angles in enumerate(gl_angles):
            pose_name = str(i)+"_key"+str(self.pose_key)
            self.posebox.Append(pose_name)
            self.pose_key +=1
            ax = [deg_2_ax(a) for a in angles]
            self.parent.project.poses[pose_name] = project.pose("",self.parent.project.count)
            #save the values to project
            for j in range(self.parent.project.count):
                self.parent.project.poses[pose_name][j]= ax[j]
            
            if do_tran == True:
                #update transition listbox
                self.tranbox.Append(pose_name +","+str(self.tranTime.GetValue()),self.curtran+1)
                self.seq_key+=1
                
    def OnPlay(self, event):
        if not event.GetIsDown():
            self.log( "Running....")
            #self.eventtext.SetLabel(str(BITMAP_DIR ))
            self.play.SetToggle(True)
            return
        self.loop=False
        self.log("We Started To run")

        self.stop.Enable(True)
        self.pause.Enable(True)
        self.play.SetToggle(False)
        self.pause.SetToggle(False)
        self.ffwd.Enable(False)  
        self.runSeq(event)      


    def OnPause(self, event):

        if event.GetIsDown():
            self.log("Pausing run sequence...")
        else:
            self.log("Playing After A Pause...")
        self.play.Enable(True)    
        self.haltSeq()           

    def OnStop(self, event=None):

        self.log("Everything Stopped")
        self.counter =0
        self.stop.Enable(False)
        self.pause.Enable(False)
        self.ffwd.Enable(True)
        self.play.Enable(True)
        self.play.SetToggle(False)
        self.pause.SetToggle(False)
        #self.canvas.line.clear()
        self.start_list[:] = []
        self.seq_list[:]=[]

        self.haltSeq() 

    def OnFFWD(self, event):
        if not event.GetIsDown():
            self.log( "Playing....")
            self.play.SetToggle(True)
            return
        self.loop=True
        self.log("Started Play Sequence...")

        self.stop.Enable(True)
        self.pause.Enable(True)
        self.play.SetToggle(False)
        self.pause.SetToggle(False)
        self.play.Enable(False)  
        self.runSeq(event) 
        
    def save(self):            
        if self.curseq != "":
            self.parent.project.sequences[self.curseq] = project.sequence()
            for i in range(self.tranbox.GetCount()):
                self.parent.project.sequences[self.curseq].append(self.tranbox.GetString(i).replace(",","|"))               
            self.parent.project.save = True

    '''  -------------------------------------------------------------
         ------   S T A R T   E  D I T O R   F U N C T I O N S   -----
         -------------------------------------------------------------'''  
    def dbl_click_pose_box(self, event):
        cur_pos = event.GetString()
        print "youjust doubleclicked", cur_pos
        print self.parent.project.poses[cur_pos]
        self.junk = self.parent.project.poses[cur_pos]
        dlg = posebox_dblclick_dialog(self, wx.ID_ANY, "Pose_Editor_DBL_click")      
        if dlg.ShowModal() == wx.ID_OK:   
            floats = map(float, dlg.panel_1.get_values())
            self.parent.project.poses[cur_pos] = floats        
            self.loadPose(str(cur_pos))   
        dlg.Destroy()
        
    # Pose Manipulation
    def updatePose(self, e=None):
        """ Save updates to a pose, do live update if neeeded. """
        if self.curpose != "":          
            error, servo_angles = self.knobs[self.style].get_servo_angles()#value with offset
            #print servo_angles, "adjusted servo angles are"
            if error is not True:
                #convert to ax values
                axs = [deg_2_ax(d) for d in servo_angles[:-1]]+[servo_angles[4]]
                self.IK_2_canvas(servo_angles)
                
                for i in range(self.parent.project.count):
                    #add the start position knobs calculate offsets
                    #this gave a key error 
                    self.parent.project.poses[self.curpose][i] = axs[i]#round
                    
                self.parent.project.save = True

    def relaxServo(self, e=None):
        """ Relax or enable a servo. """
        if self.port and (self.running_seq == False):
            for i in range(5):
                if self.toggle_relax.GetValue():#start Relaxed 
                    #relax them
                    self.port.setReg(i+1, P_TORQUE_ENABLE, [0])
                    self.log("Servos Torque Disabled")
                else:   
                    self.port.setReg(i+1, P_TORQUE_ENABLE, [1])
                    self.log("Servos Torque Enabled")
        else:
            self.toggle_relax.SetValue(False)
            self.log("no port open")
         
    #click item in the posebox event
    def loadPose(self, posename, flag=False):
        if self.curpose=="" and flag==True:
            return
        elif self.curpose == "":   # if we haven't yet, enable servo editors   
            for box in self.knobs_box:
                for widget in box:
                    widget.knob.Enable()#disable the KNOBS
            
        self.curpose = posename
        #load the pose
        ax_list = self.parent.project.poses[self.curpose]   

        #convert axs to gl canvas degrees     
        gl_ang = [ax_2_deg(ax) for ax in ax_list[:-1]]+[ax_list[4]]      
        error, knob_val = self.knobs[self.style].angle_2_knob(gl_ang)

        if error is not True:      
            #update knobs before drawing canvas
            error = self.knobs[self.style].set_values(knob_val)     
            #draw it
            self.updatePose()
            self.parent.sb.SetStatusText(('now editing pose: ' + self.curpose),0)
            
        else:
            self.log("load error: ax values are out of limits")
                      
        self.parent.project.save = True

    def doPose(self, e=None):
        """ Load a pose into the slider boxes. """
        #print "listbox selected do pose", e.GetString()
        if e.IsSelection():
            self.loadPose(str(e.GetString()))

    def capturePose(self, e=None):  
        """ Downloads the current pose from the robot to the GUI. """
        if self.port != None: 
            if self.curpose != "":  
                # this feels like a hack set style to JOINT update the pose 
                # then set it back to what it was and and reload it, works fine
                my_style = self.style 
                self.style = JOINT
                self.loadPose(self.curpose, True)
                errors = "could not read servos: "
                errCount = 0.0
                dlg = wx.ProgressDialog("capturing pose","this may take a few seconds, please wait...",self.parent.project.count + 1)
                dlg.Update(1)
                my_val =[]
                for servo in range(self.parent.project.count):
                    pos = self.port.getReg(servo+1,P_PRESENT_POSITION_L, 2)
                    if pos != -1 and len(pos) > 1:
                        my_val.append(pos[0] + (pos[1]<<8))
                    else: 
                        errors = errors + str(servo+1) + ", "
                        errCount = errCount + 1.0

                if errors != "could not read servos: ":
                    self.log(str(errors[0:-2]))   
                    # if we are failing a lot, raise the timeout
                    if errCount/self.parent.project.count > 0.1 and self.parent.port.ser.timeout < 10:
                        self.parent.port.ser.timeout = self.parent.port.ser.timeout * 2.0   
                else:
                    self.log("captured pose!"+str(my_val))
                    
                dlg.Destroy()
                self.knobs[self.style].set_values(my_val)
                self.knobs[self.style].update_text()   
                self.updatePose()
                self.style = my_style
                self.loadPose(self.curpose, True)
                
                self.parent.project.save = True
            else:
                self.log("please select a pose")
        else:
            self.log("no port open")

    '''
    def setPose(self, e=None):
        """ Write a pose out to the robot. """
        
        if self.port != None:
            if self.curpose != "":
                self.set_pos = True
                self.canvas.Refresh(True)
                self.canvas.OnSize()

                self.button_10.SetValue(False)
            else:
                self.log("please select a pose")
        else:
            self.log("no port open")
    '''

    def addPose(self, e=None):
        """ Add a new pose. """
        if self.parent.project.name != "":
            dlg = wx.TextEntryDialog(self,'Pose Name:', 'New Pose Settings')
            dlg.SetValue("")
            if dlg.ShowModal() == wx.ID_OK:
                self.posebox.Append(dlg.GetValue()) 
                self.parent.project.poses[dlg.GetValue()] = project.pose("",self.parent.project.count)
                dlg.Destroy()
            self.parent.project.save = True
        else:
            dlg = wx.MessageDialog(self, 'Please create a new robot first.', 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
    

    def renamePose(self, e=None):
        """ Rename a pose. """
        if self.curpose != "":
            dlg = wx.TextEntryDialog(self,'Name of pose:', 'Rename Pose')
            dlg.SetValue(self.curpose)
            if dlg.ShowModal() == wx.ID_OK:
                # rename in project data
                newName = dlg.GetValue()
                self.parent.project.poses[newName] = self.parent.project.poses[self.curpose]
                del self.parent.project.poses[self.curpose] 
                v = self.posebox.FindString(self.curpose)
                self.posebox.Delete(v)
                self.posebox.Insert(newName,v)
                self.posebox.SetSelection(v)
                self.curpose = newName
                self.parent.project.save = True

    def remPose(self, e=None):
        """ Remove a pose. """
        #print "rem pose", self.curpose
        if self.curpose != "":
            dlg = wx.MessageDialog(self, 'Are you sure you want to delete this pose?', 'Confirm', wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_OK:
                v = self.posebox.FindString(self.curpose)
                del self.parent.project.poses[self.curpose]
                self.posebox.Delete(v)
                self.curpose = ""
                #there is no pose  so disable the knobs
                for box in self.knobs_box:
                    for widget in box:
                        widget.knob.Enable()#disable the KNOBS
            dlg.Destroy()
            self.parent.sb.SetStatusText("please create or select a pose to edit...",0)
            self.parent.project.save = True  
         
    def set_servo_speed(self, e=None):
        """ Adjust servo_speed variable """
        dlg = wx.TextEntryDialog(self,'Enter time in mS:', 'Adjust Interpolation time')
        dlg.SetValue(str(self.servo_speed))
        if dlg.ShowModal() == wx.ID_OK:
            #print "Adjusting delta-T:" + str(dlg.GetValue())
            self.servo_speed = int(dlg.GetValue())
            if self.port and self.running_seq is False:
                for servo in range(5):      
                    self.port.setReg(servo+1, P_GOAL_SPEED_L, [self.servo_speed%256, self.servo_speed>>8])     
        dlg.Destroy()

    def portUpdated(self):
        """ Adjust delta-T button """
        print "updating port what got me here"
        if self.port != None and self.port.hasInterpolation == True:        
            self.button_10.Enable()
            for servo in range(5):
                self.port.setReg(servo+1, P_GOAL_SPEED_L, [self.servo_speed%256, self.servo_speed>>8])
        else:
            #@todo this should take care of port open check it can now be removed
            #button can not be enabled unless there is a port open
            self.button_10.Disable()
    

    ###########################################################################
    # Sequence Manipulation
    def doSeq(self, e=None):
        """ save previous sequence changes, load a sequence into the editor. """
        print "do seq"
        if e.IsSelection():
            self.save()            
            self.curseq = str(e.GetString())
            self.curtran = -1
            for i in range(self.tranbox.GetCount()):
                self.tranbox.Delete(0)      # TODO: There has got to be a better way to do this??
            for transition in self.parent.project.sequences[self.curseq]:
                self.tranbox.Append(transition.replace("|",","))
            self.tranPose.SetValue("")
            self.tranTime.SetValue(50)
            self.parent.sb.SetStatusText('now editing sequence: ' + self.curseq)
        else:
            print "no selection"
            
    def addSeq(self, e=None):       
        """ create a new sequence. """
        print "adding sequence"
        if self.parent.project.name != "":
            dlg = wx.TextEntryDialog(self,'Sequence Name:', 'New Sequence Settings')
            dlg.SetValue("")
            if dlg.ShowModal() == wx.ID_OK:
                self.seqbox.Append(dlg.GetValue())
                self.parent.project.sequences[dlg.GetValue()] = project.sequence("")
                dlg.Destroy()
                self.parent.project.save = True
        else:
            dlg = wx.MessageDialog(self, 'Please create a new robot first.', 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            
    def remSeq(self, e=None):
        """ remove a sequence. """
        print "remove sequence"
        if self.curseq != "":
            dlg = wx.MessageDialog(self, 'Are you sure you want to delete this sequence?', 'Confirm', wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_OK:
                # this order is VERY important!
                v = self.seqbox.FindString(self.curseq)
                del self.parent.project.sequences[self.curseq]
                self.seqbox.Delete(v)
                self.curseq = ""
                dlg.Destroy()
                self.parent.project.save = True

    ###########################################################################
    # Transition Manipulation
    def doTran(self, e=None):
        """ load a transition into the editor. """
        if e.IsSelection():
            if self.curseq != "":
                self.curtran = e.GetInt()
                v = str(e.GetString())   
                print "do tran",v
                self.tranPose.SetValue(v[0:v.find(",")])
                self.tranTime.SetValue(int(v[v.find(",")+1:]))
                self.parent.project.save = True 
    
    def remTran(self, e=None):
        """ remove a sequence. """
        if self.curseq != "" and self.curtran != -1:
            dlg = wx.MessageDialog(self, 'Are you sure you want to delete this transition?', 'Confirm', wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_OK:
                self.tranbox.Delete(self.curtran)
                self.curtran = -1
                self.tranPose.SetValue("")
                self.tranTime.SetValue(50)
                dlg.Destroy()
                self.parent.project.save = True

    def moveUp(self, e=None):
        if self.curtran > 0:
            self.tranbox.Delete(self.curtran)
            self.curtran = self.curtran - 1
            self.tranbox.Insert(self.tranPose.GetValue() + "," + str(self.tranTime.GetValue()), self.curtran)
            self.tranbox.SetSelection(self.curtran)
            self.parent.project.save = True
    
    def moveDn(self, e=None):
        if self.curtran < self.tranbox.GetCount()-1:
            self.tranbox.Delete(self.curtran)
            self.curtran = self.curtran + 1
            self.tranbox.Insert(self.tranPose.GetValue() + "," + str(self.tranTime.GetValue()), self.curtran)   
            self.tranbox.SetSelection(self.curtran)
            self.parent.project.save = True
    
    def updateTran(self, e=None):
        #upate the combo box
        if self.curtran != -1:
            self.tranbox.Delete(self.curtran)
            self.tranbox.Insert(self.tranPose.GetValue() + "," + str(self.tranTime.GetValue()), self.curtran)
            print "Updated: " + self.tranPose.GetValue() + "," + str(self.tranTime.GetValue()), self.curtran
            self.tranbox.SetSelection(self.curtran)
            self.parent.project.save = True 
        else:
            print "curtran is !=-1" 

    def runSeq(self, e=None):
        """ download poses, seqeunce, and send. """
        self.save() # save sequence 
        if self.curseq != "" and len(self.tranbox.GetItems()) != 0:    
            items = self.tranbox.GetItems()
            start_seq_list = [items[0]]
            
            if self.counter ==0:
                #@todo would it make more sense to do this after equation is calculated event?
                start_seq = run_sequence(self, start_seq_list,
                                  self.parent.project.poses,
                                  start_pos=self.canvas.angle,
                                  loop=self.loop, iter=float(self.vector_length.GetValue())) 
                self.start_list = start_seq.get_seq() 
            
            run_seq = run_sequence(self, self.tranbox.GetItems(),
                              self.parent.project.poses,
                              loop=self.loop, iter=float(self.vector_length.GetValue()))
            
            #self.canvas.line.clear()
            tp = run_seq.get_line_points()
            #@todo have to calculate frame rate 1mm/s?
            #number of steps /2 at 30fps /4 at 60fpa
            self.line_list = build_tool_path(tp)
            #self.canvas.line.xs = tp[0]
            #self.canvas.line.ys = tp[1]
            #self.canvas.line.zs = tp[2]
            
            self.seq_list = run_seq.get_seq()
            self.tranTime_list = run_seq.tran_time_list
            self.label_7.SetLabel(str(round(len(self.seq_list)/30.0,2))+"s")
            self.label_11.SetLabel(str(round((run_seq.total_dist),1))+"mm")
            self.label_13.SetLabel(str(round(len(self.seq_list),1)))
            self.running_seq = True
            thread.start_new_thread(self.canvas.set_reg_thread, ())
            # TODO should this be a one shot timer?
            self.seq_timer.Start(int(self.tranTime_list[0]))

        else:
            self.log("Select a Sequence")
            

    def on_seq_timer(self, e=None):
        #draw the current sequence
        if self.start_list:
            self.IK_2_canvas(self.start_list.pop(0))
        elif self.seq_list:#need to find a beter way to do this without a counter
            self.IK_2_canvas(self.seq_list[self.counter])
            if self.tranTime_list[self.counter] != self.old_tranTime:
                self.seq_timer.Start(int(self.tranTime_list[self.counter]))
            self.old_tranTime = self.tranTime_list[self.counter]
            self.counter = (self.counter+1)%len(self.seq_list)
            if self.loop is True: pass
            elif self.counter ==1: self.seq_start_time = time.time() 
            elif self.counter == 0: 
                self.label_9.SetLabel("%.2fs" %(time.time()-self.seq_start_time))
                self.OnStop()            
        else:
            self.log("error try moving robot to a safe position")
    
    seq_start_time = time.time()
    seq_list = []   
    start_list=[]
    old_tranTime = 50
    counter = 0
    
    def log(self, text):
        self.parent.sb.SetBackgroundColour('RED')
        self.parent.sb.SetStatusText(text,0) 
        self.parent.timer.Start(20)    
    
    def haltSeq(self, e=None):
        """ send halt message ("H") """ 
        #kill sequence
        self.seq_timer.Stop()
        self.running_seq = False
        
        if self.port != None:
            self.log("Halt sequence...")
            self.port.ser.write("H")
        else:
            self.log("no port open")
    
    ##########################################################################
    
    #real means angles are relative to the base origin    
    def real_TP_2_gl_angle(self, xs, ys, zs, g_a=0, griper=70):
        myangles=[]
        converter = IK_engine(TP)
        val=[]
        e=[]
        #create sequence
        count=0
        for x,y,z in zip(xs,ys,zs):
            error, v = converter.calc_positions(x,y,z, g_a, style=TP)
            if error is not True:
                v.append(griper)
                val.append(angle_2_servo_offset(v))
                myangles.append(angle_2_servo_offset(v))
                #print "calc good tool point",x,y,z
            else:
                self.log( "error in "+str(v)+' at '+str(count))
                e.append(count)
            count +=1
        return e, val
    
def build_tool_path(coord):   
    #build a tool path list
    xs, ys, zs = coord 
    gl_list = glGenLists(1)
    glNewList(gl_list, GL_COMPILE)
    #vertices = np.arange(len(coord))#create some vertices can be removed later
    glBegin(GL_LINES)
    for i in range(len(xs)-1):
        glVertex3f(xs[i], ys[i], zs[i])
        glVertex3f(xs[i+1], ys[i+1], zs[i+1])
    glEnd()
        
    glDisable(GL_TEXTURE_2D)
    glEndList() 
    return gl_list   
 
NAME = "Pose_Editor"
STATUS = "opened Pose_Editor..."