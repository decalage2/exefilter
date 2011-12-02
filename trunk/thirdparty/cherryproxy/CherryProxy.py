"""
CherryProxy

a lightweight HTTP proxy based on the CherryPy WSGI server and httplib,
extensible for content analysis and filtering.

AUTHOR: Philippe Lagadec (decalage at laposte dot net)

PROJECT WEBSITE: http://www.decalage.info/python/cherryproxy

LICENSE:

Copyright (c) 2008-2011, Philippe Lagadec (decalage at laposte dot net)

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above copyright
notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

Usage:
- either run this script directly for a demo, and use localhost:8070 as proxy.
- or create a class inheriting from CherryProxy and implement the methods
  filter_request and filter_response as desired. See the example scripts for
  more information.

Usage as a script: CherryProxy.py [options]

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

#------------------------------------------------------------------------------
# CHANGELOG:
# 2008-11-01 v0.01 PL: - first version
# 2008-11-02 v0.02 PL: - extensible CherryProxy class instead of functions
# 2009-05-05 v0.03 PL: - added comments and license
#                      - option to set server name in constructor
# 2009-05-06 v0.04 PL: - forward request body to server
# 2010-04-25 v0.05 PL: - moved nozip demo to separate script
#                      - debug option to enable/disable debug output
# 2011-09-03 v0.06 PL: - replaced attributes by thread local variables to
#                        support multithreading
# 2011-09-07 v0.07 PL: - use logging instead of print for debugging
#                      - split proxy_app into several methods
#                      - close each http connection to server
# 2011-09-15 v0.08 PL: - command-line options
# 2011-09-21 v0.09 PL: - separate main function (to be used in examples)
# 2011-09-24 v0.10 PL: - renamed adapt to filter
#                      - added methods to send response without forwarding
#                        request to server
# 2011-09-30 v0.11 PL: - added methods to filter headers before reading body
# 2011-11-15 v0.12 PL: - moved and renamed private methods with an underscore
#                      - added option to use a parent proxy
# 2011-11-29 v0.13 PL: - new option (-l) to log each request to a file
#                      - black list to block unsupported HTTP methods and schemes

#------------------------------------------------------------------------------
# TODO:
# + log_file: fix debug level without -v, add formatter
# + CLI option to dump request and response data using repr()
# + disable debug options
# + fix examples, using CT+filename, blocking some requests
# + simple doc describing API
# + methods to parse useful headers: content-type, content-disposition, etc
#   http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.17
#   http://www.ietf.org/rfc/rfc2183.txt
# + method to disable logging (if log_level=None) and to add a dummy handler
# + init option to enable debug messages or not
# + force connection close and remove keep-alive on server side
# + close connection on server side when needed
# + _send_request: reconstruct URL from its elements (if they were changed)
# + _send_request: handle connection errors

# TODO LATER:
# - update CherryPy WSGI server to the latest version 3.2.2
# - option to save each request and response (before and after adaptation) to a file
# - later, reuse http connection when no connection close header or keep-alive
# - option to uncompress body when gzip/deflate/compress is used
# - support HTTPS
# ? config file to set options?
# ? use urllib2 instead of httplib?

#--- IMPORTS ------------------------------------------------------------------

from cherrypy import wsgiserver
import urlparse, urllib2, httplib, sys, threading, logging


#--- CONSTANTS ----------------------------------------------------------------

__version__ = '0.13'

SERVER_NAME = 'CherryProxy/%s' % __version__

# Not supported methods and schemes
BLACKLIST_METHODS = ['CONNECT']
BLACKLIST_SCHEMES = ['https']


#=== CLASSES ==================================================================

class CherryProxy (object):
    """
    CherryProxy: class implementing a filtering HTTP proxy

    To use it, create a class inheriting from CherryProxy and implement the
    methods filter_request and filter_response as desired.
    Then call the start method to start the proxy.
    Note: the logging module needs to be initialized before creating a
    CherryProxy object.
    See the example scripts for more information.
    """

    # class variables:
    # unique id for each request
    _reqid = 0
    _lock_reqid = threading.Lock()

    def __init__(self, address='localhost', port=8070, server_name=SERVER_NAME,
        debug=False, log_level=logging.INFO, options=None, parent_proxy=None,
        log_file=False):
        """
        CherryProxy constructor

        address: IP address of interface to listen to, or 0.0.0.0 for all
                 (localhost by default)
        port: TCP port for the proxy (8070 by default)
        server_name: server name used in HTTP responses
        debug: enable debugging messages if set to True
        log_level: logging level (use constants from logging module)
        options: None or optparse.OptionParser object to provide additional options
        parent_proxy: parent proxy, either IP address or hostname, with optional
            port (example: 'myproxy.local:8080')
        log_file: bool, if True a log file will be generated for each request
        """
        # create HTTP server
        self.address = address
        self.port = port
        self.server = wsgiserver.CherryPyWSGIServer((address, port),
            self._proxy_app, server_name=server_name)
        # thread local variables to store request/response data per thread:
        self.req = threading.local()
        self.resp = threading.local()
        if debug:
            self.debug = self._debug_enabled
            self.debug_mode = True
        else:
            self.debug = self._debug_disabled
            self.debug_mode = False
        self.options = options
        # initialize logging
        self.log_level = log_level
##        self.log = logging.getLogger('CProxy')
##        self.log.setLevel(log_level)
        # default logger
        self.req.log = logging.getLogger('CProxy')
        self.req.log.setLevel(log_level)
        self.log_file = log_file
        # parent proxy
        self.parent_proxy = parent_proxy
        if parent_proxy:
            self.debug('Using parent proxy: %s' % parent_proxy)


    def start(self):
        """
        start proxy server
        """
        self.req.log.info('CherryProxy listening on %s:%d (press Ctrl+C to stop)'
            % (self.address, self.port))
        self.server.start()


    def stop(self):
        """
        stop proxy server
        """
        self.server.stop()
        self.req.log.info('CherryProxy stopped.')


    def filter_request_headers(self):
        """
        Method to be overridden:
        Called to analyse/filter/modify the request received from the client,
        before reading the full request with its body if there is one,
        before it is sent to the server.

        This method may call set_response() if the request needs to be blocked
        before being sent to the server.

        The following attributes can be read and MODIFIED:
            self.req.headers: dictionary of HTTP headers, with lowercase names
            self.req.method: HTTP method, e.g. 'GET', 'POST', etc
            self.req.scheme: protocol from URL, e.g. 'http' or 'https'
            self.req.netloc: IP address or hostname of server, with optional
                             port, for example 'www.google.com' or '1.2.3.4:8000'
            self.req.path: path in URL, for example '/folder/index.html'
            self.req.query: query string, found after question mark in URL

        The following attributes can be READ only:
            self.req.environ: dictionary of request attributes following WSGI
                              format (PEP 333)
            self.req.url: partial URL containing 'path?query'
            self.req.full_url: full URL containing 'scheme:netloc/path?query'
            self.req.length: length of request data in bytes, 0 if none
            self.req.content_type: content-type, for example 'text/html'
            self.req.charset: charset, for example 'UTF-8'
            self.req.url_filename: filename extracted from URL path
        """
        pass


    def filter_request(self):
        """
        Method to be overridden:
        Called to analyse/filter/modify the request received from the client,
        after reading the full request with its body if there is one,
        before it is sent to the server.

        This method may call set_response() if the request needs to be blocked
        before being sent to the server.

        The following attributes can be read and MODIFIED:
            self.req.data: data sent with the request (POST or PUT)
            (and also all listed in filter_request_headers)
        """
        pass


    def filter_response_headers(self):
        """
        Method to be overridden:
        Called to analyse/filter/modify the response received from the server,
        before reading the full response with its body if there is one,
        before it is sent back to the client.

        This method may call set_response() if the response needs to be blocked
        (e.g. replaced by a simple response) before being sent to the client.

        The following attributes can be read and MODIFIED:
            self.resp.status: int, HTTP status of response, e.g. 200, 404, etc
            self.resp.reason: reason string, e.g. 'OK', 'Not Found', etc
            self.resp.headers: response headers, list of (header, value) tuples

        The following attributes can be READ only:
            self.resp.httpconn: httplib.HTTPConnection object
            self.resp.response: httplib.HTTPResponse object
            self.resp.content_type: content-type of response
            self.resp.charset: charset of response
            self.resp.content_disp_filename: filename extracted from
                                             content-disposition header
        """
        pass


    def filter_response(self):
        """
        Method to be overridden:
        Called to analyse/filter/modify the response received from the server,
        after reading the full response with its body if there is one,
        before it is sent back to the client.

        This method may call set_response() if the response needs to be blocked
        (e.g. replaced by a simple response) before being sent to the client.

        The following attributes can be read and MODIFIED:
            self.resp.data: data sent with the response
            (and also all listed in filter_response_headers)
        """
        pass


    def set_response(self, status, reason=None, data=None, content_type='text/plain'):
        """
        set a HTTP response to be sent to the client instead of the one from
        the server.

        - status: int, HTTP status code (see RFC 2616)
        - reason: str, optional text for the response line, standard text by default
        - data: str, optional body for the response, default="status reason"
        - content_type: str, content-type corresponding to data
        """
        self.resp.status = status
        if reason is None:
            # get standard text corresponding to status
            reason = httplib.responses[status]
        self.resp.reason = reason
        if data is None:
            data = "%d %s" % (status, reason)
        self.resp.data = data
        # reset all headers
        self.resp.headers = []
        self.resp.headers.append(('content-type', content_type))
        #self.resp.headers.append(('content-length', str(len(data)))) # not required


    def set_response_forbidden(self, status=403, reason='Forbidden',
        data=None, content_type='text/plain'):
        """
        set a HTTP 403 Forbidden response to be sent to the client instead of
        the one from the server.

        - status: int, HTTP status code (see RFC 2616)
        - reason: str, optional text for the response line, standard text by default
        - data: str, optional body for the response, default="status reason"
        - content_type: str, content-type corresponding to data
        """
        self.set_response(status, reason=reason, data=data,
            content_type=content_type)


    def _proxy_app(self, environ, start_response):
        """
        main method called when a request is received from a client
        (WSGI application)
        """
        self._init_request_response()
        # parse request headers:
        self._parse_request(environ)
        # filter request headers before reading the request body:
        self.filter_request_headers()
        # check if the response was set by filter_request_headers, else continue:
        if self.resp.status is None:
            # if request has data, read it:
            self._read_request_body()
            # filter request before sending it to server:
            self.filter_request()
        # check if the response was set by filter_request, else forward to server:
        if self.resp.status is None:
            # send request to server:
            self._send_request()
            # parse response headers:
            self._parse_response()
            # filter response headers before reading the response body:
            self.filter_response_headers()
        # check if the response was set by filter_response_headers, else continue:
        # (here we need to check if resp.data is still None)
        if self.resp.data is None:
            # read the response body
            self._read_response_body()
            # filter response before sending it to client:
            self.filter_response()
        # For now we always close the connection, even if the client sends
        # several requests in one connection:
        # (not optimal performance-wise, but simpler to code)
        if self.resp.httpconn is not None:
            self.resp.httpconn.close()
        # send response to client:
        self._send_response(start_response)
        # send response body:
        return [self.resp.data]


    def _init_request_response(self):
        """
        Initialize variables when a new request is received
        """
        # set request id (simply increase number at each request)
        with self._lock_reqid:
            self._reqid +=1
            self.req.reqid = self._reqid
        reqname = 'Req%05d' % self.req.reqid
        # set a logger for each request
        # check if there is already one, set by a previous request:
        if not hasattr(self.req, 'log'):
            # no logger yet for this thread, create one:
            self.req.log = logging.getLogger(reqname)
            self.req.log.setLevel(self.log_level)
        if self.log_file:
            # force logging level to debug:
            self.req.log.setLevel(logging.DEBUG)
            # close and remove file handler from previous request:
            if hasattr(self.req, '_log_handler'):
                self.req._log_handler.close()
                self.req.log.removeHandler(self.req._log_handler)
            # add a file handler for this request
            self.req._log_handler = logging.FileHandler(reqname+'.log', 'w')
            self.req.log.addHandler(self.req._log_handler)
        # request variables
        self.req.environ = {}
        self.req.headers = {}
        self.req.method = None
        self.req.scheme = None
        self.req.netloc = None
        self.req.path = None
        self.req.query = None
        self.req.url = None
        self.req.length = 0
        self.req.content_type = None
        self.req.charset = None
        self.req.url_filename = None
        self.req.data = None
        # response variables
        self.resp.httpconn = None
        self.resp.response = None
        self.resp.status = None
        self.resp.reason = None
        self.resp.headers = [] # httplib headers is a list of (header, value) tuples
        self.resp.content_type = None
        self.resp.charset = None
        self.resp.content_disp_filename = None
        self.resp.data = None


    def _parse_request(self, environ):
        """
        parse a request received from a client
        """
        self.req.environ = environ
        #self.debug('_'*50)
        self.debug('REQUEST RECEIVED FROM CLIENT:')
        self.debug('req.environ = %s' % environ)
        #for env in environ:
        #    self.debug('%s: %s' % (env, environ[env]))
        #print environ
        # convert WSGI environ to a dict of HTTP headers:
        self.req.headers = {}
        for h in environ:
            if h.startswith('HTTP_'):
                hname = h[5:].replace('_', '-').lower()
                self.req.headers[hname] = environ[h]
        self.debug('req.headers = %s' % self.req.headers)
        # content-type and content-length are stored differently, without "HTTP_"
        # (cf. CherryPy WSGIServer source code or WSGI specs)
        #self.req.headers['content-type'] = self.req.environ.get('CONTENT_TYPE', None)
        #self.req.headers['content-length'] = self.req.environ.get('CONTENT_LENGTH', None)
        #print headers
        self.req.method = environ['REQUEST_METHOD'] # GET, POST, HEAD, etc
        self.req.scheme = environ['wsgi.url_scheme'] # http
        self.req.netloc = environ['SERVER_NAME'] # www.server.com[:80]
        self.req.path   = environ['PATH_INFO'] # /folder/index.html
        self.req.query  = environ['QUERY_STRING']
        # URL=/path?query used when forwarding directly to the server
        self.req.url = urlparse.urlunsplit(
            ('', '', self.req.path, self.req.query, ''))
        self.debug('req.url = %s' % self.req.url)
        # full URL used when forwarding to a parent proxy
        self.req.full_url = urlparse.urlunsplit(
            (self.req.scheme, self.req.netloc, self.req.path, self.req.query, ''))
        self.debug('req.full_url = %s' % self.req.full_url)
        # parse content-type and charset:
        # see RFC 2616: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.17
        #ct = self.req.headers.get('content-type', None)
        ct = self.req.environ.get('CONTENT_TYPE', None)
        if ct is not None:
            if ';' in ct:
                ct, charset = ct.split(';', 1)
                self.req.content_type = ct.strip()
                self.req.charset = charset.strip()
            else:
                self.req.content_type = ct.strip()
        self.debug('req.content_type = %s' % repr(self.req.content_type))
        self.debug('req.charset      = %s' % repr(self.req.charset))
        #self.debug('- '*25)
        self.req.log.info('Request %s %s' % (self.req.method, self.req.full_url))
        # init values before reading request body
        self.req.length = 0
        self.req.data = None
        # Reject request if method or scheme is not allowed:
        if self.req.method in BLACKLIST_METHODS:
            # here I use 501 "not implemented" rather than 405 or 401, because
            # it seems to be the most appropriate response according to RFC 2616.
            # see http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
            msg = 'Method "%s" not supported.' % self.req.method
            self.set_response(501, reason=msg)
            self.req.log.error(msg)
        if self.req.scheme in BLACKLIST_SCHEMES:
            msg = 'Scheme "%s" not supported.' % self.req.scheme
            self.set_response(501, reason=msg)
            self.req.log.error(msg)



    def _read_request_body(self):
        """
        read the request body if available
        """
        environ = self.req.environ
        # if request has data, read it:
        if 'CONTENT_LENGTH' in environ:
            self.req.length = int(environ['CONTENT_LENGTH'])
            self.debug('REQUEST BODY: content-length=%d' % self.req.length)
            self.req.data = environ['wsgi.input'].read(self.req.length)
            self.debug(self.req.data)
        else:
            self.req.length = 0
            self.req.data = None
            self.debug('No request body.')


    def _send_request(self):
        """
        forward a request received from a client to the server
        Get the response (but not the response body yet)
        """
        #TODO: reconstruct URL from its elements (if they were changed)
        #self.debug('- '*25)
        if self.parent_proxy:
            # if a parent proxy is specified, this is the address to connect to:
            netloc = self.parent_proxy
            # and the URL is the full one:
            url = self.req.full_url
            self.debug('sending request to the parent proxy: %s - %s' % (netloc, url))
        else:
            # if no parent proxy is specified, we connect directly to the server:
            netloc = self.req.netloc
            # and the URL is the full one:
            url = self.req.url
            self.debug('sending request directly to the server: %s - %s' % (netloc, url))
        # send request to server or proxy:
        self.resp.httpconn = httplib.HTTPConnection(netloc)
##        if self.debug_mode:
##            self.resp.httpconn.set_debuglevel(1)
        #TODO: handle connection errors
        self.resp.httpconn.request(self.req.method, url,
            body=self.req.data, headers=self.req.headers)
        self.resp.response = self.resp.httpconn.getresponse()
        self.resp.status = self.resp.response.status
        self.resp.reason = self.resp.response.reason
        status = "%d %s" % (self.resp.status, self.resp.reason) #'200 OK'
        #self.debug('- '*25)
        self.debug('RESPONSE RECEIVED FROM SERVER: %s' % status)


    def _parse_response(self):
        """
        parse a request received from a client
        """
        self.resp.headers = self.resp.response.getheaders() #[('Content-type','text/plain')]
        for h in self.resp.headers:
            self.debug(' - %s: %s' % (h[0], h[1]))
        # parse content-type and charset:
        # using mimetools.Message.gettype() on HTTPResponse.msg
        self.resp.content_type = self.resp.response.msg.gettype().lower()
        self.debug('resp.content_type = %s' % repr(self.resp.content_type))
##        ct = self.resp.headers.get('content-type', None)
##        if ';' in ct:
##            ct, charset = ct.split(';', 1)
##            self.req.content_type = ct.strip()
##            self.req.charset = charset.strip()
##        elif ct is not None:
##            self.req.content_type = ct.strip()
        self.req.log.info('Response %s %s' % (self.resp.status, self.resp.reason))



    def _read_response_body(self):
        """
        read the response body and close the connection
        """
        # TODO: check content-length?
        self.resp.data = self.resp.response.read()
##        print '- '*39
##        print repr(self.data)


    def _send_response(self, start_response):
        """
        send the response with headers (but no body yet)
        """
        status = "%d %s" % (self.resp.status, self.resp.reason) #'200 OK'
        #self.debug('- '*25)
        self.debug('RESPONSE SENT TO CLIENT:')
        self.debug(status)
        for h in self.resp.headers:
            self.debug(' - %s: %s' % (h[0], h[1]))
        start_response(status, self.resp.headers)


    def _debug_enabled(self, string):
        """
        debug method when debug mode is enabled
        """
        #print string
        #self.req.log.debug(string)
        self.req.log.debug(string)

    def _debug_disabled(self, string):
        """
        debug method when debug mode is disabled (does nothing)
        """
        pass


#=== MAIN =====================================================================

def main(cproxy=CherryProxy, optionparser=None):
    """
    main function for testing purposes from the command-line.

    cproxy: optional proxy class derived from CherryProxy
    optionparser: optional optparse.OptionParser object to provide additional
                  command line options
    """
    if optionparser is None:
        import optparse
        parser = optparse.OptionParser()
    else:
        parser = optionparser
    parser.add_option("-p", "--port", dest="port", type='int', default=8070,
                      help="port for HTTP proxy, 8070 by default")
    parser.add_option("-a", "--address", dest="address", default='localhost',
                      help="IP address of interface for HTTP proxy (0.0.0.0 for all, default=localhost)")
    parser.add_option("-f", "--forward", dest="proxy", default=None,
                      help="Forward requests to parent proxy, specified as hostname[:port] or IP address[:port]")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help='Verbose mode, display debugging messages')
    parser.add_option("-l", "--log", action="store_true", dest="log_file",
                      help='Log each request to a separate file (use with -v)')
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    # simple CherryProxy without filter:
    debug=False
    log_level = logging.INFO
    try:
        if options.verbose:
            debug=True
            log_level = logging.DEBUG
    except:
        pass

    # setup logging
    logging.basicConfig(format='%(name)s-%(thread)05d: %(levelname)-8s %(message)s',
        level=log_level)

    print __doc__
    proxy = cproxy(address=options.address, port=options.port,
        debug=debug, log_level=log_level, options=options,
        parent_proxy=options.proxy, log_file=options.log_file)
    while True:
        try:
            proxy.start()
        except KeyboardInterrupt:
            proxy.stop()
            sys.exit()


if __name__ == '__main__':
    main()