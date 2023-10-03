# =============================================================================
# File Name: fileSorterCLI.py
# =============================================================================
# Purpose:  Makes use of the fileSorter class and provides a command line tool.
#
# Author:   Jose Juan Jaramillo Polo
# License:  GPLv3
# Notes:    
# =============================================================================

from fileSorter import FileSorter
from fileSorter import __version__ as fileSorterVersion
from importlib.metadata import files
from jpLogger.jpLogger import *
import argparse
import os
import sys
import threading
import time

def cliProgressBar(progress):
    """Draws a progress bar on the terminal.
    It only makes sense calling recursively this function so that the progress
    bar is overridden every after calling (notice that is does \r when printing).
    
    Parameters
    ----------
    progress : double
        The percentage of progress to be drawn on the progress bar.
    """
    bar = ('⧯' * int(progress)) + ('-' * (100- int(progress)))
    print(f"\r|{bar}| {progress:.2f}%",end="\r")

def displayCliProgressBar(processReference, threadToLookAt, log):
    """Needs to be run as a thread, this function reads the value of progress 
    (from processReference) and calls cliProgressBar passing the updated value
    of the progress. It also add some logs to track this process.

    Parameters
    ----------
    processReference : obj
        An object reference to take the progress information from.
    threadToLookAt : thread
        A reference to the a thread to look at so that we can have 
        one more evaluation parameter to keep or stop this thread.
    log : obj
        An instance of jpLogger to append data to the log file.
    """
    safeCopyOfProgress = 0
    while safeCopyOfProgress < 100 and threadToLookAt.is_alive():
        try:
            with processReference.mutex:
                safeCopyOfProgress = processReference.progress
                log.info("Progress: {0}% numberOfFilesProcessed: {1} numberOfFilesToProcess: {2} ".format(safeCopyOfProgress, processReference.numberOfFilesProcessed, processReference.numberOfFilesToProcess))
        except:
            log.warning("Could not release/acquire mutex")
        cliProgressBar(safeCopyOfProgress)
    cliProgressBar(100)
    log.info("Progress: 100%, joining to main thread...")

    safeCopyOfTimeElapsed = ""
    while safeCopyOfTimeElapsed == "":
        try:
            with processReference.mutex:
                safeCopyOfTimeElapsed = processReference.timeElapsed_str
                time.sleep(0.1)
        except:
            log.warning("Could not release/acquire mutex")
    
    log.info("Job is done. Time elapsed {0} see you next time.".format(safeCopyOfTimeElapsed))
    print("\n Job is done. Time elapsed {0} see you next time.".format(safeCopyOfTimeElapsed))

def argsAreValid(sourcePath, numberOfFiles, log):
    """Evaluates if sourcePath is a directory and if numberOfFiles is a number
    within the valid range. Keep in mind that numberOfFiles set to -1 means that
    no limit has been specified so all the files will be processed.

    Parameters
    ----------
    sourcePath : str
        Dir path from where the files will be taken.
    numberOfFile : int
        Limit of files to be processed.     
    log : obj
        An instance of jpLogger to append data to the log file.
    """
    if (str(numberOfFiles).isnumeric() or str(numberOfFiles) == "-1"):
        if os.path.isdir(sourcePath):
            return True
        else:
            log.error("{0} is not a valid sourcePath".format(sourcePath))
            print("{0} is not a valid sourcePath".format(sourcePath))
    else:
        log.error("{0} is not a valid value for numberOfFiles".format(numberOfFiles))
        print("{0} is not a valid value for numberOfFiles".format(numberOfFiles))
    return False

def displayArgValues(args, log):
    """Receives an object (args) made with the parse_args() method from the argparse module
    with sourcePath, destinationPath, numberOfFiles and keepOriginalFile to display
    its value

    Parameters
    ----------
    args : argparse
        Arguments list made with the parse_args() method from the argparse module.
    log  : obj
        An instance of jpLogger to append data to the log file.
    """
    numberOfFilesInSourceFolder = FileSorter.numberOfFilesInFolder(args.sourcePath)
    log.info("sourcePath: {0}".format(args.sourcePath))
    log.info("destinationPath: {0}".format(args.destinationPath))
    log.info("numberOfFiles: {0}".format("no limit" if args.numberOfFiles == -1 else args.numberOfFiles))
    log.info("Number of files in this folder: {0}".format(numberOfFilesInSourceFolder))
    log.info("keepOriginalFiles: {0}".format(args.keepOriginalFiles))
    log.info("yesToAll: {0}".format(args.yesToAll))
    # The following print lines cannot be replaced with the logging class
    # due to tab characters that would not make sense to have in the log file. 
    print("These are the current settings:")
    print("\t\tSourcePath                          = {0} \n \
             \tNumber of files in source directory = {1} \n \
             \tDestination Path                    = {2} \n \
             \tNumber of files to be processed     = {3} \n \
             \tKeep Original Files                 = {4} \n \
             \tNo user prompts                     = {5}"
            .format(args.sourcePath,\
                numberOfFilesInSourceFolder,\
                args.destinationPath,\
                "no limit" if args.numberOfFiles == -1 else args.numberOfFiles,\
                args.keepOriginalFiles, \
                args.yesToAll))

