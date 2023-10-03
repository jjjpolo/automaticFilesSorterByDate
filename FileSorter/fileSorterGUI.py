# =============================================================================
# File Name: fileSorterGUI.py
# =============================================================================
# Purpose:  Makes use of the fileSorter class and provides a GUI tool.
#
# Author:   Jose Juan Jaramillo Polo
# License:  GPLv3
# Notes:    
# =============================================================================

from fileSorter import FileSorter
from fileSorter import __version__ as fileSorterVersion
from jpLogger.jpLogger import *
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
import os
import time
import threading
import sys

# Global variables for logging
if sys.platform.startswith('win'):
    appdata_path = os.environ['APPDATA'] + "\\FileSorter\\"
    log = jpLogger("FileSorter", appdata_path + "fileSorterGUI.log", logging.DEBUG, displayMode.fileAndConsole, 10, 50*1024*1024)
else:
    log = jpLogger("FileSorter", "fileSorterGUI.log", logging.DEBUG, displayMode.fileAndConsole, 10, 50*1024*1024)

def selectInputFolder():
    """Shows a file dialog to select a folder from where the input will be taken,
    then writes the chosen path in the corresponding GUI element (sourceFolder_txt).
    Additionally, once the source folder is selected, gets the number of files inside
    the selected folder and displays the result in the lenFiles_label GUI element. 
    """    
    global sourceFolder_txt, lenFiles_label
    log.info("Select source folder using the askdirectory window")
    sourcePath = filedialog.askdirectory()
    log.info("Source dir: " + sourcePath)
    sourceFolder_txt.delete(0,"end")
    sourceFolder_txt.insert(0, sourcePath)
    if os.path.exists(sourcePath):
        numberOfFilesInFolder = FileSorter.numberOfFilesInFolder(sourcePath)
        newLabelText = "There are: " + str(numberOfFilesInFolder) + " files in this folder."
        log.info(newLabelText)
        lenFiles_label.config (text= newLabelText)
    else:
        messagebox.showinfo("Error", "Invalid source path, try again please.")
        log.warning("Error", "Invalid source path, try again please.")
        sourceFolder_txt.delete(0,"end")

def selectOutputFolder():
    """Shows a file dialog to select a folder where the sorted files will be stored,
    then writes the chosen path in the corresponding GUI element (destinyFolder_txt).
    """ 
    global destinyFolder_txt
    log.info("Selecting output folder using the askdirectory window")
    outputDiPath = filedialog.askdirectory()
    log.info("Output dir: " + outputDiPath)
    destinyFolder_txt.delete(0,"end")
    destinyFolder_txt.insert(0, outputDiPath)

def hint(event):
    """Shows a message box for when the user clicked the threshold_txt GUI element,
    to set the limit of files to be processed. 
    
    Parameters
    ----------
    event: str
        The event that triggered the hint.
    """ 
    messagebox.showinfo("Hint", "Type an integer number to limit the job or leave it blank to process all the files")

def updateProgressBar(processReference, threadToLookAt):
    """Needs to be run as a thread, this function reads the value of progress 
    (from processReference) and updates the ProgressBar. 
    Prior to start tracking progress it disables some of the GUI elements to 
    prevent the user launches another process while this one is running.
    It also add some logs to track this process. 

    Parameters
    ----------
    processReference : obj
        An object reference to take the progress information from.
    threadToLookAt : thread
        A reference to the a thread to look at so that we can have 
        one more evaluation parameter to keep or stop this thread.
    """
    global window, bar, start_btn, sourceFolder_btn, destinyFolder_btn, keepFiles_checkbox

    log.info("Progress bar thread")
    start_btn         ["state"] = DISABLED
    sourceFolder_btn  ["state"] = DISABLED
    destinyFolder_btn ["state"] = DISABLED
    keepFiles_checkbox["state"] = DISABLED
    bar               ["value"] = 0
    window.update_idletasks()
    log.info("GUI elements disabled while thread is running.")
    time.sleep(0.20) # Waiting for mainProcess to start running...
    safeCopyOfProgress = 0
    while safeCopyOfProgress < 100 and threadToLookAt.is_alive():
        try:
            with processReference.mutex:
                log.info("Progress: {0}% numberOfFilesProcessed: {1} numberOfFilesToProcess: {2} ".format(safeCopyOfProgress, processReference.numberOfFilesProcessed, processReference.numberOfFilesToProcess))
                safeCopyOfProgress = processReference.progress
        except:
            log.warning("Could not release/acquire mutex")
        bar["value"] = safeCopyOfProgress
        window.update_idletasks()
        time.sleep(0.1)
    bar["value"] = 100
    window.update_idletasks()   

    safeCopyOfTimeElapsed = ""
    while safeCopyOfTimeElapsed == "":
        try:
            with processReference.mutex:
                safeCopyOfTimeElapsed = processReference.timeElapsed_str
                time.sleep(0.1)
        except:
            log.warning("Could not release/acquire mutex")
    log.info("Job is done. Time elapsed {0} see you next time.".format(safeCopyOfTimeElapsed))
    messagebox.showinfo(title="Info", message="\n FileSorter Job is done. Time elapsed {0} see you next time.".format(safeCopyOfTimeElapsed))
    
    start_btn         ["state"] = NORMAL
    sourceFolder_btn  ["state"] = NORMAL
    destinyFolder_btn ["state"] = NORMAL
    keepFiles_checkbox["state"] = NORMAL
    bar               ["value"] = 0
    log.info("GUI elements reenabled since process is done.")

