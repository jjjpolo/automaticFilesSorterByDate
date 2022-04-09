""" ===Build Executables.===

This script makes use of the pyintaller tool to create the corresponding
exe/out binaries that can be run on either Windows, Linux or Unix systems.
If pyinstaller is not installed this script will do it for you. 

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = "José Juan Jaramillo Polo"
__contact__ = "josejuan.jaramillopolo@gmail.com"
__date__ = "2022/05/02"
__deprecated__ = False
__license__ = "GPLv3"

* HOW TO USE IT.
  * DO NOT run it with Visual Studio Debugger since the current dir (pwd) is the
    one for the main solution, thus the relative paths in this scripts would not be valid.
  * Option 1. Using the Windows File Explorer just double click on it. 
  * Option 2. Build the Wix Installer Project (FileSorterInstaller), it will call it
              as a Pre Build event.
  * Option 3. On Unix based systems just run it from its current location. 
"""

import subprocess
import sys
import os

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
    runCommand("pyinstaller --onefile --icon=../tools/ReleaseTools/icons/gui.ico --distpath=../../bin/dist --workpath=../../bin/build --specpath=../../bin --version-file=../tools/ReleaseTools/versionFile.txt ../../fileSorterGUI.py")