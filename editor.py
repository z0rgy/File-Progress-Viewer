
import wx
import wx.stc
import os
import math


class FileItem(object):
    N_LINES = 5

    def __init__(self, filename):
        self._filename = filename
        self.current_line = 0

        self.lines = []
        self.nbytes_read = 0

    @property
    def next_line(self):
        return self.current_line + 5

    @property
    def previous_line(self):
        return self.current_line - 5

    def GetCurrentContent(self):
        return self.GetContent(self.current_line)

    def GetContent(self, offset):        
        return "".join(self.lines[offset:offset + FileItem.N_LINES])

    def set_filename(self, filename):
        self._filename = filename
        with open(self._filename, "r", newline="") as f:
            self.lines = f.readlines()

        self.nbytes_read = self.get_nbytes(self.GetCurrentContent())

    def get_nbytes(self, line):
        return len(line.encode('utf-8'))

    def GetNextContent(self):
        if (self.next_line <= len(self.lines)):
            line = self.GetContent(self.next_line)
            self.nbytes_read += self.get_nbytes(line)
            self.current_line = self.next_line

        else:
            line = self.GetCurrentContent()

        return line

    def GetPreviousContent(self):

        if (self.previous_line >= 0):
            line = self.GetContent(self.previous_line)
            self.nbytes_read -= self.get_nbytes(line)
            self.current_line = self.previous_line

        else:
            line = self.GetCurrentContent()

        return line

    def GetProgress(self):
        if (self.current_line == 0):
            return 0.0

        elif (self.current_line == len(self.lines)):
            return 100.0
        
        else:
            total_bytes = os.stat(self._filename).st_size
            # In this calculation vim excludes the current view point from the total.

            return math.floor((self.nbytes_read / total_bytes) * 100.0)


class ButtonPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.prev_button = wx.Button(self, label="Previous")
        self.next_button = wx.Button(self, label="Next")
        button_panel_sizer = wx.GridBagSizer()
        button_panel_sizer.Add(self.prev_button, pos=(0, 0))
        button_panel_sizer.Add(self.next_button, pos=(0, 1))
        self.SetSizer(button_panel_sizer)
        self.SetBackgroundColour("white")


class Frame(wx.Frame):

    def __init__(self):
        super(Frame, self).__init__(parent=None, title="File Viewer")
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

        openFileItem = fileMenu.Append(wx.ID_ANY, 'Open...', 'Open File')
        fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)
        self.Bind(wx.EVT_MENU, self.OnOpen, openFileItem)

        self.textControl = wx.stc.StyledTextCtrl(parent=self)

        sizer = wx.GridBagSizer()
        sizer.Add(self.textControl, pos=(0, 0), flag=wx.EXPAND)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)


        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText('-')

        self.button_panel = ButtonPanel(parent=self)
        self.button_panel.next_button.Bind(wx.EVT_BUTTON, self.OnNextButton)
        self.button_panel.prev_button.Bind(wx.EVT_BUTTON, self.OnPrevButton)

        sizer.Add(self.button_panel, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=10)
        self.SetBackgroundColour("white")
        self.SetSizerAndFit(sizer)

        self._fileReader = FileItem("")

    def OnQuit(self, _):
        self.Close()

    def OnNextButton(self, _):
        self.ChangeContent(self._fileReader.GetNextContent())
        
    def OnPrevButton(self, _):
        self.ChangeContent(self._fileReader.GetPreviousContent())

    def OnOpen(self, _):

        with wx.FileDialog(self,
                           "Open file", wildcard="*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            wx.CallAfter(self.OnDisplayFilename, pathname)

    def OnDisplayFilename(self, pathname):
        self._fileReader.set_filename(pathname)
        content = self._fileReader.GetCurrentContent()
        self.ChangeContent(content)

    def ChangeContent(self, content):
        self.textControl.SetEditable(True)
        self.textControl.ClearAll()
        self.textControl.AddText(content)
        self.textControl.SetEditable(False)

        progressAsString = "{:.2f}".format(self._fileReader.GetProgress())
        self.statusbar.SetStatusText(progressAsString)

if __name__ == "__main__":
    app = wx.App()

    frame = Frame()
    frame.Show(True)
    app.MainLoop()