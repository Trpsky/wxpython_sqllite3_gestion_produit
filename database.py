import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)')

    def insert_user(self, first_name, last_name):
        self.cursor.execute('INSERT INTO admins (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
        self.conn.commit()

    def get_users(self):
        self.cursor.execute('SELECT * FROM admins')
        return self.cursor.fetchall()

db = Database('gestion_produit.db')
db.create_table()
db.insert_user('ELMEHDI', 'ACHAHED')
users = db.get_users()
print(users)
