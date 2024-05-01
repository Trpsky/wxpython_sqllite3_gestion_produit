import wx
import sqlite3

class AddUserForm(wx.Frame):
    def __init__(self, parent, title):
        super(AddUserForm, self).__init__(parent, title=title, size=(300, 200))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.name_label = wx.StaticText(panel, label='Nom:')
        self.first_name = wx.TextCtrl(panel)
        sizer.Add(self.name_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.first_name, 0, wx.ALL | wx.EXPAND, 5)

        self.age_label = wx.StaticText(panel, label='Prenom:')
        self.last_name = wx.TextCtrl(panel)
        sizer.Add(self.age_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.last_name, 0, wx.ALL | wx.EXPAND, 5)

        self.submit_btn = wx.Button(panel, label='Ajouter Admin')
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        sizer.Add(self.submit_btn, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)
        self.Show()

    def on_submit(self, event):
        first_name = self.first_name.GetValue()
        last_name = self.last_name.GetValue()

        db = sqlite3.connect('gestion_produit.db')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)')
        cursor.execute('INSERT INTO admins (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
        db.commit()
        db.close()

        wx.MessageBox('Admin est ete ajouter a la base de donne!')

if __name__ == '__main__':
    app = wx.App()
    AddUserForm(None, title='Ajouter une nouvelle admin')
    app.MainLoop()
