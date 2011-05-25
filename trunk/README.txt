ExeFilter

ExeFilter is an open-source tool and framework to filter file formats in 
e-mails, web pages or files. It detects many common file formats and can remove 
active content (scripts, macros, etc) according to a configurable policy.

Authors: Philippe Lagadec, Arnaud Kerreneur, Tanguy Vinceleux

Copyright DGA/CELAR 2004-2008, NC3A 2008-2010

Homepage: http://www.decalage.info/exefilter

Project website: http://adullact.net/projects/exefilter

License: CeCILL (open-source GPL compatible), see source code for details.
         http://www.cecill.info


For more information, see ExeFilter_documentation_EN.pdf.

-------------------------------------------------------------------------------
REQUIREMENTS:

- Python 2.5 or 2.6 (v3 is not supported yet)
- Pywin32 extensions on Windows
- wxPython for the GUI
- Ruby if you want to use the Origami engine for PDF analysis

(unless you use the Portable ExeFilter version: see README_portable.txt)

-------------------------------------------------------------------------------
SAMPLE GUI USAGE:

1) Open ExeFilter_GUI.py 
2) select source file or directory
3) click on the Scan button.
4) or select select destination file or directory, then click the Clean button.


-------------------------------------------------------------------------------
SAMPLE COMMAND-LINE USAGE:

1) How to SCAN a file or directory: 

On Windows:
ExeFilter.py <source file or dir>

On Unix/Linux/MacOSX:
python ExeFilter.py <source file or dir>


2) How to CLEAN a file or directory: 

On Windows:
ExeFilter.py <source file or dir> -d <destination dir>
or
ExeFilter.py <source file> -o <destination file>

On Unix/Linux/MacOSX:
python ExeFilter.py <source file or dir> -d <destination dir>
or
python ExeFilter.py <source file> -o <destination file>

-------------------------------------------------------------------------------
QUICK DEMO:

1) open each file in the demo_files folder, to look at active content.

2) On Windows: simply run DEMO.bat, or type:
ExeFilter.py demo_files -d demo_output

On Unix/Linux/MacOSX:
python ExeFilter.py demo_files -d demo_output

3) Then open each file in demo_output, and compare results.