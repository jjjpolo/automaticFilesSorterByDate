from tkinter import *
from tkinter import filedialog #Lets use file browser
from tkinter.ttk import Progressbar #Lets use progress bar
from fileSorterCLI import *
import time
from tkinter import messagebox

window = Tk()
window.geometry('500x300')
window.title("Automatic Photo Sorter")

#_________________________________________________ROW 0:

source_label = Label(window, text="*Source folder:", font=("Arial Bold", 12))
source_label.grid(column=0, row=0,padx = (10,5), pady = (20,10))

sourceFolder_txtbox = Entry(window,width=50)
sourceFolder_txtbox.grid(column=1, row=0, padx = 5, pady = (20,10))

def selectInputFolder():
    print("Select input folder...")
    filename = filedialog.askdirectory()
    print(filename)
    sourceFolder_txtbox.delete(0,"end")
    sourceFolder_txtbox.insert(0, filename)
    try:
        lenFiles_label.config (text= "There are: " + str(len(os.listdir(sourceFolder_txtbox.get()))) + " files in the source folder")
    except:
        print("Error source folder")
sourceFolder_btn = Button(window, text="...", command=selectInputFolder)
sourceFolder_btn.grid(column=2, row=0, padx = (5,10), pady = (20,10))

#_________________________________________________ROW 1:

lenFiles_label = Label(window, text="Waiting for select source folder input...", font=("Arial Bold", 8))
lenFiles_label.grid(column=0, columnspan=6, row=1, padx = (10,5), pady =(0,10))

#_________________________________________________ROW 2:

destiny_label = Label(window, text="*Destiny folder:", font=("Arial Bold", 12))
destiny_label.grid(column=0, row=2,padx = (10,5), pady = 10)

destinyFolder_txtbox = Entry(window,width=50)
destinyFolder_txtbox.grid(column=1, row=2, padx = 5, pady = 10)

def selectOutputFolder():
    print("Select output folder...")
    filename = filedialog.askdirectory()
    print(filename)
    destinyFolder_txtbox.delete(0,"end")
    destinyFolder_txtbox.insert(0, filename)
destinyFolder_btn = Button(window, text="...", command=selectOutputFolder)
destinyFolder_btn.grid(column=2, row=2, padx = (5,10), pady = 10)


#_________________________________________________ROW 3:

threshold_label = Label(window, text="Limit the job to :", font=("Arial Bold", 12))
threshold_label.grid(column=0, row=3,padx = (10,5), pady = 10)

threshold_txtbox = Entry(window,width=50)
threshold_txtbox.grid(column=1, row=3, padx = 5, pady = 10)

threshold_label2 = Label(window, text="files", font=("Arial Bold", 12))
threshold_label2.grid(column=2, columnspan = 3, row=3,padx = (5,10), pady = 10)
#_________________________________________________ROW 4:

bar = Progressbar(window, length=480)
bar.grid(column=0, columnspan = 3, row=4,  sticky = W+E, pady= 10, padx = 10)

#_________________________________________________ROW 5:

def mainProcess_GUImode(sourcePath, destinyPath, threshold = -1):
    totalAmoutnFiles = len(os.listdir(sourcePath))
    if threshold == -1:
        threshold = totalAmoutnFiles
    count = 0
    #print(threshold)
    with os.scandir(sourcePath) as files:
        for file in files:
            sortFile(sourcePath, file, destinyPath)   

            percent = (count * 100) / threshold
            print(str(percent) + "%")
            bar['value'] = percent
            window.update_idletasks()
            time.sleep(0.1)

            count = count + 1
            if count >= threshold:
                break;
    bar['value'] = 100
    print("\n DONE!")
    messagebox.showinfo(title="Info", message="Done!")

def callPhotoSorter():
    sourcePath =sourceFolder_txtbox.get()
    destinyPath = destinyFolder_txtbox.get()
    threshold = threshold_txtbox.get()
    if(sourcePath == "" or sourcePath == " " or len(sourcePath)== 0 or (False == os.path.exists(sourcePath))):
        print("Please check the source path input")
        source_isOK = False
    else:
        source_isOK = True

    if (destinyPath == "" or destinyPath == " " or len(destinyPath)== 0 or (False == os.path.exists(destinyPath))):
        print("Please check the destiny path input")
        destiny_isOK = False
    else:
        destiny_isOK = True
    
    if(source_isOK and destiny_isOK):
        if (threshold is None or threshold == " " or 0 == len(threshold)):
                print("All the files will be processed...")
                mainProcess_GUImode(sourcePath, destinyPath)
        else:
            if threshold.isnumeric():
                print("Only " + str(threshold) + " files")
                mainProcess_GUImode(sourcePath, destinyPath, int(threshold))
            else:
                print("Wrong limit value entered")
        #print(sourcePath)
        #print(destinyPath)
        #print(threshold)
    else:
        print("Please chel input parameters!")

start_btn = Button(window, text=" Start ", command=callPhotoSorter, font=("Arial Bold", 14))
start_btn.grid(column=0, columnspan = 3, row=5, pady = (10,20))

window.mainloop()