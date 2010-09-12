"""
origapy.py - Philippe Lagadec

A Python client for the pipe interface of the Origami pdfclean.rb script, in
order to clean PDF files by disabling all active content (javascript, launch,
embedded files, etc).

Usage: import origapy, create a PDF_Cleaner object, use its clean() method to
clean a PDF file (see end of script for an example).

Author: Philippe Lagadec (http://www.decalage.info)

License: GPL v3 (see COPYING.txt file)

Project website: http://www.decalage.info/python/origapy
"""
__version__ = '0.09'
__author__  = 'Philippe Lagadec'

#--- CHANGELOG ----------------------------------------------------------------
# 2009-07-12 v0.01 PL: - 1st version (simple loop)
# 2009-07-13 v0.02 PL: - PDF_Cleaner class
# 2009-08-06 v0.03 PL: - updated pipe interface
# 2009-08-07 v0.04 PL: - use proper logging instead of print
#                      - find ruby script in same directory by default
# 2009-08-09 v0.05 PL: - change working directory to launch Ruby script
# 2009-08-28 v0.06 PL: - added output file path
# 2009-09-30 v0.07 PL: - detect when file is clean or cleaned
#                      - raise an exception when an error occurs
# 2009-10-02 v0.08 PL: - updated origami to v1.0.0-beta1
# 2010-09-12 v0.09 PL: - updated origami to v1.0.0-beta3

#-------------------------------------------------------------------------------
#TODO:
# + handle [error] properly, and when slave quits during the loop
# + generic RubyPipe class?
# + use rython for full access to the Origami API
# + add timeout option to kill ruby process if it takes too long


#--- IMPORTS ------------------------------------------------------------------

import os, logging
from subprocess import Popen, PIPE, STDOUT


#--- CONSTANTS ----------------------------------------------------------------

# results after scanning and cleaning a file:
CLEAN   = 0
CLEANED = 1

# keywords to communicate with server:
PIPE_CMD_END = '<<end>>'
PIPE_EXIT    = '<<exit>>'
FLAG_ERROR   = '[error]'
FLAG_CLEANED = '[CLEANED]'

# absolute path of this module:
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# absolute path of the pdfclean_server.rb script (in origami/scripts/antivir):
PDFCLEAN_PATH   = os.path.join(MODULE_PATH, 'origami', 'scripts', 'antivir')
PDFCLEAN_SCRIPT = 'pdfclean_server.rb'

#=== CLASSES ==================================================================

class PDF_Cleaner (object):
    """
    cleaning engine for PDF files
    """

    def __init__(self,  pdfclean_path=PDFCLEAN_PATH, logger=logging):
        """
        PDF_Cleaner constructor.

        Optional parameters:
        - pdfclean_path: absolute path of Origami pdfclean_server.rb script
        - logger: module or object for logging (standard logging by default)
        """
        self.pdfclean_path = pdfclean_path
        self.pdfclean_script = os.path.join(pdfclean_path, PDFCLEAN_SCRIPT)
        self._launched = False
        self.log = logger
        self.launch()


    def launch(self):
        """
        Launch pdfclean_server.rb script using the Ruby interpreter, with popen().
        """
        self.log.debug('launching %s...' % self.pdfclean_script)
##        # save original dir:
##        original_dir = os.path.abspath(os.getcwdu())
##        # go to pdfclean dir:
##        os.chdir(MODULE_PATH)
        # launch Ruby script with popen:
        # (using the ruby script path as working directory)
        self.pdfclean = Popen(['ruby', self.pdfclean_script],
            stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=self.pdfclean_path)
##        # go back to original dir:
##        os.chdir(original_dir)
        # check if pdfclean is alive:
        if self.pdfclean.poll() is not None:
            self.log.debug('slave has terminated.')
            raise RuntimeError, 'Error while launching %s' % self.pdfclean_path
        self._launched = True


    def clean (self, input_file, output_file):
        """
        clean a PDF file into a new file.
        - input_file: str, absolute path of input PDF file.
        - output_file: str, absolute path of output PDF file.

        Return CLEAN if the input file does not contain active content, or
        CLEANED if some active content was found and disabled in output file.
        Raise an exception if any error occured while parsing or cleaning.
        """
        # make sure paths are absolute (they may be relative to the current
        # working dir):
        input_file = os.path.abspath(input_file)
        output_file = os.path.abspath(output_file)
        self.log.debug('input file : %s' % input_file)
        self.log.debug('output file: %s' % output_file)
        # check if pdfclean has terminated, if so relaunch it:
        if not self._launched or self.pdfclean.poll() is not None:
            self.launch()
        # write the input filename to pdfclean's stdin
        self.pdfclean.stdin.write(input_file + '\n')
        # write the output filename to pdfclean's stdin
        self.pdfclean.stdin.write(output_file + '\n')
        # no need to flush here, seems unbuffered?
        #self.pdfclean.stdin.flush()
        # result will be a list of lines:
        result = []
        # flag to detect errors
        error = False
        # read slave output line by line, until we reach "<<end>>"
        while True:
            # check if pdfclean has terminated, if so raise error:
            if self.pdfclean.poll() is not None:
                error = True
                break
                #raise RuntimeError, 'Unable to launch pdfclean engine'
                #TODO: or read all lines??
            # read one line, remove newline chars and trailing spaces:
            line = self.pdfclean.stdout.readline().rstrip()
            #print 'line:', line
            if line == PIPE_CMD_END:
                break
            # add line to result, ignoring empty lines:
            if line:
                result.append(line)
        self.log.debug('result:')
        result = '\n'.join(result)
        self.log.debug(result)
        # check if an error occured:
        if error or FLAG_ERROR in result:
            self.log.debug('*** ERROR ***')
            raise RuntimeError, 'Error while parsing PDF content'
        # check if active content was found and cleaned or not:
        if FLAG_CLEANED in result:
            self.log.debug('Active content was found and cleaned.')
            return CLEANED
        else:
            self.log.debug('File is clean, no active content was found.')
            return CLEAN


    def stop (self):
        """
        Stop server
        """
        if not self._launched:
            self.pdfclean.stdin.write(PIPE_EXIT+'\n')
        self._launched = False



#=== MAIN =====================================================================

if __name__ == '__main__':
    print __doc__
    print ''
    # console logger with debug level:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(message)s')

    # hack to change default encoding to Latin-1 instead of ASCII:
    import sys
    reload(sys)
    sys.setdefaultencoding( 'latin-1' )

    pdfcleaner = PDF_Cleaner()
    while True:
        # read user input, expression to be evaluated:
        infile = raw_input('Enter input PDF filename or exit:')
        if infile == 'exit':
            break
        outfile = raw_input('Enter output PDF filename or exit:')
        pdfcleaner.clean(infile, outfile)


# This module was coded while listening to Drop Nineteens "Delaware" :-)