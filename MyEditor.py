import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

from pomegranate import *
import numpy as np

# create model from file
with open('model.txt', 'r') as f:
    model_json = f.read()

model = HiddenMarkovModel.from_json(model_json)

with open('dictionary.txt', 'r') as f:
    dictionary = f.readlines()

dictionary = [w.lower()[:-1] for w in dictionary]

# GUI
root = Tk()
root.title("MyEditor")
root.geometry("750x500")

var = IntVar(value=1)
c = Checkbutton(root, text="Enable Live Correction", variable=var)
c.pack(side=BOTTOM, anchor='w')



lastword = ''
def correction_event(*args):
    text = txt.get("insert linestart", "insert")
    
    try:
        word = text[text.rfind(' ') + 1:]
    except:
        word = text
    print(word)
    
    global lastword
    lastword = word
    
    if (var.get() == 1):
        
        if (word.lower() in dictionary):
            print(word.lower() + ' is in the dictionary')
            corrected_word = word
        else:
            seq = np.array(list(word.lower()))
            hmm_prediction = model.predict(seq, algorithm='viterbi')
            corrected_word = ''.join([chr(s + 97) for s in hmm_prediction[1:-1]])
        
        corrected_word = ''.join(
            [c.upper() if word[i].istitle() else c 
                for i, c in enumerate(list(corrected_word))]
        )
        
        print(model.log_probability(list(word.lower())))
        print(model.log_probability(list(corrected_word.lower())))
        
        txt.delete("%s-%dc" % (tk.INSERT, len(word)), tk.INSERT)
        txt.insert(tk.INSERT, corrected_word)
    
    

#
def newfile():
    msgBox = tk.messagebox.askquestion('New File', 'Are you sure? Current data will be lost')
    if (msgBox == 'yes'):
        txt.delete("1.0", tk.END)

def openfile():
    filename = filedialog.askopenfilename(
        filetypes=(("text files","*.txt"),("all files","*.*"))
    )
    if (filename):
        txt.delete("1.0", tk.END)
        f = open(filename, 'r')
        txt.insert("1.0", f.read())
    
def savefile():
    filename =  filedialog.asksaveasfilename(
        initialdir = "/",
        title = "Select File",
        filetypes = (("text files","*.txt"),("all files","*.*"))
    )
    print(filename)
    f = open(filename, 'w')
    f.write(txt.get('1.0', 'end-1c'))
    f.close()
    tk.messagebox.showinfo('File Saved', 'File Saved')

def dictionary_event(*args):
    insert_index = len(txt.get("1.0", tk.INSERT))
    end_index = len(txt.get("1.0", tk.END))
    print(insert_index+1)
    print(end_index)
    if (not (insert_index + 1 == end_index)):
        print('not uguali')
    if (insert_index + 1 == end_index):
        if (not txt.get("insert linestart", "insert")[-1].isalpha()):
            global lastword
            print('lastword: ' + lastword)
            txt.delete("%s-1c-%dc" % (tk.INSERT, len(lastword)), "insert-1c")
            txt.insert("insert-1c", lastword)



menubar = Menu(root)
menubar.add_command(label="New", command=newfile)
menubar.add_command(label="Open", command=openfile)
menubar.add_command(label="Save", command=savefile)
menubar.add_command(label="Undo", command=dictionary_event)
root.config(menu=menubar)

# Vertical (y) Scroll Bar
yscrollbar = Scrollbar(root)
yscrollbar.pack(side=RIGHT, fill=Y)


txt = Text(root, width=750, height=500, wrap=NONE,
            yscrollcommand=yscrollbar.set)
txt.pack()

# Configure the scrollbars
yscrollbar.config(command=txt.yview)



txt.bind("<space>", correction_event)
txt.bind(".", correction_event)
txt.bind(",", correction_event)
txt.bind(";", correction_event)
txt.bind("!", correction_event)
txt.bind("?", correction_event)


txt.bind('<Control-u>', dictionary_event)
txt.bind('<Control-U>', dictionary_event)

b = Button(root, text='UNDO', command=dictionary_event)
b.pack()

root.mainloop()
