import os    
import sys                   
from datetime import datetime   # To handle datetime 
import platform                 # To identify the operative system used
import shutil                   # To copy, move, and rename files
import argparse                 # to handle arguments from the command line.
import time
import threading

version = "v1.1.0"
numberOfFilesProcessed = 0
mainProcessIsRunning = False
numberOfFilesToProcess = 0
progress = 0 
mutex = threading.Lock()

def convert_date(timestamp):
    """Receives a date in epoch format and returns a string 
    human-readable format.

    Parameters
    ----------
    timestamp : str
        Date in epoch format.

    Returns
    -------
    str
        Date in a human-readable format.
    """
    d = datetime.utcfromtimestamp(timestamp)
    formated_date = d.strftime('%Y-%m-%d') #YYYY-MM-DD
    return formated_date

def createFolder(newDirPath):
    """Creates a new folder in the path specified

    Parameters
    ----------
    newDirPath : str
        Full directory path to be created.
    """
    if(False == os.path.exists(newDirPath)):
        os.umask(0)
        os.makedirs(newDirPath, 7777)

def sortFile(sourcePath, file, destinyPath, keepOriginalFile = True):
    """Sorts a file based on its last modification date properties.
    If keepOriginalFile is True, the file will be copied to the, if keepOriginalFile
    is False, the file will moved to the destination directory.

    Parameters
    ----------
    sourcePath : str
        Directory path where the file to be sorted is located.
    file : str
        Name of the file to be sorted. 
        (This will be appended to the sourcePath to create the full path)
    destinyPath : str
        Directory path where the sorted file will be either copied or moved.
    keepOriginalFile : bool, optional
        If this set to True, the original file will be copied, otherwise it will be moved.

    Returns
    -------
    str
        Date in a human-readable format.
    """
    sourceFilePath = os.path.join(sourcePath, file.name)
    if os.path.isdir(sourceFilePath): 
        print("\n[sortFile] " +  str(file.name) + " is a folder, the software will skip it.")
        return False
    elif ("fileSorter" in file.name):
        print("\n[sortFile] " + str(file.name) + " seems to be part of fileSorter software, the software will skip it.")
        return False
    else:
        fileProperties = file.stat() # Getting file's properties. 
        lastModificationDate = convert_date(fileProperties.st_mtime) # Getting Last Modification date and convert it from epoch to human format.
        destinyFileFolderPath = os.path.join(destinyPath, lastModificationDate) # Creating destiny folder path based on last modification date. 
        createFolder(destinyFileFolderPath)
        print("\n[sortFile] " + sourceFilePath + " || " + lastModificationDate  + "  -->  " + destinyFileFolderPath)
        
        if(False == os.path.exists(destinyFileFolderPath + "\\" +file.name)):
            if(keepOriginalFile):
                shutil.copy2(sourceFilePath, destinyFileFolderPath) # FYI shutil copy can't copy folders, instead use copytree
            else:
                shutil.move(sourceFilePath, destinyFileFolderPath)
            return True
        else:
            print("[sortFile] There is a file with the same name on the destiny folder.")
            return False

def releaseMutex(functionName = "Undefined", logging = False): 
    """Tries to release the global mutex to protect shared variables among
    mainProcess and updateAndDisplayProgress.
    In case it is not possible to release the mutex it handles the exception
    so that the software can continue.

    Parameters
    ----------
    functionName : str
        The name of the function that is trying to release the mutex.
        This is mainly for logging purposes.
    logging : bool, optional
        Logging enable.
    
    Returns
    -------
    bool
        True it everything goes well and False in cases an exception shows up.
    """
    global mutex
    if(logging):
        try:
            print("[{0}] About to release mutex.".format(functionName))
            mutex.release()
        except:
            print("[{0}] Unable to release mutex".format(functionName))
            return False
        print("[{0}] Mutex released successfully.".format(functionName))
    else:
        try:
            mutex.release()
        except:
            return False
    return True

def acquireMutex(functionName = "Undefined", logging = False): 
    """Tries to acquire the global mutex to protect shared variables among
    mainProcess and updateAndDisplayProgress.
    In case it is not possible to acquire the mutex it handles the exception
    so that the software can continue.

    Parameters
    ----------
    functionName : str
        The name of the function that is trying to acquire the mutex.
        This is mainly for logging purposes.
    logging : bool, optional
        Logging enable.
    
    Returns
    -------
    bool
        True it everything goes well and False in cases an exception shows up.
    """
    global mutex
    if(logging):
        try:
            print("[{0}] About to acquire mutex.".format(functionName))
            mutex.acquire()
        except:
            print ("[{0}] Unable to acquire mutex".format(functionName))
            return False
        print("[{0}] Mutex acquired successfully.".format(functionName))
    else:
        try:
            mutex.acquire()
        except:
            return False
    return True

