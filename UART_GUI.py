

import time
from Tkinter import *
import tkMessageBox, tkFileDialog
import serial
import serial.tools.list_ports
import os,stat
from datetime import datetime
import binascii
import tkinter.font as font



class UART_Readout():
    def __init__(self, UART_logger , Flag_Hex_read, Filename):
        self.UART_logger = UART_logger
        self.Flag_Hex_read = Flag_Hex_read
        self.Filename = Filename 
        
    def SendCommandandRead_UART(self, cmd_string, Flag_Hex_write): 
        if Flag_Hex_write:
            cmd_bytes = bytearray.fromhex(cmd_string)
            
            for cmd_byte in cmd_bytes:
                hex_byte = ("{0:02x}".format(cmd_byte))
            
                self.UART_logger.write(bytearray.fromhex(hex_byte))
        else: 
            self.UART_logger.write(cmd_string)
            
            
        self.ReadValue_UART()
        
        
    def ReadValue_UART(self): 
        #print "read data"
        try: 
            inter= ''
            inter = self.UART_logger.read(100)
            #output Hex
            if self.Flag_Hex_read:
                inter = binascii.b2a_hex(inter) 
            else: 
                print "\n"
                
                
            if len(inter)>0:
                #write protection
                try:
                    os.chmod(self.Filename , stat.S_IWRITE)
                except:
                    pass
                
                with open (self.Filename , 'a') as f:
                    f.write(str(time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime())) + '--->'+ inter+"\n")
                    
                    #write protection
                    os.chmod(self.Filename , stat.S_IREAD)
                    
            print time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime()), inter
            
            
        except:
            pass




