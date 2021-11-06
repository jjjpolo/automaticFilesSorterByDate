import os
from datetime import datetime
import platform #to identify the operative system used
import shutil #it lets copy move and rename files


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

def mainProcess_climode(sourcePath, destinyPath, threshold = -1, keepOriginalFile = True):
    totalAmoutnFiles = len(os.listdir(sourcePath))
    if threshold == -1:
        threshold = totalAmoutnFiles
    count = 0
    #print(threshold)
    with os.scandir(sourcePath) as files:
        for file in files:
            sortFile(sourcePath, file, destinyPath, keepOriginalFile)   

            count = count + 1
            if count >= threshold:
                break;
    print("\n DONE!")
    pause = input("You can close this shell now...")


if __name__== "__main__":
    print("Automatic Photo Sorter v1.0.0")
    sourcePath = "./"
    destinyPath = "./"
    print ("There are: " + str(len(os.listdir(sourcePath))) + " files in the source folder.")
    threshold = input ("Limit for this job (leave it blanks if you want to process al the files): ")
    keepOriginalFile_input = input ("Do you want to keep the original files? s/n: ")
    if (keepOriginalFile_input == 's' or keepOriginalFile_input == 'S'):
        keepOriginalFile = True
    else:
        keepOriginalFile = False
    if (threshold is None or threshold == " " or 0 == len(threshold)):
        print("All the files will be processed...")
        mainProcess_climode(sourcePath, destinyPath, -1,  keepOriginalFile)
    else:
        if threshold.isnumeric():
            print("Only " + str(threshold) + " files")
            mainProcess_climode(sourcePath, destinyPath, int(threshold),keepOriginalFile)
        else:
            print("Wrong limit value entered")