import os    
import sys                   
from datetime import datetime   # To handle datetime 
import platform                 # To identify the operative system used
import shutil                   # To copy, move, and rename files
import argparse                 # to handle arguments from the command line.

version = "v1.1.0"

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
    formated_date = d.strftime('%Y-%m-%d')
    return formated_date

def createFolder(onWorkPath):
    if(False == os.path.exists(onWorkPath)):
        os.umask(0)
        os.makedirs(onWorkPath, 7777)

def sortFile(sourcePath, file, destinyPath, keepOriginalFile = True):
    sourceFilePath = os.path.join(sourcePath, file.name)
    if os.path.isdir(sourceFilePath): #if the current analyzed file is a directory skips it because we are only looking for files || FYI shutil copy can not copy folders, instead use copytree
        print("\n" +  str(file.name) + " is a folder, the software will skip it.")
    elif ("fileSorter" in file.name):
        print("\n " + str(file.name) + " seems to be part of fileSorter software, the software will skip it.")
    else:
        fileProperties = file.stat()#get the properties file
        lastModificationDate = convert_date(fileProperties.st_mtime) #get Last Modification date and convert it from epoch to human format
        destinyFileFolderPath = os.path.join(destinyPath, lastModificationDate)
        
        print("\n" + sourceFilePath + " || " + lastModificationDate  + "  -->  " + destinyFileFolderPath)
        
        createFolder(destinyFileFolderPath)
        if(False == os.path.exists(destinyFileFolderPath + "\\" +file.name)):
            if(keepOriginalFile):
                shutil.copy2(sourceFilePath, destinyFileFolderPath) # FYI shutil copy can not copy folders, instead use copytree
            else:
                shutil.move(sourceFilePath, destinyFileFolderPath)

        else:
            print("There is a file with the same name on the destiny folder")

def doTheJob(sourcePath, destinationPath, numberOfFiles = -1, keepOriginalFile = True):
    """Scans all the files in the source directory and passes them as a parameter to the 
    sortFile function to be sorted based on its last modification property.

    Parameters
    ----------
    sourcePath : str
        Dir path from where the files will be taken.
    destinationPath : str
        Dir path where the sorted files will be located.
    numberOfFiles : int
        Limit of files to be processed. If it was set to -1 there will be no limit.
    keepOriginalFile : bool
        Boolean flag indicating if the file should be copied or moved when sorting it.   
    """
    with os.scandir(sourcePath) as currentDirectory:
        count = 0
        for path in currentDirectory:
            if(os.path.isfile(path)):
                sortFile(sourcePath, path, destinationPath, keepOriginalFile)   

            count = count + 1

            if numberOfFiles is not -1: # This means that there is no limit on the number of files to be processed.
                if count >= numberOfFiles:
                    break;

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
            print ("{0} is not a valid sourcePath.".format(sourcePath))
    else:
        print ("{0} is not a valid value for numberOfFiles".format(numberOfFiles))
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
                        help="Number of files to processed. Skip this for no limit.",
                        default=-1,
                        nargs='?',
                        const=-1)
    parser.add_argument("-k","--keepOriginalFiles",
                        metavar="<keepOriginalFiles>",
                        type=str, # Based on argparse documentation bool type is not recommended since void str is false. 
                        help="By default this is set to True so files will be sorted as a copy of the originals. \
                            If you want to move files instead of copying them, set this explicitly to False.",
                        default="True", # Value for when no using this parameter.
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
        sys.exit()
    
    # Arguments validation (directory path and numberOfFiles to be processed)    
    if argsAreValid(args.sourcePath, args.numberOfFiles):
        doTheJob(args.sourcePath, args.destinationPath, args.numberOfFiles, False if (args.keepOriginalFiles.lower() == "false") else True) # moveFiles is passed to keepOriginal so they are opposite values.
        pause = input("\nDONE! \nYou can close this shell now...")
    else:
        print("Error due to invalid arguments.")
        sys.exit(1)

if __name__== "__main__":
    main(sys.argv[1:])  # Ignoring sys.argv[0] since it is the python name file
                        # e.g. python.exe fileSorterCLI.py