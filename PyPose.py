#!/usr/bin/env python2.7

""" 
  Description: this sets up the Frame and imports the tools folder

  pyPincher: A fork of the pyPose controller from Vanadium labs and Michael Ferguson.
   The project is customized for the phantomX pincher arms design.

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
# begin wxGlade: dependencies
import gettext
# end wxGlade

import sys, time, os
sys.path.append("tools")#imports everything from tools folder
import wxversion
wxversion.select('3.0')

import wx
print wx.VERSION_STRING
import serial

from ax12 import *
from driver import Driver

#from Pose_Editor import *
#from SeqEditor import *
from project import *
from wx.lib.masked import NumCtrl

VERSION = "PyPincher2"

###############################################################################
# Main editor window
class editor(wx.Frame):
    """ Implements the main window. """
    ID_NEW=wx.NewId()
    ID_OPEN=wx.NewId()
    ID_SAVE=wx.NewId()
    ID_SAVE_AS=wx.NewId()
    ID_EXIT=wx.NewId()
    #ID_EXPORT=wx.NewId()
    ID_RELAX=wx.NewId()
    ID_PORT=wx.NewId()
    ID_ABOUT=wx.NewId()
    ID_TEST=wx.NewId()
    ID_TIMER=wx.NewId()
    ID_COL_MENU=wx.NewId()
    #ID_LIVE_UPDATE=wx.NewId()
    ID_2COL=wx.NewId()
    ID_3COL=wx.NewId()
    ID_4COL=wx.NewId()
    ID_ROB_COL=wx.NewId()
    ID_FORCE_FIELDS=wx.NewId()
    ID_SET_COLLISION = wx.NewId()
    ID_SET_SPHERE_SIZE=wx.NewId()
    ID_SHOW_TOOL_PATH = wx.NewId()
    
    ID_SET_LIMITS = wx.NewId()
    ID_ENABLE_SAFETY = wx.NewId()

    def __init__(self):
        """ Creates pose editor window. """
        print ("creating the frame named " + VERSION)
        wx.Frame.__init__(self, None, -1, VERSION, style = wx.DEFAULT_FRAME_STYLE)# & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        # key data for our program
        self.project = project()        # holds data for our project
        self.tools = dict()             # our tool instances
        self.toolIndex = dict()         # holds tool folder classes
        self.saveReq = False
        self.panel = None               #the main panel
        self.port = None                #the serial port
        self.filename = ""              #name of the current file being edoted
        self.dirname = ""               #directy that the file is saved in

        self.robot_color = robot_color() #0.3,1,.1
        # for clearing red color on status bar
        self.timer = wx.Timer(self, self.ID_TIMER)
        self.timeout = 0
        
        # build our menu bar  
        menubar = wx.MenuBar()
        prjmenu = wx.Menu()
        prjmenu.Append(self.ID_NEW, "new") # dialog with name, # of servos
        prjmenu.Append(self.ID_OPEN, "open") # open file dialog
        prjmenu.Append(self.ID_SAVE,"save") # if name unknown, ask, otherwise save
        prjmenu.Append(self.ID_SAVE_AS,"save as") # ask for name, save
        prjmenu.AppendSeparator()
        prjmenu.Append(self.ID_EXIT,"exit") 
        menubar.Append(prjmenu, "project")

        toolsmenu = wx.Menu()
        # find our tools
        toolFiles = list()
        for file in os.listdir("tools"):
            if file[-3:] == '.py' and file != "__init__.py" and file != "ToolPane.py":
                toolFiles.append(file[0:-3])       
        # load tool names, give them IDs
        print "Importing the following  modules from the tools folder:"
        for t in toolFiles:#this imports commander.py I think it gets path from operating system
            module = __import__(t, globals(), locals(), ["NAME"])    
            name = getattr(module, "NAME")
            if name == "SKIP":
                continue
            id = wx.NewId()
            self.toolIndex[id] = (t, name)
            toolsmenu.Append(id,name)   
        #toolsmenu.Append(self.ID_EXPORT,"export to AVR") # save as dialog
        for t in self.toolIndex:
            print t
        menubar.Append(toolsmenu,"tools")

        configmenu = wx.Menu()
        configmenu.Append(self.ID_PORT,"port") # dialog box: arbotix/thru, speed, port
        
        menubar.Append(configmenu, "config")
        
        #build settings menu 
        settings_menu = wx.Menu()  
        settings_menu.Append(self.ID_ROB_COL,"robot_color") 
        
        self.enable_safety_limits = settings_menu.Append(self.ID_ENABLE_SAFETY, "Enable Limits", kind=wx.ITEM_CHECK)
        self.collision_detect = settings_menu.Append(self.ID_SET_COLLISION,"Collision_Detect",kind=wx.ITEM_CHECK)
        settings_menu.Append(self.ID_SET_LIMITS,"Set Limits")
        settings_menu.Append(self.ID_SET_SPHERE_SIZE, "Spheres_size")
        self.show_force_fields = settings_menu.Append(self.ID_FORCE_FIELDS,"Show Force Fields",kind=wx.ITEM_CHECK)
        self.show_tool_path = settings_menu.Append(self.ID_SHOW_TOOL_PATH,"Show Tool Path",kind=wx.ITEM_CHECK)
        menubar.Append(settings_menu, "settings") 
        
        helpmenu = wx.Menu()
        helpmenu.Append(self.ID_ABOUT,"about")
        menubar.Append(helpmenu,"help")

        self.SetMenuBar(menubar)    
        # configure events
        wx.EVT_MENU(self, self.ID_NEW, self.newFile)
        wx.EVT_MENU(self, self.ID_OPEN, self.openFile)
        wx.EVT_MENU(self, self.ID_SAVE, self.saveFile)
        wx.EVT_MENU(self, self.ID_SAVE_AS, self.saveFileAs)
        wx.EVT_MENU(self, self.ID_EXIT, sys.exit)
        
        for t in self.toolIndex.keys():
            wx.EVT_MENU(self, t, self.loadTool)
        #wx.EVT_MENU(self, self.ID_EXPORT, self.export)     

        wx.EVT_MENU(self, self.ID_RELAX, self.doRelax)   
        wx.EVT_MENU(self, self.ID_PORT, self.doPort)
        wx.EVT_MENU(self, self.ID_TEST, self.doTest)
        wx.EVT_MENU(self, self.ID_ABOUT, self.doAbout)
        self.Bind(wx.EVT_CLOSE, self.doClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=self.ID_TIMER)
        wx.EVT_MENU(self, self.ID_ROB_COL, self.robot_color_dlg)
        #wx.EVT_MENU(self, self.ID_LIVE_UPDATE, self.setLiveUpdate)
        wx.EVT_MENU(self, self.ID_FORCE_FIELDS, self.set_force_fields)
        wx.EVT_MENU(self, self.ID_SET_COLLISION, self.set_collision_detect)
        wx.EVT_MENU(self, self.ID_SET_SPHERE_SIZE, self.set_sphere_size)
        wx.EVT_MENU(self, self.ID_SHOW_TOOL_PATH, self.set_show_tool_path)
        
        wx.EVT_MENU(self, self.ID_ENABLE_SAFETY, self.enable_safety)
        wx.EVT_MENU(self, self.ID_SET_LIMITS, self.set_safety_limits)
        
        # editor area       
        self.sb = self.CreateStatusBar(2)
        self.sb.SetStatusWidths([-1,150])
        self.sb.SetStatusText('not connected',1)

        self.loadTool()
        self.sb.SetStatusText('please create or open a project...',0)
        self.Centre()
        # small hack for windows... 9-25-09 MEF
        self.color = (211,211,211)
        self.SetBackgroundColour(self.color)
        self.Show(True)

    ###########################################################################
    # toolpane handling   
    def loadTool(self, e=None):
        if e == None:
            t = "Pose_Editor"
        else:
            t = self.toolIndex[e.GetId()][0]  # get name of file for this tool  
            if self.tool == t:
                return
        if self.panel != None:
            self.panel.save()
            self.sizer.Remove(self.panel)
            self.panel.Destroy()
        self.ClearBackground()
        print self.panel
        # instantiate
        module = __import__(t, globals(), locals(), [t,"STATUS"])

        panelClass = getattr(module, t)
        self.panel = panelClass(self,self.port)
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel,1,wx.EXPAND|wx.ALL,10)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.sb.SetStatusText(getattr(module,"STATUS"),0)
        self.tool = t
        self.Layout()
        self.panel.SetFocus()
        #update the settings
        #self.setLiveUpdate()
        #@todo these should be set at initialization of panel
        self.enable_safety()
        self.set_force_fields()
        self.set_collision_detect()
        self.set_show_tool_path()

    ###########################################################################
    # file handling                
    def newFile(self, e):  
        """ Open a dialog that asks for robot name and servo count. """ 
        #@todo make this more pyPincher add model names 
        #and load and save the model here
        dlg = NewProjectDialog(self, -1, "Create New pyPincher Project")
        if dlg.ShowModal() == wx.ID_OK:
            self.project.new(dlg.name.GetValue(), dlg.count.GetValue(), int(dlg.resolution.GetValue()))    
            self.sb.SetStatusText('created new project ' + self.project.name + ', please create a pose...')
            self.SetTitle(VERSION+" - " + self.project.name)
            self.panel.saveReq = True
            self.filename = ""#dlg.name.GetValue()
        dlg.Destroy()

    def openFile(self, e):
        """ Loads a robot file into the GUI. """ 
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, 
                            "", "*.ppr", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.dirname = dlg.GetDirectory()
            print "Opening: " + self.filename            
            self.project.load(self.filename)  
            self.SetTitle(VERSION+" - " + self.project.name)
            dlg.Destroy()
            self.sb.SetStatusText('opened ' + self.filename)
            self.loadTool()
            print self.project.poses
            
    def saveFile(self, e=None):
        """ Save a robot file from the GUI. """
        if self.filename == "": 
            dlg = wx.FileDialog(self, "Choose a file", self.dirname,
                                '', "*.ppr",wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetPath()
                self.dirname = dlg.GetDirectory()
                dlg.Destroy()
            else:
                return  
        if self.filename[-4:] != ".ppr":
            self.filename = self.filename + ".ppr"
        print "saving file with poses =  ", self.project.poses
        self.project.saveFile(self.filename)
        self.sb.SetStatusText('saved ' + self.filename)

    def saveFileAs(self, e):
        self.filename = ""
        self.saveFile()                

    ###########################################################################
    # Export functionality
    '''
    def export(self, e):        
        """ Export a pose file for use with Sanguino Library. """
        if self.project.name == "":
            self.sb.SetBackgroundColour('RED')
            self.sb.SetStatusText('please create a project')
            self.timer.Start(20)
            return
        dlg = wx.FileDialog(self, "Choose a file", self.dirname,"","*.h",wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.project.export(dlg.GetPath())
            self.sb.SetStatusText("exported " + dlg.GetPath(),0)
            dlg.Destroy()  
    '''      

    def robot_color_dlg(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            self.sb.SetStatusText('You selected: %s\n' % str(data.GetColour().Get()))
            self.robot_color.set_value(data.GetColour().Get())
        dlg.Destroy()
        self.Layout()

    ###########################################################################
    # Port Manipulation
    def findPorts(self):
        """ return a list of serial ports """
        self.ports = list()
        # windows first
        for i in range(20):
            try:
                s = serial.Serial("COM"+str(i))
                s.close()
                self.ports.append("COM"+str(i))
            except:
                pass
        if len(self.ports) > 0:
            return self.ports
        # mac specific next:        
        try:
            for port in os.listdir("/dev/"):
                if port.startswith("tty.usbserial"):
                    self.ports.append("/dev/"+port)
        except:
            pass
        # linux/some-macs
        for k in ["/dev/ttyUSB","/dev/ttyACM","/dev/ttyS"]:
                for i in range(6):
                    try:
                        s = serial.Serial(k+str(i))
                        s.close()
                        self.ports.append(k+str(i))
                    except:
                        pass
        return self.ports
    def doPort(self, e=None):
        """ open a serial port """
        if self.port == None:
            self.findPorts()
        dlg = wx.SingleChoiceDialog(self,'Port (Ex. COM4 or /dev/ttyUSB0)','Select Communications Port',self.ports)
        #dlg = PortDialog(self,'Select Communications Port',self.ports)
        if dlg.ShowModal() == wx.ID_OK:
            if self.port != None:
                self.port.ser.close()
            print "Opening port: " + self.ports[dlg.GetSelection()]
            try:
                # TODO: add ability to select type of driver
                self.port = Driver(self.ports[dlg.GetSelection()], 38400, True) # w/ interpolation
                self.panel.port = self.port
                self.panel.portUpdated()
                self.sb.SetStatusText(self.ports[dlg.GetSelection()] + "@38400",1)
            except Exception as err:
                self.port = None
                self.sb.SetBackgroundColour('RED')
                self.sb.SetStatusText(("Could Not Open Port"+str(err)),0) 
                self.sb.SetStatusText('not connected',1)
                self.timer.Start(20)
            dlg.Destroy()
        
    def doTest(self, e=None):
        if self.port != None:
            #self.port.execute(253, 25, list())
            for servo in range(5):
                pos=50
                print "setting speed to 50 at servo #",servo
                self.port.setReg(servo+1, P_GOAL_SPEED_L, [pos%256, pos>>8])

    def doRelax(self, e=None):
        """ Relax servos so you can pose them. """
        if self.port != None:
            print "PyPose: relaxing servos..."      
            for servo in range(self.project.count):
                self.port.setReg(servo+1,P_TORQUE_ENABLE, [0,])    
        else:
            self.sb.SetBackgroundColour('RED')
            self.sb.SetStatusText("No Port Open",0) 
            self.timer.Start(20)

    def doAbout(self, e=None):
        license= """This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA)
