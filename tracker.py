from tkinter import *
import os
import sqlite3
import customtkinter

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
rootDir = os.path.dirname(os.path.abspath(__file__))


class App(customtkinter.CTk):
    width = 900
    height = 600

    def __init__(self):
        super().__init__()

        # configure window
        self.title("Task Tracker")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar1 frame
        self.filter_frame = customtkinter.CTkFrame(self)
        self.filter_frame.grid(row=0, column=0, padx=(
            20, 20), pady=(20, 0), sticky="nsew")
        self.filter_to_do = customtkinter.CTkButton(
            self.filter_frame, text='To Do', command=lambda: self.loadTask('TODO'))

        self.filter_to_do.grid(row=1, column=0, padx=20, pady=10, sticky="n")
        self.filter_done = customtkinter.CTkButton(
            self.filter_frame, text='Done', command=lambda: self.loadTask('DONE'))
        self.filter_done.grid(row=2, column=0, padx=20, pady=10, sticky="n")
        self.filter_all = customtkinter.CTkButton(
            self.filter_frame, text='All', command=lambda: self.loadTask('ALL'))
        self.filter_all.grid(row=3, column=0, padx=20, pady=10, sticky="n")

        # create sidebar2 frame
        self.task_frame = customtkinter.CTkFrame(self)
        self.task_frame.grid(row=1, column=0, padx=(
            20, 20), pady=(20, 0), sticky="nsew")
        self.task_delete = customtkinter.CTkButton(
            self.task_frame, text='Delete Task', command=self.delTask)
        self.task_delete.grid(row=1, column=0, padx=20, pady=10)
        self.task_done = customtkinter.CTkButton(
            self.task_frame, text='Mark Done', command=self.markDone)
        self.task_done.grid(row=2, column=0, padx=20, pady=10)
        self.task_undone = customtkinter.CTkButton(
            self.task_frame, text='Mark UnDone', command=self.markUnDone)
        self.task_undone.grid(row=3, column=0, padx=20, pady=10)

        # create sidebar3 frame
        self.task_new = customtkinter.CTkFrame(self)
        self.task_new.grid(row=2, column=0, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        self.task_name_entry = customtkinter.CTkTextbox(
            self.task_new, height=100, width=150)
        self.task_name_entry.grid(row=0, column=0, padx=10, pady=10)
        self.task_name_entry.insert("1.0", text="[Tag] Task Name")
        self.task_create = customtkinter.CTkButton(
            self.task_new, text="Add New Task", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.addTask)
        self.task_create.grid(row=1, column=0, padx=20, pady=10)

        # create Task View
        self.task_view_frame = customtkinter.CTkFrame(self)
        self.task_view_frame.grid(row=0, column=1, rowspan=3, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        self.task_view_area = Listbox(self.task_view_frame, width=79, height=28,
                                      selectmode=MULTIPLE, background='#474747', font=('Times', 15))
        self.task_view_area.grid(
            row=0, column=1, rowspan=3, pady=(0, 10), sticky="nsew")

        self.log_lable = customtkinter.CTkLabel(
            self.task_view_frame, text="Logger", font=customtkinter.CTkFont(size=15))
        self.log_lable.grid(row=3, column=1, padx=20, pady=(0, 5))

        self.loadTask('TODO')

    def connectToDb(self):
        if 'taskTracker.db' not in os.listdir(rootDir):
            conn = sqlite3.connect(os.path.join(rootDir, 'taskTracker.db'))

            conn.execute('''CREATE TABLE TRACKER
            (TASK_ID INTEGER PRIMARY KEY,
            TASK            TEXT     NOT NULL,
            STATE        INT);''')
            conn.commit()
            self.log_lable.configure(text="Created to taskTracker.db")
            return conn
        else:
            self.log_lable.configure(text="Connected to taskTracker.db")
            return sqlite3.connect(os.path.join(rootDir, 'taskTracker.db'))

    def loadTask(self, state):
        self.task_view_area.delete(0, END)
        conn = self.connectToDb()
        query = "SELECT * from TRACKER "
        self.task_done.configure(state="enabled")
        self.task_undone.configure(state="enabled")
        self.task_undone.configure()
        count = 0
        logText = f"All Task : "
        selectedColour = '#3498DB'
        deSelectedColour = '#154360'
        colourCode = [deSelectedColour, deSelectedColour, selectedColour]

        if state == 'TODO':
            colourCode = [selectedColour, deSelectedColour, deSelectedColour]
            query = query + "where STATE == 0 "
            self.task_done.configure(state="enabled")
            self.task_undone.configure(state="disabled")
            self.log_lable.configure(text="To Do")
            logText = f"To Do Task : "
        if state == 'DONE':
            colourCode = [deSelectedColour, selectedColour, deSelectedColour]
            query = query + "where STATE == 1 "
            self.task_done.configure(state="disabled")
            self.task_undone.configure(state="enabled")
            self.log_lable.configure(text="Completed Task")
            logText = f"Completed Task : "
        cursor = conn.execute(query)

        for i, row in enumerate(cursor):
            count = i+1
            task = (f'{row[0]} | {row[1]}\n')
            self.task_view_area.insert(i, task)
            self.task_view_area.itemconfig(i, {'fg': 'white'})
            if row[2] == 1:
                self.task_view_area.itemconfig(
                    i, {'fg': 'black', 'bg': '#58D68D'})

        self.filter_to_do.configure(fg_color=colourCode[0])
        self.filter_done.configure(fg_color=colourCode[1])
        self.filter_all.configure(fg_color=colourCode[2])

        conn.close()
        self.log_lable.configure(text=logText+str(count))

    def addTask(self):
        conn = self.connectToDb()
        task_name = self.task_name_entry.get("1.0", END)
        if task_name != '[Tag] Task Name\n':
            conn.execute(
                f"INSERT INTO TRACKER (TASK,STATE) VALUES ('{task_name}', 0 )")
            conn.commit()
            self.log_lable.configure(text=f'Created >> {task_name}')
        else:
            self.log_lable.configure(text='Enter Task Name')
        conn.close()
        self.task_name_entry.delete("1.0", END)
        self.task_name_entry.insert("1.0", text="[Tag] Task Name")
        self.loadTask('TODO')

    def markDone(self):
        if len(self.task_view_area.curselection()) != 0:
            for i in self.task_view_area.curselection():
                taskId = self.task_view_area.get(i).split(' | ')[0]
                conn = self.connectToDb()
                conn.execute(
                    f"UPDATE TRACKER set STATE = 1 where TASK_ID = {taskId}")
                conn.commit()
                conn.close()
                self.log_lable.configure(text=f'Updated as Done')
            self.loadTask('DONE')
        else:
            self.log_lable.configure(text='Select Any Task')

    def markUnDone(self):
        if len(self.task_view_area.curselection()) != 0:
            for i in self.task_view_area.curselection():
                taskId = self.task_view_area.get(i).split(' | ')[0]
                conn = self.connectToDb()
                conn.execute(
                    f"UPDATE TRACKER set STATE = 0 where TASK_ID = {taskId}")
                conn.commit()
                conn.close()
                self.log_lable.configure(text=f'Updated as Undone')
            self.loadTask('TODO')
        else:
            self.log_lable.configure(text='Select Any Task')

    def delTask(self):
        if len(self.task_view_area.curselection()) != 0:
            for i in self.task_view_area.curselection():
                taskId = self.task_view_area.get(i).split(' | ')[0]
                conn = self.connectToDb()
                conn.execute(
                    f"DELETE from TRACKER where TASK_ID = {taskId}")
                conn.commit()
                conn.close()
                self.log_lable.configure(text=f'Task Deleted')
            self.loadTask('TODO')
        else:
            self.log_lable.configure(text='Select Any Task')


if __name__ == "__main__":
    app = App()
    app.mainloop()
