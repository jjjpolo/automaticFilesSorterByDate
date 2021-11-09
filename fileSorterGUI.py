from tkinter import *
from tkinter import filedialog #Lets use file browser
from tkinter.ttk import Progressbar #Lets use progress bar
import fileSorterCLI
import time
from tkinter import messagebox
import os
import threading

def selectInputFolder():
    """Shows a file dialog to select a folder from where the input will be taken,
    then writes the chosen path in the corresponding GUI element (sourceFolder_txt).
    Additionally, once the source folder is selected, gets the number of files inside
    the selected folder and displays the result in the lenFiles_label GUI element. 
    """    
    print("Select input folder...")
    sourcePath = filedialog.askdirectory()
    print(sourcePath)
    global sourceFolder_txt
    sourceFolder_txt.delete(0,"end")
    sourceFolder_txt.insert(0, sourcePath)
    if os.path.exists(sourcePath):
        numberOfFilesInFolder = fileSorterCLI.numberOfFilesInFolder(sourcePath)
        global lenFiles_label
        lenFiles_label.config (text= "There are: " + str(numberOfFilesInFolder) + " files in this folder.")
    else:
        messagebox.showinfo("Error", "Invalid source path, try again please.")
        sourceFolder_txt.delete(0,"end")

def selectOutputFolder():
    """Shows a file dialog to select a folder where the sorted files will be stored,
    then writes the chosen path in the corresponding GUI element (destinyFolder_txt).
    """ 
    print("Select output folder...")
    outputDiPath = filedialog.askdirectory()
    print(outputDiPath)
    global destinyFolder_txt
    destinyFolder_txt.delete(0,"end")
    destinyFolder_txt.insert(0, outputDiPath)

def hint(event):
    """Shows a message box for when the user clicked the threshold_txt GUI element,
    to set the limit of files to be processed. 
    """ 
    messagebox.showinfo("Hint", "Enter an integer number to limit the job or leave it blank to process all the files")

def updateProgressBar():
    """Run as a thread, this function reads the value of progress (global var in fileSorterCLI)
    and update the value of the progress bar based on it. 
    """
    print("[updateProgressBar] Progress bar thread")
    global window, bar, start_btn
    start_btn ["state"] = DISABLED
    bar["value"] = 0
    window.update_idletasks()
    time.sleep(0.20) # Waiting for mainProcess to start running...
    keepUpdatingProgressBar = True #This var will tack fileSorterCLI.mainProcessIsRunning and will be updated only after mutex.acquired()
    while keepUpdatingProgressBar:
        fileSorterCLI.acquireMutex("updateProgressBar")
        progress = (fileSorterCLI.numberOfFilesProcessed * 100) / fileSorterCLI.numberOfFilesToProcess
        bar["value"] = progress
        keepUpdatingProgressBar = fileSorterCLI.mainProcessIsRunning
        print("[updateProgressBar] progress: {0}% numberOfFilesProcessed: {1} numberOfFilesToProcess: {2} mainProcessIsRunning: {3}".format(progress, fileSorterCLI.numberOfFilesProcessed, fileSorterCLI.numberOfFilesToProcess, keepUpdatingProgressBar))
        window.update_idletasks()
        fileSorterCLI.releaseMutex("updateProgressBar")
        time.sleep(0.1)
    bar["value"] = 100
    window.update_idletasks()
    messagebox.showinfo(title="Info", message="Done!")
    start_btn ["state"] = NORMAL

def doTheJobWrapper():
    """Acts similar to 'doTheJob' function in fileSorterCLI by preparing what is needed
    to start the main process (calling the corresponding function from fileSorterCLI).
    Creates two main threads for calling fileSorterCLI.doTheJob and for displaying the 
    percentage of progress in the progress bar.
    """
    sourcePath =sourceFolder_txt.get()
    destinyPath = destinyFolder_txt.get()
    threshold = threshold_txt.get()

    if not os.path.exists(sourcePath):
        messagebox.showinfo("Error", "Invalid source path!")        
        return
    
    if threshold == "" or threshold == " " or threshold.isnumeric():
        mainThread = threading.Thread(target=fileSorterCLI.doTheJob,args = (sourcePath,destinyPath,-1 if threshold == "" else int(threshold), keepOriginalFile_state.get()))
        mainThread.start()
        progressBarThread = threading.Thread(target=updateProgressBar,args=())
        progressBarThread.start()
    else:
        messagebox.showinfo("Error", "Wrong limit of files value!")        
        return

