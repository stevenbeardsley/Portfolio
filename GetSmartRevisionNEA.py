from tkinter import *
import datetime
import time
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import csv
import random
import matplotlib
from matplotlib.figure import Figure
import numpy as np
import smtplib, ssl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as soup
import urllib.request
from urllib.request import urlopen as uReq
import os
import hashlib
import binascii

root = Tk()
root.title("Steven Beardsley NEA")
root.geometry("400x400")

conn = sqlite3.connect(r"Steven_Coursework.db")
conn.execute("PRAGMA foreign_keys = 1")#enables foreign keys
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS account (userid INTEGER PRIMARY KEY,
                                    username VARCHAR(50) NOT NULL,
                                    password VARCHAR(50) NOT NULL ,
                                    firstname VARCHAR(50) NOT NULL,
                                    surname VARCHAR(50) NOT NULL,
                                    gender VARCHAR(50),
                                    email VARCHAR(50) )""")

c.execute("""CREATE TABLE IF NOT EXISTS class (classid INTEGER PRIMARY KEY,
                                subname TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS teacher (teacherid INTEGER PRIMARY KEY,
                                title TEXT,
                                surname TEXT,
                                username TEXT,
                                password TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS scjoin (userid INT,
                                classcode INTEGER,
                                totalhours INT,
                                averagehours INT,
                                FOREIGN KEY (classcode) REFERENCES teacherclassjoin(classcode),
                                FOREIGN KEY (userid) REFERENCES account(userid),
                                PRIMARY KEY (userid,classcode))""")


c.execute("""CREATE TABLE IF NOT EXISTS teacherclassjoin (classcode INTEGER PRIMARY KEY,
                                classid INTEGER,
                                teacherid INTEGER,
                                level TEXT,
                                FOREIGN KEY (teacherid) REFERENCES teacher(teacherid),
                                FOREIGN KEY (classid) REFERENCES class(classid))""")


c.execute("""CREATE TABLE IF NOT EXISTS stats (userid INT,
                                classcode INT,
                                DATE TIMESTAMP not null,
                                TIME TIMESTAMP not null,
                                hours INT,
                                yearday INT not null,
                                FOREIGN KEY (userid) REFERENCES account(userid),
                                FOREIGN KEY (classcode) REFERENCES teacherclassjoin(classcode),
                                PRIMARY KEY (userid,classcode,DATE,TIME))""")

c.execute("""CREATE TABLE IF NOT EXISTS flashcard (setid INT,
                                heading TEXT,
                                info TEXT) """)


c.execute("""CREATE TABLE IF NOT EXISTS flashcardjoin ( setid INTEGER PRIMARY KEY ,
                                userid INT ,
                                classcode INT,
                                title VARCHAR(50),
                                FOREIGN KEY (userid) REFERENCES account (userid),
                                FOREIGN KEY (classcode) REFERENCES teacherclassjoin (classcode)) """)

class Create_Login:#Login screen
    def __init__(self,master,c,conn):
        self.master = master
        self.c = c
        self.conn = conn
        self.TitleFrame = Frame(self.master)
        self.TitleLabel = Label(self.TitleFrame, text = "GetSmart Revision Tracker",font =("Comic Sans",12,'bold'), foreground = "green")
        self.TitleLabel.grid(row=0, column = 2, columnspan= 4,pady=5)

        self.MainFrame = Frame(self.master)
        self.AccLabel = Label(self.MainFrame, text= "Account type:")
        self.AccLabel.grid(row=1,column=1)
        self.accountclick = StringVar()
        self.accountclick.set("Student")
        self.AccountType = OptionMenu(self.MainFrame,self.accountclick,"Student","Teacher")
        self.AccountType.grid(row=1,column=2,columnspan=2)
        self.UsernameLabel=Label(self.MainFrame,text="Username",background="white")
        self.UsernameLabel.grid(row = 2, column = 1)
        self.UsernameEntry = Entry(self.MainFrame,width=30)
        self.UsernameEntry.grid(row = 2, column = 2, columnspan = 2,pady = 5)

        self.PasswordLabel = Label(self.MainFrame,text="Password",background = "white")
        self.PasswordLabel.grid(row = 3, column = 0,columnspan = 2, pady= 5)

        self.PasswordEntry = Entry(self.MainFrame,width = 30,show='*')
        self.PasswordEntry.grid(row = 3, column = 2, columnspan = 2)

        self.EnterButton = Button(self.MainFrame,text = "Login", command = self.Login,bg = "#90EE90")
        self.EnterButton.grid(row = 4, column = 2, pady= 15)

        self.CreateAccButton = Button(self.MainFrame, text="Sign Up",command = self.SignUp,bg = "#90EE90")
        self.CreateAccButton.grid(row = 4, column = 4,pady=20)

        self.TitleFrame.pack()
        self.MainFrame.pack()

    def Invalid(self):
        self.NW.destroy()
        Create_Login.ClearScreen(self)
        Create_Login(self.master,self.c,self.conn)

    def WrongDetails(self,message):#Wrong details popup showing its own error message
        self.NW = Toplevel()
        self.NW.geometry("200x120")
        self.NW.title('Revision tool')
        self.NW.config(bg= "#E00719")
        self.ErrorLabel = Label(self.NW,text= message,bg= "#E00719")
        self.ErrorLabel.pack(pady=10,padx=10)
        self.OkButton = Button(self.NW, text = 'OK', command = self.Invalid)
        self.OkButton.pack()



    def Login(self):
        self.username,self.password = self.GetEntry()
        #Check the database
        self.message = "Wrong details"
        if self.accountclick.get() == 'Student':
                self.c.execute("SELECT username FROM account WHERE username == '"+self.username+"'")
                if self.c.fetchall() == []:
                    self.WrongDetails('Username or password not found')
                else: ##username is correct
                    self.c.execute("SELECT password FROM account WHERE username == '"+self.username+"'")
                    StoredPassword = self.c.fetchone()[0]
                    Verify = EncryptPassword.CheckPassword(self,StoredPassword,self.password)
                    if Verify:
                        self.c.execute("SELECT userid FROM account WHERE username == '"+self.username+"' AND password == '"+StoredPassword+"'")
                        self.userid = self.c.fetchone()[0]
                        MainScreen(self.master,self.c,self.conn,self.userid)
                    else:
                        self.WrongDetails(self.message)

        if self.accountclick.get() == 'Teacher':
            self.c.execute("SELECT username FROM teacher WHERE username== '"+self.username+"'")
            if self.c.fetchall() == []:
                self.WrongDetails(self.message)
            else:
                self.c.execute("SELECT password FROM teacher WHERE username== '"+self.username+"' ")
                StoredPassword = self.c.fetchone()[0]
                Verify = EncryptPassword.CheckPassword(self,StoredPassword,self.password)
                if Verify:
                    self.c.execute("SELECT teacherid FROM teacher WHERE username == '"+self.username+"' AND password == '"+StoredPassword+"'")
                    self.teacherid = self.c.fetchone()[0]
                    l=TeacherMainScreen(self.master,self.c,self.conn,self.teacherid)

                else:
                    self.WrongDetails(self.message)





    def CheckDetails(self,password,username):

        #Check for username and password in database
        Message1 = "Password must be \n atleast 7 characters \n and involve a number \n and a capital letter"
        self.c.execute(f"SELECT username FROM account WHERE username== '{username}'")
        check = self.c.fetchall()
        if check != []:#username is taken already
            self.WrongDetails("Username is taken")
        else:
            if len(password) < 7:#password isnt long enough
                self.WrongDetails(Message1)
            NumCount = 0
            Upper = False

            for character in  password:
                if character.isnumeric() == True:
                     NumCount += 1
                if character.isupper() == True:
                    Upper = True

        NumCount=5
        Upper=True

    def SignUp(self):
        username,password = self.GetEntry()
        self.CheckDetails(password,username)#Checks passwords and username
        if self.accountclick.get() == "Student":
            self.UserLoginFrame = Frame(self.master)
            self.NameLabel = Label(self.UserLoginFrame, text = "First name:")
            self.NameLabel.grid(row =5, column = 2,pady=15)
            self.SurnameLabel = Label(self.UserLoginFrame,text = "Surname:")
            self.SurnameLabel.grid(row=6, column = 2,pady=15)
            self.NameEntry = Entry(self.UserLoginFrame, width = 30)
            self.NameEntry.grid(row =5, column = 3, columnspan = 2)

            self.SurnameEntry = Entry(self.UserLoginFrame,width = 30)
            self.SurnameEntry.grid(row = 6, column = 3, columnspan = 2 )
            self.GenderLabel =Label(self.UserLoginFrame,text = "Gender:")
            self.GenderLabel.grid(row=7,column = 2,pady=15)
            self.clicked = StringVar()
            self.clicked.set("Male")
            self.GenderEntry = OptionMenu(self.UserLoginFrame,self.clicked,"Male","Female","Other")
            self.GenderEntry.grid(row=7,column=3,columnspan=2)
            self.EmailLabel = Label(self.UserLoginFrame,text=' Address:')
            self.EmailLabel.grid(row=8,column=2)
            self.EmailEntry = Entry(self.UserLoginFrame, width=20)
            self.EmailEntry.grid(row=8,column=3)
            self.CreateButton = Button(self.UserLoginFrame, text= "Create", fg = "green",command = self.CreateAccount).grid(row = 8, column = 6,pady=15)
            self.UserLoginFrame.pack()

        if self.accountclick.get() == "Teacher":
            self.TeacherCreateAccount()

    def TeacherCreateAccount(self):
         #       self.Frame1 = LabelFrame(self.master, text = "NEA Revision Software ",bg = "#ADD8E6",width = 400,font = 15)
        #self.Frame1.pack(anchor = N, fill = "x", expand =False)
        self.TeacherFrame = LabelFrame(self.master,text="Teacher Details",bg="#ADD8E6",pady=25,padx=5)
        self.TeacherFrame.pack()

        if self.accountclick.get() == "Student":

            with self.conn:#inserts the values into the table
                self.c.executemany('INSERT INTO account (username,password,firstname,surname,gender,email) VALUES (?,?,?,?,?,?)',values)
            self.conn.commit()
        self.TitleLabel  = Label(self.TeacherFrame,text = "Title:",bg="#ADD8E6")
        self.TitleLabel.grid(row =0,column=0,pady=15,padx=10)
        self.TitleClick = StringVar()
        self.TitleClick.set("")
        self.TitleMenu = OptionMenu(self.TeacherFrame,self.TitleClick,"Mr","Ms","Dr")
        self.TitleMenu.grid(row=0,column=3)
        self.SurnameLabel = Label(self.TeacherFrame, text="Surname:",bg="#ADD8E6")
        self.SurnameLabel.grid(row=1,column=0,pady=10)
        self.SurnameEntry = Entry(self.TeacherFrame)
        self.SurnameEntry.grid(row=1,column=2,columnspan=2,pady=10)
        self.EnterButton = Button(self.TeacherFrame, text= "Enter", bg='#90EE90',padx=20,command =self.TeacherSignIn)
        self.EnterButton.grid(row=3,column=5,padx=20,pady=20)

    def TeacherSignIn(self):
        self.username,self.password = self.GetEntry()
        self.surname= self.SurnameEntry.get()
        self.title= self.TitleClick.get()
        self.password = EncryptPassword.HashPassword(self,self.password)

        values = [
                    (self.title,self.surname,self.username,self.password)
                ]
        with self.conn:#inserts the values into the table
            self.c.executemany('INSERT INTO teacher (title,surname,username,password) VALUES (?,?,?,?)',values)
        self.conn.commit()
        self.c.execute("SELECT teacherid FROM teacher WHERE username = '"+self.username+"'")
        self.teacherID = self.c.fetchone()
        TeacherMainScreen(self.master,self.c,self.conn,self.teacherID[0])




    def CreateAccount(self):
        self.firstname = self.NameEntry.get()
        self.username, self.password = self.GetEntry()
        self.lastname = self.SurnameEntry.get()
        self.gender = self.clicked.get()
        self.Email = self.EmailEntry.get()
        self.HashPassword = EncryptPassword.HashPassword(self,self.password)

        values = [
                    (self.username,self.HashPassword,self.firstname,self.lastname,self.gender,self.Email)
                        ]
        if self.accountclick.get() == "Student":


            with self.conn:#inserts the values into the table
                self.c.executemany('INSERT INTO account (username,password,firstname,surname,gender,email) VALUES (?,?,?,?,?,?)',values)
            self.conn.commit()
            #GETS USER ID
            self.c.execute("SELECT userid FROM account WHERE username = '"+self.username+"'")
            self.userid = self.c.fetchone()[0]

            self.ValidateDetails(self.username,self.password)

    def GetEntry(self):
        username = self.UsernameEntry.get()
        password = self.PasswordEntry.get()
        return username, password

    def ValidateDetails(self,username,password):
        self.ClearScreen()
        MainScreen(self.master,self.c,self.conn,self.userid)

    def ClearScreen(self):#Clears the screen, utility method
        list = self.master.pack_slaves()
        for l in list:
            l.destroy()
        grid = self.master.grid_slaves()
        for l in grid:
            l.destroy()





class TeacherMainScreen(Create_Login):
    def __init__(self,master,c,conn,teacherID):
        self.Dictionary = {}
        super().__init__(master,c,conn)#instantiates from the previous class
        self.teacherID=teacherID
        self.ClearScreen()
        self.PrintAccountDetails()
        self.TitleFrame = Frame(self.master,bg="#98FB98")
        self.TitleFrame.pack(expand= True, fill= "both",anchor =N,ipady=20)
        self.ClassFrame = Frame(self.master, bg="white")
        self.ClassFrame.pack(expand=True,fill="both",anchor=N,ipady=90)
        self.CheckClass()
        self.GetTeacherName()
        self.Label1= Label(self.TitleFrame, text=f"{self.FullName} Homepage",font=('Helvetica',20),bg="#98FB98").pack()
        self.Menu = Menu(master)
        self.master.config(menu =self.Menu)#configs menu to be used
        self.ExitMenu= Menu(self.Menu)
        self.Menu.add_cascade(label = "Exit", menu =self.ExitMenu)
        self.ExitMenu.add_command(label = "Exit", command = master.quit)
        ###checks for classes
        self.ClassMenu = Menu(self.Menu)
        self.LogMenu = Menu(self.Menu)
        self.Menu.add_cascade(label = "Class", menu=self.ClassMenu)
        self.ClassMenu.add_cascade(label = "Add Class",command =self.GenerateClass)
        self.ClassMenu.add_cascade(label= "Delete Class", command = self.DeleteClassScreen)
        self.Menu.add_cascade(label='Log Out',menu = self.LogMenu)
        self.LogMenu.add_cascade(label="Logout",command=self.LogOut)
        self.ProfileMenu = Menu(self.Menu)
        self.Menu.add_cascade(label='Profile',menu=self.ProfileMenu)
        self.ProfileMenu.add_command(label='Profile',command= lambda : Profile(self.master,self.c,self.conn,self.teacherID,'teacher'))
        self.HomepageMenu = Menu(self.Menu)
        self.Menu.add_cascade(label='Homepage',menu=self.HomepageMenu)
        self.HomepageMenu.add_command(label='Homepage',command = lambda: TeacherMainScreen(self.master,self.c,self.conn,self.teacherID))

        ##Class Frame
    def DeleteClassScreen(self):
        self.top = Toplevel()
        self.top.geometry("300x150")
        self.top.title('Revision tool')
        self.top.config(bg= "#EA5252")
        self.Title=Label(self.top,text="Delete Class",font =('Helvetica',12,'bold'),fg="white",bg="#EA5252")
        self.Title.grid(row=0,column=0,ipadx=10,pady=5)
        self.IDLabel = Label(self.top,text="Enter the classID:",font =('Helvetica',10),fg="black",bg="#EA5252")
        self.IDLabel.grid(row=1,column=0,padx=10,pady=10)
        self.IDEntry = Entry(self.top,width=10)
        self.IDEntry.grid(row=1,column=1)
        check=[]
        self.DeleteButton = Button(self.top,text="Delete",command = self.DeleteClass)
        self.DeleteButton.grid(row=2,column=0)

    def DeleteClass(self):
        classcode = self.IDEntry.get()
        ##check they are assigned to the class
        self.c.execute(f"SELECT * FROM teacherclassjoin WHERE classcode == '{classcode}' AND teacherid == '{self.teacherID}'")
        classes = self.c.fetchall()
        if classes == []:#class does not exist
            self.Invalid = Label(self.top,text = "Invalid Class Entered",font =('Helvetica',10,"bold"),fg="black",bg="#EA5252")
            self.Invalid.grid(row=5,column=0)
        else:
            with self.conn:
                self.c.execute(f"DELETE FROM scjoin WHERE classcode == '{classcode}'")
                self.c.execute(f"DELETE FROM stats WHERE classcode == '{classcode}'")
                self.c.execute(f"DELETE  FROM teacherclassjoin WHERE classcode =='{classcode}' AND teacherid == '{self.teacherID}'")
            self.top.destroy()
            Create_Login.ClearScreen(self)
            l =TeacherMainScreen(self.master,self.c,self.conn,self.teacherID)

    def LogOut(self):
        MainScreen.LogOut(self)

    def GetTeacherName(self):
        self.c.execute("SELECT surname FROM teacher WHERE teacherid == '"+self.teacherID+"'")
        self.surname = self.c.fetchone()[0]
        self.c.execute("SELECT title FROM teacher WHERE teacherid == '"+self.teacherID+"'")
        self.title=self.c.fetchone()[0]
        self.FullName = self.title + " "+ self.surname

    def PrintAccountDetails(self):
        self.teacherID=str(self.teacherID)
        self.c.execute("SELECT * FROM teacher WHERE teacherid =='"+self.teacherID+"'")
        details = self.c.fetchall()
        self.c.execute("SELECT * FROM teacherclassjoin WHERE teacherid == '"+self.teacherID+"'")
        AccountDetails = self.c.fetchall()

    def CheckClass(self):
        self.c.execute("SELECT * FROM teacherclassjoin WHERE teacherid== '"+str(self.teacherID)+"'")
        check= self.c.fetchall()
        colourwheel = ["#28BFBF","#287BBF","#3D1EC7","#EBBC15","#EB1535","#DE8C98","#8CDEDC","#10E052","#B6F2C9"]
        if len(check) ==0:##No classes already
            self.NoClassesLabel = Label(self.ClassFrame, text="You have no current classes",font =('Helvetica',12),bg="white")
            self.NoClassesLabel.pack()
        else:
            self.idlist = []
            self.buttonlist=[]
            for x in range (len(check)):##for as many classes as there already are
                self.colour = colourwheel[random.randint(0,len(colourwheel)-1)]
                Class = check[x-1]

                classid= str(Class[1])
                classcode = str(Class[0])
                self.idlist.append(classcode)
                level = Class[3]
                self.c.execute("SELECT subname FROM class WHERE classid == '"+classid+"'")
                subname = self.c.fetchone()

                self.Frame = LabelFrame (self.ClassFrame, text = f"Class {x+1}",bg=self.colour)
                self.Frame.grid(row=x,column=0,ipadx=50,pady=10)
                self.buttonlist.append(Button(self.Frame, text = subname,bg="white",command = lambda x=x: self.GoToClassScreen(x)))
                self.buttonlist[x].pack()
                self.Description = Label(self.Frame, text = f"Class Code: {classcode} \n Level: {level}",bg=self.colour)
                self.Description.pack()

    def GoToClassScreen(self,buttonid):
        button =  (self.buttonlist[buttonid])
        Create_Login.ClearScreen(self)
        classcode = self.idlist[buttonid]
        Class_Screen(self.master,self.c,self.conn,self.teacherID,self.colour,classcode)

    def GenerateClass(self):
        self.ClearScreen()
        self.Frame1 = LabelFrame(self.master,bg="white")
        self.Frame1.pack(fill=BOTH,ipady=300)
        self.TitleLabel = Label(self.Frame1,text="Create a new class",font=('Helvetica',20),bg="white",fg="green")
        self.TitleLabel.grid(row=0,column=0,padx=0,columnspan=12,sticky='NSEW')
        self.SubjectLabel = Label(self.Frame1,text="Information:", font=('Helvetica',10),bg='white')
        self.SubjectLabel.grid(row=2,column=6,sticky= 'NSEW')
        self.SubjectMenu = Listbox(self.Frame1,bd=5)
        self.GetClassList()
        for classes in sorted(self.ClassList):#Inserts classes into the list box alphabetically
            self.SubjectMenu.insert(END,classes)

        self.SubjectMenu.grid(row=3,column=6,sticky='NSEW',rowspan=3)
        self.CreateClassButton = Button(self.Frame1,text="Add class",command = self.AddClassGUI)
        self.CreateClassButton.grid(row=3,column=7)
        self.Subclicked = StringVar()
        self.Subclicked.set("Academic level")
        self.LevelMenu = OptionMenu(self.Frame1,self.Subclicked,"GCSE","A Level")
        self.LevelMenu.grid(row=7,column=6,sticky='NSEW')
        self.CreateButton = Button(self.Frame1, text= "Create new class", font= ('Helvetica',10), bg="#90EE90", activebackground = "#2d912c", command = self.AddClass)
        self.CreateButton.grid(row=7,column=8,columnspan=3,sticky='W',pady=5,padx=50)

    def InsertClass(self):
        subject = self.ClassNameEntry.get()
        self.ClassList.append(subject)
        self.SubjectMenu.insert(END,subject)
        self.ClassNameEntry.delete(0,END)

    def AddClassGUI(self):
        self.ClassNameEntry= Entry(self.Frame1)
        self.ClassNameEntry.insert(0,"classname")
        self.ClassNameEntry.grid(row=3,column=8,columnspan=2)
        self.SubmitButton = Button(self.Frame1, text="Submit",command = self.InsertClass,bg="#63EC0D")
        self.SubmitButton.grid(row=3,column=10)

    def GetClassList(self):
        self.c.execute("SELECT subname FROM class")#Returns classlist
        self.ClassList = self.c.fetchall()

    def AddClass(self):
        self.SubjectName = self.SubjectMenu.get(ANCHOR)
        if not self.SubjectName:
            messagebox.showerror('Error','Class must have a name')
            self.GenerateClass()
        if self.SubjectName:

            if type(self.SubjectName) == tuple:
                self.SubjectName = self.SubjectName[0]

            self.Level = self.Subclicked.get()
            self.c.execute("SELECT classid FROM class WHERE subname=='"+self.SubjectName+"'" )
            check = self.c.fetchall()

            if len(check)== 0:##Class does not exist already
                values = [
                            (None,self.SubjectName)
                        ]
                self.c.executemany("INSERT INTO class VALUES (?,?)",(values))
                self.conn.commit()
            self.SubmitClass()


    def SubmitClass(self):
        ###Once the class is in the database
        ##Insert class details into classteacherjoin
        self.c.execute("SELECT classid FROM class WHERE subname == '"+self.SubjectName+"'")
        self.ClassID= self.c.fetchone()[0]
        values = [
                    (None,self.ClassID,self.teacherID,self.Level)
            ]
        with self.conn:
            self.c.executemany("INSERT INTO teacherclassjoin VALUES (?,?,?,?)",values)
        self.ClearScreen()
        TeacherMainScreen(self.master,self.c,self.conn,self.teacherID)
    def ClearScreen(self):
        Create_Login.ClearScreen(self)



class Class_Screen(TeacherMainScreen):
    def __init__(self,master,c,conn,teacherID,colour,classcode):#Createes class sreen and involving windows
        super().__init__(master,c,conn,teacherID)
        Create_Login.ClearScreen(self)
        self.colour = colour
        self.classcode = classcode
        colour = '#4CD9D9'
        self.GetDetails()
        ##Create the GUI
        Create_Login.ClearScreen(self)

        self.HeadingFrame = Frame(self.master,bg= colour)
        self.HeadingFrame.pack(anchor=N,fill="x",expand=True,ipady=10)
        self.Title = Label(self.HeadingFrame, text = self.Class[1],font =("Big Caslon",20),bg=colour)
        self.Title.pack()
        self.IDLabel = Label(self.HeadingFrame,text = f'Class ID: {self.classid}',bg=colour)
        self.IDLabel.pack()
        self.Notebook = ttk.Notebook(self.master)
        self.MainFrame = Frame(self.Notebook, bg="white")
        self.MainFrame.pack(fill= BOTH,side=BOTTOM,expand =True)
        #EmailFrame##################################
        self.EmailFrame = Frame(self.Notebook)
        self.Header = Label(self.EmailFrame, text = 'Send Mail',font =("Big Caslon",15))
        self.Header.grid(row=0,column=4)
        self.SendToLabel = Label(self.EmailFrame, text='Send to:')
        self.SendToLabel.grid(row=2,column=1,padx=10)
        self.EmailFrame.pack(fill= BOTH,side=BOTTOM,expand =True)
        self.GetClassList()
        self.ClassListFrame =Frame(self.EmailFrame)
        self.scrollbar = Scrollbar(self.ClassListFrame,orient = VERTICAL)

        self.ClassList = Listbox(self.ClassListFrame,yscrollcommand=self.scrollbar.set,height=5,selectmode=MULTIPLE)
        self.scrollbar.config(command=self.ClassList.yview)
        for Class in self.classlist:
            self.ClassList.insert(END, Class)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.ClassList.pack()
        self.ClassListFrame.grid(row=2,column=2,columnspan=3,pady=5)
        self.SubjectLabel = Label(self.EmailFrame,text = 'Subject')
        self.SubjectLabel.grid(row=3,column=1,pady=5)
        self.Subject = Text(self.EmailFrame,width=20,height=1, font=('bold'))
        self.Subject.grid(row=3,column=2,padx=5,columnspan=4)
        self.MessageLabel = Label(self.EmailFrame, text='Message')
        self.MessageLabel.grid(row=4,column=1,pady=5)
        self.Message = Text(self.EmailFrame,width=30,height=5)
        self.Message.grid(row=4,column=2,columnspan=4)
        self.Send = Button(self.EmailFrame, text ='Send',bg='#90EE90',command =self.GetRecievers)
        self.Send.grid(row=5,column=5)
        ######################################
        self.Notebook.pack(ipady=200,expand=1,ipadx=200,fill=BOTH)
        self.Notebook.add(self.MainFrame,text= "Main Page")
        self.Notebook.add(self.EmailFrame,text= "Mail")

        ###MainPage
        self.TPLabel =  Label(self.MainFrame, text = "Top Performers",bg='white',font =('Helvetica',16))
        self.TPLabel.grid(row=0,column=0,rowspan=2)
        self.CreateTopPerformers()
        self.TP.grid(row=2,column=0,padx=5,columnspan=5)

        self.GetAvRev()

        self.BackButton = Button(self.MainFrame, text = "Back", command = lambda: TeacherMainScreen(self.master,self.c,self.conn,self.teacherID),bg='#F43737')
        self.BackButton.grid(row=8,column=0,ipadx=7,ipady=2)
        self.ClassScreenButton = Button(self.MainFrame,text="Open Class Database",bg=colour,command = lambda: Class_DBScreen(self.master,self.c,self.conn,self.teacherID,colour,self.classcode) )
        self.ClassScreenButton.grid(row=8,column=3,pady=10,ipady=1)
        ##Rank Page
        self.RankFrame = Frame(self.Notebook)
        self.FillRankFrame()
        self.RankFrame.pack(fill= BOTH,side=BOTTOM,expand =True)
        self.Notebook.add(self.RankFrame,text="Rankings")

    def FillRankFrame(self):
        Header = Label(self.RankFrame, text="Class Ranking",font=('Comic Sans',17,'bold'))
        Header.grid(row=0,column=0)
        self.c.execute("SELECT teacherid FROM teacherclassjoin WHERE classid =='"+self.classid+"'")
        teacherlist = self.c.fetchall()
        if teacherlist == []:#No students in class
            Label1 = Label(self.RankFrame, text = "No students are in this class!",font =("Arial",15),fg='red')
            Label1.grid(row=4,column=0,padx=10)
        else:
            self.ClassDetails = []
            for teacher in teacherlist:
                #Get teacher name
                self.c.execute("SELECT title, surname FROM teacher WHERE teacherid == '"+str(teacher[0])+"'")
                title,surname = self.c.fetchone()
                self.c.execute("SELECT classcode FROM teacherclassjoin WHERE classid == '"+self.classid+"' AND teacherid == '"+str(teacher[0])+"'")#Gets all the Classes
                classlist = self.c.fetchall()
                for classcode in classlist:
                    classcode = classcode[0]
                    self.c.execute("SELECT totalhours FROM scjoin WHERE classcode == '"+str(classcode)+"'")
                    HourList = self.c.fetchall()
                    TotalHours = 0
                    for hour in HourList:
                        TotalHours += hour[0]
                    #Get hours pp
                    size = len(HourList)
                    if TotalHours== 0 or size == 0 :
                        Class = (title+ ' '+ surname,0,0,classcode)
                    else:
                        PPhours = TotalHours// size
                        Class = (title+ ' '+ surname,TotalHours,PPhours,classcode)
                    self.ClassDetails.append(Class)

            self.Sort()
            self.ClassDetails.reverse()
            for Class in self.ClassDetails:
                if int(Class[3]) == int(self.classcode):
                    rank = self.ClassDetails.index(Class) + 1
            style = ttk.Style()
            style.theme_use('default')
            self.RankTableFrame = Frame (self.RankFrame)
            self.RankTableFrame.grid(row=2,column=0,padx=5,pady=10)
            self.TreeScroll = Scrollbar(self.RankTableFrame)

            self.RankTable = ttk.Treeview(self.RankTableFrame,height=3,yscrollcommand=self.TreeScroll.set)
            self.TreeScroll.pack(side =RIGHT, fill=Y)
            self.RankTable['columns'] = ('Place','Teacher','Total Hours','Hours per person')
            self.RankTable.column("#0",width=0,stretch=NO)
            self.RankTable.column("Place",anchor=W,width=40)
            self.RankTable.column("Teacher",anchor=W,width=80)
            self.RankTable.column("Total Hours",anchor=W,width=70)
            self.RankTable.column("Hours per person",anchor=CENTER,width=100)
            #Create Headings
            self.RankTable.heading("#0",text='',anchor=W)
            self.RankTable.heading('Place',text='Place',anchor=W)
            self.RankTable.heading('Teacher',text='Teacher',anchor=W)
            self.RankTable.heading('Total Hours',text='Total Hours',anchor=W)
            self.RankTable.heading('Hours per person',text = "Hours per person",anchor=W)
            self.RankTable.pack()
            self.TreeScroll.config(command=self.RankTable.yview)
            count = 0
            for Class in self.ClassDetails:

                self.RankTable.insert(parent='',index='end',iid=count, values = (count+1,Class[0],Class[1],Class[2]),tags='blue')
                count+=  1
            self.c.execute("SELECT title,surname FROM teacher WHERE teacherid == '"+self.teacherID+"'")
            name = self.c.fetchone()
            name = name[0]+name[1]
            for Class in self.ClassDetails:
                if Class[0] == name:
                    rank = self.ClassDetails.index(Class) + 1


            count += 1
            self.font = ('Comic Sans',13,'bold')
            message = Label(self.RankFrame, text=f"Your class ranks number {rank}",font = self.font)
            message.grid(row=3,column=0)

            if rank == 1:
                label = Label(self.RankFrame,text="Well done!",fg='green',font = self.font)
            if rank <  4  and rank != 1:
                label = Label(self.RankFrame,text='On the podium',font=self.font,fg='orange')
            if rank > 3:
                label =Label (self.RankFrame, text='Keep trying',font=self.font,fg='red')
            label.grid(row=4,column=0)

    def Sort(self):
        ##Bubble sort
        length= len(self.ClassDetails)
        for i in range (0,length-1):#iterates thrpugh each element in the list
            for j in range (0,length-1-i):#Compares each element with the elements infront
                if self.ClassDetails[j][1] >self.ClassDetails[j+1][1]:
                    self.ClassDetails[j],self.ClassDetails[j+1] = self.ClassDetails[j+1],self.ClassDetails[j]#Swaps if the number is greater


    def GetAvRev(self):#Calculates the average revision time for a class
        self.c.execute(f"SELECT averagehours FROM scjoin WHERE classcode=='{self.classcode}'")
        RevTimes = self.c.fetchall()
        if RevTimes == []:
            self.total = 0
        else:
            self.total = 0
            for time in RevTimes:#gets mean of revision time
                self.total += time[0]
            self.total = self.total// len(RevTimes)
        if self.total <3:
            colour = "red"
        elif self.total <3 and self.total< 5:#Determines the colour depedant on the mean
            colour = "orange"
        elif self.total> 4:
            colour = "green"
        self.RevLabel = Label(self.MainFrame, text='Your class average revision time is, ', bg='white')
        self.RevLabel.grid(row=4,column=0)
        self.TimeLabel = Label(self.MainFrame, text = f'{self.total}',bg='white',fg=self.colour,font=('Comic Sans MS',15,'bold'))
        self.TimeLabel.grid(row=4,column=2)
        if self.total == 1:
            self.Label = Label (self.MainFrame, text = "hour per week",bg='white')
        elif self.total > 1 or self.total == 0:
             self.Label = Label (self.MainFrame, text = "hours per week",bg='white')

        self.Label.grid(row=4,column=3)

    def CreateTopPerformers(self):
        self.TP = ttk.Treeview(self.MainFrame,height=3)

        self.TP['columns'] = ('Name','Surname','Total', 'Average')
        self.TP.column("#0",width=0,stretch=NO)
        self.TP.column("Name",anchor=W,width=60)
        self.TP.column("Surname",anchor=W,width=60)
        self.TP.column("Total",anchor=CENTER,width=40)
        self.TP.column("Average",anchor=W,width=40)
        #Create Headings
        self.TP.heading("#0",text='',anchor=W)
        self.TP.heading('Name',text='Name',anchor=W)
        self.TP.heading('Surname',text='Surname',anchor=W)
        self.TP.heading('Total',text = "Total",anchor=CENTER)
        self.TP.heading("Average",text = 'Average')

        self.c.execute(f"SELECT * FROM scjoin WHERE classcode== '"+self.classcode+"'")
        self.classlist = self.c.fetchall()
        self.classlist.sort(key=lambda tup: tup[3],reverse=True)
        count = 0
        for student in self.classlist:
            self.c.execute(f"SELECT firstname, surname FROM account WHERE userid == '{student[0]}'")
            firstname, surname = self.c.fetchone()
            self.TP.insert(parent='',index='end',iid=count, values = (firstname,surname,student[2],student[3]),tags='blue')#Inserts each student into the table
            count += 1

    def GetRecievers(self):
        #get selected students
        Students = self.ClassList.curselection()
        EmailList = []
        if not Students:
            messagebox.showerror('Error','No students are selected')#Error handling if no students are selected
        if Students:
            for Student in Students:
                user = self.classlist[Student]
                userid = user[0]
                self.c.execute("SELECT email FROM account WHERE userid == '"+str(userid)+"'")
                EmailList.append(self.c.fetchone()[0])

            Subject = self.Subject.get('1.0',END)
            Message = self.Message.get('1.0',END)
            for email in EmailList:
                Send_Email(self.master,self.c,self.conn,email,Subject,Message)

    def GetClassList(self):
        self.c.execute("SELECT classcode FROM teacherclassjoin WHERE classid =='"+self.classid+"' AND teacherid =='"+self.teacherID+"'")
        self.classcode =str( self.c.fetchone()[0])
        self.c.execute("SELECT userid FROM scjoin WHERE classcode == '"+self.classcode+"'")
        IDlist = self.c.fetchall()
        self.classlist=[]
        for ID in IDlist:
            self.c.execute("SELECT firstname, surname FROM account WHERE userid == '"+str(ID[0])+"'")
            name = self.c.fetchone() + ID
            self.classlist.append(name)

    def GetDetails(self):
        self.c.execute("SELECT classid FROM teacherclassjoin WHERE teacherid == '"+self.teacherID+"'  AND classcode == '"+self.classcode+"'")
        self.classid = str(self.c.fetchone()[0])
        self.c.execute("SELECT * FROM class WHERE classid == '"+self.classid+"'")
        self.Class = self.c.fetchone()

class Send_Email():
    def __init__(self,master,c,conn,emaillist,subject,message):
        self.master = master
        self.c = c
        self.conn= conn
        self.Emails = emaillist
        self.subject= subject
        self.text = message
        self.port = 587  # For starttls
        self.smtp_server = "smtp.gmail.com"
        self.context = ssl.create_default_context()
        self.SenderEmail = 'getsmartrevision@gmail.com'
        self.Password = 'coursework'
        self.FormatMessage()
        self.Send()

    def FormatMessage(self):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.SenderEmail

        #Creates a plain text and html version of the message
        text = f"{self.subject} \ {self.text}"
        html = f"""\
        <html>
          <head></head>
          <body>
            <p>{self.subject}<br>
               {self.text}
            </p>
          </body>
        </html>
        """
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.message = msg.as_string()

    def Send(self):
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            for reciever in self.Emails:
                server.starttls(context=self.context)
                server.login(self.SenderEmail,self.Password)#Logs into GetSmart gmail account
                server.sendmail(self.SenderEmail, reciever, self.message)#Sends email


class Class_DBScreen(Class_Screen):
    def __init__(self,master,c,conn,teacherID,colour,classid):
        super().__init__(master,c,conn,teacherID,colour,classid)
        self.window = Toplevel()
        self.colour = '#ADD8E6'
        self.window.geometry("700x400")
        self.window.title('Class Database')
        self.window.config(bg= "#ADD8E6")
        self.Title = Label(self.window, text="Class Database", bg= '#ADD8E6',font=("Helvetica",20,'bold'))
        self.Title.grid(row=0,column=3)
        self.DBFrame = Frame(self.window, bg=self.colour)
        self.CreateTable()
    def CreateTable(self):
        style = ttk.Style()
        style.theme_use('default')

        self.DB = ttk.Treeview(self.DBFrame,height=12)

        self.DB['columns'] = ('ID','Name','Surname','Total', 'Average')
        self.DB.column("#0",width=0,stretch=NO)
        self.DB.column("ID",width=50,stretch=NO)
        self.DB.column("Name",anchor=W,width=100)
        self.DB.column("Surname",anchor=W,width=100)
        self.DB.column("Total",anchor=CENTER,width=100)
        self.DB.column("Average",anchor=W,width=100)
        #Create Headings
        self.DB.heading("#0",text='',anchor=W)
        self.DB.heading("ID",text='ID',anchor= CENTER)
        self.DB.heading('Name',text='Name',anchor=W)
        self.DB.heading('Surname',text='Surname',anchor=W)
        self.DB.heading('Total',text = "Total",anchor=CENTER)
        self.DB.heading("Average",text = 'Average')


        self.DBFrame.grid(row=2,column=0,rowspan=5,columnspan=5)

        self.GetID()

        self.DetailsFrame = Frame(self.window,bg=self.colour)
        self.SearchLabel = Label(self.DetailsFrame, text='Search surname',bg=self.colour)
        self.SearchLabel.grid(row=0,column=2)
        self.SearchEntry = Entry(self.DetailsFrame,width=20)
        self.SearchEntry.grid(row=0,column=3)
        self.SearchButton = Button(self.DetailsFrame, text="Search",bg='#ADD8E6',command =lambda: self.SearchDB(self.SearchEntry.get()))
        self.SearchButton.grid(row=1,column=3)
        self.DeleteButton = Button(self.DetailsFrame,text="Delete Student",command = self.DeleteStudent)
        self.DeleteButton.grid(row=2,column=3,pady=10)
        self.SaveButton = Button(self.DetailsFrame, text='Save table',command= self.SaveTable)
        self.SaveButton.grid(row=3,column=3,pady=10)
        self.ResetButton = Button(self.DetailsFrame, text= 'Reset',command = self.CreateTable)
        self.ResetButton.grid(row=10,column=3)
        self.DetailsFrame.grid(row=2,column=5)
    def DeleteStudent (self):
        #Get selected student
        student = self.DB.item(self.DB.focus())
        userid = str(student['values'][0])
        ##Delete student from databases
        with self.conn:
            self.c.execute("DELETE FROM stats WHERE userid == '"+userid+"' AND classcode == '"+self.classid+"'")
            self.c.execute("DELETE FROM scjoin WHERE userid == '"+userid+"' AND classcode == '"+self.classid+"'")

        self.CreateTable()
    def FormatName(self):
        TeacherMainScreen.GetTeacherName(self)#Get Teacher Name
        self.c.execute("SELECT subname FROM class WHERE classid == '"+self.classid+"'")
        subname = self.c.fetchone()[0]
        self.FileName = (f'{self.FullName}_{subname}.csv')
    def SaveTable(self):
        self.FormatName()
        with open(self.FileName, "w", newline='') as myfile:
            csvwriter = csv.writer(myfile, delimiter=',')

            for row_id in self.DB.get_children():
                row = self.DB.item(row_id)['values']
                csvwriter.writerow(row)

    def DeleteTreeview(self):
        for item in self.DB.get_children():
            self.DB.delete(item)
    def SearchDB(self,surname):
        self.c.execute("SELECT userid FROM account WHERE surname = '"+surname+"'")#Searches for student by surname in database
        result = self.c.fetchall()

        if not result:#Error handling if student is not in class
            self.NoResult = Label(self.DetailsFrame, text= 'No student found')
            self.NoResult.grid(row=7,column=3)
        self.EnterValues(result)

    def GetID(self):
        self.c.execute("SELECT userid FROM scjoin WHERE classcode == '"+self.classcode+"'")
        self.classlist= self.c.fetchall()
        self.EnterValues(self.classlist)

    def EnterValues(self,classlist):
        count = 0
        self.DeleteTreeview()
        for student in classlist:
            student = str(student[0])
            self.c.execute("SELECT firstname,surname FROM account WHERE userid == '"+str(student)+"'")
            firstname,surname = self.c.fetchone()
            self.c.execute(f"SELECT totalhours,averagehours from scjoin WHERE classcode == '{self.classcode}' AND userid == '{student}'")
            totalhours, averagehours = self.c.fetchone()
            self.DB.tag_configure('oddrow',background='white')
            self.DB.tag_configure('evenrow',background='#ADD8E6')
            if count % 2 == 0:
                self.DB.insert(parent ='',index='end',iid=count,text='',values= (student,firstname,surname,totalhours,averagehours),tags=('evenrow',))
            else:
                self.DB.insert(parent='',index='end',iid=count,text='', values = (student,firstname,surname,totalhours,averagehours),tags=('oddrow',))

            count += 1
        self.DB.grid(row=0,column=0,columnspan=5,rowspan=5)



class MainScreen():#Homepage
    def __init__(self,master,c,conn,userid):
        self.master = master
        self.userid = str(userid)
        self.c = c
        self.conn = conn
        #Creates the frames
        Create_Login.ClearScreen(self)
        self.Frame1 = LabelFrame(self.master, text = "NEA Revision Software ",bg = "#ADD8E6",width = 400,font = 15)
        self.Frame1.pack(anchor = N, fill = "x", expand =False)
        self.TitleLabel = Label(self.Frame1, text = "GetSmart revision tracker software",bg = "#ADD8E6")
        self.TitleLabel.grid(row =0, column = 0,columnspan=2 )
        self.c.execute("SELECT firstname FROM account WHERE userid== '"+self.userid+"'")
        name = self.c.fetchone()[0]
        self.WelcomeLabel = Label(self.Frame1,text = f"Hello, welcome back {name}",bg = "#ADD8E6")
        self.WelcomeLabel.grid(row = 1, column = 1,sticky = W+E)

        self.Frame2 = LabelFrame(master,bg="white")
        self.Frame2.pack(anchor=W,fill="both",expand=True)


        self.Class1Frame = Frame(self.Frame2,bg ='#FFFF66',height =100)
        self.Class1Frame.pack(anchor=N,fill="both",expand =True)

        self.Class2Frame = Frame(self.Frame2, bg='#FF7F7F')
        self.Class2Frame.pack(anchor=N,fill="both",expand =True)

        self.Class3Frame = Frame(self.Frame2, bg='#90ee90')
        self.Class3Frame.pack(anchor=N,fill="both",expand =True)
        for x in range (3):
            classlist = [self.Class1Frame,self.Class2Frame,self.Class3Frame]
            self.Frame = classlist[x-1]
            self.CheckClass()
        self.Menu = Menu(master)
        self.master.config(menu =self.Menu)#configs menu to be used

        self.ExitMenu= Menu(self.Menu)
        self.Menu.add_cascade(label = "Exit", menu =self.ExitMenu)
        self.ExitMenu.add_command(label = "Exit", command = master.quit)

        self.EditMenu = Menu(self.Menu)
        self.Menu.add_cascade(label = "Edit", menu=self.EditMenu)
        self.EditMenu.add_cascade(label = "Upload activity", command = self.upload_activity)
        self.EditMenu.add_cascade(label=  'Remove Class',command = self.RemoveClassGUI)

        self.LogOutMenu = Menu(self.Menu)
        self.Menu.add_cascade(label = "Log Out",menu=self.LogOutMenu)
        self.LogOutMenu.add_cascade(label = "Log Out",command = self.LogOut)

        self.HomepageMenu = Menu(self.Menu)
        self.Menu.add_cascade(label='Homepage',menu=self.HomepageMenu)
        self.HomepageMenu.add_command(label='Homepage',command = lambda: MainScreen(self.master,self.c,self.conn,self.userid))

        self.ProfileMenu = Menu(self.Menu)
        self.Menu.add_cascade(label='Profile',menu=self.ProfileMenu)
        self.ProfileMenu.add_command(label='Profile',command= lambda : Profile(self.master,self.c,self.conn,self.userid,'student'))

    def RemoveClassGUI(self):
        self.top = Toplevel()
        self.top.geometry("150x150")
        self.top.title('Revision tool')
        self.top.config(bg= "#ADD8E6")

        self.title = Label(self.top, text = "Delete Class",font =("Helletica",10,"bold"),bg="#ADD8E6")
        self.title.grid(row=0,column=0,columnspan=2)

        self.ClassIDLabel=Label(self.top,text='Class ID:',bg="#ADD8E6")
        self.ClassIDLabel.grid(row=1,column=0)
        self.ClassIDEntry = Entry(self.top,width =8,)
        self.ClassIDEntry.grid(row=1,column=2)
        self.ClassIDEntry.insert(0,"000")
        self.EnterButton = Button(self.top,text="Enter", bg ="#ADD8E6",command =self.RemoveClass)
        self.EnterButton.grid(row=4,column=1,pady=10)
    def RemoveClass(self):
        classcode = self.ClassIDEntry.get()
        ##check they are assigned to the class
        self.c.execute(f"SELECT * FROM scjoin WHERE classcode == '{classcode}' AND userid == '{self.userid}'")
        classes = self.c.fetchall()
        if classes == []:#class does not exist
            self.Invalid = Label(self.top,text = "Invalid Class Entered",font =('Helvetica',10,"bold"),fg="black",bg="#EA5252")
            self.Invalid.grid(row=5,column=0)
        else:
            with self.conn:
                self.c.execute(f"DELETE  FROM scjoin WHERE classcode =='{classcode}' AND userid == '{self.userid}'")
                self.c.execute(f"DELETE FROM stats WHERE userid == '{self.userid}' AND classcode == '{classcode}'")
            self.top.destroy()
            Create_Login.ClearScreen(self)
            MainScreen(self.master,self.c,self.conn,self.userid)


    def CheckClass(self):#Checks for any classes the user has
        self.c.execute("SELECT classcode FROM scjoin WHERE userid == '"+self.userid+"' ")
        colours = ['#FFFF66','#FF7F7F','#90ee90']
        classlist = self.c.fetchall()
        self.ButtonList=  []
        for x in range (3):#loops througb the 3 classes popping each class which is done
            FrameList = [self.Class1Frame,self.Class2Frame,self.Class3Frame]
            self.Frame = FrameList[x]
            if classlist == []:#No classes
                self.AddClassButton = Button(self.Frame, text = "Add Class", command = self.AddClass)
                self.AddClassButton.grid(row=0,column=0)
            else:
                classcode = str(classlist[0][0])
                classid = self.GetClassID(classcode)
                self.c.execute("SELECT subname FROM class WHERE classid == '"+str(classid)+"'")
                subname = self.c.fetchone()
                self.ButtonList.append(Button (self.Frame, text = subname,command = lambda x=x: self.GoToUserClassScreen(x),padx=5))
                self.ButtonList[x].grid(row=0,column=0,pady=5,padx=5)
                self.c.execute(f"SELECT totalhours, averagehours FROM scjoin WHERE classcode == '{classcode}' AND userid == '{self.userid}'")
                info = self.c.fetchone()
                self.TeacherInfo(classcode)

                details = Label(self.Frame,text=f"Teacher: {self.teachername}     Class ID: {classcode} \n Total Hours: {info[0]}    Average Hours: {info[1]}",bg=colours[x],font = ('Hellevetica',10))
                details.grid(row=2,column=2,pady=5)
                classlist.remove(classlist[0])
    def TeacherInfo(self,classcode):
        self.c.execute("SELECT teacherid FROM teacherclassjoin WHERE classcode == '"+classcode+"'")
        self.teacherid = str(self.c.fetchone()[0])
        self.c.execute("SELECT title,surname FROM teacher WHERE teacherid == '"+self.teacherid+"'")
        teachername = self.c.fetchone()
        self.teachername = teachername[0]+' '+ teachername[1]
    def GetClassID(self,classcode):
        self.c.execute("SELECT classid FROM teacherclassjoin WHERE classcode == '"+classcode+"'")
        return str (self.c.fetchone()[0])

    def GoToUserClassScreen(self,buttonid):
        self.c.execute("SELECT classcode FROM scjoin WHERE userid == '"+self.userid+"' ")
        classlist = self.c.fetchall()
        Create_Login.ClearScreen(self)
        button = self.ButtonList[buttonid]
        classcode = classlist[buttonid]
        User_ClassScreen(self.master,self.c,self.conn,self.userid,classcode)


    def UpdateClass(self):##Adds class to the scjoin table
        self.classcode = self.ClassIDEntry.get()
        #Get classID
        self.c.execute("SELECT classid FROM teacherclassjoin WHERE classcode == '"+self.classcode+"'")
        classid = self.c.fetchone()
        if not classid:
            messagebox.showerror("Error","Invalid class ID")
            self.AddClass()
        if classid:
            classid = str(classid[0])
            self.c.execute("SELECT subname FROM class WHERE classid == '"+classid+"'")
            SubName = self.c.fetchall()
            if SubName == []:    #class does not exist
                self.ErrorMessage()
            else:##class exists
                #Check if the users already in the class
                self.c.execute(f"SELECT * FROM scjoin WHERE userid == '{self.userid}' AND classcode == '{self.classcode}'")
                check = self.c.fetchone()
                if not check:
                    SubName = SubName[0]
                    self.c.execute ("SELECT teacherid FROM teacherclassjoin WHERE classid == '"+classid+"'")
                    teacherid = self.c.fetchone()[0]
                    values = [self.userid,self.classcode,0,0]
                    self.conn.commit()
                    with self.conn:
                        self.c.execute("INSERT INTO scjoin VALUES (?,?,?,?)",values)#Inserts a new class into scjoin
                    self.top.destroy()
                    MainScreen(self.master,self.c,self.conn,self.userid)
                if check:
                    messagebox.showerror('Error','Class is already registered to this account')





    def AddClass(self):##Add class window

        self.top = Toplevel()
        self.top.geometry("150x150")
        self.top.title('Revision tool')
        self.top.config(bg= "#ADD8E6")

        self.title = Label(self.top, text = "Create Class",font =("Helletica",10,"bold"),bg="#ADD8E6")
        self.title.grid(row=0,column=0,columnspan=2)

        self.ClassIDLabel=Label(self.top,text='Class ID:',bg="#ADD8E6")
        self.ClassIDLabel.grid(row=1,column=0)
        self.ClassIDEntry = Entry(self.top,width =8)
        self.ClassIDEntry.grid(row=1,column=2)
        self.ClassIDEntry.insert(0,"000")

        self.EnterButton = Button(self.top,text="Enter", bg ="#ADD8E6",command =self.UpdateClass)
        self.EnterButton.grid(row=4,column=1,pady=10)



    def ErrorMessage(self):
        self.NW = Toplevel()
        self.NW.geometry("150x100")
        self.NW.title('Revision tool')
        self.NW.config(bg= "#E00719")

        self.ErrorLabel = Label(self.NW,text= "Invalid class code",font=('Helvetica',8,'bold'),bg="#E00719",fg="white")
        self.ErrorLabel.pack(pady=10,padx=10)
        self.top.destroy()
        self.OkButton = Button(self.NW, text = 'OK', command= lambda:self.NW.destroy())
        self.OkButton.pack()


    def upload_activity(self):
        Upload_Activity(self.master,self.c,self.conn,self.userid)


    def LogOut(self):
        Create_Login.ClearScreen(self)
        Create_Login(self.master,self.c,self.conn)


class Upload_Activity():
    def __init__(self,master,c,conn,userid):
        self.master = master
        self.c = c
        self.conn = conn
        self.userid=userid
        Create_Login.ClearScreen(self)
        self.TitleLabel = Label(self.master,text = "Upload Activity",font=('Comic Sans',15))
        self.TitleLabel.grid(row=0,column=0,columnspan=2)#
        self.GetClasses()

        if self.classlist == []:
            self.NoClass = Label(self.master, text='You have no current classes',font= ('Hellvetica',12),fg = 'red')
            self.NoClass.grid(row=2,column=1,pady=10)
        else:
            self.classlabel = Label(self.master,text = "Class:",font=("Comic Sans",12))
            self.classlabel.grid(row=1,column=0)
            self.GetClasses()
            self.clicked = StringVar()
            self.clicked.set(self.classlist[0])
            self.ClassMenu = OptionMenu(self.master,self.clicked, *self.classlist)
            self.ClassMenu.grid(row=1,column=1,pady=5)
            self.TimeSpent = Label(self.master,text= "Time Spent (Hours)",font=('Comic Sans',12))
            self.TimeSpent.grid(row=2,column=0)
            self.hoursEntry = Spinbox(self.master,from_=0,to=10,font=("Comic Sans",12))
            self.hoursEntry.grid(row=2,column=1,pady=5)
            self.ManualEntry = Button(self.master,text="Create Timer", command = self.Timer,bg="#90EE90")
            self.ManualEntry.grid(row=3,column=0)
            self.Submit = Button(self.master,text="Submit",bg="#90EE90",command = lambda:  self.SubmitActivity(self.hoursEntry.get()))
            self.Submit.grid(row=3,column=1,ipadx=5,pady=5)

    def Timer(self):
         self.hour=StringVar()
         self.minute=StringVar()
         self.second=StringVar()
         self.hour.set("00")
         self.minute.set("00")
         self.second.set("00")
         self.TimeFrame = Frame (self.master)
         self.TimeFrame.grid(row=4,column=1,pady=20)
         HourEntry= Entry(self.TimeFrame, width=3, font=("Helvetica",18,""),textvariable=self.hour)
         HourEntry.grid(row=0,column=0)
         MinuteEntry = Entry(self.TimeFrame, width=3, font=("Helvetica",18,""),textvariable=self.minute)
         MinuteEntry.grid(row=0,column=1)
         SecondEntry = Entry(self.TimeFrame, width=3, font=("Helvetica",18,""),textvariable=self.second)
         SecondEntry.grid(row=0,column=2)

         TimerButton = Button(self.TimeFrame, text="Start", command = self.RunTimer, bg ='#90EE90')
         TimerButton.grid(row=3,column=4)
    def RunTimer(self):
        TotalTime = int(self.hour.get())*3600 + int(self.minute.get())*60 + int(self.second.get())
        self.Time = TotalTime
        while TotalTime > -1:
            min,sec = divmod(TotalTime,60)#Divides and returns the remainder
            hours = 0
            if min > 60:
                hours, min = divmod(min,60)
            self.hour.set("{0:2d}".format(hours))
            self.minute.set("{0:2d}".format(min))
            self.second.set("{0:2d}".format(sec))
            self.master.update()
            time.sleep(1)
            TotalTime -= 1
            if TotalTime == 0:
                messagebox.showinfo("GetSmart Revision","Activity complete ")
                Upload= Button (self.TimeFrame, text = 'Upload', command = self.UploadTimer,bg='light blue')
                Upload.grid(row=4,column=4)

    def UploadTimer (self):
            self.Time  = self.Time/  3600 #converts seconds to hours
            self.Time = round(self.Time*2) / 2
            self.SubmitActivity(self.Time)

    def Updateuserstats(self):
        self.GetClassCode(self.subject)
        self.c.execute("SELECT * FROM scjoin WHERE userid=='"+self.userid+"' AND classcode == '"+str(self.classcode)+"' ")
        self.UserStats = self.c.fetchone()
        if self.UserStats == None:#No activites for the classes
            values = [
                self.userid,self.classcode,0,0
                ]
            with self.conn:
                self.c.execute("INSERT INTO scjoin VALUES (?,?,?,?) WHERE userid == '"+str(self.userid)+"' AND classid == '"+str(self.classid)+"'",values)
            hours = 0
            totalhours = 0

        #Get total hours
        self.c.execute("SELECT totalhours FROM scjoin WHERE userid == '"+self.userid+"' AND classcode =='"+str(self.classcode)+"' ")
        total_hours = self.c.fetchone()[0]
        #Add new hours
        total_hours = int(self.hours) #+ int(total_hours)
        with self.conn:
            self.c.execute("UPDATE scjoin SET totalhours = '"+str(total_hours)+"' WHERE userid == '"+self.userid+"' AND classcode =='"+str(self.classcode)+"'")
        week_ago = int(self.year_day) -7
        self.c.execute("SELECT hours FROM stats WHERE yearday>= '"+str(week_ago)+"'")
        hourlist = self.c.fetchall()#past weeks revision hours
        total = 0
        for hours in hourlist:
            total += hours[0]
        average_hours = total//7
        with self.conn:
            self.c.execute("UPDATE scjoin SET averagehours = '"+str(average_hours)+"' WHERE userid == '"+self.userid+"' AND classcode =='"+str(self.classcode)+"'")



    def GetClasses(self):
        self.c.execute("SELECT classcode FROM scjoin WHERE userid == '"+str(self.userid)+"'")
        self.CodeList = self.c.fetchall()
        self.classlist = []
        for codes in self.CodeList:
            codes = str(codes[0])
            self.c.execute("SELECT classid FROM teacherclassjoin WHERE classcode == '"+codes+"'")
            classid = str(self.c.fetchone()[0])
            self.c.execute("SELECT subname FROM class WHERE classid == '"+classid+"'")
            self.classlist.append(self.c.fetchone()[0])

    def GetClassCode(self,subname):
        self.c.execute("SELECT classid FROM class WHERE subname == '"+subname+"'")
        classid = str(self.c.fetchone()[0])
        self.c.execute("SELECT classcode FROM teacherclassjoin WHERE classid == '"+classid+"'")
        classcodes = self.c.fetchall()
        for code in classcodes:
            self.c.execute("SELECT classcode FROM  scjoin WHERE classcode == '"+str(code[0])+"' AND userid == '"+self.userid+"'")
            check = self.c.fetchone()
            if check:
                self.classcode = check[0]

    def SubmitActivity(self,hours):
        subject = self.clicked.get()
        self.subject = subject
        self.GetClassCode(subject)
        self.hours = hours
        self.c.execute("SELECT classid FROM class WHERE subname == '"+subject+"'")
        self.classid = self.c.fetchone()[0]
        ##Insert into stats
        full_date = datetime.datetime.now()
        #date = full_date.strftime("%x")
        date = datetime.date.today()
        current_time = full_date.strftime("%X")
        self.year_day = full_date.strftime("%j")
        ##Check for activity already on that day
        self.c.execute(f"SELECT * FROM stats WHERE date == '{date}' AND userid == '{self.userid}' AND classcode == '{self.classcode}'")
        result = self.c.fetchone()
        if  result == None:
            values =[self.userid,self.classcode,date,current_time,self.hours,self.year_day]
            with self.conn:
                self.c.execute("INSERT INTO stats VALUES (?,?,?,?,?,?)",values)
        else:##Update that days stats
            with self.conn:
                #get hours
                hours = result[4]
                self.hours = hours + int(self.hours)
                self.c.execute(f"UPDATE stats SET hours = '{self.hours}' WHERE userid == '{self.userid}' AND classcode== '{self.classcode}' AND DATE == '{date}'")
        self.Updateuserstats()
        Create_Login.ClearScreen(self)
        l = User_ClassScreen(self.master,self.c,self.conn,self.userid,str(self.classcode))




class User_ClassScreen(MainScreen):
    def __init__(self,master,c,conn,userid,classcode):
        super().__init__(master,c,conn,userid)
        self.classcode  = str(classcode[0])


        colour = '#4CD9D9'
        self.GetDetails()
        Create_Login.ClearScreen(self)
        self.Notebook =ttk.Notebook(self.master)
        self.HeadingFrame = LabelFrame(self.master,bg = colour)
        self.HeadingFrame.pack(ipadx=100,side=TOP,ipady=0)
        self.HeadingTitle  = Label(self.HeadingFrame, text = self.SubName, bg= colour,font =('Helvetica',16,'bold') )
        self.HeadingTitle.grid(row=0,column=0,ipadx=100,columnspan=4)
        self.TeacherSubHeader = Label(self.HeadingFrame, text= self.TeacherName,bg= colour, font =('ComicSans'))
        self.TeacherSubHeader.grid(row=1,column=3)
        self.ClassHeader = Label(self.HeadingFrame, text=f"Class Code: {self.classid}", bg=colour, font=('ComicSans'))
        self.ClassHeader.grid(row=2,column=3)

        self.MainFrame = Frame(self.Notebook, bg= 'white')
        self.MainFrame.pack(fill= BOTH,side=BOTTOM,expand =True)
        self.ClassStats= Label(self.MainFrame,text = "Class Statistics",font =('Helvetica',14,'bold'),bg='white')
        self.ClassStats.grid(row=0,column=0)
        self.LeaderBoardFrame = Frame(self.MainFrame)
        self.LeaderBoardFrame.grid(row=1,column=0)
        ##Add scrolllbar
        self.TreeScroll = Scrollbar(self.LeaderBoardFrame)
        self.TreeScroll.pack(side =RIGHT, fill=Y)
        self.LB = ttk.Treeview(self.LeaderBoardFrame,height=3,yscrollcommand =self.TreeScroll.set)

        self.LB['columns'] = ('Name','Surname','Total', 'Average')
        self.LB.column("#0",width=0,stretch=NO)
        self.LB.column("Name",anchor=W,width=60)
        self.LB.column("Surname",anchor=W,width=60)
        self.LB.column("Total",anchor=CENTER,width=60)
        self.LB.column("Average",anchor=W,width=60)
        #Create Headings
        self.LB.heading("#0",text='',anchor=W)
        self.LB.heading('Name',text='Name',anchor=W)
        self.LB.heading('Surname',text='Surname',anchor=W)
        self.LB.heading('Total',text = "Total",anchor=CENTER)
        self.LB.heading("Average",text = 'Average')
        self.LB.pack()
        self.TreeScroll.config(command=self.LB.yview)

        self.CreateLB()

        self.Pstats =Label(self.MainFrame,text = "Personal Statistics",font =('Helvetica',14,'bold'),bg='white')
        self.Pstats.grid(row=2,column=0)
        self.PLBFrame = Frame(self.MainFrame)
        self.PLBFrame.grid(row=3,column=0,ipadx=10)
        self.PLBTreeScroll = Scrollbar(self.PLBFrame)
        self.PLBTreeScroll.pack(side =RIGHT, fill=Y)
        #Add style
        style = ttk.Style()
        #Pick a theme
        style.theme_use("clam")

        self.PLB = ttk.Treeview(self.PLBFrame,height=3,yscrollcommand =self.PLBTreeScroll.set)

        self.PLB['columns'] = ('Date','Time','Hours')
        self.PLB.column("#0",width=0,stretch=NO)
        self.PLB.column("Date",anchor=W,width=60)
        self.PLB.column("Time",anchor=W,width=60)
        self.PLB.column("Hours",anchor=CENTER,width=60)
        #Create Headings
        self.PLB.heading("#0",text='',anchor=W)
        self.PLB.heading('Date',text='Date',anchor=W)
        self.PLB.heading('Time',text='Time',anchor=W)
        self.PLB.heading('Hours',text = "Hours",anchor=CENTER)
        #self.PLB.grid(row=3,column=0)
        self.PLB.pack(ipadx=20)
        self.PLBTreeScroll.config(command=self.PLB.yview)
        self.GetPLB()

        self.Notebook.pack(ipady=100,expand=1,ipadx=100)


        self.Notebook.add(self.MainFrame,text= "Main Page")

        CreateTable(self.master,self.c,self.conn,self.userid,self.classcode,self.Notebook)

        UniversityPage(self.master,self.c,self.conn,self.userid,self.classid,self.Notebook)
        FlashCards(self.master,self.c,self.conn,self.userid,self.classid,self.Notebook).GetCards()

    def CreateLB(self):
        self.GetClassList()

    def GetDetails(self):
        self.userid=str(self.userid)
        self.c.execute("SELECT classid FROM teacherclassjoin WHERE classcode == '"+self.classcode+"'")
        self.classid = str(self.c.fetchone()[0])
        self.c.execute("SELECT subname FROM class WHERE classid== '"+self.classid+"'")
        self.SubName = self.c.fetchall()
        self.c.execute("SELECT teacherid FROM teacherclassjoin WHERE classcode== '"+self.classcode+"' ")
        teacherid = str(self.c.fetchone()[0])
        self.c.execute("SELECT title,surname FROM teacher WHERE teacherid == '"+teacherid+"' ")
        title,surname = self.c.fetchone()
        self.TeacherName = title + " "+ surname

    def GetClassList(self):
        self.c.execute("SELECT * FROM scjoin WHERE classcode == '"+self.classcode+"'")
        classlist = self.c.fetchall()
        count = 0
        for students in classlist:
            self.c.execute("SELECT firstname, surname FROM account WHERE userid == '"+str(students[0])+"'")
            names = self.c.fetchall()[0]
            firstname, surname = names[0], names[1]
            details = [firstname, surname, students[2],students [3]]
            self.LB.insert(parent='',index='end',iid=count, values = (details[0],details[1],details[2],details[3]))
            count += 1

    def GetPLB(self):
        self.c.execute("SELECT * FROM stats WHERE userid == '"+self.userid+"' AND classcode == '"+self.classcode+"'")
        records = self.c.fetchall()

        records.reverse()#sorts list in order it was added to the database
        count =0
        for x in range (len(records)):
            self.PLB.insert(parent='',index='end',iid=count, values = (records[x][2],records[x][3],records[x][4]),tags='blue')
            count += 1

class FlashCards:
    def __init__(self,master,c,conn,userid,classcode,frame):
        self.master = master
        self.c = c
        self.conn = conn
        self.userid,self.classcode = userid, classcode
        self.Notebook = frame
        self.Frame1 = Frame(self.Notebook,bg='white')
        self.Frame1.pack(expand=1)
        self.Notebook.add(self.Frame1,text="Flashcards")
        self.S1 = Stack()

    def GetCards(self):
        self.c.execute("SELECT setid FROM flashcardjoin WHERE userid  == '"+self.userid+"' AND classcode == '"+self.classcode+"'")
        sets = self.c.fetchall()
        if sets:#If the user has any flashcard sets already created
            Title = Label(self.Frame1, text = "Revision Flashcards",font = ("Arial",13),bg='white')
            Title.grid(row=0,column=3)
            self.idlist = []
            buttonlist = []
            SetFrame = Frame(self.Frame1,bg='white')
            SetFrame.grid(row=2,column=0)
            AddSetButton = Button(SetFrame, text= "Add set!",fg= 'green',command = self.AddSet)
            AddSetButton.pack()
            RemoveSetButton = Button(SetFrame, text = "Delete set", fg='red', command = self.DeleteSetWindow)
            RemoveSetButton.pack(pady=5,padx=5)
            for x in range (len(sets)):
                self.idlist.append(sets[x])
                self.c.execute("SELECT title FROM flashcardjoin WHERE setid == '"+str(sets[x][0])+"'")
                title = self.c.fetchone()
                buttonlist.append(Button(SetFrame,text=f"{title[0]} \n Set ID:{sets[x][0]}",bg='#72f542',command = lambda x=x: self.GoToSet(x)))
                buttonlist[x].pack(ipadx=5,ipady=5,pady=5,padx=5)
        if not sets:#If the user has no created flashcard sets
            Label1 = Label(self.Frame1, text = "You have no current set of flashcards",fg = 'red', font = ("Arial",12),bg='white')
            Label1.grid(row=1,column=0,padx=30,pady=30)
            AddSetButton = Button(self.Frame1, text= "Add set!",fg= 'green',command = self.AddSet)
            AddSetButton.grid(row=2,column=0,pady=5,ipadx=5)

    def DeleteSetWindow(self):
        self.window = Toplevel()
        self.window.geometry("200x200")
        Title = Label (self.window,text = "Delete Flashcards", font = ("Comic Sans Ms",13,"bold"),fg='red')
        Title.grid(row=0,column=0,columnspan=2,pady=10)
        Label1 = Label(self.window,text="Enter set ID:",font = ("Arial"))
        Label1.grid(row=2,column=0)
        Entry1 = Entry(self.window,width=15)
        Entry1.grid(row=2,column=1,pady=5,padx=10)
        Entry1.insert(0,"000")
        Delete = Button(self.window,text = "Confirm", fg='red',command = lambda: self.DeleteSet(Entry1.get()))
        Delete.grid(row=3,column=1,pady=5)

    def DeleteSet(self,setid):
        with self.conn:#Deletes set from database
            self.c.execute(f"DELETE FROM flashcardjoin WHERE setid == '{setid}'")
            self.c.execute(f"DELETE FROM flashcard WHERE setid == '{setid}' ")
        self.window.destroy()
        User_ClassScreen(self.master,self.c,self.conn,self.userid,self.classcode)


    def GoToSet(self,index):
        self.setid = str(self.idlist[index][0])
        #Create_Login.ClearScreen(self)
        self.Set()

    def AddSet(self):
        window = Toplevel()
        colour = '#42ddf5'
        window.geometry("300x300")
        window.title('Revision tool')
        window.config(bg=colour)
        Title = Label(window,text= "Add Revision set",bg=colour,font = ('Arial',13,'bold'))
        Title.grid(row=0,column=3)
        NameLabel= Label(window,text = "Set name",bg=colour)
        NameLabel.grid(row=1,column=1,pady=5)
        NameEntry = Entry (window,width=20)
        NameEntry.grid(row=1,column=2,columnspan=2,padx=3)
        NextButton = Button(window,text='Next',bg='#90EE90',command = lambda:  self.CreateSet(NameEntry.get(),window))
        NextButton.grid(row=3,column=3,pady=5)

    def CreateSet(self,setname,window):
        values = [(None,self.userid,self.classcode,setname)]
                    #    self.c.executemany('INSERT INTO account (username,password,firstname,surname,gender,email) VALUES (?,?,?,?,?,?)',values)
        with self.conn:
            self.c.executemany('INSERT INTO flashcardjoin (setid,userid,classcode,title) VALUES (?,?,?,?)',values)
        Create_Login.ClearScreen(self)
        window.destroy()
        User_ClassScreen(self.master,self.c,self.conn,self.userid,self.classcode)

    def Set(self):
        self.c.execute("SELECT title FROM flashcardjoin WHERE setid == '"+self.setid[0]+"'")
        title = self.c.fetchone()[0]
        colour = '#90EE90'
        window = Toplevel()
        self.c.execute('SELECT heading, info FROM flashcard WHERE setid == "'+self.setid+'"')
        cards = self.c.fetchall()
        for card in cards:
            self.S1.Push(card)#Pushes card onto stack
        window.geometry("300x300")
        window.title('Revision tool')
        window.config(bg=colour)
        TitleLabel = Label(window, text = f"Flashcard set: {title}",font = ("Comic Sans Ms", 15,'bold'),bg=colour)
        TitleLabel.grid(row=0,column=0,columnspan=3)
        self.c.execute("SELECT heading, info FROM flashcard WHERE setid == '"+self.setid+"'")
        self.cards = self.c.fetchall()
        AddButton = Button(window, text = 'Add Flashcards',bg ='white',command = self.AddCard)
        AddButton.grid(row=1,column=0,pady=5,ipadx=5,ipady=2,padx=5)
        if len(self.cards) > 3:#If the user has enough vards to test
            TestButton = Button(window, text = "Test!",bg = 'white',command =  lambda: Test(window,self.c,self.conn,self.setid,self.userid,self.classcode,self.master))
            TestButton.grid(row=1,column=2,pady=5,ipadx=5,ipady=2,padx=5)
        self.CardFrame = Frame(window,bg= 'white')
        self.CardFrame.grid(row=3,column=0,columnspan=4,rowspan=5,pady=20)
        self.Toolbar = Frame(window)
        self.Toolbar.grid(row=10,column=0,columnspan=4,pady=5)
        self.FillCardFrame(False,0)


    def FillCardFrame(self,Info,index):
        for widgets in self.CardFrame.grid_slaves():
            widgets.destroy()
        self.c.execute("SELECT heading, info FROM flashcard WHERE setid =='"+self.setid+"'")
        cards = self.c.fetchall()
        if self.S1.IsEmpty():#Checks if the stack is empty and returns a Boolean val
                Label1 = Label (self.CardFrame, text = "Add Cards now!",font = ("Comic Sans Ms",13,"bold"),bg='#90EE90')
                Label1.grid(row=0,column=0)

        else:
            if index == len(cards):
                index = 0
            if index == -1:
                index = len(cards)-1
            card = cards[index]
            if Info == False:
                Text = Label(self.CardFrame, text = card[0],font = ("Comic Sans Ms",12))#Determines what side of the card to show
            else:
                Text = Label(self.CardFrame, text = card[1],font = ("Comic Sans Ms",12))
            Text.grid(row=0,column=0,ipadx=10,ipady=10,columnspan=3)

            Back = Button(self.Toolbar, text = '<==',command = lambda: self.FillCardFrame(False,index-1))
            Back.grid(row=1,column=0)

            Flip = Button(self.Toolbar,text="Flip",command = lambda: self.FillCardFrame(not Info,index))##recursion to flip the card
            Flip.grid(row=1,column=1)

            Forward = Button(self.Toolbar,text = '==>',command = lambda: self.FillCardFrame(False,index+1))
            Forward.grid(row=1,column=3)

    def AddCard(self):
        root  = Toplevel()
        root.geometry("400x200")
        root.title("Flashcard Maker")
        Label1 = Label(root,text="Keyword")
        Label1.grid(row=0,column=0,pady=5,padx=5)
        self.WordEntry = Entry(root,width = 20)
        self.WordEntry.grid(row=1,column=1)
        Label2 = Label(root,text="Description")
        Label2.grid(row=2,column=0,pady=5)
        self.Info = Text(root,width=30,height=5)
        self.Info.grid(row=3,column=1)
        Add = Button(root,text='Add',bg = '#72f542',command = lambda:  self.SaveCard(self.WordEntry.get(),self.Info.get('1.0',END)))
        Add.grid(row=4,column=1)

    def SaveCard(self,word,info):
        values = [(self.setid,word,info)]
        self.S1.Push((word,info))
        with self.conn:
            self.c.executemany('INSERT INTO flashcard (setid,heading,info) VALUES (?,?,?)',values)
        self.WordEntry.delete(0,END)
        self.Info.delete('1.0','end')

class Stack (FlashCards):
    def __init__(self,stack=None):
        if stack ==None:
            self.stack = []
        else:
            self.stack = stack

    def Shuffle (self):
        for i in range (len(self.stack)-1,0,-1):
            rand = random.randint(0,i)
            self.stack[i], self.stack[rand] = self.stack[rand],self.stack[i]
        return self.stack

    def Pop(self):#Remove and return the card from the top of the stack
        self.card = self.stack[-1]
        self.stack.pop(-1)
        return self.card

    def Push(self,card):#Push card to the top of the stack
        if card not in self.stack:
            self.stack.append(card)

    def Peek(self):#Return the card on the top of the stack
        return self.stack[-1]

    def IsEmpty(self):
        if len(self.stack) == 0:
            return True
        else:
            return False

    def PrintStack(self):
        for card in self.stack:
            print (card)

class Test:
    def __init__(self,frame,c,conn,setid,userid,classcode,master):
        #super().__init__(master,c,conn,userid,classcode,frame)
        self.frame = frame
        self.c =c
        self.conn = conn
        self.setid = setid
        self.userid = userid
        self.classcode = classcode
        self.master = master
        self.Testr(self.frame)
    def Testr(self,window):
        window.destroy()
        window = Toplevel()
        self.MainWindow = window
        window.geometry("500x400")
        window.title("Flashcard test")
        self.Frame = Frame(window)
        self.Frame.pack(expand=1,ipady=100)
        Title = Label(self.Frame, text= "Flaschard Test!",font = ('Comic Sans Ms',15,'bold'))
        Title.grid(row=0,column=0,columnspan=2)
        Label1 = Label(self.Frame, text="Number of questions: ")
        Label1.grid(row=2,pady=20,column=1)
        self.SortClick = StringVar()
        self.SortClick.set(10)
        Number = OptionMenu(self.Frame,self.SortClick,5,10,15,20)
        Number.grid(row=2,column=3)
        self.Qnumber = 0
        Go = Button(self.Frame,text="Start!",fg="green",command = self.TestWindow)
        Go.grid(row=3,column=3,pady=10,ipady=5,ipadx=10)

    def TestWindow(self):
        self.number = self.SortClick.get()
        for widget in self.Frame.winfo_children():
            widget.destroy()

        self.GetQuestions()

    def GetQuestions(self):
        self.c.execute("SELECT heading,info FROM flashcard WHERE setid == '"+self.setid+"'")
        self.CardsList = self.c.fetchall()
        self.Cards= Stack(self.CardsList)
        print ()
        print (self.Cards)
        self.Cards.PrintStack()
        self.Cards = self.Cards.Shuffle()
        #self.Cards.PrintStack()
        QuestionNumber = 1
        self.totalright = 0
        self.Stats = Frame(self.Frame)
        self.Stats.grid(row=1,column=4)
        self.Correct = "Correct: 0"
        self.QuestionTitle = "Question 0"
        self.Prompt = Label (self.Frame, text=self.Cards[0][0],font = ("Comic Sans Ms",15,"bold"),fg='blue')
        self.Prompt.grid(row=1,column=2)
        self.React = Label(self.Frame,font =("Comic Sans Ms",12),fg='green')
        self.React.grid(row=4,column=2,columnspan=2)

        self.NextQuestion(QuestionNumber)


    def NextQuestion(self,QuestionNumber):
        self.Title = Label (self.Frame, text = self.QuestionTitle, font = ("Arial",15,"bold"))
        self.Title.grid(row=0,column=0,columnspan=2)
        self.CorrectQ = Label(self.Stats, text= self.Correct,font = ("Comic Sans Ms",10))
        self.CorrectQ.grid(row=0,column=0)
        self.QNum = QuestionNumber

        ##Quiz Loop
        if self.QNum == int(self.number)+1:
            for widget in self.Frame.winfo_children():
                widget.destroy()
            self.EndScreen(self.totalright)

        else:
            self.temp = []
            self.card = self.Cards[0]
            #Print the question
            self.QuestionFrame  = Frame(self.Frame,borderwidth=10,highlightbackground= 'blue',relief = RIDGE)
            self.QuestionFrame.grid(row=3,column=1,columnspan=3,pady=10,ipady=10,ipadx=20)
            for card in self.Cards:
                self.temp.append(card)
            self.temp.remove(self.card)

            self.GetWrongAnswers()
            self.GenerateQuestions()
    def UpdateStats(self,right):
        self.totalright += right
        self.Correct  = f"Correct {self.totalright}"
        self.CorrectQ.config(text=self.Correct)
        self.Cards.pop(0)
        self.Cards.insert(-1,self.card)#Moves the card from the back to the front
        #Update the screen
        self.QuestionTitle = f"Question {self.QNum}"
        self.Title.config(text=self.QuestionTitle)
        self.Prompt.config(text=self.Cards[0][0])
        if right == 1:
            text = "✔ CORRECT"
            fg1 = 'green'
        else :
            text = "✘Incorrect Answer"
            fg1 = 'red'
        self.React.config(text = text,fg=fg1)
        self.QuestionFrame.destroy()
        self.NextQuestion(self.QNum+1)
    def GetWrongAnswers(self):
        self.wrong_answers = []
        for x in range (3):
            index = random.randint(0,len(self.temp)-1)
            self.wrong_answers.append(self.temp[index][1])
            self.temp.pop(index)


    def GenerateQuestions(self):
        question = self.card[0]
        right_answer  =self.card[1]
        coords = [(0,0),(1,0),(0,1),(1,1)]
        index = random.randint(0,3)
        rightcoords = coords[index]
        coords.pop(index)
        r = IntVar()
        r.get
        #r.set()
        R1 = Radiobutton(self.QuestionFrame,text=right_answer, value = 1, variable = r,command = lambda: self.clicked(r.get()))
        R1.grid(row= rightcoords[0],column = rightcoords[1])
        c = 2
        for x in range (3):
            R1 = Radiobutton(self.QuestionFrame, text=self.wrong_answers[x], value = c, variable = r , command = lambda: self.clicked(r.get()))
            R1.grid(row=coords[x][0], column= coords[x][1])
            c += 1
    def clicked(self,value):
        if value == 1:#right answer
            right = 1
        else:#wrong answer
            right = 0
        self.UpdateStats(right)
    def EndScreen(self,totalright):
        Title = Label(self.Frame, text = "Test Complete",font = ("Comic Sans Ms",15))
        Title.grid(row=0,column=0,pady=5)
        Label1 = Label(self.Frame, text = f"You finished with {totalright} answers out of {self.number}",font = ('bold'),fg='blue')
        Label1.grid(row=2,column=0)
        percentage = (totalright / int(self.number)) * 100
        percentage = round(percentage,1)
        if percentage < 50:
            colour = 'red'
        if percentage >= 50 and percentage < 80:
            colour = 'orange'
        if percentage > 79 :
            colour = 'green'
        Label2 = Label(self.Frame, text = f"{percentage}%",font = ("Comic Sans Ms ",25,'bold'),fg=colour)
        Label2.grid(row=3,column=0)
        Return = Button (self.Frame, text = "Return",command = lambda: self.MainWindow.destroy())

        Return.grid(row=4,column=0)


class CreateTable():
    def __init__(self,master,c,conn,userid,classcode,notebook):
        self.master = master
        self.c = c
        self.conn = conn
        self.userid = userid
        self.classcode = classcode
        self.Notebook = notebook
        ##CREATE TAB
        self.Frame1 = Frame(self.Notebook,bg="grey")
        self.Frame1.pack(expand=1)
        self.Notebook.add(self.Frame1,text = 'Progress')
        self.CreateGraph()

    def CreateGraph(self):
        self.c.execute("SELECT * FROM stats WHERE userid == '"+self.userid+"' AND classcode== '"+self.classcode+"'")
        dates = self.c.fetchall()
        dates_list = []
        time_list = []
        fig = plt.Figure(figsize = (5, 4),
                     dpi = 100)
        canvas = FigureCanvasTkAgg(fig,master = self.Frame1)

        for value in dates:
            date = value[2]
            time = value[4]
            dates_list.append(date)
            time_list.append(time)
        fig.add_subplot(111).plot(dates_list,time_list)
        canvas.draw()

    # placing the canvas on the Tkinter window
        toolbar = NavigationToolbar2Tk(canvas,self.Frame1)
        toolbar.update()
        canvas.get_tk_widget().pack()

class UniversityPage(User_ClassScreen):
    def __init__(self,master,c,conn,userid,classid,notebook):
        self.master = master
        self.c = c
        self.conn = conn
        self.userid = userid
        self.classid = classid
        self.Notebook = notebook
        self.UniFrame = Frame(self.Notebook)
        self.UniFrame.pack(fill= BOTH,side=BOTTOM,expand =True)
        self.Title= Label(self.UniFrame, text = 'Search University Courses',font = ('Helvetica',15))
        self.Title.grid(row=0,column=3)
        self.CourseEntry =  Entry(self.UniFrame, width=20)
        self.CourseEntry.grid(row=1,column=2,pady=5,columnspan=2)
        self.CourseEntry.insert(0,"Course Name")
        self.Search = Button(self.UniFrame, text = 'Search', command = lambda: GetUni(self.master,self.c,self.conn,self.CourseEntry.get(),self.UniFrame),bg = '#90EE90')
        self.Search.grid(row=1,column=5)
        self.Notebook.add(self.UniFrame,text = 'University')



class GetUni(UniversityPage):
    def __init__(self,master,c,conn,coursename,UniFrame):
        self.master = master
        self.c = c
        self.conn = conn
        self.coursename = coursename
        self.UniFrame = UniFrame
        self.FormatURL()
        self.page_soup = self.OpenWebsite(self.URL)
        self.GetValues()
        self.PrintValues()
        self.FilterButton = Button(self.UniFrame, text = 'Filter', command = self.Filter)
        self.FilterButton.grid(row=2,column=5)


    def Filter(self):
        self.colour = "#8DF8D7"
        self.window = Toplevel()
        self.font = ('Hellvetica',10)
        self.window.geometry("300x300")
        self.window.title('Revision tool')
        self.window.config(bg=self.colour)
        self.Title = Label(self.window,text='Filter Universities', bg = self.colour,font=('Apple Color Emoji',20))
        self.Title.grid(row=0,column=0,columnspan=4,ipadx=30)
        self.SortByLabel = Label(self.window,text="Sort by", font = self.font,bg=self.colour)
        self.SortByLabel.grid(row=1,column=0,pady=10)

        self.SortClick = StringVar()
        self.SortClick.set('')
        self.SortMenu = OptionMenu(self.window,self.SortClick,"Ascending","Descending")
        self.SortMenu.grid(row=1,column=3)
        self.SortButton = Button(self.window,text="Sort",command = lambda : self.MergeSort(self.SortClick.get()))
        self.SortButton.grid(row=5,column=0)

    def OpenWebsite(self,url):
        self.opener = AppURLopener()
        self.uClient = self.opener.open(url)
        self.page_html = self.uClient.read()#saves it as a variable
        self.uClient.close()#closes it
        self.page_soup = soup(self.page_html,"html.parser")
        return self.page_soup


    def PrintValues(self):#Puts universities onto the page
        self.TableFrame = Frame(self.UniFrame)
        self.scrollbar = Scrollbar(self.TableFrame,orient = VERTICAL)
        self.scrollbar.pack(side=RIGHT,fill=Y)

        self.UniTable = ttk.Treeview(self.TableFrame,height=6,yscrollcommand = self.scrollbar.set)
        self.UniTable['columns'] = ('University','Location','Grades')
        self.UniTable.column("#0",width=0,stretch=NO)
        self.UniTable.column("University",anchor=W,width=120)
        self.UniTable.column("Location",anchor=W,width=100)
        self.UniTable.column("Grades",anchor=CENTER,width=80)
        #Create Headings
        self.UniTable.heading("#0",text='',anchor=W)
        self.UniTable.heading('University',text='University',anchor=W)
        self.UniTable.heading('Location',text='Location',anchor=W)
        self.UniTable.heading('Grades',text = "Grades",anchor=CENTER)
        self.scrollbar.config(command=self.UniTable.yview)
        count = 0

        for uni in self.UniList:#Insert values into table
            self.UniTable.insert(parent='',index='end',iid=count, values = (uni['name'],uni['location'],uni['grade']),tags='blue')
            count += 1
            self.UniTable.pack()
            self.TableFrame.grid(row=3,column=0,columnspan=5,rowspan=2)

    def GetValues(self):#Gets Universities
        location = self.page_soup.findAll('span',{'class':'institution_location'})
        ucas = self.page_soup.findAll('div',{'class':'points'})
        unilist = []
        ucaslist = []
        for grade in ucas:
            ucaslist.append(grade.text)
        UniList = []
        dictionary = {}
        for x in range (len(location)):
            both = location[x].text.split('|')#gets the location and the uni name
            uniname = both[0]
            unilocation = both[1]
            grade = ucas[x].text.split()[2]
            dictionary = {'name': uniname,
                            'location':unilocation,
                            'grade':grade}
            UniList.append(dictionary)#Creates a list of dictionaries containing each university
        self.UniList = UniList

    def MergeSort(self,sorter):
        def Sort(List):
            if len(List)> 1:#base case
                mid = len(List)//2
                left = List[:mid]
                right = List[mid:]
                Sort(left)
                Sort(right)
                #Merge
                i = 0#Left counter
                j = 0#Right counter
                k = 0#Main list counter
                while i<len(left) and j<len(right):
                    if left [i]['grade'].split('-')[0] =='':#Fixes the webscraped numbers
                        left [i]['grade'].split('-')[0] = left[i]['grade'] = '0''0'
                    if right[j]['grade'].split('-')[0] =='':
                        right[j]['grade'].split('-')[0] = right[j]['grade'] = '0'

                    if int(left[i]['grade'].split('-')[0]) <  int(right[j]['grade'].split('-')[0]):
                        List[k]= left[i]
                        i += 1
                        k += 1
                    else:
                        List[k] = right[j]
                        j += 1
                        k += 1
                while i<len(left):
                    List[k] = left[i]
                    i += 1
                    k += 1
                while j<len(right):
                    List[k] = right[j]
                    j+= 1
                    k +=1


        Sort(self.UniList)
        if sorter == 'Descending':
            self.UniList.reverse()
        count =0
        self.UniTable.delete(*self.UniTable.get_children())

        for uni in self.UniList:#Insert values into table
            self.UniTable.insert(parent='',index='end',iid=count, values = (uni['name'],uni['location'],uni['grade']),tags='blue')
            count += 1
            self.UniTable.pack()
            self.TableFrame.grid(row=3,column=0,columnspan=5,rowspan=2)


    def FormatURL(self):
        url = 'https://www.theuniguide.co.uk/search/course?utf8=%E2%9C%93&c%5Bq%5D='
        words = self.coursename.split()
        if len(words) >= 1:
            for x in range (len(words)):
                if x == 0:
                    my_url = f'https://www.theuniguide.co.uk/search/course?utf8=%E2%9C%93&c%5Bq%5D={words[0]}'
                else:
                    my_url = my_url+f'{"+"}{words[x]}'
        self.URL = my_url

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

class EncryptPassword(Create_Login):

    def __init__(self,root,c,conn,password):
        super().__init__(root,c,conn)

    def HashPassword(self,password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')#Creates a salt
        password_hash = hashlib.pbkdf2_hmac('sha512',password.encode('utf-8'),
        salt, 100000)#Uses a hashing algorithm to create the hash
        password_hash = binascii.hexlify(password_hash)
        return (salt+password_hash).decode('ascii')


    def CheckPassword(self,stored_password, user_password):
        salt = stored_password[:64]#Gets the salt
        stored_password = stored_password[64:]
        password_hash = hashlib.pbkdf2_hmac('sha512',user_password.encode('utf-8'),
        salt.encode('ascii'),
        100000)
        password_hash = binascii.hexlify(password_hash).decode('ascii')
        return password_hash == stored_password

class Profile:
    def __init__(self,master,c,conn,ID,AccType):
        self.master = master
        self.c = c
        self.conn = conn
        self.ID = ID
        self.AccType = AccType
        self.Frame1 = Frame(self.master)
        self.font = ('Hellvetica', 10)
        Create_Login.ClearScreen(self)
        self.Title = Label (self.Frame1, text= 'Your Details',font= ('Hellvetica',20,'bold'),fg="green")
        self.Title.grid(row=0,column=2,columnspan=2)
        self.GetDetails()
        self.UpdateButton = Button(self.Frame1,text='Update',bg='#90EE90',command = self.Update)
        self.UpdateButton.grid(row=6,column=4,ipadx=10,ipady=3,pady=10)

        if AccType == 'teacher':
            self.TeacherProf()
        if AccType == 'student':
            self.StudentProf()
        self.Frame1.pack(fill=BOTH)

    def GetDetails(self):
        if self.AccType == 'teacher':
            self.c.execute(f"SELECT * FROM teacher WHERE teacherid == {self.ID} ")
        if self.AccType == 'student':
            self.c.execute(f"SELECT * FROM account WHERE userid == '{self.ID}' ")
        self.details = self.c.fetchone()
    def TeacherProf(self):
        self.Title = Label(self.Frame1, text= 'Title' , font = self.font)
        self.Title.grid(row=1,column=0)
        self.TitleClick = StringVar()
        self.TitleClick.set(self.details[1])
        self.TitleMenu = OptionMenu(self.Frame1,self.TitleClick,"Mr","Ms","Dr")
        self.TitleMenu.grid(row=1,column=3)

        self.NameLabel = Label(self.Frame1,text='Name', font = self.font)
        self.NameLabel.grid(row=2,column=0)
        self.NameEntry = Entry(self.Frame1,width=20)
        self.NameEntry.grid(row=2,column=3,pady=5)
        self.NameEntry.insert(0,self.details[2])

    def StudentProf(self):
        self.UsernameLabel = Label(self.Frame1,text='Username', font = self.font)
        self.UsernameLabel.grid(row=1,column=0)
        self.UsernameEntry = Entry(self.Frame1,width=20)
        self.UsernameEntry.insert(0,self.details[1])
        self.UsernameEntry.grid(row=1,column=3)


        self.FirstnameLabel = Label(self.Frame1,text='Firstname', font = self.font)
        self.FirstnameLabel.grid(row=2,column=0)
        self.FirstEntry = Entry(self.Frame1,width=20)
        self.FirstEntry.insert(0,self.details[3])
        self.FirstEntry.grid(row=2,column=3)

        self.LastLabel = Label(self.Frame1,text='Lastname',font= self.font)
        self.LastLabel.grid(row=3,column=0)
        self.LastEntry = Entry(self.Frame1,width=20)
        self.LastEntry.insert(0,self.details[4])
        self.LastEntry.grid(row=3,column=3)

        self.GenderLabel =Label(self.Frame1,text = "Gender:")
        self.GenderLabel.grid(row=4,column = 0)
        self.clicked = StringVar()
        self.clicked.set(self.details[5])
        self.GenderEntry = OptionMenu(self.Frame1,self.clicked,"Male","Female","Other")
        self.GenderEntry.grid(row=4,column=3)

        self.EmailLabel = Label(self.Frame1,text='Email Address')
        self.EmailLabel.grid(row=5,column=0)
        self.EmailEntry = Entry(self.Frame1,width=30)
        self.EmailEntry.insert(0,self.details[6])
        self.EmailEntry.grid(row=5,column=3,columnspan=2,padx=20)


    def Update(self):
        if self.AccType == 'student':
                statement = (f"UPDATE account SET username =  '{self.UsernameEntry.get()}',firstname = '{self.FirstEntry.get()}',surname= '{self.LastEntry.get()}',gender='{self.clicked.get()}',email='{self.EmailEntry.get()}'  WHERE userid == '{self.ID}' ")
        if self.AccType == 'teacher':
            statement = (f"UPDATE teacher SET title='{self.TitleClick.get()}', surname='{self.NameEntry.get()}' WHERE teacherid == '{self.ID}' ")
        with self.conn:
            self.c.execute(statement)
        label = Label(self.Frame1,text="Update Successful",fg='green')
        label.grid(row=7,column=4)




c=Create_Login(root,c, conn)

root.mainloop()
conn.close()
