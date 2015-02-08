#!/usr/bin/env python
# -*- coding: CP1252 -*-
#
# generated by wxGlade 0.6.7 (standalone edition) on Sat Feb 07 12:34:16 2015
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

class MyPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _("Base"))
        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, _(str(self.Parent.values[0])))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, _("Shoulder"))
        self.text_ctrl_2 = wx.TextCtrl(self, wx.ID_ANY, _(str(self.Parent.values[1])))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, _("Elbow"))
        self.text_ctrl_3 = wx.TextCtrl(self, wx.ID_ANY, _(str(self.Parent.values[2])))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, _("Wrist"))
        self.text_ctrl_4 = wx.TextCtrl(self, wx.ID_ANY, _(str(self.Parent.values[3])))
        self.label_5 = wx.StaticText(self, wx.ID_ANY, _("Gripper"))
        self.text_ctrl_5 = wx.TextCtrl(self, wx.ID_ANY, _(str(self.Parent.values[4])))
        self.button_1 = wx.Button(self, wx.ID_OK, _("OK"))
        self.button_2 = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.txt_ctrl1_event, self.text_ctrl_1)
        self.Bind(wx.EVT_TEXT, self.txt_ctrl2_event, self.text_ctrl_2)
        self.Bind(wx.EVT_TEXT, self.txt_ctrl3_event, self.text_ctrl_3)
        self.Bind(wx.EVT_TEXT, self.txt_ctrl4_event, self.text_ctrl_4)
        self.Bind(wx.EVT_TEXT, self.txt_ctrl5_event, self.text_ctrl_5)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyPanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyPanel.__do_layout
        grid_sizer_1 = wx.FlexGridSizer(6, 2, 3, 3)
        grid_sizer_1.Add(self.label_1, 0, wx.ALL, 3)
        grid_sizer_1.Add(self.text_ctrl_1, 0, 0, 0)
        grid_sizer_1.Add(self.label_2, 0, wx.ALL, 3)
        grid_sizer_1.Add(self.text_ctrl_2, 0, 0, 0)
        grid_sizer_1.Add(self.label_3, 0, wx.ALL, 3)
        grid_sizer_1.Add(self.text_ctrl_3, 0, 0, 0)
        grid_sizer_1.Add(self.label_4, 0, wx.ALL, 3)
        grid_sizer_1.Add(self.text_ctrl_4, 0, 0, 0)
        grid_sizer_1.Add(self.label_5, 0, wx.ALL, 3)
        grid_sizer_1.Add(self.text_ctrl_5, 0, 0, 0)
        grid_sizer_1.Add(self.button_1, 0, wx.ALL, 5)
        grid_sizer_1.Add(self.button_2, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)
        grid_sizer_1.AddGrowableCol(0)
        # end wxGlade
        
    def get_values(self):
        return [self.text_ctrl_1.GetValue(), self.text_ctrl_2.GetValue(), self.text_ctrl_3.GetValue(),
                self.text_ctrl_4.GetValue(), self.text_ctrl_5.GetValue()]

    def txt_ctrl1_event(self, event):  # wxGlade: MyPanel.<event_handler>
        print "Event handler 'txt_ctrl1_event' not implemented!"
        event.Skip()

    def txt_ctrl2_event(self, event):  # wxGlade: MyPanel.<event_handler>
        print "Event handler 'txt_ctrl2_event' not implemented!"
        event.Skip()

    def txt_ctrl3_event(self, event):  # wxGlade: MyPanel.<event_handler>
        print "Event handler 'txt_ctrl3_event' not implemented!"
        event.Skip()

    def txt_ctrl4_event(self, event):  # wxGlade: MyPanel.<event_handler>
        print "Event handler 'txt_ctrl4_event' not implemented!"
        event.Skip()

    def txt_ctrl5_event(self, event):  # wxGlade: MyPanel.<event_handler>
        print "Event handler 'txt_ctrl5_event' not implemented!"
        event.Skip()

# end of class MyPanel


# end of class MyPanel
class posebox_dblclick_dialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.parent_panel = args[0]
        print self.parent_panel
        
        if self.parent_panel:
            self.values = self.parent_panel.junk
        else:
            self.values=[1,2,3,4,5]
        
        
        sizer_1  = wx.GridSizer(1, 1, 0, 0)

        self.panel_1  = MyPanel(self, wx.ID_ANY)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
    
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog4.__set_properties
        self.SetTitle(_("PoseBox DBL_click Editor"))
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
    dialog_5 = posebox_dblclick_dialog(None, wx.ID_ANY, "")
    app.SetTopWindow(dialog_5)
    dialog_5.Show()
    app.MainLoop()

NAME = "SKIP"
STATUS = "Pose_Editor dialog..."