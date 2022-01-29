import sqlite3

class creatingDatabase():
    def __init__(self):

        self.toDoDB = sqlite3.connect('todo.db')
        self.cursorDB = self.toDoDB.cursor()

        self.cursorDB.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            name text NOT NULL,
            priority text NOT NULL,
            date text NOT NULL,
            status text NOT NULL
        )
        """)

        self.toDoDB.commit()
        self.toDoDB.close()

