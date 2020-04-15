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

def main(sourcePath, destinyPath, threshold = -1):
    totalAmoutnFiles = len(os.listdir(sourcePath))
    if threshold == -1:
        threshold = totalAmoutnFiles
    count = 0
    #print(threshold)
    with os.scandir(sourcePath) as files:
        for file in files:
            sourceFilePath = os.path.join(sourcePath, file.name)
            if os.path.isdir(sourceFilePath): #if the current analized file is a directory skips it because we are only looking for files || FYI shutil copy can not copy folders, instead use copytree
                continue
            else:
                fileProperties = file.stat()#get the properties file
                lastModificationDate = convert_date(fileProperties.st_mtime) #get Last Modification date and convert it from epoch to human format
                destinyFileFolderPath = os.path.join(destinyPath, lastModificationDate)
                
                print(sourceFilePath + " || " + lastModificationDate  + "  -->  " + destinyFileFolderPath)
                
                createFolder(destinyFileFolderPath)
                if(False == os.path.exists(destinyFileFolderPath + "\\" +file.name)):
                    shutil.copy2(sourceFilePath, destinyFileFolderPath) # FYI shutil copy can not copy folders, instead use copytree
                else:
                    print("There is a file with the same name on the destiny folder")

            if __name__ != "__main__":
                percent = (count * 100) / totalAmoutnFiles                

            count = count + 1
            if count >= threshold:
                break;
    print("DONE!")


if __name__== "__main__":
    sourcePath = "./"
    destinyPath = "./"
    print ("There are: " + str(len(os.listdir(sourcePath))) + " files in the source folder.")
    threshold = input ("Limit for this job (leave it blanks if you want to process al the files): ")
    if (threshold is None or threshold == " " or 0 == len(threshold)):
        print("All the files will be processed...")
        main(sourcePath, destinyPath)
    else:
        if threshold.isnumeric():
            print("Only " + str(threshold) + " files")
            main(sourcePath, destinyPath, int(threshold))
        else:
            print("Wrong limit value entered")