def main():
    """Defines GUI elements, sizes, positions and behaviors.
    """
    global window
    window = Tk()
    window.geometry('515x280')
    window.title("Automatic Photo Sorter {0}".format(fileSorterCLI.version))

    #----------------------------------------row separator 0:
    source_label = Label(window, text="*Source folder:", font=("Arial Bold", 12))
    source_label.grid(column=0, row=0, padx = (10,5), pady = (20,10))
    #||||||||||||||||||||column separator 0:
    global sourceFolder_txt
    sourceFolder_txt = Entry(window,width=50)
    sourceFolder_txt.grid(column=1, row=0, padx = 5, pady = (20,10))
    #||||||||||||||||||||column separator 1:
    sourceFolder_btn = Button(window, text="...", command=selectInputFolder)
    sourceFolder_btn.grid(column=2, row=0, padx = (5,10), pady = (20,10))

    #----------------------------------------row separator 1:
    global lenFiles_label
    lenFiles_label = Label(window, text="Waiting for  a valid source path dir to be selected...", font=("Arial Bold", 8))
    lenFiles_label.grid(column=0, columnspan=6, row=1, padx = (10,5), pady =(0,10))

    #----------------------------------------row separator 2:
    destiny_label = Label(window, text="*Destiny folder:", font=("Arial Bold", 12))
    destiny_label.grid(column=0, row=2, padx = (10,5), pady = 10)
    #||||||||||||||||||||column separator 1:
    global destinyFolder_txt
    destinyFolder_txt = Entry(window,width=50)
    destinyFolder_txt.grid(column=1, row=2, padx = 5, pady = 10)
    #||||||||||||||||||||column separator 2:
    destinyFolder_btn = Button(window, text="...", command=selectOutputFolder)
    destinyFolder_btn.grid(column=2, row=2, padx = (5,10), pady = 10)

    #----------------------------------------row separator 3:
    threshold_label = Label(window, text="Limit the job to :", font=("Arial Bold", 12))
    threshold_label.grid(column=0, row=3, padx = (10,5), pady = 10)
    #||||||||||||||||||||column separator 0:
    global threshold_txt 
    threshold_txt = Entry(window,width=50)
    threshold_txt.grid(column=1, row=3, padx = 5, pady = 10)
    threshold_txt.bind("<1>", hint)
    #||||||||||||||||||||column separator 1:
    threshold_label2 = Label(window, text="files", font=("Arial Bold", 12))
    threshold_label2.grid(column=2, columnspan = 3, row=3,padx = (5,10), pady = 10)

    #----------------------------------------row separator 4:
    global bar
    bar = Progressbar(window, length=480)
    bar.grid(column=0, columnspan = 3, row=4,  sticky = W+E, pady= 10, padx = 10)

    #----------------------------------------row separator 5:
    global keepOriginalFile_state
    keepOriginalFile_state = BooleanVar()
    keepOriginalFile_state.set(True) #set check state
    keepFiles_checkbox = Checkbutton(window, text='Keep original files', var = keepOriginalFile_state, font=("Arial Bold", 10))
    keepFiles_checkbox.grid(column=0, row=5, padx=(10,0))
    #||||||||||||||||||||column separator 0:
    global start_btn
    start_btn = Button(window, text=" Start ", command=doTheJobWrapper, font=("Arial Bold", 14))
    start_btn.grid(column=0, columnspan = 3, row=5, pady = (10,20))

    window.mainloop()

if __name__ == "__main__":
    main()