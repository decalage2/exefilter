#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==============================================================================
"""
tempfilemgr

A Python module to easily create temporary files and directories, and to make
sure that all of them are deleted after use.

Main advantages (compared to the standard tempfile module):
- Files and directories are created using tempfile.mkstemp and mkdtemp (see
  Python help), which means they should only accessible to the user that
  created them.
- Temporary files can be closed and reopened.
- It is possible to access them using their filename, for example with external
  tools.
- unlike mkstemp, newTempFile returns a file object instead of an OS-level
  file handle.
- It is possible to delete them when needed, or to request deletion of all
  existing temporary files after processing, to avoid omissions. (for example
  when a fatal exception occurs)

Notes on usage:
- The atexit module can be used to clean all temporary files/dirs at the end of
  a script:

  import atexit, tempfilemgr
  atexit.register(tempfilemgr.deleteAllTempFiles)

License: CeCILL (open-source GPL compatible), see source code for details.
         http://www.cecill.info

Author: Philippe Lagadec

Project website: http://www.decalage.info/python/tempfilemgr
"""
#==============================================================================

#--- LICENSE ------------------------------------------------------------------

# Copyright 2007-2011 Philippe Lagadec
#
# This software is a computer program whose purpose is to improve temporary
# files management in Python programs.
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

# 2007-06-29 v0.01 PL: - 1st version
# 2007-08-31       PL: - added license
# 2011-02-08 v0.02 PL: - added newTempDir

#--- TO DO --------------------------------------------------------------------

# + rename deleteAllTempFiles to delete_all_temp?
# - rename all functions using lowercase
# ? provide functions so that this module can replace tempfile without changing
#   old code ?
# - add option to overwrite files before deleting them (wipe)
# - keep track of file objects too, to close them if still open before deleting
# ? TempFileMgr class to manage/delete temp file for specific contexts, rather
#   than just one list (better for long time running apps with threads)
# - use optional logger object to log actions at debug level
# - portable spooled tempfile for python <2.6 (fallback to normal temp file)
# - separate functions to return only a name or only a handle?


#--- IMPORTS ------------------------------------------------------------------

import tempfile, os, os.path, sys

#--- GLOBAL VARIABLES ---------------------------------------------------------

# list of temporary files and dirs names
_tempfiles = []
_tempdirs  = []


#--- FUNCTIONS ----------------------------------------------------------------

def newTempFile (suffix="", prefix=tempfile.template, dir=None, text=False):
    """
    creates a new temporary file using tempfile.mkstemp (see Python help):
    Creates a temporary file in the most secure manner possible. There are no
    race conditions in the file’s creation, assuming that the platform properly
    implements the os.O_EXCL flag for os.open(). The file is readable and
    writable only by the creating user ID. If the platform uses permission bits
    to indicate whether a file is executable, the file is executable by no one.
    The file descriptor is not inherited by child processes.

    The user of mkstemp() is responsible for deleting the temporary file when
    done with it.
    This can be done using deleteAllTempFiles when the application terminates.

    If suffix is specified, the file name will end with that suffix, otherwise
    there will be no suffix. mkstemp() does not put a dot between the file name
    and the suffix; if you need one, put it at the beginning of suffix.

    If prefix is specified, the file name will begin with that prefix;
    otherwise, a default prefix is used.

    If dir is specified, the file will be created in that directory;
    otherwise, a default directory is used. The default directory is chosen
    from a platform-dependent list, but the user of the application can control
    the directory location by setting the TMPDIR, TEMP or TMP environment
    variables. There is thus no guarantee that the generated filename will have
    any nice properties, such as not requiring quoting when passed to external
    commands via os.popen().

    If text is specified, it indicates whether to open the file in binary mode
    (the default) or text mode. On some platforms, this makes no difference.

    returns a tuple: (file object, file name)

    NOTE: unlike tempfile.mkstemp, a file object is returned instead of an
    inconvenient OS-level file handle.
    """
    handle, filename = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
    _tempfiles.append(filename)
    # the OS-level file handle returned by mkstemp is converted to a file object
    f = os.fdopen(handle, 'w')
    return f, filename


def newTempDir (suffix="", prefix=tempfile.template, dir=None):
    """
    creates a new temporary directory using tempfile.mkdtemp (see Python help):
    Creates a temporary directory in the most secure manner possible.
    There are no race conditions in the directory’s creation. The directory is
    readable, writable, and searchable only by the creating user ID.

    The user of mkdtemp() is responsible for deleting the temporary directory
    and its contents when done with it.
    This can be done using deleteAllTempFiles when the application terminates.

    returns a str: absolute pathname of the new directory
    """
    newdir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    _tempdirs.append(newdir)
    return newdir


def deleteAllTempFiles(stop_on_exception=False):
    """
    deletes all remaining temporary files and directories that were created by
    this module.
    returns: a list of exceptions, if any. (tuples returned by sys.exc_info())
    Note:
    - directory deletion uses rmtree to remove all files and subdirectories
      recusrively.
    - files and dirs that no longer exist are simply ignored.
    - exceptions raised during deletion are added to a list which is returned
      at the end of processing, except if stop_on_exception is set to True.
    """
    import shutil
    exceptions = []
    for f in _tempfiles:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            exceptions.append(sys.exc_info())
            if stop_on_exception:
                #return exceptions
                raise
    for d in _tempdirs:
        try:
            if os.path.exists(d):
                shutil.rmtree(d)
        except:
            exceptions.append(sys.exc_info())
            if stop_on_exception:
                #return exceptions
                raise
    return exceptions


def set_atexit_deleteall ():
    import atexit
    atexit.register(deleteAllTempFiles)


#=== MAIN (tests) =============================================================

if __name__ == '__main__':
    f, n = newTempFile()
    f.write('test')