"""
        info = wx.AboutDialogInfo()
        info.SetName(VERSION)
        info.SetDescription("A lightweight pose and capture software for the ArbotiX robocontroller")
        info.SetCopyright("Copyright (c) 2008-2010 Michael E. Ferguson.  All right reserved.")
        info.SetLicense(license)
        info.SetWebSite("http://www.vanadiumlabs.com")
        wx.AboutBox(info)

    def doClose(self, e=None):
        # TODO: edit this to check if we NEED to save...
        if self.project.save == True:
            dlg = wx.MessageDialog(None, 'Save changes before closing?', '',
            wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            r = dlg.ShowModal()            
            if r == wx.ID_CANCEL:
                e.Veto()
                return
            elif r == wx.ID_YES:
                self.saveFile()
                pass
        self.Destroy()
            
    def OnTimer(self, e=None):
        self.timeout = self.timeout + 1
        if self.timeout > 50:
            self.sb.SetBackgroundColour(self.color)
            self.sb.SetStatusText("",0)
            self.sb.Refresh()
            self.timeout = 0
            self.timer.Stop()

    '''
    def setLiveUpdate(self, e=None):
        if self.tool == "Pose_Editor":
            self.panel.live = self.live.IsChecked()
    '''

    def set_force_fields(self, e=None):
        if self.tool == "Pose_Editor":
            self.panel.show_force_fields = self.show_force_fields.IsChecked()
            self.Refresh()
            
    def set_collision_detect(self, e=None):
        if self.tool == "Pose_Editor":
            self.panel.collision_detect = self.collision_detect.IsChecked()
            
    def enable_safety(self, e=None):
        if self.tool == "Pose_Editor":
            self.panel.enable_limits = self.enable_safety_limits.IsChecked()
            
    def set_sphere_size(self, e=None):
        dlg = set_sphere_dialog(self, -1, "Set Sphere Values")
        if dlg.ShowModal() == wx.ID_OK:
            if self.tool == "Pose_Editor":
                
                rad = (dlg.radius.GetValue())
                if rad =="": 
                    rad=40               
                else: rad=int(rad)
                self.panel.spheres[str(dlg.sphere_name.GetValue())].radius= rad 
                #@todo this should update the sphere size initializer in panel
                self.sb.SetStatusText('set_sphere_values')
                self.Refresh()
        dlg.Destroy()
    
    def set_show_tool_path(self, e=None):    
        if self.tool == "Pose_Editor":
            self.panel.show_tool_path = self.show_tool_path.IsChecked()
           
    def set_safety_limits(self, e=None):
        if self.tool == "Pose_Editor" and self.panel.port:
            dlg = set_limits(self, -1, "Set Servo limits")
            if dlg.ShowModal() == wx.ID_OK:
                self.project.safety_limits = self.panel.limits = dlg.limits  
                self.sb.SetStatusText(('safety_limits:'+str(self.project.safety_limits)),0)    
            dlg.Destroy()  
        else:
            self.sb.SetStatusText('please configure serial port...',0)  
            
class robot_color():
    #recieves all values as RGB and turns them into float
    def __init__(self, color=(75,255,25)):
        self.color = color = [val/255.0 for val in color]  
    def get_value(self):
        return self.color
    def set_value(self, color):
        self.color = [val/255.0 for val in color] 

class set_limits(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)#, size=(400,100))
        self.parent = parent
        self.limits = self.parent.panel.limits
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_2 = limits_panel(self.panel_1, wx.ID_ANY)
        self.sizer_6_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY, _("Move servo to limit and press button"))
        self.button_5 = wx.Button(self.panel_1, wx.ID_OK, _("OK"))
        self.button_6 = wx.Button(self.panel_1,  wx.ID_CANCEL, _("Cancel"))
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle(_("Set Servo Limits"))

    def __do_layout(self):
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_6_staticbox.Lower()
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_6.Add(self.panel_2, 1, 0, 0)
        sizer_5.Add(sizer_6, 1, 0, 0)
        sizer_7.Add(self.button_5, 0, wx.LEFT | wx.ALIGN_RIGHT, 30)
        sizer_7.Add(self.button_6, 0, wx.LEFT, 5)
        sizer_5.Add(sizer_7, 0, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_5)
        sizer_3.Add(self.panel_1, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()

class limits_panel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyPanel1.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.frame = self.Parent.Parent.parent
        self.selected = 0
        self.limits = self.Parent.Parent.limits#panel_1
        self.combo_box_1 = wx.ComboBox(self, wx.ID_ANY, choices=[_("Base"), _("Shoulder"), _("Elbow"), _("Wrist"), _("Gripper")], style=wx.CB_DROPDOWN | wx.CB_DROPDOWN)
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _("Hi Limit:"), style=wx.ALIGN_CENTRE)
        self.text_ctrl_1 = wx.StaticText(self, wx.ID_ANY, _(str(self.limits[0][0])), style=wx.ALIGN_CENTRE)
        self.label_2 = wx.StaticText(self, wx.ID_ANY, _("Low Limit:"), style=wx.ALIGN_CENTRE)
        self.text_ctrl_2 = wx.StaticText(self, wx.ID_ANY, _(str(self.limits[0][1])), style=wx.ALIGN_CENTRE)
        self.button_1 = wx.Button(self, wx.ID_ANY, _("Set_Hi_Limit"))
        self.button_2 = wx.Button(self, wx.ID_ANY, _("Set_Low_Limit"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.set_hi_limit_event, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.set_low_limit_event, self.button_2)
        self.Bind(wx.EVT_COMBOBOX, self.combo_box_event, self.combo_box_1)
        # end wxGlade

    def __set_properties(self):
        self.SetSize((392, 273))
        self.combo_box_1.SetSelection(self.selected)

    def __do_layout(self):
        grid_sizer_1 = wx.GridSizer(2, 2, 0, 0)
        grid_sizer_2 = wx.GridSizer(2, 2, 0, 0)
        grid_sizer_1.Add(self.combo_box_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_2.Add(self.label_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_2.Add(self.text_ctrl_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_2.Add(self.label_2, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_2.Add(self.text_ctrl_2, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.button_1, 0, wx.ALL | wx.ALIGN_RIGHT, 3)
        grid_sizer_1.Add(self.button_2, 0, wx.ALL, 3)
        self.SetSizer(grid_sizer_1)
        # end wxGlade

    def set_hi_limit_event(self, event):  # wxGlade: MyPanel1.<event_handler>
        vals = self.frame.panel.port.getReg((self.selected+1), P_PRESENT_POSITION_L, 2)
        if vals: 
            if len(vals) > 1:
                cur_pos = vals[0] + (vals[1]<<8)
                print cur_pos
                self.limits[self.selected][0]=cur_pos
                self.text_ctrl_1.SetLabel(str(self.limits[self.selected][0]))
            else:
                print "error reading values"
        event.Skip()

    def set_low_limit_event(self, event):  # wxGlade: MyPanel1.<event_handler>
        vals= self.frame.panel.port.getReg((self.selected+1), P_PRESENT_POSITION_L, 2)
        if vals: 
            if len(vals) > 1:
                print vals
                cur_pos = vals[0] + (vals[1]<<8)
                self.limits[self.selected][1]=cur_pos
                self.text_ctrl_2.SetLabel(str(self.limits[self.selected][1]))
        event.Skip()
        
    def combo_box_event(self, event):
        self.selected =  self.combo_box_1.GetSelection()
        self.text_ctrl_1.SetLabel(str(self.limits[self.selected][0]))#high
        self.text_ctrl_2.SetLabel(str(self.limits[self.selected][1]))#low
      
###############################################################################
# New Project Dialog
class NewProjectDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(310, 180))  

        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)

        wx.StaticBox(panel, -1, 'PHANTOMX Project Parameters', (5, 5), (300, 120))
        wx.StaticText(panel, -1, 'Name:', (15,30))
        self.name = wx.TextCtrl(panel, -1, '', (105,25)) 
        wx.StaticText(panel, -1, '# of Servos:', (15,55))
        self.count = wx.SpinCtrl(panel, -1, '5', (105, 50), min=5, max=5)
        wx.StaticText(panel, -1, 'Resolution:', (15,80))
        self.resolution =  wx.ComboBox(panel, -1, '1024', (105, 75), choices=['1024'])#choices=['1024','4096'])

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(70, 30))
        closeButton = wx.Button(self, wx.ID_CANCEL, 'Close', size=(70, 30))
        hbox.Add(okButton)
        hbox.Add(closeButton)

        vbox.Add(panel)
        vbox.Add(hbox, -1, wx.ALIGN_CENTER , 3)
        self.SetSizer(vbox)
        
class set_sphere_dialog(wx.Dialog):
    def __init__(self, parent, id, title):
    #def __init__(self, *args, **kwds):
        # begin wxGlade: set_sphere_dialog.__init__
        wx.Dialog.__init__(self, parent, id, title, size=(400,100))  
        panel = sphere_dialog(self)
        
        self.sphere_name = panel.combo_box_1
        self.radius = panel.text_ctrl_1
        #self.position = panel.text_ctrl_2 
           
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(70, 30))
        closeButton = wx.Button(self, wx.ID_CANCEL, 'Close', size=(70, 30))
        hbox.Add(okButton)
        hbox.Add(closeButton)
        vbox.Add(panel, -1)
        vbox.Add(hbox, -1, wx.ALIGN_CENTER , 3)
        self.SetSizer(vbox)
        
class sphere_dialog(wx.Panel):
    def __init__(self, parent):
        # begin wxGlade: set_sphere_dialog.__init__
        # kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, parent)
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _("Shere: "), style=wx.ALIGN_CENTRE)
        self.combo_box_1 = wx.ComboBox(self, wx.ID_ANY, choices=[_("base"), _("shoulder"), _("elbow"), _("wrist")], style=wx.CB_DROPDOWN | wx.CB_DROPDOWN | wx.CB_READONLY)
        self.label_2 = wx.StaticText(self, wx.ID_ANY, _("Radius:"))
        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, "")
        #self.label_3 = wx.StaticText(self, wx.ID_ANY, _("Position:"), style=wx.ALIGN_CENTRE)
        #self.text_ctrl_2 = wx.TextCtrl(self, wx.ID_ANY, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: set_sphere_dialog.__set_properties
        self.combo_box_1.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: set_sphere_dialog.__do_layout
        sizer_1 = wx.FlexGridSizer(1, 4, 0, 0)
        sizer_1.Add(self.label_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizer_1.Add(self.combo_box_1, 0, wx.ALL, 2)
        sizer_1.Add(self.label_2, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizer_1.Add(self.text_ctrl_1, 0, wx.ALL, 2)
        #sizer_1.Add(self.label_3, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 2)
        # sizer_1.Add(self.text_ctrl_2, 0, 0, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        # end wxGlade


if __name__ == "__main__":
    print "PyPose starting editor class... "
    gettext.install("app") # replace with the appropriate catalog name
    app = wx.App()
    frame = editor()
    app.MainLoop()

