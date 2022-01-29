import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from turtle import width
from tkcalendar import *
from datetime import datetime
from calendar import monthrange
from todo_db import creatingDatabase
import sqlite3


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        creatingDatabase()

        self.title("TODO")
        
        self.addBtnFrame = tk.Frame(self)
        self.addBtnFrame.grid(column=0,row=0, pady=10)
        self.addBtn = tk.Button(self.addBtnFrame, text="Dodaj Zadanie", command=self.addtask, width=15)
        self.addBtn.grid(column=0, row=0)
        self.endTaskBtn = tk.Button(self.addBtnFrame, text="Zakończ zadanie", command=self.endTask, width=15, state=DISABLED)
        self.endTaskBtn.grid(column=1, row=0, padx=(20,10))
        self.deleteTaskBtn = tk.Button(self.addBtnFrame, text="Usuń zadanie", command=self.deleteTask, width=15, state=DISABLED)
        self.deleteTaskBtn.grid(column=2, row=0, padx=(10,20))
        self.shiftTaskBtn = tk.Button(self.addBtnFrame, text="Przesuń zadanie", command=self.shiftTask, width=15, state=DISABLED)
        self.shiftTaskBtn.grid(column=3, row=0)

        self.dateBtnsFrame = tk.Frame(self)
        self.dateBtnsFrame.grid(column=0, row=1)

        self.previousBtn = tk.Button(self.dateBtnsFrame, text="<", command=self.previousDate, width=4)
        self.previousBtn.grid(row=0, column=0)

        self.date = datetime.today()
        self.dataBtn = tk.Button(self.dateBtnsFrame, text=self.date.strftime('%Y-%m-%d'), command=self.pickDate, width=20)
        self.dataBtn.grid(row=0, column=1)

        self.nextBtn = tk.Button(self.dateBtnsFrame, text=">", command=self.nextDate, width=4)
        self.nextBtn.grid(row=0, column=2)

        self.taskFrame = tk.Frame(self)
        self.taskFrame.grid(column=0, row=2)

        self.treeScrollBar = ttk.Scrollbar(self.taskFrame)
        self.treeScrollBar.pack(side="right", fill='y')
        self.todoList = ttk.Treeview(self.taskFrame, yscrollcommand=self.treeScrollBar.set, selectmode="browse")
        self.todoList['columns']=('Nazwa','Priorytet','Data','Status')
        self.todoList.column('#0', width=0, stretch=NO)
        self.todoList.column('Nazwa', anchor=CENTER, width=250)
        self.todoList.column('Priorytet', anchor=CENTER, width=100)
        self.todoList.column('Data', anchor=CENTER, width=100)
        self.todoList.column('Status', anchor=CENTER, width=100)
        self.todoList.heading('#0', text='', anchor=CENTER)
        self.todoList.heading('Nazwa', text='Nazwa', anchor=CENTER)
        self.todoList.heading('Priorytet', text='Priorytet', anchor=CENTER)
        self.todoList.heading('Data', text='Data', anchor=CENTER)
        self.todoList.heading('Status', text='Status', anchor=CENTER)
        self.todoList.pack(side="left")
        self.treeScrollBar.config(command=self.todoList.yview)

        self.treeTaskView()
        self.todoList.bind('<<TreeviewSelect>>', self.item_selected)

    def item_selected(self, event):
            self.endTaskBtn.config(state=DISABLED)
            self.deleteTaskBtn.config(state=DISABLED) 
            self.shiftTaskBtn.config(state=DISABLED) 
            for selected_item in self.todoList.selection():
                item = self.todoList.item(selected_item)
                self.data = item['values']

            if 'Wykonano' in self.data:
                self.deleteTaskBtn.config(state=ACTIVE)  
            else:
                self.endTaskBtn.config(state=ACTIVE)
                self.deleteTaskBtn.config(state=ACTIVE)
                self.shiftTaskBtn.config(state=ACTIVE)  
        
    def treeTaskView(self):
        self.todoList.delete(*self.todoList.get_children())
        connection = sqlite3.connect('todo.db')
        cursorDB = connection.cursor()
        cursorDB.execute("SELECT * FROM tasks WHERE date=?", (self.date.strftime('%Y-%m-%d'),))
        tasks = cursorDB.fetchall()
        connection.commit()

        for task in tasks:
            self.todoList.insert('',tk.END, values=task)

        connection.close()

    def shiftTask(self):
        def shiftTasks():
            stringDate = calendar.get_date()
            self.date = datetime.strptime(stringDate, '%Y-%m-%d')
            try:
                self.dataBtn.config(text=self.date.strftime('%Y-%m-%d'))
                self.todoDate.config(text=self.date.strftime('%Y-%m-%d'))
                calendarWindow.destroy()
            except AttributeError:
                self.dataBtn.config(text=self.date.strftime('%Y-%m-%d'))
                calendarWindow.destroy()
            except tk.TclError:
                self.addTaskWindow.destroy()
                calendarWindow.destroy()
                
            connection = sqlite3.connect('todo.db')
            cursorDB = connection.cursor()
            cursorDB.execute("UPDATE tasks SET date=? WHERE name=? AND priority=? AND date=? AND status=?", (self.date.strftime('%Y-%m-%d'),self.data[0],self.data[1],self.data[2],self.data[3],))
            connection.commit()
            connection.close()
            self.endTaskBtn.config(state=DISABLED)
            self.deleteTaskBtn.config(state=DISABLED)
            self.shiftTaskBtn.config(state=DISABLED)
            self.treeTaskView()
            
        year = self.date.year
        month = self.date.month
        day = self.date.day
        calendarWindow = tk.Toplevel()
        calendarWindow.title('Kalendarz')
        calendar = Calendar(calendarWindow, selectmode='day', year=year, month=month, day=day, date_pattern='yyyy-mm-dd')
        calendar.pack()
        pickBtn = tk.Button(calendarWindow, text='Wybierz Datę', command=shiftTasks)
        pickBtn.pack(fill = BOTH, expand=True)
        
        


    def endTask(self):
        connection = sqlite3.connect('todo.db')
        cursorDB = connection.cursor()
        cursorDB.execute("UPDATE tasks SET status='Wykonano' WHERE name=? AND priority=? AND date=? AND status=?", (self.data[0],self.data[1],self.data[2],self.data[3],))
        connection.commit()
        connection.close()
        self.endTaskBtn.config(state=DISABLED)
        self.deleteTaskBtn.config(state=DISABLED)
        self.shiftTaskBtn.config(state=DISABLED)
        self.treeTaskView()
        

    def deleteTask(self):
        connection = sqlite3.connect('todo.db')
        cursorDB = connection.cursor()
        cursorDB.execute("DELETE FROM tasks WHERE name=? AND priority=? AND date=? AND status=?", (self.data[0],self.data[1],self.data[2],self.data[3],))
        connection.commit()
        connection.close()
        self.endTaskBtn.config(state=DISABLED)
        self.deleteTaskBtn.config(state=DISABLED)
        self.shiftTaskBtn.config(state=DISABLED)  
        self.treeTaskView()

    def addtask(self):
        def getData():
            
            stringStatusValue = 0
            if self.statusValue.get() == 1:
                stringStatusValue = 'Wykonano'
            elif self.statusValue.get() == 0:
                stringStatusValue = 'Todo'

            connection = sqlite3.connect('todo.db')
            cursorDB = connection.cursor()
            cursorDB.execute("INSERT INTO tasks VALUES(:taskName, :priority, :todoDate, :todoStatus)",
                {
                    'taskName': taskName.get(),
                    'priority': priority.get(),
                    'todoDate': self.date.strftime('%Y-%m-%d'),
                    'todoStatus': stringStatusValue
                })
            connection.commit()
            connection.close()

            self.treeTaskView()
            self.addTaskWindow.destroy()

        self.addTaskWindow = tk.Toplevel()
        self.addTaskWindow.title("Dodaj zadanie")

        priorityOptions = ['H','M','L']
        
        options1 = {}
        options2 = {"pady": 10, "sticky":"nsew", "padx": 10}
        options3 = {"padx": 10}

        taskNameLabel = tk.Label(self.addTaskWindow, text = "Nazwa")
        taskNameLabel.grid(column=0, row=0, **options3)
        taskName = tk.Entry(self.addTaskWindow, **options1)
        taskName.grid(column=1, row=0, **options2)

        priorityLabel = tk.Label(self.addTaskWindow, text = "Priorytet")
        priorityLabel.grid(column=0, row=1, **options3)
        priority = ttk.Combobox(self.addTaskWindow, value = priorityOptions, state='readonly', **options1)
        priority.grid(column=1, row=1, **options2)

        todoDateLabel = tk.Label(self.addTaskWindow, text="Data")
        todoDateLabel.grid(column=0, row=2, **options3)
        self.todoDate = tk.Button(self.addTaskWindow, text=self.date.strftime('%Y-%m-%d'), command=self.pickDate, **options1)
        self.todoDate.grid(column=1, row=2, **options2)

        self.statusValue = tk.IntVar()
        todoStatusLabel = tk.Label(self.addTaskWindow, text="Status")
        todoStatusLabel.grid(column=0, row=3, **options3)
        todoStatus = tk.Checkbutton(self.addTaskWindow, **options1, variable=self.statusValue, onvalue=1, offvalue=0)
        todoStatus.grid(column=1, row=3, **options2)

        addButton = tk.Button(self.addTaskWindow, text='Dodaj zadanie', command=getData, **options1, width=20)
        addButton.grid(column=0, row=4, columnspan=2, pady=20)


    def nextDate(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        try:
            self.date = self.date.replace(day=day+1)
        except ValueError:
            month = month+1
            if month == 13:
                month = 1
                year = year+1
                self.date = self.date.replace(day=1, month=month, year=year)
            else:
                self.date = self.date.replace(day=1, month=month)
        self.dataBtn.config(text=self.date.strftime('%Y-%m-%d'))
        self.endTaskBtn.config(state=DISABLED)
        self.deleteTaskBtn.config(state=DISABLED)
        self.shiftTaskBtn.config(state=DISABLED) 
        self.treeTaskView()

    def previousDate(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        try:
            self.date = self.date.replace(day=day-1)
        except ValueError:
            month = month-1
            if month == 0:
                month = 12
                year = year-1
                rangeMonth = monthrange(year, month)  
                self.date = self.date.replace(day=rangeMonth[1], month=month, year=year)
            else:
                rangeMonth = monthrange(year, month)
                self.date = self.date.replace(day=rangeMonth[1], month=month)
        self.dataBtn.config(text=self.date.strftime('%Y-%m-%d'))
        self.endTaskBtn.config(state=DISABLED)
        self.deleteTaskBtn.config(state=DISABLED)
        self.shiftTaskBtn.config(state=DISABLED) 
        self.treeTaskView()
        

    def pickDate(self):
        def selectDate():
            stringDate = calendar.get_date()
            self.date = datetime.strptime(stringDate, '%Y-%m-%d')
            self.endTaskBtn.config(state=DISABLED)
            self.deleteTaskBtn.config(state=DISABLED)
            self.shiftTaskBtn.config(state=DISABLED)  
            self.treeTaskView()
            try:
                self.dataBtn.config(text=self.date.strftime('%Y-%m-%d'))
                self.todoDate.config(text=self.date.strftime('%Y-%m-%d'))
                calendarWindow.destroy()
            except AttributeError:
                self.dataBtn.config(text=self.date.strftime('%Y-%m-%d'))
                calendarWindow.destroy()
            except tk.TclError:
                self.addTaskWindow.destroy()
                calendarWindow.destroy()
        
        year = self.date.year
        month = self.date.month
        day = self.date.day
        calendarWindow = tk.Toplevel()
        calendarWindow.title('Kalendarz')
        calendar = Calendar(calendarWindow, selectmode='day', year=year, month=month, day=day, date_pattern='yyyy-mm-dd')
        calendar.pack()
        pickBtn = tk.Button(calendarWindow, text='Wybierz Datę', command=selectDate)
        pickBtn.pack(fill = BOTH, expand=True)
             
if __name__ == '__main__':
    app = App()
    app.mainloop()