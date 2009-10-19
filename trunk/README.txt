ExeFilter

ExeFilter is an open-source tool and framework to filter file formats in 
e-mails, web pages or files. It detects many common file formats and can remove 
active content (scripts, macros, etc) according to a configurable policy.

Authors: Philippe Lagadec, Arnaud Kerreneur, Tanguy Vinceleux

Copyright DGA/CELAR 2004-2008, NC3A 2008-2009

Homepage: http://www.decalage.info/exefilter

Project website: http://adullact.net/projects/exefilter

License: CeCILL (open-source GPL compatible), see source code for details.
         http://www.cecill.info


For more information, see ExeFilter_documentation_EN.pdf.

-------------------------------------------------------------------------------
SAMPLE USAGE:

On Windows:
ExeFilter.py <source file or dir> -d <destination dir>


On Unix/Linux/MacOSX:
python ExeFilter.py <source file or dir> -d <destination dir>

-------------------------------------------------------------------------------
QUICK DEMO:

1) open each file in the demo_files folder, to look at active content.

2) On Windows: simply run DEMO.bat, or type:
ExeFilter.py demo_files -d demo_output

On Unix/Linux/MacOSX:
python ExeFilter.py demo_files -d demo_output

3) Then open each file in demo_output, and compare results.