def doTheJob(log,args):
    """Once the arguments were validated, this function will
    launch the 3 threads needed to do the job. 
    It will wait for them to join (get done) and then will 
    return to the where this function was called. 

    Parameters
    ----------
    log  : obj
        An instance of jpLogger to append data to the log file.
    args : str-list
        Arguments passed from the command line.
    """

    # Waiting for threads (i.e. using join method) blocks the progress bar
    # so the measuring of elapsed time has been moved to the displayCliProgressBar
    # method. I am leaving this comment here just for future personal reference.

    #Objects needed instantiation:
    masterMutex = threading.Lock()
    fileSorterInstance = FileSorter(log, args.sourcePath, \
                                    args.destinationPath, \
                                    args.numberOfFiles,   \
                                    False if (args.keepOriginalFiles.lower() == "false") else True,\
                                    masterMutex)

    # Thread instantiation: 
    fileSorterThread = threading.Thread(target=fileSorterInstance.run, args=())
    updateAndLogProgressThread = threading.Thread(target=fileSorterInstance.updateAndLogProgress, \
                                                  args=(fileSorterInstance,))
    displayCliProgressBarThread = threading.Thread(target=displayCliProgressBar,\
                                                   args=(fileSorterInstance, fileSorterThread, log))
    
    # Launch threads
    fileSorterThread.start()
    updateAndLogProgressThread.start()
    displayCliProgressBarThread.start()

    # Waiting for threads to join.
    updateAndLogProgressThread.join()
    fileSorterThread.join()
    displayCliProgressBarThread.join()

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
    # Some of the print statements cannot be replaced with the logging class
    # due to tab characters that would not make sense to have in the log file,
    # thus, the log is going to be in displayMode.fileOnly mode and those print 
    # statements needed as a feedback for the user will remain in as print() function.
    if sys.platform.startswith('win'):
        appdata_path = os.environ['APPDATA'] + "\\FileSorter\\"
        log = jpLogger("FileSorter", appdata_path + "fileSorterCLI.log", logging.DEBUG, displayMode.fileAndConsole, 10, 50*1024*1024)
    else:
        log = jpLogger("FileSorter", "fileSorterCLI.log", logging.DEBUG, displayMode.fileAndConsole, 10, 50*1024*1024)
    log.info("Automatic Photo Sorter {0}".format(fileSorterVersion))
    print("Automatic Photo Sorter {0}".format(fileSorterVersion))
    parser = argparse.ArgumentParser(description = "Searches for files recursively in a directory, \
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
    parser.add_argument("-y","--yesToAll",
                        metavar="<yesToAll>",
                        type=str, # Based on argparse documentation bool type is not recommended since void str is false. 
                        help="By default this is set to False so the user will be prompted before starting the process.\
                            If you want to skip any user prompts, set this to True (adding -y is good enough).",
                        default="False", # Default value for when no using this parameter.
                        nargs='?',
                        const="True")  # Default value for when using this parameter with no explicit value typed.
    
    # Arguments length validation
    args=parser.parse_args()
    if len(argv) == 0:
        parser.print_help()
        log.info("No arguments detected. Will use default values.")
        print("No arguments detected. Will use default values.")

    # Ask user for confirmation before continuing (whenever yesToAll is "False")
    displayArgValues(args, log)
    confirmation = "y" if ("True" == args.yesToAll) else input("\n\tContinue? Y/n: ")
    if (confirmation.lower().split(" ")[0] not in ("y", "yes")):
        log.info("Action cancelled, exiting now...")
        print("Action cancelled, exiting now...")
        sys.exit(0)
    
    # Arguments validation (directory path and numberOfFiles to be processed)    
    if argsAreValid(args.sourcePath, args.numberOfFiles, log):
        doTheJob(log, args)
        sys.exit(0)
    else:
        log.error("Error due to invalid arguments.")
        print("Error due to invalid arguments.")
        sys.exit(1)

if __name__== "__main__":
    main(sys.argv[1:])  # Ignoring sys.argv[0] since it is the python name file
                        # e.g. python.exe fileSorterCLI.py