import wx
import sqlite3

class ActionPanel(wx.Panel):
    def __init__(self, parent, update_callback, delete_callback, add_callback):
        super().__init__(parent)

        self.update_btn = wx.Button(self, label='Update', size=(70, 30))
        self.delete_btn = wx.Button(self, label='Delete', size=(70, 30))
        self.add_btn = wx.Button(self, label='Add', size=(70, 30))

        self.update_btn.Bind(wx.EVT_BUTTON, update_callback)
        self.delete_btn.Bind(wx.EVT_BUTTON, delete_callback)
        self.add_btn.Bind(wx.EVT_BUTTON, add_callback)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.update_btn, 0, wx.ALL, 5)
        sizer.Add(self.delete_btn, 0, wx.ALL, 5)
        sizer.Add(self.add_btn, 0, wx.ALL, 5)
        self.SetSizer(sizer)

    def show_buttons(self, show=True):
        self.update_btn.Show(show)
        self.delete_btn.Show(show)
        self.add_btn.Show(show)
        self.Layout()

class CustomListCtrl(wx.ListCtrl):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.action_panels = {}

    def set_item_action_panel(self, index, action_panel):
        self.action_panels[index] = action_panel

    def get_item_action_panel(self, index):
        return self.action_panels.get(index)

    def remove_action_panels(self):
        for index, action_panel in self.action_panels.items():
            action_panel.Destroy()
        self.action_panels = {}