class Uart_Gui_Interface():
    def __init__(self):
        port_list = list(serial.tools.list_ports.comports())
        
        self.ports=[]
        
        if len(port_list) <= 0:
            print port_list
        else:
            for i in range(len(port_list)):
                 port_list_0 =list(port_list[i])
                 self.ports.append(port_list_0[0])
        
        self.com = None
        self.entries = [] #get all the definition from Entry for uart setting
        
        self.entry_command  = None #
        
        self.Filename = None 
        self.UART_logger = None 
        
        self.Flag_Hex_read = False #flag to read hex format or not 
        self.Flag_Hex_write = False #flag to write hex format or not
        
        self.Flag_interval = False #falst - sending command only once, true-sending command per second
        
        self.command = "" # command to write per second
        
        self.seek_after = 0 #time of correct second for data logging 
        
        
    def GUI_init(self):
        self.root = Tk()
        self.root.title("Sensirion Tool")
        
        w = 340
        h = 635
        x = 700
        y = 100
        self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        
        self.root.resizable(0, 0)# fixed windows
        
        
        #the title
        frame0 = Frame(self.root)
        frame0.grid(row=0, column=0)
        
        Label(frame0, text="UART Logger",width = 48, height = 2, bg='green').grid(row=0, column=0)
        
        Label(frame0, text="").grid(row=1, column=0) #seperated empty line
        
        
        
        #layout for com port
        frame_COM= Frame(self.root)
        frame_COM.grid(row=1, column=0)
        
        Label(frame_COM, text="COM_Port",width = 20,  bg='#191970', fg='#ffffff').grid(row=0, column=0)
        
        self.variable1 = StringVar(frame_COM)
        self.variable1.set("Click_Choose") # default value
        self.variable1.trace("w", self.option_changed)
        w = apply(OptionMenu, (frame_COM, self.variable1)  + tuple(self.ports))
        w.config(width=15)
        w.grid(row=1, column=0)
        
        Label(frame_COM, text="").grid(row=2, column=0) #seperated empty line
        
        
        ###Frame of serial setting
        #layout serial title 
        frame_title_uart = Frame(self.root)
        frame_title_uart.grid(row=2, column=0)
        
        Label(frame_title_uart, text="Uart Setting",width = 20,  bg='#191970', fg='#ffffff').grid(row=0, column=0)
        
        #Serial Setting
        frame_serial=Frame(self.root)
        frame_serial.grid(row=3, column=0)
        
        
        val_item=["Baudrate:","Bytesize:","Parity:","Stopbits:"]
        val_setting = ['9600','8','N','1']
        
        for i in range(4):
            label = Label(frame_serial, text=val_item[i], width=10, anchor=W, justify=LEFT)
            label.grid(row=i, column=0)
            entry = Entry(frame_serial, width=10)
            entry.insert(0, val_setting[i])
            
            entry.grid(row=i, column=1)
            self.entries.append(entry)
        
        Label(frame_serial, text="").grid(row=4, column=0) #seperated empty line
        
        
        
        ###Frame or Data Writing
        #Write command to device
        frame_title_command = Frame(self.root)
        frame_title_command.grid(row=4, column=0)
        
        Label(frame_title_command, text="Commands write",width = 20, bg='#4682B4').grid(row=0, column=0)
        
        #Frequency of writing
        frame_Command=Frame(self.root)
        frame_Command.grid(row=5, column=0)
        
        
        self.interval_once = IntVar() #funny, only works stay together
        l = Checkbutton(frame_Command, text="Command/onlyonce", variable = self.interval_once, command=self.change_interval_commandonce)
        l.grid(row=0, column=0)
        
        
        self.entry_command_once = Entry(frame_Command, width=20)
        self.entry_command_once.grid(row=0, column=1)
        
        
        
        self.interval = IntVar() #funny, only works stay together
        l = Checkbutton(frame_Command, text="Command/second", variable = self.interval, command=self.change_interval)
        l.grid(row=1, column=0)
        
        
        self.entry_command = Entry(frame_Command, width=20)
        self.entry_command.grid(row=1, column=1)
        
        
        
        Label(frame_Command, text="").grid(row=4, column=0) #seperated empty line
        
        
        #dataformat Write 
        frame_title_dataformat = Frame(self.root)
        frame_title_dataformat.grid(row=6, column=0)
        
        Label(frame_title_dataformat, text="Dataformat Write",width = 20, bg='#4682B4').grid(row=0, column=0)
        
        #Hex write or not
        frame_dataformat=Frame(self.root)
        frame_dataformat.grid(row=7, column=0)
        
        
        
        self.Hex_write = IntVar() #funny, only works stay together
        l = Checkbutton(frame_dataformat, text="Hex Input", variable = self.Hex_write, command=self.change_write)
        l.grid(row=0, column=0)
        
        
        Label(frame_dataformat, text="").grid(row=1, column=0) #seperated empty line
        
        
        
        ###Frame or Data Reading
        #dataformat read 
        frame_title_dataformat = Frame(self.root)
        frame_title_dataformat.grid(row=8, column=0)
        
        Label(frame_title_dataformat, text="Dataformat Read",width = 20, bg='#0000c0', fg='#b8860b').grid(row=0, column=0)
        
        #Hex output or not
        frame_dataformat=Frame(self.root)
        frame_dataformat.grid(row=9, column=0)
        
        
        
        self.Raw_Hex = IntVar() #funny, only works stay together
        l = Checkbutton(frame_dataformat, text="Hex output", variable = self.Raw_Hex, command=self.change)
        l.grid(row=0, column=0)
        
        
        Label(frame_dataformat, text="").grid(row=1, column=0) #seperated empty line
        
        
        
        #logging file
        frame_file=Frame(self.root)
        frame_file.grid(row=10, column=0)
        Label(frame_file, text="Path of data logging",width = 20, bg='#0000c0', fg='#b8860b').grid(row=0, column=0)
        
        #logging file
        frame_file=Frame(self.root)
        frame_file.grid(row=11, column=0)
        
        Label(frame_file, text="C:\Sensirion_Test_Data\\",width = 18).grid(row=0, column=0)
         
        self.entry_file = Entry(frame_file, width=10)
        self.entry_file.grid(row=0, column=1)
        
        
        Label(frame_file, text="").grid(row=1, column=0) #seperated empty line
        
        
        
        #Big button
        self.frame_start = Frame(self.root)
        self.frame_start.grid(row=12, column=0)
        myFont = font.Font(size=20,family='Helvetica')
        btn = Button(self.frame_start, text="START",width=15, height = 2,bg='#0052cc', fg='#ffffff',command=lambda:self.Start_Run())
        btn['font'] = myFont
        btn.grid(row=0, column=0)
        
        self.root.mainloop()
        
        
    def option_changed(self, *args):
        self.com = self.variable1.get()
        
        print "COM port is selected: ", self.com
        
        
    def change(self): 
        if self.Raw_Hex.get():
            self.Flag_Hex_read = True
            print "Hex read"
        else: 
            self.Flag_Hex_read = False
            print "raw read"
            
            
    def change_write(self): 
        if self.Hex_write.get()==1:
            self.Flag_Hex_write = True
            print "Hex write"
        else: 
            self.Flag_Hex_write = False
            print "raw write"
            
            
    def change_interval(self):  
        self.command = self.entry_command.get().replace(" ","")
        
        if len(self.command)>0:
            self.interval_once.set(0)
            
            if self.interval.get()==1:
                self.Flag_interval = True
                print "sending command per second: ", self.command 
                
        else: 
            self.interval.set(0)
            self.command = ""
            
            tkMessageBox.showerror('ERROR', 'need input the command')
        
        
        
    def change_interval_commandonce(self):  
        self.command = self.entry_command_once.get().replace(" ","")
        
        if len(self.command)>0:
            self.interval.set(0)
            
            if self.interval_once.get()==1:
                self.Flag_interval = False
                print "sending command once: ", self.command 
                
        else: 
            self.interval_once.set(0)
            self.command = ""
            
            tkMessageBox.showerror('ERROR', 'need input the command')
        
        
        
    def Start_Run(self):
        print "COM Port is ", self.com
        
        bnd = int(self.entries[0].get().replace(" ",""))
        legth = int(self.entries[1].get().replace(" ",""))
        plo = self.entries[2].get().replace(" ","")
        stop =int(self.entries[3].get().replace(" ",""))
        
        print "UART setting are ", bnd , legth, plo , stop 
        
        self.command = self.entry_command.get().replace(" ","")
        
        if(self.com!=None):
            if len(self.entry_file.get().replace(" ",""))>0:
                #try to open the com port. if open, proceed
                try:
                    #UART_logger = serial.Serial(self.com, baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout= 0.1) 
                    self.UART_logger= serial.Serial(self.com, baudrate=bnd, bytesize=legth, parity=plo, stopbits=stop, timeout=0.1)
                    time.sleep(2)
                    
                    
                    print "flag if hex: ",self.Flag_Hex_read
                    
                    Folder_Name = "C:\Sensirion_Test_Data\\" + self.entry_file.get().replace(" ","")
                    
                    #check the path and build it if no exist
                    if os.path.exists(Folder_Name):
                        pass
                    else:
                        os.makedirs(Folder_Name)
                    
                    now = datetime.now()
                    self.Filename = Folder_Name +"\\"+'Datalogging_'+str(self.com)+'_{}_{}_{}_{}_{}_{}.csv'.format(now.year, str(now.month).zfill(2),str(now.day).zfill(2),str(now.hour).zfill(2),str(now.minute).zfill(2),str(now.second).zfill(2))
                    print "Data logged at address: ", self.Filename 
                    
                    
                    
                    ##handle the GUI interface
                    for entry in self.entries:
                        entry.config(state='disabled')
                    
                    self.entry_file.config(state='disabled')
                    
                    self.frame_start.destroy()
                    
                    
                    self.root.after(1000, self.Runonce_perSecond) #loop to get the data per second
                    
                    
                    
                except:
                    self.UART_logger.close()
                    
                    try: 
                        self.UART_logger= serial.Serial(self.com, baudrate=bnd, bytesize=legth, parity=plo, stopbits=stop, timeout=0.1)
                        
                        self.root.after(1000, self.Runonce_perSecond)
                        
                    except: 
                        print "the setting of COM port is wrong" 
                        tkMessageBox.showerror('ERROR', "the setting of COM port is wrong")
                        
            else: 
                tkMessageBox.showerror('ERROR', "Pld input the folder name")
        else:
            tkMessageBox.showerror('ERROR',"pls select a com port")
            
            
            
    #7E0000020100FC7E
    #7E000300FC7E
    #7E000100FE7E 
    def Runonce_perSecond(self):
        seek = time.strftime("%S", time.localtime())   #set bentch mark, and always compare with this time
        if int(seek)>int(self.seek_after) or (int(seek)==0 and int(self.seek_after)==59):  # if this time is lager than last time, then record.
            if len(self.command)>0:
                
                ##loop to send command 
                if self.Flag_interval:
                    UART_Readout(self.UART_logger, self.Flag_Hex_read,self.Filename).SendCommandandRead_UART(self.command, self.Flag_Hex_write)
                    
                    
                else:
                    UART_Readout(self.UART_logger, self.Flag_Hex_read,self.Filename).SendCommandandRead_UART(self.command, self.Flag_Hex_write)
                    print "Wait for next command"
                    
                    self.command = ''
            else:
                UART_Readout(self.UART_logger, self.Flag_Hex_read,self.Filename).ReadValue_UART()
        
        self.seek_after=seek  #every time, give the time to seek_after
        self.root.after(100, self.Runonce_perSecond)
        
        
Uart_Gui_Interface().GUI_init()







