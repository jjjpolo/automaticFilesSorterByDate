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

## Installation:
* Paste fileSorterGUI.exe in the folder of your preference
* If you want to do a quick job (see CLI release notes) paste fileSorterCLI.exe in the folder of interest.

## Development notes:
* While developing fileSorterGUI.py needs to import fileSorterCLI.py so you must have them in the same folder
* Of course, it is better starting by cloning this project.

## Screenshots
### GUI Mode:
![alt text](./gui-before.jpg)
![alt text](./gui-during.jpg)
![alt text](./gui-done.jpg)
![alt text](./gui-after.jpg)

### CLI Mode
![alt text](./cli-before.jpg)
![alt text](./cli-during.jpg)
![alt text](./cli-after.jpg)