class AddDialog(wx.Dialog):
    def __init__(self, parent, title, fields, categories=None):
        super().__init__(parent, title=title, size=(400, 300))

        self.fields = fields
        self.input_boxes = {}
        self.categories = categories or []

        sizer = wx.BoxSizer(wx.VERTICAL)

        for field in self.fields:
            if field == 'category_id':
                label = wx.StaticText(self, label=f"{field.capitalize()}:")
                category_choices = [category['name'] for category in self.categories]
                category_combo = wx.ComboBox(self, choices=category_choices, style=wx.CB_READONLY)
                self.input_boxes[field] = category_combo
            else:
                label = wx.StaticText(self, label=f"{field.capitalize()}:")
                input_box = wx.TextCtrl(self)
                self.input_boxes[field] = input_box

            sizer.Add(label, 0, wx.ALL, 5)
            if field == 'category_id':
                sizer.Add(category_combo, 0, wx.EXPAND | wx.ALL, 5)
            else:
                sizer.Add(input_box, 0, wx.EXPAND | wx.ALL, 5)

        btn_ok = wx.Button(self, wx.ID_OK, label="OK")
        btn_cancel = wx.Button(self, wx.ID_CANCEL, label="Cancel")

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_ok, 0, wx.ALL, 5)
        btn_sizer.Add(btn_cancel, 0, wx.ALL, 5)

        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizerAndFit(sizer)

    def get_input_values(self):
        values = {}
        for field, input_box in self.input_boxes.items():
            if isinstance(input_box, wx.ComboBox):
                selected_index = input_box.GetSelection()
                if selected_index != wx.NOT_FOUND:
                    values[field] = self.categories[selected_index]['id']
            else:
                values[field] = input_box.GetValue()
        return values


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(800, 600))

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.create_navigation()
        self.create_list_ctrl()
        self.create_add_button()

        self.fields = []  # Define fields attribute
        self.categories = []  # Define categories attribute

        self.panel.SetSizerAndFit(self.sizer)
        self.Layout()

        self.selected_model = None

        self.Show()


    def create_navigation(self):
        self.navbar = wx.Panel(self.panel, style=wx.BORDER_SIMPLE)
        self.nav_sizer = wx.BoxSizer(wx.HORIZONTAL)

        models = ['Produits', 'Fournisseur', 'Category', 'Client']
        for model in models:
            btn = wx.Button(self.navbar, label=model)
            btn.Bind(wx.EVT_BUTTON, lambda event, model=model: self.on_model_select(event, model))
            self.nav_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 5)

        self.navbar.SetSizer(self.nav_sizer)
        self.sizer.Add(self.navbar, 0, wx.EXPAND)

    def create_list_ctrl(self):
        self.list_ctrl = CustomListCtrl(self.panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.sizer.Add(self.list_ctrl, 1, wx.EXPAND)

        self.selected_row = None

    def create_add_button(self):
        self.add_btn = wx.Button(self.panel, label='Add', size=(70, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.show_add_dialog)
        self.sizer.Add(self.add_btn, 0, wx.ALL, 5)

    def on_model_select(self, event, model):
        self.selected_model = model
        self.update_list_ctrl(model)

    def show_add_dialog(self, event):
        if self.selected_model is not None:
            db = sqlite3.connect('gestion_produits.db')
            cursor = db.cursor()
            cursor.execute(f"PRAGMA table_info({self.selected_model})")
            col_info = cursor.fetchall()
            self.fields = [info[1] for info in col_info if info[1] != 'id']  # Update fields attribute
                
            if self.selected_model == 'Produits':
                cursor.execute("SELECT id, name FROM Category")
                self.categories = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]  # Update categories attribute
            else:
                self.categories = []

            dialog = AddDialog(self, f'Add {self.selected_model}', self.fields, self.categories)
            if dialog.ShowModal() == wx.ID_OK:
                values = dialog.get_input_values()
                self.add_row(self.selected_model, values)
                self.update_list_ctrl(self.selected_model)

            dialog.Destroy()
            db.close()
        else:
            print("Please select a model first.")


    def create_tables_if_not_exist(self):
        db = sqlite3.connect('gestion_produits.db')
        cursor = db.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                category_id INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Fournisseur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                address TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Client (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT
            )
        ''')


        db.commit()
        db.close()

    def update_list_ctrl(self, model):
        self.create_tables_if_not_exist()

        db = sqlite3.connect('gestion_produits.db')
        cursor = db.cursor()

        cursor.execute(f"PRAGMA table_info({model})")
        col_info = cursor.fetchall()
        col_labels = [info[1] for info in col_info]
        col_labels.append('Actions')

        self.list_ctrl.ClearAll()
        self.list_ctrl.remove_action_panels()

        self.list_ctrl.InsertColumn(0, 'ID')

        for col_idx, col_label in enumerate(col_labels):
            if col_label != 'Actions':
                self.list_ctrl.InsertColumn(col_idx + 1, col_label)
            else:
                self.list_ctrl.InsertColumn(col_idx + 1, col_label, width=150)

        if model == 'Produits':
            cursor.execute(f"SELECT * FROM Produits")
        else:
            cursor.execute(f"SELECT * FROM {model}")
        rows = cursor.fetchall()
        for row_idx, row in enumerate(rows):
            index = self.list_ctrl.InsertItem(row_idx, str(row[0]))
            for col_idx in range(1, len(row)):
                self.list_ctrl.SetItem(index, col_idx, str(row[col_idx]))  # Update column index without subtracting 1

            action_panel = ActionPanel(self.list_ctrl,
                    update_callback=lambda event, row=row: self.update_row(model, row, self.fields, self.categories),
                    delete_callback=lambda event, row=row: self.delete_row(model, row),
                    add_callback=self.show_add_dialog)



            self.list_ctrl.set_item_action_panel(index, action_panel)

            if model != 'Produits':
                action_panel.show_buttons()

            rect = self.list_ctrl.GetItemRect(index)
            action_panel.SetSize(rect.x + rect.width - 150, rect.y, 150, rect.height + 10)
            action_panel.Show()

        db.close()


    def update_row(self, model, item_data, fields, categories):
        db = sqlite3.connect('gestion_produits.db')
        cursor = db.cursor()

        dialog = AddDialog(self, f'Update {model}', fields, categories)
        if dialog.ShowModal() == wx.ID_OK:
            values = dialog.get_input_values()
            update_query = f"UPDATE {model} SET {', '.join(f'{key} = ?' for key in values.keys())} WHERE id = ?"
            cursor.execute(update_query, tuple(values.values()) + (item_data[0],))
            db.commit()
            print(f"Updated {model} row with ID {item_data[0]}")
            self.update_list_ctrl(model)
        dialog.Destroy()
        db.close()



    def delete_row(self, model, item_data):
        db = sqlite3.connect('gestion_produits.db')
        cursor = db.cursor()

        # Assuming item_data contains the ID of the row to delete
        delete_query = f"DELETE FROM {model} WHERE id = ?"
        cursor.execute(delete_query, (item_data[0],))  # Assuming item_data[0] is the ID
        db.commit()
        print(f"Deleted {model} row with ID {item_data[0]}")
        self.update_list_ctrl(model)  # Refresh the list control

        db.close()


    def add_row(self, model, values):
        db = sqlite3.connect('gestion_produits.db')
        cursor = db.cursor()

        fields = ', '.join(values.keys())
        placeholders = ', '.join(['?'] * len(values))
        sql = f"INSERT INTO {model} ({fields}) VALUES ({placeholders})"

        try:
            cursor.execute(sql, tuple(values.values()))
            db.commit()
            print(f"Added a new row to {model} with values:", values)
        except sqlite3.Error as e:
            print("Error:", e)
            db.rollback()
        finally:
            db.close()


if __name__ == '__main__':
    app = wx.App()
    MainFrame(None, title='Gestionnaire de Produits')
    app.MainLoop()
