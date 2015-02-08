#!/usr/bin/env python2.7

'''
  Description: Equation dialog class

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
import numpy as np
from numpy import *

import gettext

#@todo clean up
class my_panel(wx.Panel):
    def __init__(self, *args, **kwds):
        self.parent=args[0]
        # begin wxGlade: MyPanel3.__init__
        kwds["style"] = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        #self.label_6 = wx.StaticText(self, wx.ID_ANY, _("Max Vector Length:"))
        #self.vector_length = wx.TextCtrl(self, wx.ID_ANY, "1")
        self._Start = wx.StaticText(self, wx.ID_ANY, _("t_Interval Start"), style=wx.ALIGN_CENTRE)
        self._Stop = wx.StaticText(self, wx.ID_ANY, _("t_Interval Stop"), style=wx.ALIGN_CENTRE)
        self._Step = wx.StaticText(self, wx.ID_ANY, _("t_Interval Step"), style=wx.ALIGN_CENTRE)
        self.start = wx.TextCtrl(self, wx.ID_ANY, "0")
        self.stop = wx.TextCtrl(self, wx.ID_ANY, "15")
        self.step = wx.TextCtrl(self, wx.ID_ANY, "1")
        self.x_box = wx.StaticText(self, wx.ID_ANY, _(" X ="), style=wx.ALIGN_CENTRE)
        self.text_x = wx.TextCtrl(self, wx.ID_ANY, "200*cos(t)")
        self.y_box = wx.StaticText(self, wx.ID_ANY, _(" Y ="), style=wx.ALIGN_CENTRE)
        self.text_y = wx.TextCtrl(self, wx.ID_ANY, "200*sin(t)")
        self.z_box = wx.StaticText(self, wx.ID_ANY, _(" Z ="), style=wx.ALIGN_CENTRE)
        self.text_z = wx.TextCtrl(self, wx.ID_ANY, "10*t+5")
        self.button_1 = wx.Button(self, wx.ID_OK, _("Enter"))
        self.button_2 = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        # Define main variables of function
        self.__set_properties()
        self.__do_layout()

        #self.Bind(wx.EVT_TEXT_ENTER, self.x_text_event, self.text_x)
        #self.Bind(wx.EVT_TEXT_ENTER, self.y_text_event, self.text_y)    
        #self.Bind(wx.EVT_TEXT_ENTER, self.z_text_event, self.text_z)
        self.Bind(wx.EVT_BUTTON, self.enter_event, self.button_1)
        #self.Bind(wx.EVT_BUTTON, handler, source, id, id2)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyPanel3.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyPanel3.__do_layout
        sizer_1 = wx.FlexGridSizer(4, 1, 0, 0)
        grid_sizer_3 = wx.GridSizer(3, 2, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(2, 3, 0, 0)
        grid_sizer_1 = wx.GridSizer(1, 2, 0, 0)
        #grid_sizer_2 = wx.GridSizer(1, 2, 0, 0)
        #grid_sizer_1.Add(self.label_6, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer_1.Add(self.vector_length, 0, wx.EXPAND, 0)
        #sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self._Start, 0, wx.ALL | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 3)
        grid_sizer_2.Add(self._Stop, 0, wx.ALL | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 3)
        grid_sizer_2.Add(self._Step, 0, wx.ALL | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 3)
        grid_sizer_2.Add(self.start, 0, wx.EXPAND, 0)
        grid_sizer_2.Add(self.stop, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_2.Add(self.step, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_2.AddGrowableRow(1)
        sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_3.Add(self.x_box, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_3.Add(self.text_x, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_3.Add(self.y_box, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_3.Add(self.text_y, 0, wx.ALL | wx.EXPAND, 3)
        grid_sizer_3.Add(self.z_box, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_3.Add(self.text_z, 0, wx.ALL | wx.EXPAND, 3)
        sizer_1.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.button_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_1.Add(self.button_2, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        # end wxGlade

    def x_text_event(self, event):  # wxGlade: MyPanel3.<event_handler>
        print "Event handler 'x_text_event' not implemented!"
        event.Skip()

    def y_text_event(self, event):  # wxGlade: MyPanel3.<event_handler>
        print "Event handler 'y_text_event' not implemented!"
        event.Skip()

    def enter_event(self, event):  # wxGlade: MyPanel3.<event_handler>
        #v_l = self.vector_length.GetValue()
        start = self.start.GetValue()
        stop = self.stop.GetValue()
        step = self.step.GetValue()
        t_x = self.text_x.GetValue()
        t_y = self.text_y.GetValue()
        t_z = self.text_z.GetValue()
        #strings = ([ start, stop, step, t_x, t_y, t_z])
        try:
            t = arange(float(start), float(stop), float(step))  
            #print t_x
            #print t_y  
            #print t_z    
            self.parent.parent_panel.xs = eval( t_x )
            self.parent.parent_panel.ys = eval( t_y )
            self.parent.parent_panel.zs = eval( t_z )
            
            #print "sucess fully evaluated equation"
        except Exception as error:
            print error
        event.Skip()

class eq_dialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog4.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        sizer_1  = wx.GridSizer(1, 1, 0, 0)
        self.parent_panel = args[0]
        print self.parent_panel
        self.panel_1  = my_panel(self, wx.ID_ANY)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
    
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog4.__set_properties
        self.SetTitle(_("Equation Editor"))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog4.__do_layout
        self.Fit()
        self.Layout()
        # end wxGlade

# end of class MyDialog4
if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    dialog_5 = eq_dialog(None, wx.ID_ANY, "")
    app.SetTopWindow(dialog_5)
    dialog_5.Show()
    app.MainLoop()

NAME = "SKIP"
STATUS = "Pose_Editor dialog..."