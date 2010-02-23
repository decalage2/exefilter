plx is a module providing a few functions to improve Python portability on 
Windows and Unix.

Python is a very portable language, and it’s a pleasure to write one script 
and run it seemlessly on Windows, Linux and MacOSX. But many features in the 
standard library are not available on all platforms. I’m always frustrated 
when I come across "Avalability: UNIX" in the Python Library reference...

I’ve started to write a few helper functions for several projects in order to 
improve portability and to add some useful features. plx is simply a handy 
module to collect all these functions.

Features

    * get_username: to get the current logged in user
    * Popen_timer: to launch a process with a timeout
    * kill_process: to kill a process launched by Popen
    * display_html_file: to open a local HTML file in the default browser
    * get_main_dir: to determine the directory of the main script
    * unistr: to convert any string or object to Unicode
    * str_console: to convert any string or object using a suitable codec for console output
    * print_console: to print any string or object to the console using the suitable codec

License

CeCILL: open-source, GPL-compatible
see LICENCE.txt


Download

see http://www.decalage.info/en/python/plx

Requirements

    * A not-too-old Python interpreter
    * on Windows: the Python for Windows extensions