def updateAndDisplayProgress():
    """Run as a thread, this function do the maths to update the progress of 
    the process and prints its in the standard output. 
    """
    global progress, mutex
    keepUpdatingProgress =  True #This var will tack mainProcessIsRunning and will be updated only after mutex.acquired()
    time.sleep(0.15) #Waiting for global variables to be set for the 1st time.
    while keepUpdatingProgress:
        acquireMutex("updateAndDisplayProgress")
        keepUpdatingProgress = mainProcessIsRunning   #Updating its value only when mutex.acquire() is called.
        progress = (numberOfFilesProcessed * 100) / numberOfFilesToProcess
        print("[updateAndDisplayProgress] progress: {0}% numberOfFilesProcessed: {1} numberOfFilesToProcess: {2} mainProcessIsRunning: {3}".format(progress, numberOfFilesProcessed, numberOfFilesToProcess, keepUpdatingProgress))
        releaseMutex("updateAndDisplayProgress")
        time.sleep(0.1)
    print("[updateAndDisplayProgress] progress: 100%")

def mainProcess(sourcePath, destinationPath, keepOriginalFile = True):
    """Scans recursively all the files in the source directory an subdirectories, 
    and passes them as a parameter to the sortFile function to be sorted based on
    its last modification date property.

    Parameters
    ----------
    sourcePath : str
        Dir path from where the files will be taken.
    destinationPath : str
        Dir path where the sorted files will be located.
    numberOfFiles : int
        Limit of files to be processed. If it was set to -1 there will be no limit.
    keepOriginalFile : bool, optional
        Boolean flag indicating if the file should be copied or moved when sorting it.   
    """
    global numberOfFilesProcessed, mutex
    if numberOfFilesProcessed >= numberOfFilesToProcess:
        return
    currentDirectory = os.scandir(sourcePath)
    for path in currentDirectory:
        acquireMutex("mainProcess")
        if(os.path.isfile(path)):
            if numberOfFilesProcessed >= numberOfFilesToProcess:
                releaseMutex("mainProcess") #Releasing mutex due to end condition. 
                return
            if sortFile(sourcePath, path, destinationPath, keepOriginalFile):
                numberOfFilesProcessed = numberOfFilesProcessed + 1
            releaseMutex("mainProcess") #Releasing mutex before next for iteration.
        else:
            releaseMutex("mainProcess") #Releasing mutex before recursive iteration.
            mainProcess(os.path.join(sourcePath, path.name),destinationPath, keepOriginalFile)

def numberOfFilesInFolder(dirPath):
    """Returns the number of files in the given directory (recursively).

    Parameters
    ----------
    dirPath : str
        Dir path from where we need the number of files.
    
    Returns
    -------
    int
        Number of files in the given directory.
    """
    total = 0
    for root, dirs, files in os.walk(dirPath):
            total += len(files) 
    return total

def doTheJob(sourcePath, destinationPath, numberOfFiles = -1, keepOriginalFile = True, updateProgressFunction = None):
    """This is the main organizer function which calls the needed functions in the right 
    order, creates thread for the main process and the progress calc and display, and handles
    the threads starting by passing the corresponding parameters to each one. 

    Parameters
    ----------
    sourcePath : str
        Dir path from where the files will be taken.
    destinationPath : str
        Dir path where the sorted files will be located.
    numberOfFiles : int, optional
        Limit of files to be processed. If it was set to -1 there will be no limit.
    keepOriginalFile : bool, optional
        Boolean flag indicating if the file should be copied or moved when sorting it.   
    updateProgressFunction : func, optional
        A function pointer that helps to identify who is going to update the progress (GUI or CLI mode).
        In CLI mode it is updateAndDisplayProgress(), in GUI mode is updateProgressBar.

    """
    global numberOfFilesToProcess, numberOfFilesProcessed, mainProcessIsRunning
    numberOfFilesProcessed = 0
    numberOfFilesToProcess = numberOfFilesInFolder(sourcePath) if numberOfFiles == -1 else numberOfFiles
    mainProcessIsRunning = True

    mainThread = threading.Thread(target=mainProcess, args=(sourcePath, destinationPath, keepOriginalFile))
    mainThread.start()
    
    if updateProgressFunction is not None: #Means that doTheJob was called by the CLI mode
        progressUpdateThread = threading.Thread(target=updateProgressFunction, args=())
        progressUpdateThread.start()
    #else  #In GUI the updating progress is handled in fileSorterGUI.py

    mainThread.join()               #Waiting for the mainThread to be done.
    mainProcessIsRunning = False    #Notifying progressUpdateThread that mainThread is done.
    if updateProgressFunction is not None:
        progressUpdateThread.join()
    print("[doTheJob] Process Done!")

