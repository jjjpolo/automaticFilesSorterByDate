# =============================================================================
# File Name: fileSorter.py
# =============================================================================
# Purpose:  This is the base Class that does the main job which is reading the
#           the metadata of the file and move it to a folder named based on the
#           creation date of the file.
#           This class needs to be instantiated as an object to that we can
#           make us of it either as a CLI or as a GUI tool. 
#
# Author:   Jose Juan Jaramillo Polo
# License:  GPLv3
# Notes:    
# =============================================================================

from datetime import datetime   # To handle datetime 
import os
import threading
import time
import shutil                   # To copy, move, and rename files

#Global version variable to be reachable from anywhere.
__version__ = "v1.1.0"

class FileSorter():
    def __init__(self, log, sourcePath, destinationPath, numberOfFiles = -1, keepOriginalFile = True, mutex = None) -> None:
        log.info("FileSorter constructor has been called")
        self.log = log
        self.sourcePath = sourcePath
        self.destinationPath = destinationPath
        self.numberOfFiles = numberOfFiles
        self.keepOriginalFile = keepOriginalFile
        if mutex is None:
            self.mutex = threading.Lock()
            log.warning("No mutex object was passed. Creating a new mutex")
        else:
            self.mutex = mutex
        self.numberOfFilesToProcess = self.numberOfFilesInFolder(self.sourcePath) if self.numberOfFiles == -1 else self.numberOfFiles
        self.numberOfFilesProcessed = 0
        self.progress = 0 
        
    @staticmethod
    def numberOfFilesInFolder(dirPath) -> int:
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

    def doTheJob(self, sourcePath, destinationPath, keepOriginalFile = True):
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
        self.log.info("About to do the job on: " + sourcePath)
        self.log.info("Destination path: " + destinationPath)
        self.log.info("Is it keeping the original files?: " + str(keepOriginalFile))
        if self.numberOfFilesProcessed >= self.numberOfFilesToProcess:
            self.log.info("Base case has been reached, returning...")
            return
        currentDirectory = os.scandir(sourcePath)
        for path in currentDirectory:
            self.acquireMutex("doTheJob")
            if(os.path.isfile(path)):
                if self.numberOfFilesProcessed >= self.numberOfFilesToProcess:
                    self.releaseMutex("doTheJob") #Releasing mutex due to end condition. 
                    self.log.info("First base case has been reached, returning...")
                    return
                if self.sortFile(sourcePath, path, destinationPath, keepOriginalFile):
                    self.numberOfFilesProcessed = self.numberOfFilesProcessed + 1
                self.releaseMutex("doTheJob") #Releasing mutex before next for iteration.
            else:
                self.releaseMutex("doTheJob") #Releasing mutex before recursive iteration.
                self.doTheJob(os.path.join(sourcePath, path.name),destinationPath, keepOriginalFile)

    def run(self):
        self.doTheJob(self.sourcePath, self.destinationPath, self.keepOriginalFile)
        self.log.info("FileSorter job is done.")

    @staticmethod
    def updateAndLogProgress(processReference):
        """Needs to be run as a thread, this function do the maths to calc the
        progress of the process and logs it in the log file. 

        Parameters
        ----------
        processReference : obj
            An object reference to take the progress information from.
            It also includes a log object and a mutex.
    
        """
        safeCopyOfProgress = 0
        while safeCopyOfProgress < 100: 
            with processReference.mutex:
                processReference.progress = (processReference.numberOfFilesProcessed * 100) / processReference.numberOfFilesToProcess
                processReference.log.info("Progress: {0}% numberOfFilesProcessed: {1} numberOfFilesToProcess: {2} ".format(processReference.progress, processReference.numberOfFilesProcessed, processReference.numberOfFilesToProcess))
                safeCopyOfProgress = processReference.progress
            time.sleep(0.1)
        processReference.log.info("Progress: 100%, job is done.")

    def acquireMutex(self, functionName = "Undefined", logging = False): 
        """Tries to acquire the global mutex to protect shared variables among
        mainProcess and updateAndLogProgress.
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
        if(logging):
            try:
                self.log.debug("[{0}] About to acquire mutex.".format(functionName))
                self.mutex.acquire()
            except:
                self.log.debug("[{0}] Unable to acquire mutex".format(functionName))
                return False
            self.log.debug("[{0}] Mutex acquired successfully.".format(functionName))
        else:
            try:
                self.mutex.acquire()
            except:
                return False
        return True

    def releaseMutex(self, functionName = "Undefined", logging = False): 
        """Tries to release the global mutex to protect shared variables among
        mainProcess and updateAndLogProgress.
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
        if(logging):
            try:
                self.log.debug("[{0}] About to release mutex.".format(functionName))
                self.mutex.release()
            except:
                self.log.debug("[{0}] Unable to release mutex".format(functionName))
                return False
            self.log.debug("[{0}] Mutex released successfully.".format(functionName))
        else:
            try:
                self.mutex.release()
            except:
                return False
        return True

    def sortFile(self, sourcePath, file, destinyPath, keepOriginalFile = True):
        """Sorts a file based on its last modification date properties.
        If keepOriginalFile is True, the file will be copied to the, if keepOriginalFile
        is False, the file will moved to the destination directory.

        *Note: Some of the logs are being encoded to "utf-8" since some of the filenames
        could make the logger throw an exception by not being able to handle special characters
        such as "\u0301"

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
        try:
            sourceFilePath = os.path.join(sourcePath, file.name)
            self.log.info(("About to sort file: " + str(sourceFilePath)).encode("utf-8"))
            if os.path.isdir(sourceFilePath): 
                self.log.info((str(file.name) + " is a folder, skipping it.").encode("utf-8"))
                return False
            elif ("fileSorter" in file.name):
                self.log.info((str(file.name) + " seems to be part of fileSorter software, the software will skip it.").encode("utf-8"))
                return False
            else:
                fileProperties = file.stat() # Getting file's properties. 
                lastModificationDate = self.convert_date(fileProperties.st_mtime) # Getting Last Modification date and convert it from epoch to human format.
                destinyFileFolderPath = os.path.join(destinyPath, lastModificationDate) # Creating destiny folder path based on last modification date. 
                self.createFolder(destinyFileFolderPath)
                self.log.info(("Processing: " +  sourceFilePath + " || " + lastModificationDate  + " --> " + destinyFileFolderPath).encode("utf-8"))
            
                if(False == os.path.exists(destinyFileFolderPath + "\\" +file.name)):
                    if(keepOriginalFile):
                        shutil.copy2(sourceFilePath, destinyFileFolderPath) # FYI shutil copy can't copy folders, instead use copytree
                        self.log.info(("File has been copied from " + sourceFilePath + " to " + destinyFileFolderPath).encode("utf-8"))
                    else:
                        shutil.move(sourceFilePath, destinyFileFolderPath)
                        self.log.info(("File has been moved from " + sourceFilePath + " to " + destinyFileFolderPath).encode("utf-8"))
                    return True
                else:
                    self.log.info("There is a file with the same name on the destiny folder, skipping it.")
                    return True # True response needed to do the calc of progress properly.
        except Exception:
            self.log.error(("Something went wrong while sorting file {0}", sourcePath).encode("utf-8"))
            self.log.error("Exception error was: {0}", str(Exception))
            return True # TODO: Return false and look for a better way to keepOriginalFile
                        # updating the progress taking in account this failure.


    def createFolder(self, newDirPath):
        """Creates a new folder in the path specified

        Parameters
        ----------
        newDirPath : str
            Full directory path to be created.
        """
        if(False == os.path.exists(newDirPath)):
            self.log.info("Creating dir {0}".format(newDirPath))
            os.umask(0)
            os.makedirs(newDirPath, 7777)
        else:
            self.log.info("Dir: " + newDirPath + " already exists")


    def convert_date(self, timestamp):
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
        formatted_date = d.strftime('%Y-%m-%d') #YYYY-MM-DD
        self.log.info("Formatting date from: " + str(timestamp) + " to " + str(formatted_date))
        return formatted_date