"""
Simple CherryProxy demo

This demo simply blocks EXE files (application/octet-stream) and allows
everything else.

usage: cproxy_blockexe.py [-d]

-d: debug mode

Philippe Lagadec 2010-04-30
"""

# CHANGELOG:
# 2010-04-30 v0.01 PL: - first version
# 2011-10-04 v0.02 PL: - fixed using new CherryProxy API

# TODO:
# + check filename.ext in location header
# + check filename.ext in content-disposition header

import sys, os
sys.path.append('../..')
import cherryproxy

class CherryProxy_blockexe(cherryproxy.CherryProxy):
    """
    Sample CherryProxy class demonstrating how to adapt a response.
    This demo simply blocks EXE files and allows everything else.
    """

    def filter_request_headers(self):
        # extract filename extension from URL:
        ext = os.path.splitext(self.req.path)[1]
        self.log.debug('extension: %s' % ext)
        if str(ext).lower() == '.exe':
            msg = 'Request blocked due to filename with executable extension in URL'
            self.log.warning(msg)
            self.set_response_forbidden(reason=msg)

    def filter_response_headers(self):
        # check content-type
        if self.resp.content_type == 'application/octet-stream':
            # it's an exe file, return a 403 Forbidden response:
            msg = 'Response blocked due to executable content-type'
            self.log.warning(msg)
            self.set_response_forbidden(reason=msg)

    def filter_response(self):
        # check if data starts with "MZ":
        if isinstance(self.resp.data, str) and self.resp.data.startswith('MZ'):
            # it's an exe file, return a 403 Forbidden response:
            msg = 'Response blocked due to potentially executable content'
            self.log.warning(msg)
            self.set_response_forbidden(reason=msg)

cherryproxy.main(CherryProxy_blockexe)
