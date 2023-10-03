# =============================================================================
# File Name: builldExecutables.py
# =============================================================================
# Purpose:  This script makes use of the pyintaller tool to create the 
#           corresponding exe/out binaries that can be run on either Windows, 
#           Linux or Unix systems.
#           If pyinstaller is not installed this script will do it for you.
#
# Author:   Jose Juan Jaramillo Polo
# License:  GPLv3
# Notes:    HOW TO USE IT.
#           * DO NOT run it with Visual Studio Debugger since the current dir 
#             (pwd) is the one for the main solution, thus the relative paths 
#             in this scripts would not be valid.
#           * Option 1. Using the Windows File Explorer just double click on it. 
#           * Option 2. Build the Wix Installer Project (FileSorterInstaller), 
#                       it will call it as a Pre Build event.
#           * Option 3. On Unix based systems just run it from its current 
#                       location.  
# =============================================================================

import os
import subprocess
import sys

def runCommand(cmd):
    """Executes a command in a shell such as batch or bash. 

    Parameters
    ----------
    cmd : str
        The command to be executed. 
    """
    os.system(cmd)

def install(package):
    """Builds a command to install a python package using the pip manager.

    Parameters
    ----------
    package : str
        The name of the python package to be installed.
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    """ Builds the exe/out version of the two main python scripts (fileSorterCLI.py and fileSorterGUI.py).
    It works similar as if Visual Studio were building a Visual Studio Solution by placing the output in 
    the corresponding bin folder of this solution (../..bin).
    """

    install("pyinstaller")
    
    '''Notes
    * icons path ared based on where specpath puts spec files. Spec files are the main descriptor files.
    * version file path is based on where specpaht puts spec files. Spec files are the main descriptor files.
    '''
    runCommand("pyinstaller --onefile --icon=../tools/ReleaseTools/icons/cli.ico --distpath=../../bin/dist --workpath=../../bin/build --specpath=../../bin --version-file=../tools/ReleaseTools/versionFile.txt ../../fileSorterCLI.py")
    runCommand("pyinstaller --onefile --noconsole --icon=../tools/ReleaseTools/icons/gui.ico --distpath=../../bin/dist --workpath=../../bin/build --specpath=../../bin --version-file=../tools/ReleaseTools/versionFile.txt ../../fileSorterGUI.py")