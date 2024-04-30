import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 300))

        panel = wx.Panel(self)
        btn = wx.Button(panel, label='Click Me')
        btn.Bind(wx.EVT_BUTTON, self.on_button_click)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 20)
        panel.SetSizer(sizer)

        self.Show()

    def on_button_click(self, event):
        wx.MessageBox('Button clicked!')

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, 'My App')
    app.MainLoop()