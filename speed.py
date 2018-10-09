from gpiozero import LED, Button as GpioButton
from time import sleep, time
from datetime import datetime
from random import uniform
from sys import exit
from tkinter import *
from tkinter import ttk

TRIAL_NUM = 8    
LED_PIN = 4
LB_PIN  = 14
RB_PIN  = 15

# init GPIO stuff
led = LED(LED_PIN)
extP1Button = GpioButton(RB_PIN)
extP2Button = GpioButton(LB_PIN)

p1Reacted = False
p2Reacted = False

def p1Pressed(button):
    global p1Reacted
    #print(str(button.pin.number) + ' pressed')
    p1Reacted = True
        
def p2Pressed(button):
    global p2Reacted
    #print(str(button.pin.number) + ' pressed')
    p2Reacted = True

extP1Button.when_pressed = p1Pressed
extP2Button.when_pressed = p2Pressed

def measureReactions():
    global p1Reacted
    global p2Reacted
    p1Time = 0
    p2Time = 0
    p1Reacted = False
    p2Reacted = False
    p1Prev = False
    p2Prev = False

    startTime = datetime.now()
    led.on()
    while not (p1Prev and p2Prev):
        if ((not p1Prev) and p1Reacted):
            p1Prev = p1Reacted
            p1dif = datetime.now() - startTime
            p1Time = int(p1dif.total_seconds() * 1000)
            print('P1=', p1Time)

        if ((not p2Prev) and p2Reacted):
            p2Prev = p2Reacted
            p2dif = datetime.now() - startTime
            p2Time = int(p2dif.total_seconds() * 1000)
            print('P2=', p2Time)

        elapsed = datetime.now() - startTime
        if elapsed.total_seconds() > 10:
            print('timeout')
            break
    led.off()
    return p1Time, p2Time
    
class Window(Frame):

    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master
        
        #declare and initialize lists for easy iteration
        self.p1results = [None]*TRIAL_NUM 
        self.p2results = [None]*TRIAL_NUM 

        self.init_window()

    def init_window(self):
        self.master.title("Zawody na refleks")
        self.grid(sticky=N+S+E+W)

        self.nameP1 = StringVar()
        self.nameP2 = StringVar()

        self.lastP1 = StringVar()
        self.lastP2 = StringVar()

        self.avgP1 = StringVar()
        self.avgP2 = StringVar()

        self.p1Time = 0.0
        self.p2Time = 0.0

        self.lastP1.set('0')
        self.lastP2.set('0')

        self.avgP1.set('0')
        self.avgP2.set('0')

        self.turnNum = 0
        self.turnRes = {}
        
        startButton = Button(self, text="Start", command=self.game_go)
        startButton.grid(row=0, rowspan=2, column=1, sticky=E+W)
        
        labelP1 = Label(self, text='Pierwszy (niebieski) gracz', justify='center')
        labelP1.grid(row=0, column=0)
        entryP1 = Entry(self, width = 30, textvariable=self.nameP1)
        entryP1.grid(row=1, column=0)

        labelP2 = Label(self, text='Drugi (czarny) gracz', justify='center')
        labelP2.grid(row=0, column=2)
        entryP2 = Entry(self, width = 30, textvariable=self.nameP2)
        entryP2.grid(row=1, column=2)

        self.labelStatus = Label(self, text='', justify='center')
        self.labelStatus.config(font=("Courier", 18))
        self.labelStatus.grid(row=2, columnspan=3, sticky=N+E+W)

        self.progressb = ttk.Progressbar(self, orient='horizontal', length=200, maximum=TRIAL_NUM-1)
        self.progressb.grid(row=3, ipady=10, sticky=E+W, columnspan=3)

        self.separator1 = ttk.Separator(self, orient='horizontal')
        self.separator1.grid(row=4, column=0, columnspan=3, pady=10, sticky=W+E)
        self.separator2 = ttk.Separator(self, orient='vertical')
        self.separator2.grid(row=5, column=1, rowspan=5, sticky=S)
        
        label2P1 = Label(self, text='Ostatni wynik [ms]', justify='center')
        label2P1.grid(row=6, column=0)
        label2P2 = Label(self, text='Ostatni wynik [ms]', justify='center')
        label2P2.grid(row=6, column=2)

        self.labelLastP1 = Label(self, text='00', justify='center', textvariable=self.lastP1)
        self.labelLastP1.config(font=("Courier", 44))
        self.labelLastP1.grid(row=7, column=0)
        self.labelLastP2 = Label(self, text='00', justify='center', textvariable=self.lastP2)
        self.labelLastP2.config(font=("Courier", 44))
        self.labelLastP2.grid(row=7, column=2)

        self.separator3 = ttk.Separator(self, orient='horizontal')
        self.separator3.grid(row=8, columnspan=3, ipady=10, sticky=W+E)

        label3P1 = Label(self, text='Sredni wynik [ms]', justify='center')
        label3P1.grid(row=9, column=0)
        label3P2 = Label(self, text='Sredni wynik [ms]', justify='center')
        label3P2.grid(row=9, column=2)

        self.labelAvgP1 = Label(self, text='00', justify='center', relief=RIDGE, textvariable=self.avgP1)
        self.labelAvgP1.config(font=("Courier", 44))
        self.labelAvgP1.grid(row=10, column=0)
        self.labelAvgP2 = Label(self, text='00', justify='center', relief=RIDGE, textvariable=self.avgP2)
        self.labelAvgP2.config(font=("Courier", 44))
        self.labelAvgP2.grid(row=10, column=2)

        self.separator4 = ttk.Separator(self, orient='horizontal')
        self.separator4.grid(row=11, columnspan=3, ipady=10, sticky=W+E)

        self.textBox = Text(self)#, state=DISABLED)
        self.grid(row=0, column=3, rowspan=11)

    def game_go(self):
        if not(self.nameP1.get().strip() and self.nameP2.get().strip()):
            self.labelStatus.config(text='Podaj imiona obu graczy')
            return
        else:
            self.labelStatus.config(text='Przygotować się...!')
            self.update_idletasks()
            sleep(5)
            self.labelStatus.config(text='')
            self.update_idletasks()

        self.turnNum += 1
        
        print(self.nameP1.get())
        print(self.nameP2.get())
        
        for i in range(0, TRIAL_NUM-1):

            #random pause before next round
            sleep(uniform(2, 5))

            self.p1Time, self.p2Time = measureReactions()
            
            if self.p1Time != 0:
                self.p1results[i] = self.p1Time
            if self.p2Time != 0:
                self.p2results[i] = self.p2Time

            #update score and looks
            self.displayResults(i)
            self.progressb.step()
            self.update_idletasks()           

        self.labelStatus.config(text='Koniec rundy')
        self.update_idletasks()

        #save turn result into dictionary
        self.turnRes[self.turnNum] = ({self.nameP1.get(): self.p1results}, {self.nameP2.get(): self.p2results}) 
        print(self.turnRes)
        

    def displayResults(self, index):
        self.lastP1.set(self.p1results[index]) 
        self.lastP2.set(self.p2results[index])

        listTemp = [i for i in self.p1results if i is not None]
        if listTemp:
            avg = float(sum(listTemp)/len(listTemp))
            #print(avg)
            self.avgP1.set(int(avg))
            
        listTemp = [i for i in self.p2results if i is not None]
        if listTemp:
            avg = float(sum(listTemp)/len(listTemp))
            #print(int(avg))
            self.avgP2.set(int(avg))

        
#start GUI    
root = Tk()
#root.geometry("400x500")
Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
app = Window(root)
root.mainloop()
 
