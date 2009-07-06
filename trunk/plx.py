#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
plx - Python portability layer extensions

v0.14 2008-01-24 Philippe Lagadec

This module contains several small useful functions to extend Python features,
especially to improve portability on Windows and Unix.

Project website: http://www.decalage.info/python/plx

License: CeCILL (open-source GPL compatible), see source code for details.
         http://www.cecill.info
"""

__version__ = '0.14'
__date__    = '2008-01-24'
__author__  = 'Philippe Lagadec'

#--- LICENSE ------------------------------------------------------------------

# Copyright Philippe Lagadec - see http://www.decalage.info/contact for contact info
#
# This software is a Python module/package which contains several small useful
# functions to extend Python features, especially to improve portability on
# Windows and Unix.
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# A copy of the CeCILL license is also provided in these attached files:
# Licence_CeCILL_V2-en.html and Licence_CeCILL_V2-fr.html
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


#--- CHANGES ------------------------------------------------------------------

# 2005-04-08 v0.01 PL: - first version: srt_lat1(), str_oem(), print_oem()
# 2005-07-25 v0.02 PL: - added Popen_timer and stop_pid
#                      - auto-tests if module launched directly
# 2005-07-28 v0.03 PL: - improved print_oem to avoid exceptions
# 2005-10-21 v0.04 PL: - improved str_lat1() and str_oem() to convert unicode
#                        or str
#                      - renamed str_oem and print_oem to str_console and
#                        print_console (OEM comes from MS-DOS and Windows)
#                      - codec for str_console is now configured at
#                        module import, not at each call
#                      - added unistr() to convert any string to unicode
# 2005-10-23 v0.05 PL: - improved stop_pid() to log errors
# 2006-01-16 v0.06 PL: - added main_is_frozen() and get_main_dir() for py2exe
# 2007-07-24 v0.07 PL: - added get_username to improve portability
# 2007-09-10 v0.08 PL: - fixed OpenProcess args in stop_pid()
#                      - fixed creationflags portability for Popen_Timer
# 2007-09-18 v0.09 PL: - improved portability for stop_pid
# 2007-10-22 v0.10 PL: - fixed EXIT_KILL_PTIMER to use with F-Prot 6
#                      - added display_html_file
# 2007-12-06 v0.11 PL: - added filename check in display_html_file
# 2007-12-16 v0.12 PL: - added main with a few tests
#                      - fixed a bug in display_html_file on Linux
#                      - added os.path.abspath in get_main_dir
# 2007-12-17 v0.13 PL: - bugfixes in Popen_timer/stop_pid for Unix
# 2008-01-24 v0.14 PL: - renamed stop_pid to kill_process
#                      - Popen_timer is now thread-safe (no global var)

#--- TO DO --------------------------------------------------------------------

# + Find a reliable way to set CODEC_CONSOLE according to system settings on
#   Windows and Unix ?
# - move tests to a separate script, use unittest
# - test Popen_timer with several threads
# - convert module to package with submodules (e.g. plx.subprocess, plx.test, etc)

#--- IMPORTS ------------------------------------------------------------------

import os, os.path, sys, urllib, imp, webbrowser, threading, signal
from subprocess import *

# specific modules for Windows:
if sys.platform == 'win32':
    try:
        import win32api, win32process, win32con
    except:
        raise ImportError, "the pywin32 module is not installed: "\
                           +"see http://sourceforge.net/projects/pywin32"

# specific modules for Unix:
try:
    import pwd
except:
    pass

#--- CONSTANTS ----------------------------------------------------------------

# CONSOLE:
# codec used for console display, which depends on OS and on country:
if sys.platform == 'win32':
    # on Windows in Western Europe the CMD.exe console uses MS-DOS CP850 encoding:
    CODEC_CONSOLE = 'cp850'
elif sys.platform in ('linux2', 'darwin'):
    # on Linux and MacOSX it's UTF-8:
    CODEC_CONSOLE = 'utf-8'
else:
    raise NotImplementedError, \
    "The console display is not configured for this platform (%s)" % sys.platform

# FOR POPEN_TIMER:
# Default timeout for a process launched Popen_timer (seconds)
POPEN_TIMEOUT = 60
# Exit code for a process killed by Popen_timer if it reaches the timeout:
if sys.platform == 'win32':
    # On Windows this has to be a positive value <255 which is not used by
    # used tools. Here we choose a value which is unused by F-Prot 6.
    EXIT_KILL_PTIMER = 128+64+32+16+8+4 # old value: 200
else:
    # On Unix this is the value of the SIGKILL signal (-9) used to kill the
    # process (negative value):
    EXIT_KILL_PTIMER = -signal.SIGKILL
# Default parameter for Popen_Timer:
if sys.platform == 'win32':
    # On Windows to launch a process without opening a new window:
    CF_CREATE_NO_WINDOW = win32process.CREATE_NO_WINDOW
else:
    # On Unix this parameter is not used:
    CF_CREATE_NO_WINDOW = 0


#--- GLOBAL VARIABLES ---------------------------------------------------------


#=== FUNCTIONS ================================================================

def unistr (string, errors='strict', default_codec='latin_1'):
    """
    To convert any string (unicode or 8-bit str) in a Unicode string.
    If string is str, it will be converted using the specified codec (Latin-1
    by default). A unicode string is returned unchanged.
    Any other object is converted using unicode(object).

    @param string: string or object to convert
    @type  string: str, unicode, or any object
    @param errors: see Python doc for unicode()
    @type  errors: str
    @return: converted string
    @rtype: unicode
    """
    if isinstance(string, unicode):
        return string
    else:
        return unicode(string, default_codec, errors)


def str_lat1 (string, errors='strict'):
    """
    To convert any string (unicode or 8-bit str) in a str "Latin-1" string.
    If string is str, it is returned unchanged.
    Any other object is converted using str(object).

    @param string: string or object to convert
    @type  string: str, unicode, or any object
    @param errors: see Python doc for unicode()
    @type  errors: str
    @return: converted string
    @rtype: str
    """
    if isinstance(string, unicode):
        return string.encode('latin_1', errors)
    elif isinstance(string, str):
        return string
    else:
        return str(string)


def str_console (string, errors='strict', initial_encoding='latin_1'):
    """
    To convert any string (unicode or 8-bit str) in a str string with a
    suitable encoding for console display ("CP850" on Windows, "UTF-8" on Linux
    or MacOSX, ...).
    If string is str, it is first decoded using initial_encoding ("Latin-1" by
    default). Any other object is converted using unicode(object) first.

    @param string: string or object to convert
    @type  string: str, unicode, or any object
    @param errors: see Python doc for unicode()
    @type  errors: str
    @return: converted string
    @rtype: str
    """
    ustring = unistr(string, errors, initial_encoding)
    return ustring.encode(CODEC_CONSOLE, errors)


def print_console (string, errors='strict', initial_encoding='latin_1'):
    """
    To print any string (unicode or 8-bit str) on console with a suitable 
    encoding ("CP850" on Windows, "UTF-8" on Linux or MacOSX, ...).
    If string is str, it is first decoded using initial_encoding ("Latin-1" by
    default). Any other object is converted using unicode(object) first.

    @param string: string or object to convert
    @type  string: str, unicode, or any object
    @param errors: see Python doc for unicode()
    @type  errors: str
    @return: converted string
    @rtype: str
    """
    print str_console(string, errors, initial_encoding)


def get_username(with_domain=False):
    """
    Returns the username of the current logged on user.
    Portable on Windows and Unix.
    If with_domain=True, on Windows the domain or machine name is added to the
    username as "\\domain\user" or "\\machine\user".
    """
    # TODO: why not return user@machine on Unix if with_domain=True ?
    if sys.platform == 'win32':
        # on Windows it is a Win32 call:
        if with_domain:
            # add domain name if requested:
            return '\\\\' + win32api.GetDomainName() + '\\' + win32api.GetUserName()
        else:
            # else only user name:
            return win32api.GetUserName()
    else:
        # on Unix the info is extracted from /etc/passwd:
        uid = os.getuid()
        return pwd.getpwuid(uid)[0]


def main_is_frozen():
    """
    To determine whether the script is launched from the interpreter or if it
    is an executable compiled with py2exe.
    See http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
    """
    return (hasattr(sys, "frozen") # new py2exe
        or hasattr(sys, "importers") # old py2exe
        or imp.is_frozen("__main__")) # tools/freeze


def get_main_dir():
    """
    To determine the directory where the main script is located.
    Works if it is launched from the interpreter or if it is an executable
    compiled with py2exe.
    See http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
    """
    if main_is_frozen():
        # script compiled with py2exe:
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # else the script is sys.argv[0]
        return os.path.dirname(os.path.abspath(sys.argv[0]))


def display_html_file (htmlfile_abspath):
    """
    Portable function to display a local HTML file in the default web browser.
    Uses os.startfile() on Windows, else webbrowser.open().
    (on Windows, webbrowser only works for http/ftp URLs, not file:///...)
    htmlfile_abspath should be an absolute path, at least on Unix.

    WARNING: on Windows, filename MUST have an HTML extension (.html, .htm,
    .xml), else the file will be opened in its default application instead of
    the web browser. A ValueError exception will be raised otherwise.
    """
    #TODO: add os.abspath ?
    if sys.platform == 'win32' :
        # check extension to avoid launching another application:
        if os.path.splitext(htmlfile_abspath.lower())[1] not in ('.html','.htm',
            '.xml'):
            raise ValueError, 'On Windows, filename extension must be .html,.htm or .xml'
        # on Windows, os.startfile is used:
        os.startfile(htmlfile_abspath)
    else:
        # on other OSes, webbrowser.open with a file URL:
        file_url = 'file://' + urllib.pathname2url(htmlfile_abspath)
        webbrowser.open(file_url)


#------------------------------------------------------------------------------
# KILL_PROCESS
#---------------------
def kill_process(process, log=None):
    """
    To kill a process launched by Popen_timer, if timeout is reached
    (POPEN_TIMEOUT). This function is called by a threading.Timer object.
    The process terminates and returns EXIT_KILL_PTIMER as errorlevel code.
    
    process: process object, as created by Popen.
    log: optional logging module to log eventual debug and error messages.
         (may be the standard logging module, or any compatible object with
         exception and debug methods)
    """
    # All the process output is logged at debug level, BUT only if stdout
    # and stderr were defined as "PIPE" when calling Popen_timer:
    if process.stdout and log:
        log.debug("Process display:")
        log.debug(process.stdout.read())
    if process.stderr and log:
        log.debug(process.stderr.read())
    try:
        if sys.platform == 'win32':
            reqdAccess = win32con.PROCESS_TERMINATE   # or PROCESS_ALL_ACCESS ?
            #TODO: see MSDN and win32con.py, change reqdAccess if error.
            handle = win32api.OpenProcess(reqdAccess, True, process.pid)
            win32api.TerminateProcess(handle, EXIT_KILL_PTIMER)
        else:
            #TODO: a tester pour les autres OS
            os.kill(processus.pid, signal.SIGKILL)
        if log:
            log.debug("Process PID=%d killed." % process.pid)
    except:
        if log:
            # log or display the whole exception:
            log.exception("Unable to kill process PID=%d." % process.pid)
        # raise exception
        raise


#------------------------------------------------------------------------------
# POPEN_TIMER
#---------------------
def Popen_timer (args, stdin=PIPE , stdout=PIPE, stderr=PIPE,
                      creationflags = CF_CREATE_NO_WINDOW,
                      timeout = POPEN_TIMEOUT, log=None):
    """
    To launch a process with Popen, with a timeout (see POPEN_TIMEOUT).
    If timeout is reached, the process is killed and returns EXIT_KILL_PTIMER.
    See subprocess module in standard Python library help for Popen options.

    @param args: process to launch and arguments (list or string)
    @param timeout: maximum execution time for process
    @param creationflags: parameters for CreateProcess on Windows
    @param log: optional logging module to log eventual debug and error messages.
         (may be the standard logging module, or any compatible object with
         exception and debug methods)
    """
    # process is launched with Popen to hide its display:
    process = Popen(args, stdin=stdin , stdout=stdout, stderr=stderr,
                      creationflags=creationflags)
    # TODO: handle OSError exception ?
    if log:
        log.debug("Process launched, PID = %d" % process.pid)
    # Timer to kill process if timeout reached:
    timer = threading.Timer(timeout, kill_process, args=[process, log])
    timer.start()
    if log:
        log.debug("Timer started: %d seconds..." % timeout)
    result_process = process.wait()
    # if process has finished before timeout, timer is cancelled:
    timer.cancel()
    if log:
        log.debug("Exit code returned by process: %d" % result_process)
    return result_process


def _test_Popen_timer ():
    """
    tests for Popen_timer
    """
    print 'Tests for Popen_timer:'
    print '1) a quick command which ends normally before timeout'
    if sys.platform == 'win32':
        # Windows
        cmd1 = ['cmd.exe', '/c', 'dir']
    else:
        # Unix
        cmd1 = ['/bin/sh', '-c', 'ls /etc']
    print 'cmd1 = ' + repr(cmd1)
    print 'Popen_timer (cmd1)...'
    res = Popen_timer (cmd1)
    if res == 0:
        print 'OK, exit code = 0'
    else:
        print 'NOK, exit code = %d instead of 0' % res
    print ''

    timeout = 3
    print '2) a long command which reaches timeout (%d s)' % timeout
    if sys.platform == 'win32':
        cmd2 = ['cmd.exe', '/c', 'pause']
    else:
        #cmd2 = ['/bin/sh', '-c', 'read -p waiting...']
        cmd2 = ['/bin/sh', '-c', 'read']
    print 'cmd2 = ' + repr(cmd2)
    print 'Popen_timer (cmd2, timeout=%d)...' % timeout
    res = Popen_timer (cmd2, stdin=None, stdout=None, stderr=None,
        timeout=timeout)
    if res == EXIT_KILL_PTIMER:
        print 'OK, exit code = EXIT_KILL_PTIMER (%d)' % res
    else:
        print 'NOK, exit code = %d instead of EXIT_KILL_PTIMER (%d)' % (res,
            EXIT_KILL_PTIMER)
    print ''

    # same tests with logging enabled:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print '3) a quick command which ends normally before timeout + LOG'
    print 'cmd1 = ' + repr(cmd1)
    print 'Popen_timer (cmd1)...'
    res = Popen_timer (cmd1, log=logging)
    if res == 0:
        print 'OK, exit code = 0'
    else:
        print 'NOK, exit code = %d instead of 0' % res
    print ''

    timeout = 3
    print '4) a long command which reaches timeout (%d s)' % timeout
    print 'cmd2 = ' + repr(cmd2)
    print 'Popen_timer (cmd2, timeout=%d)...' % timeout
    res = Popen_timer (cmd2, stdin=None, stdout=None, stderr=None,
        timeout=timeout, log=logging)
    if res == EXIT_KILL_PTIMER:
        print 'OK, exit code = EXIT_KILL_PTIMER (%d)' % res
    else:
        print 'NOK, exit code = %d instead of EXIT_KILL_PTIMER (%d)' % (res,
            EXIT_KILL_PTIMER)
    print ''


#=== MAIN =====================================================================

if __name__ == "__main__":
    print __doc__
    # A few tests:
    print '-'*79
    print 'Tests for module "%s" :' % __file__
    print '-'*79
    print ''
    
    print "get_username()                 =", get_username()
    print "get_username(with_domain=True) =", get_username(with_domain=True)
    print ''

    print "main_is_frozen() =", main_is_frozen()
    print "get_main_dir()   =", get_main_dir()
    print ''

    print 'Test str and console functions:'
    str_accents = 'éèêëçà'
    ustr_accents = u'éèêëçà'
    assert isinstance(unistr(str_accents), unicode)
    print_console(str_accents)
    print_console(ustr_accents)
    print_console(str_lat1(ustr_accents))
    print_console(unistr(str_accents))
    print_console(unistr(ustr_accents))
    print ''

    # Test Popen_timer:
    _test_Popen_timer()
    print ''

    print "Tests for display_html_file():"
    if sys.platform == 'win32' :
        # on Windows, check that extensions except html, htm, xml are not
        # allowed:
        try:
            display_html_file('c:\\boot.ini')
            print 'NOK: any file extension is allowed !'
        except ValueError:
            print 'OK: extensions are checked by display_html_file.'
    filename = 'test_plx.html'
    print "should now open %s in the default browser." % filename
    try:
        raw_input('Press enter to launch browser... (or Ctrl+C to stop)')
        f = open(filename, 'w')
        f.write('<html><body>Test plx.<b>display_html_file</b></body></html>')
        f.close()
        display_html_file(os.path.abspath(filename))
        os.remove(filename)
    except KeyboardInterrupt:
        print '\nstopped.'

    
# This module was coded while listening at Spoon "Ga ga ga ga ga" album. ;-)