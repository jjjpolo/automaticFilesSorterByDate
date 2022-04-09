# Automatic Files Sorter By Date
It is a personal little project to help me sorting my thousands of photos and videos taken by myself.
Sorts the files inside a folder by date and moves them into new folders with the date as the name's folder. (Group by date).
It's useful helping you sorting photos and videos since it grupos them by last date modification, then you only need to rename each folder.
Ok, you still have left work to do,  but it is better renaming 25 folders than classifying 2000 files, is not it?

## Release notes

### Version 1.0.0
* There are two available modes: GUI and CLI
#### GUI mode:
* Lets you choose the source folder and the destiny folder
* Lets you specify the limit of files that you want for the current job.
* By changing the checkbox state, specify if you want to move or to copy the files
#### CLI mode:
* Works with the files in the same folder where the software is located
* It only asks you if you want to move or to copy the source files and the limit for the current job
* The result will appear in the same folder
* Hence, do not let you specify the source and destiny folder
* Pretends to be a quick solution for quick jobs.

## Building exe/out files
1. Add the following path to your environment var path
    * C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python36-32\Scripts 
2. Run the buildExecutables.py
## Installation:
* Paste fileSorterGUI.exe in the folder of your preference
* If you want to do a quick job (see CLI release notes) paste fileSorterCLI.exe in the folder of interest.

## Development notes:
* While developing fileSorterGUI.py needs to import fileSorterCLI.py so you must have them in the same folder
* Of course, it is better starting by cloning this project.
### Making exe files:
* Use: auto-py-to-exe.exe

### Future possible features
* Add a log file to report each action.
* Add an asking method when detecting duplicated files. If there is a file with the same name in the destination ask if you want to replace or skip it item and what does the software should do with the next similar situations during the current job.

## Screenshots
### GUI Mode:
Files Before using the software:

![Before](images/gui-before.JPG)

The software working:

![During](images/gui-during.JPG)

The software when the job is done:

![Done](images/gui-done.JPG)

Files after using the software:

![After](images/gui-after.JPG)

### CLI Mode
Files Before using the software:

![Before](images/cli-before.JPG)

The software working:

![During & Done](images/cli-during.JPG)

Files after using the software:

![After](images/cli-after.JPG)