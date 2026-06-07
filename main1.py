from tkinter import *
from tkinter import ttk
import tkcalendar
import qrcode
from tkinter import messagebox
from csv import *
import pygame
import webbrowser
import pandas as pd

def start():
    root =Tk()
    root.geometry('470x340')
    root.title('Employee Qrcode And EXcel [Aiqan]')
    root.resizable(False,False)
    root.config(background='#290B0B')
   



    #title
    title = Label(root, text='       Employee Registering', font='Calibre 20 bold',bg='#290B0B',fg='white')
    title.grid(row=0,column=0 ,pady=10,columnspan=4)#مكان الظهور نفس عملplace   -- pady لجل ان يبتعد من العناصر التاليه
    #first and last name 
    fname_lable =Label(root, text='First Name',bg='#290B0B',fg='white')
    fname_lable.grid(row=1,column=0,padx=10 ,sticky='w')

    fname_Entry =Entry(root,width=20)
    fname_Entry.grid(row=1,column=1 )

    lname_lable =Label(root, text='    Last Name',bg='#290B0B',fg='white')
    lname_lable.grid(row=1,column=2,padx=10)

    lname_Entry =Entry(root,width=20)
    lname_Entry.grid(row=1,column=3,pady=5 )

    #birth date
    birth_lable =Label(root, text='Birth Date',bg='#290B0B',fg='white')
    birth_lable.grid(row=2,column=0 ,padx=10,sticky='w')

    birth_Entry =tkcalendar.DateEntry(root,width=20)
    birth_Entry.grid(row=2,column=1,pady=5,columnspan=3,sticky='we' )

    #gender
    Gender =Label(root,text='Gender',bg='#290B0B',fg='white')
    Gender.grid(row=3,column=0,padx=10,sticky='w' )

    gender =  StringVar()
    gender.set('none')
    male= Radiobutton(root, text='Male',variable=gender ,value='Male',)#activebackground='#954332',
    #activeforeground='white',bg='#290B0B')
    male.grid(row=3,column=1,pady=5,sticky='w')

    female= Radiobutton(root, text='Female',variable=gender ,value='Famale')
    female.grid(row=3,column=2,pady=5,sticky='w')

    #country
    country_lable =Label(root, text='Country',bg='#290B0B',fg='white')
    country_lable.grid(row=4,column=0 ,padx=10,sticky='w')

    country_choices =ttk.Combobox(root,width=20,values=['Saudi Arabia', 'Syria','Egypt','UAE','Yemen','Meracco'])
    country_choices.grid(row=4,column=1,pady=5,columnspan=3,sticky='we' )

    #Address
    text_lable =Label(root, text='Address',bg='#290B0B',fg='white')
    text_lable.grid(row=5,column=0 ,padx=10,sticky='nw')

    text_Entry =Text(root,width=20,height=5)
    text_Entry.grid(row=5,column=1,pady=5,columnspan=3,sticky='we' )

    #Buttons
    #عمل داله لتعمل اكشن يعني لما اعمل حفظ ينقل المعلومات الى ملف في جهازي
    def record():
        firstname= fname_Entry.get()
        lastname = lname_Entry.get()
        gender_ = gender.get()
        birthdate = birth_Entry.get()
        countray=country_choices.get()
        address=text_Entry.get("1.0", "end-1c")
        text = firstname + "," +lastname + "," +gender_ + "," + birthdate + "," + countray + "," + address + "\n"
        with open(r"C:\Users\ZBOOK\Desktop\pro\file6.CSV", "a") as file :
            file.write(text) 
        clear_all()


    def clear_all():
        fname_Entry.delete(0,"end")
        lname_Entry.delete(0,"end")
        gender.set("none")
        birth_Entry.delete(0 , "end")
        country_choices.delete(0 , "end")
        text_Entry.delete("1.0" , "end")
        fname_Entry.focus_set()#عشان بعد الحذف يرجع المؤشر الى هذا الحقل
    
    # def read():
    #     import pandas as pd
    #     df = pd.read_csv('C:\Users\ZBOOK\Desktop\final project\file6.CSV')
    #     print(df)

    #الباركود
    def Sv():
        namefile=En_save.get()
        firstname=fname_Entry.get()
        lastname = lname_Entry.get()
        gender_ = gender.get()
        birthdate = birth_Entry.get()
        countray=country_choices.get()
        address=text_Entry.get("1.0", "end-1c")
        info = qrcode.make('First name is :'+firstname +'\nLIST NAME IS : '+ lastname +'\nBirthday is : ' 
                        +birthdate +'\nGemder is :' + gender_  +'\nCountry is :'+ countray + '\nAddress is :'+address + "\n\t thank you very much")
        info.save('EMPOLYEE/'+namefile+'.jpg')
        messagebox.showinfo('Save','Save ['+ namefile + ' ] employee')
        clear_all()
    #exeal 
    
    l_save= Label(root,text='Save in Exeal : ',font=('Tajawal',10),bg='#290B0B',fg='white')
    l_save.place(x='5', y='278')
    save = Button(root, text='Save',command=record,cursor='sizing',
    activebackground='#954332',
    activeforeground='white')
    save.place(x='100',y='278')

    # read1 = Button(root, text='read', command=read) 
    # read1.place(x='150',y='300')

    clear = Button(root, text='Clear',command=clear_all,
    cursor='sizing',
    activebackground='#954332',
    activeforeground='white')
    clear.place(x='150',y='278')

    #read from Excel
    def create_data_window():
        """Creates a new window to display the data from the CSV file."""
        data_window = Tk()
        data_window.geometry('470x340')
        data_window.title('Essential Employees')
        data_window.resizable(False,False)
        data_window.config(background='yellow')

        # Create a scrollable Text widget to display the data
        data_text = Text(data_window, wrap=WORD)
        scrollbar = Scrollbar(data_window, orient=VERTICAL, command=data_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        data_text.pack(fill=BOTH, expand=True)

        # Read the data and display it in the Text widget
        df = pd.read_csv('file6.csv')
        data_text.insert(END, df.to_string(index=False))

        data_window.mainloop()

    def read_data():
        """Reads the data from the CSV file and creates a new window to display it."""
        try:
            create_data_window()
        except FileNotFoundError:
            # Handle the case where the file is not found
            messagebox.showerror('Error', 'File not found! Please check the file path.')


   


    read_button =Button(root,text='Show Emp☑',fg='black',bg='white',
    font=('Tajawal',9),
    command=read_data,
    cursor='sizing',
    activebackground='#954332',
    activeforeground='white')
   
    read_button.place(x='300', y='280')

   


    #الباركود

    l_save = Label(root,text='File name :',font=('Tajawal',10),bg='#290B0B',fg='white')
    l_save.place(x='5',y='310')
    En_save=Entry(root,font=('Tajawal',10),width=14)
    En_save.place(x='100',y='310')
    b_save=Button(root,text='Save As QR ☑',fg='black',bg='white',
    font=('Tajawal',9),
    command=Sv,
    cursor='sizing',
    activebackground='#954332',
    activeforeground='white')
    b_save.place(x='210',y='310')


    #الحقوق
    l_copy= Label(root,text='Developer by Aiqan&2024 ♡',font=('Times New Roman',11,'underline'),bg='#290B0B',fg='white')
    l_copy.place(x=310,y=320)
    
    pygame.mixer.init()

    def play():
        pygame.mixer.music.load("welcom.mp3.mp3")
        pygame.mixer.music.play(loops=0)
    play()    
    root.mainloop()

# ايقونه البرنامج
# root.iconbitmap('C:\Users\ZBOOK\Desktop\final project\oip.ico')

# Scroll bar
# sc1=Scrollbar(root, orient=VERTICAL)
# sc1.pack(side=RIGHT,fill=Y)

# password
pro = Tk()
pro.geometry('470x340')   #size of hight and width of the widow//(+) the postion of the window in the screen
pro.resizable(False,False)  #disable the sizeable of the widow from the horzintal and virtical
pro.title('Employee Qrcode And EXcel [Aiqan]')  #change the title of the widow
pro.config(background='#290B0B')
#pro.iconbitmap('C:\\Users\\ZBOOK\\Desktop\\super market\\i.ico')
title = Label(pro, text='Employee Qrcode And EXcel [Aiqan]',fg='white',bg='#290B0B',font=('Tajawal',12))#pro position then characters
title.pack(fill=X)   # pack defualt palce -to run the lablel and make the back color fill horizitally

u1000='https://www.facebook.com/profile.php?id=100025345324796'
u2='https://t.me/vw_83'
u3='https://youtube.com/@mohdadnan23?si=yzss5owSgXQWCgQq'
def open1():
    webbrowser.open_new(u1)
def open2():
    webbrowser.open_new(u2)
def open3():
    webbrowser.open_new(u3)  
def about1():
    messagebox.showinfo('developer','I am Ammar Aqan. I live in Sanaa and study at the University of Science and Technology')
def about2():
   messagebox.showinfo('Employee Registering','Python project on Tkinter \n Subject teachers : \n 1 - Khaled Al-Arshi \n 2 - Mohammad Al-Suti ')   
def log():
    user = En1.get()
    password = En2.get()
    if user =='Aiqan' and password=='123456':
        messagebox.showinfo('Welcome','Welcome to the project ')
        pro.destroy()
        start()
        
        
          
    else:
        messagebox.showerror('Error','The data is wrong')    

F1 = Frame(pro, width=170,height=1000,bg='#290B0B')
F1.place(x=0,y=29) #place to choose the postion not by defualt
Title1=Label(F1, text='Employee Registering',fg='white',bg='#290B0B', font=('Sakkal Majalla',18,'bold'))
Title1.place(x=0,y=0)

Title2=Label(F1, text='Project',fg='white',bg='#290B0B', font=('Sakkal Majalla',18,'bold'))
Title2.place(x=0,y=26)


#Title3 = Label(F1,text='Developer Aiqan ',fg='white',bg='#290B0B', font=('Sakkal Majalla',18,'bold'))
#Title3.place(x=0,y=50)
Title4 = Label(F1,text='Contact me : ',fg='white',bg='#290B0B', font=('Sakkal Majalla',18,'bold'))
Title4.place(x=0,y=50)
B1 = Button(F1,text='My Facebook account',height=2, width=26,fg='black',bg='#0055C7',command=open1 )
B1.place(x=4,y=78)
B2 = Button(F1,text='My Telegram account',height=2, width=26,fg='black',bg='#00FFD2',command=open2)
B2.place(x=4,y=113)
B3 = Button(F1,text='My Youtube Channel',height=2 ,width=26,fg='black',bg='#FF0000',command=open3)
B3.place(x=4,y=150)
B4 = Button(F1,text='A glimpse of the developer', height=2 ,width=26,fg='black',bg='#FF8800',command=about1)
B4.place(x=4,y=190)
B5 = Button(F1,text='A glimpse of the project',height=2 , width=26,fg='black',bg='#DBA901',command=about2)
B5.place(x=4,y=230)
B6 = Button(F1,text='Close the program',height=2 , width=26,fg='black',bg='#DB4B4B',command=quit)
B6.place(x=4,y=270)



#photo = PhotoImage(file='D:\\IT\\univercity\\Y1a\\b\\bython\\2.png')
imo = Label(pro)
imo.place(x=170,y=43,width=308,height=202)
# F2 = Frame(pro, width=300,height=90,bg='#0B2F3A')
# F2.place(x=120,y=200)
#photo1 = PhotoImage(file='D:\\IT\\univercity\Y1a\\b\\bython\\lock_100px.png')
imo1 = Label (pro)
imo1.place(x=490,y=335,width=110,height=110)
L1= Label(pro,text='User Name :',fg='white',bg='#290B0B',font=('Sakkal Majalla',18,'bold'))
L1.place(x=170,y=245)
L2= Label(pro,text='Password  : ',fg='white',bg='#290B0B',font=('Sakkal Majalla',19,'bold'))
L2.place(x=170,y=275)
En1=Entry(pro,font=('Sakkal Majalla',12,'bold'),justify='center',width=20)
En1.place(x=290,y=250)
En2=Entry(pro,font=('Sakkal Majalla',12,'bold'),justify='center',width=20)
En2.place(x=290,y=280)
B  = Button(pro, text='Login',bg='white',font=('Sakkal Majalla',18,'bold'),command=log,cursor='sizing',
    activebackground='#954332',
    activeforeground='white')
B.place(x=416,y=250)

photo = PhotoImage(file= 'image/9.png')
pane1 = Label(pro , imag=photo)
pane1.place(x=250,y=45,width='280',height='200')

pro.mainloop()
     



