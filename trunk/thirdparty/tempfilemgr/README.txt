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
