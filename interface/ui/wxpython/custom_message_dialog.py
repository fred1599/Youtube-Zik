import wx

class CustomMessageDialog(wx.MessageDialog):
    def __init__(self, parent, message, caption="Message", style=wx.OK | wx.ICON_INFORMATION):
        super().__init__(parent, message, caption, style)
