import cx_Freeze
import sys
import os
import selenium


base = None

os.environ['TCL_LIBRARY'] = r'C:\Users\PB6\AppData\Local\Programs\Python\Python37\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\PB6\AppData\Local\Programs\Python\Python37\tcl\tk8.6'


syspath = r"C:\Users\PB6\AppData\Local\Programs\Python\Python37\DLLs"

includes      = []
include_files = [syspath + '/tcl86t.dll', syspath + '/tk86t.dll', 'Jnj48.ico', 'chromedriver.exe', 'phantomjs.exe']

'''
if sys.platform == 'win32':
    base = "Win32GUI"
'''

executables = [cx_Freeze.Executable("complaint handler.py", base=base, icon="Jnj48.ico")]

cx_Freeze.setup(
    name = "CatsWeb Complaint Handler",
    options = {"build_exe": {"includes": includes, "include_files": include_files,"packages":["tkinter","selenium"]}},
    version = "1.0.0",
    description = "CatsWeb complaint handler for Level 1 and Level 2 complaints",
    executables = executables
    )
