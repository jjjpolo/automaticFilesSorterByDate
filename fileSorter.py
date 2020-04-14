import os
from datetime import datetime
import platform #to dentify the oparative system used
import shutil #it lets copy move and rename files

def convert_date(timestamp):
    d = datetime.utcfromtimestamp(timestamp)
    formated_date = d.strftime('%d-%m-%Y')
    return formated_date

def createFolder(onWorkPath):
    if(False == os.path.exists(onWorkPath)):
        os.umask(0)
        os.makedirs(onWorkPath, 7777)

def main():
    inputPath = " "
    outputPath = " "
    pathFolder = ".\samplePictures"
    threshold = input("how many photos do you want to process? (Write 'all' to process the entry folder)")
    if threshold == "" or threshold == "all":
        threshold = len(os.listdir(pathFolder))
    else:
        if threshold.isnumeric():
            threshold = int(threshold)
        else:
            threshold = -1
            print("Wrong input")
    count = 0
    with os.scandir(pathFolder) as files:
        while count < threshold:
            for file in files:
                sourceFilePath = os.path.join(pathFolder, file.name)
                if os.path.isdir(sourceFilePath): #if the current analized file is a directory skips it because we are only looking for files || FYI shutil copy can not copy folders, instead use copytree
                    continue
                else:
                    fileProperties = file.stat()#get the properties file
                    lastModificationDate = convert_date(fileProperties.st_mtime) #get Last Modification date and convert it from epoch to human format
                    destinyFileFolderPath = os.path.join(pathFolder, lastModificationDate)
                    
                    print(sourceFilePath + " || " + lastModificationDate  + "  -->  " + destinyFileFolderPath)
                    
                    createFolder(destinyFileFolderPath)
                    if(False == os.path.exists(destinyFileFolderPath + "\\" +file.name)):
                        shutil.copy2(sourceFilePath, destinyFileFolderPath) # FYI shutil copy can not copy folders, instead use copytree
                    else:
                        print("There is a file with the same name on the destiny folder")
                    
                count += 1

def recivingParameters(sourcePath, destinyPath, threshold):
    print(os.listdir(sourcePath))
    print(os.listdir(sourcePath))
    print(threshold)


    print("DONE!")
if __name__== "__main__":
    #sourcePath = "./"
    #destinyPath = "./"
    #threshold = input ("Limit for this job (leave it blanks if you want to process al the files): ")
    #recivingParameters(sourcePath, destinyPath, threshold)
    main()