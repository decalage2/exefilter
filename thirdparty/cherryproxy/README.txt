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


USAGE AS A TOOL (simple proxy):

1) run CherryProxy.py [options]

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

2) setup your browser to use localhost:8070 as proxy


USAGE IN A PYTHON APPLICATION:

- import cherryproxy
- create a subclass of cherryproxy.CherryProxy
- implement methods filter_request and/or filter_response to enable filtering as
  needed.
- see provided examples