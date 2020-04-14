from tkinter import *
from tkinter import filedialog #Lets use file browser
from tkinter.ttk import Progressbar #Lets use progress bar

window = Tk()
window.geometry('500x250')
window.title("Automatic Photo Sorter")

#_________________________________________________ROW 0:

input_label = Label(window, text="*Source folder:", font=("Arial Bold", 12))
input_label.grid(column=0, row=0,padx = (10,5), pady = (20,10))

inputFolder_txtbox = Entry(window,width=50)
inputFolder_txtbox.grid(column=1, row=0, padx = 5, pady = (20,10))

def selectInputFolder():
    print("Select input folder...")
    filename = filedialog.askdirectory()
    print(filename)
    inputFolder_txtbox.delete(0,"end")
    inputFolder_txtbox.insert(0, filename)
inputFolder_btn = Button(window, text="...", command=selectInputFolder)
inputFolder_btn.grid(column=2, row=0, padx = (5,10), pady = (20,10))

#_________________________________________________ROW 1:

output_label = Label(window, text="*Destiny folder:", font=("Arial Bold", 12))
output_label.grid(column=0, row=1,padx = (10,5), pady = 10)

outputFolder_txtbox = Entry(window,width=50)
outputFolder_txtbox.grid(column=1, row=1, padx = 5, pady = 10)

def selectOutputFolder():
    print("Select output folder...")
    filename = filedialog.askdirectory()
    print(filename)
    outputFolder_txtbox.delete(0,"end")
    outputFolder_txtbox.insert(0, filename)
outputFolder_btn = Button(window, text="...", command=selectOutputFolder)
outputFolder_btn.grid(column=2, row=1, padx = (5,10), pady = 10)

#_________________________________________________ROW 2:

threshold_label = Label(window, text="Limit the job to :", font=("Arial Bold", 12))
threshold_label.grid(column=0, row=2,padx = (10,5), pady = 10)

threshold_txtbox = Entry(window,width=50)
threshold_txtbox.grid(column=1, row=2, padx = 5, pady = 10)

threshold_label2 = Label(window, text="files", font=("Arial Bold", 12))
threshold_label2.grid(column=2, columnspan = 3, row=2,padx = (5,10), pady = 10)
#_________________________________________________ROW 3:

bar = Progressbar(window, length=480)
bar.grid(column=0, columnspan = 3, row=3,  sticky = W+E, pady= 10, padx = 10)

#_________________________________________________ROW 4:

def callPhotoSorter():
    print("Calling photo sorter with current arguments...")

start_btn = Button(window, text=" Start ", command=callPhotoSorter, font=("Arial Bold", 14))
start_btn.grid(column=0, columnspan = 3, row=4, pady = (10,20))

window.mainloop()