#_________________________________________________ for CLI mode

def argsAreValid(sourcePath, numberOfFiles):
    """Evaluates if sourcePath is a directory and if numberOfFiles is a number
    within the valid range. Keep in mind that numberOfFiles set to -1 means that
    no limit has been specified so all the files will be processed.

    Parameters
    ----------
    sourcePath : str
        Dir path from where the files will be taken.
    numberOfFile : int
        Limit of files to be processed.     
    """
    if (str(numberOfFiles).isnumeric() or str(numberOfFiles) == "-1"):
        if os.path.isdir(sourcePath):
            return True
        else:
            print ("[argsAreValid] {0} is not a valid sourcePath.".format(sourcePath))
    else:
        print ("[argsAreValid] {0} is not a valid value for numberOfFiles".format(numberOfFiles))
    return False

def displayArgValues(args):
    """Receives an object (args) made with the parse_args() method from the argparse module
    with sourcePath, destinationPath, numberOfFiles and keepOriginalFile to display
    its value

    Parameters
    ----------
    args : argparse
        Arguments list made with the parse_args() method from the argparse module.
    """
    print( "\t\tsourcePath        =   {0} \n \
            \tdestinationPath   =   {1} \n \
            \tnumberOfFiles     =   {2} \n \
            \tkeepOriginalFiles =   {3}"
            .format(args.sourcePath, args.destinationPath, "no limit" if args.numberOfFiles == -1 else args.numberOfFiles, args.keepOriginalFiles))

def main(argv):
    """Receives arguments (argv) from the command line and makes a decision based on
    what the user typed.
    If no arguments were passed by the user (i.e. len(argv)==0), the default values 
    (sourcePath, destinationPath, numberOfFiles, keepOriginalFile) will be used.

    Parameters
    ----------
    argv : str-list
        Arguments passed from the command line.
    """
    print("\nAutomatic Photo Sorter {0} \n".format(version))
    parser = argparse.ArgumentParser(description = "Searchs for files recursively in a directory, \
                                                    gets the last modification date, \
                                                    and sorts each file based on it")
    parser.add_argument("-s", "--sourcePath",
                        metavar="<sourcePath>",
                        type=str,
                        help="Path of the source directory. Skip it for default value (./)",
                        default="./",
                        nargs='?',
                        const="./")
    parser.add_argument("-d", "--destinationPath",
                        metavar="<destinationPath>",
                        type=str,
                        help="Path of the destination path. Skip it for default value (./)",
                        default="./",
                        nargs='?',
                        const="./")
    parser.add_argument("-n","--numberOfFiles",
                        metavar="<numberOfFiles>",
                        type=int,
                        help="(Optional) The number of files to be processed. Skip this for no limit.",
                        default=-1,
                        nargs='?',
                        const=-1)
    parser.add_argument("-k","--keepOriginalFiles",
                        metavar="<keepOriginalFiles>",
                        type=str, # Based on argparse documentation bool type is not recommended since void str is false. 
                        help="By default this is set to True so files will be sorted as a copy of the originals. \
                            If you want to move files instead of copying them, set this explicitly to False.",
                        default="True", # Default value for when no using this parameter.
                        nargs='?',
                        const="True")  # Default value for when using this parameter with no explicit value typed.
    
    # Arguments length validation
    args=parser.parse_args()
    if len(argv) == 0:
        parser.print_help()
        print("\n\tNo arguments detected. Will use default values:")
    else:
        print("\n\tThese are the current settings:")

    # Ask user for confirmation before continuing
    displayArgValues(args)
    confirmation = input("\n\tContinue? Y/n: ")
    if (confirmation.lower() == "n"):
        print("Action cancelled, exiting now...")
        sys.exit(0)
    
    # Arguments validation (directory path and numberOfFiles to be processed)    
    if argsAreValid(args.sourcePath, args.numberOfFiles):
        doTheJob(args.sourcePath, args.destinationPath, args.numberOfFiles, False if (args.keepOriginalFiles.lower() == "false") else True, updateAndDisplayProgress)
        sys.exit(0)
    else:
        print("Error due to invalid arguments.")
        sys.exit(1)

if __name__== "__main__":
    main(sys.argv[1:])  # Ignoring sys.argv[0] since it is the python name file
                        # e.g. python.exe fileSorterCLI.py