def doTheJob():
    """Prepares what is needed to start the main process (instantiating a 
    fileSorter object). 
    Creates 3 main threads for: calling fileSorter.run, updateAndLogProgress 
    (which actually calcs the progress) and one for displaying the percentage
    of progress in the progress bar.
    """
    log.info("GUI is about to do the job.")
    sourcePath =sourceFolder_txt.get()
    destinyPath = destinyFolder_txt.get()
    threshold = threshold_txt.get()
    log.info("Source dir: " + sourcePath)
    log.info("Output dir: " + destinyPath)
    log.info("Files to be processed: " + threshold)
    log.info("Keep original files: " + ("True" if keepOriginalFile_state.get() is True else "False"))

    if not os.path.exists(sourcePath):
        messagebox.showinfo("Error", "Invalid source path!")
        log.error("Source path not found")
        return
    
    if not os.path.exists(destinyPath):
        messagebox.showinfo("Error", "Invalid destiny path!")
        log.error("Destiny path not found")
        return
    
    if threshold == "" or threshold == " " or threshold.isnumeric():

        # Waiting for threads (i.e. using join method) blocks the progress bar
        # so the measuring of elapsed time has been moved to the updateProgressBar
        # method. I am leaving this comment here just for future personal reference.

        # Object needed instantiation:
        masterMutex = threading.Lock()
        fileSorterInstance = FileSorter(log, sourcePath, destinyPath, -1 if threshold == "" else int(threshold), keepOriginalFile_state.get(),masterMutex)
        log.info("Mutex and fileSorterInstance have been instantiated")

        # Threads creation: 
        fileSorterThread = threading.Thread(target=fileSorterInstance.run, args=())
        updateAndLogProgressThread = threading.Thread(target=fileSorterInstance.updateAndLogProgress, args=(fileSorterInstance,))
        updateProgressBarThread = threading.Thread(target=updateProgressBar, args=(fileSorterInstance,fileSorterThread))
        log.info("Threads have been created and are ready to get started.")
        
        # Launch and wait for threads
        fileSorterThread.start()
        updateAndLogProgressThread.start()
        updateProgressBarThread.start()
        log.info("Threads are now running.")

        # Somehow waiting for threads to "join" does not allow the progress bar
        # to be updated successfully, however, from the user perspective it is
        # not needed to wait for the threads to join since the main buttons are
        # DISABLED while the progress is less than 100 so the user shall wait
        # for the threads to be done.

    else:
        messagebox.showinfo("Error", "Wrong limit of files value!")        
        return

def main():
    """Defines GUI elements, sizes, positions and behaviors.
    """
    global window
    window = Tk()
    window.geometry('515x280')
    window.title("Automatic Photo Sorter {0}".format(fileSorterVersion))
    log.info("Automatic Photo Sorter {0}".format(fileSorterVersion))
    log.info("Base GUI has been created")

    #----------------------------------------row separator 0:
    source_label = Label(window, text="*Source folder:", font=("Arial Bold", 12))
    source_label.grid(column=0, row=0, padx = (10,5), pady = (20,10))
    #||||||||||||||||||||column separator 0:
    global sourceFolder_txt
    sourceFolder_txt = Entry(window,width=50)
    sourceFolder_txt.grid(column=1, row=0, padx = 5, pady = (20,10))
    #||||||||||||||||||||column separator 1:
    global sourceFolder_btn
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
    global destinyFolder_btn
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
    global keepOriginalFile_state, keepFiles_checkbox
    keepOriginalFile_state = BooleanVar()
    keepOriginalFile_state.set(True) #set check state
    keepFiles_checkbox = Checkbutton(window, text='Keep original files', var = keepOriginalFile_state, font=("Arial Bold", 10))
    keepFiles_checkbox.grid(column=0, row=5, padx=(10,0))
    #||||||||||||||||||||column separator 0:
    global start_btn
    start_btn = Button(window, text=" Start ", command=doTheJob, font=("Arial Bold", 14))
    start_btn.grid(column=0, columnspan = 3, row=5, pady = (10,20))

    log.info("All the GUI elements have been added to the main view")
    window.mainloop()

if __name__ == "__main__":
    main()
    log.info("Powering off...")