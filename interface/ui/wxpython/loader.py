import wx

class Loader(wx.Frame):
    def __init__(self, parent, id, title):
        super().__init__(parent, id, title, size=(400, 200))
        panel = wx.Panel(self)
        text = wx.StaticText(panel, label="Loading...")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 1, wx.ALIGN_CENTER)
        panel.SetSizer(sizer)
