"""
Simple web proxy with ExeFilter and CherryProxy (for testing purposes only)


License: see ExeFilter

Usage: xfweb.py [options]

Options:
  -h, --help            show this help message and exit
  -p PORT, --port=PORT  port for HTTP proxy, 8070 by default
  -a ADDRESS, --address=ADDRESS
                        IP address of interface for HTTP proxy (0.0.0.0 for
                        all, default=localhost)
  -f PROXY, --forward=PROXY
                        Forward requests to parent proxy, specified as
                        hostname[:port] or IP address[:port]
  -v, --verbose         Verbose mode, display debugging messages
  -l, --log             Log each request to a separate file (use with -v)
"""

# CHANGELOG:
# 2011-08-25 v0.01 PL: - initial version
# 2011-10-05 v0.02 PL: - rewritten according to new CherryProxy API

# TODO:
# + fix content-disposition parsing
# + fix content-type algorithm
# + check bug when html content is empty
# + option to load policy from file
# + one policy for requests, one for responses?
# + parse content-type with charset (ex: google.com)
# + move some generic code to CherryProxy

# import the necessary modules:
from thirdparty import cherryproxy
import sys

import ExeFilter as xf
import Journal, Politique
import traceback
import re

# regex to extract the filename from a content-disposition header:
re_content_disposition = re.compile(r'(?i)filename\s*=\s*"([^"]*)"')

# debug mode
xf.mode_debug(True)

# force logfile option
p = Politique.Politique()
p.parametres['journal_securite'].set(True)

# init console logging
Journal.init_console_logging()

class CherryProxy_xf(cherryproxy.CherryProxy):
    """
    Simple web proxy with ExeFilter
    """

##    def filter_request_headers(self):
##        # extract filename extension from URL:
##        ext = os.path.splitext(self.req.path)[1]
##        self.log.debug('extension: %s' % ext)
##        if str(ext).lower() == '.exe':
##            msg = 'Request blocked due to filename with executable extension in URL'
##            self.log.warning(msg)
##            self.set_response_forbidden(reason=msg)

    def filter_response_headers(self):
        # check if content-type is in the list of allowed values
        if self.resp.content_type not in xf.CT_to_ext\
        and self.resp.content_type != 'application/x-download':
            msg = 'Response blocked, content-type "%s" not allowed by policy' % self.resp.content_type
            self.log.warning(msg)
            self.set_response_forbidden(reason=msg)


    def filter_response(self):
        global p
        filename=None
        # need to handle the specific case of application/x-download:
        if self.resp.content_type == 'application/x-download':
            self.debug('Content-Type header is "application/x-download"')
            #TODO: maybe check this whatever the content-type is?
            # TO BE REWRITTEN USING NEW API
##            cd = self.resp.headers.get('content-disposition', '')
##            self.debug('Content-Disposition: %s' % cd)
##            if 'filename' in cd.lower():
##                m = re_content_disposition.search(cd)
##                if m is not None:
##                    filename = m.group(1)
##                    self.debug('Content-Disposition filename: "%s"' % filename)
##                else:
##                    self.debug('Content-Disposition filename not found')
        #TODO: else split the URL to find if there is a filename
        exitcode, cleaned_data = xf.clean_string(self.resp.data, filename=filename,
            content_type=self.resp.content_type,
            policy=p, logfile='xfweb.log')
        if exitcode == xf.EXITCODE_CLEAN:
            # data is clean, nothing to change
            pass
        elif exitcode == xf.EXITCODE_CLEANED:
            # data was cleaned
            self.data = cleaned_data
        elif exitcode == xf.EXITCODE_BLOCKED:
            # data should be blocked, return a 403 Forbidden response:
            self.set_response_forbidden(reason='Forbidden by policy')
            print 'DATA:'
            print self.resp.data
        elif exitcode == xf.EXITCODE_ERROR:
            # error during analysis, return a 403 Forbidden response:
            self.set_response(500, reason='Error during analysis')
            print 'DATA:'
            print self.resp.data


cherryproxy.main(CherryProxy_xf)
