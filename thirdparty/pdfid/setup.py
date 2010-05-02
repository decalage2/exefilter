"""
Setup script for pdfid_PL
"""

import distutils.core
import pdfid_PL

DESCRIPTION = "A Python module to analyze and sanitize PDF files, based on Didier Stevens' PDFiD"

LONG_DESCRIPTION = """pdfid_PL is a Python module to analyze and sanitize PDF files.
It is a slightly modified version of Didier Stevens' PDFiD, to be imported
in Python applications more easily.
See http://www.decalage.info/python/pdfid for more information.
"""

kw = {
    'name': "pdfid_PL",
    'version': pdfid_PL.__version__,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'author': "Philippe Lagadec, Didier Stevens",
    'author_email': "decalage (a) laposte.net",
    'url': "http://www.decalage.info/python/pdfid",
    'license': "Public Domain",
    'py_modules': ['pdfid_PL']
    }


# If we're running Python 2.3+, add extra information
if hasattr(distutils.core, 'setup_keywords'):
    if 'classifiers' in distutils.core.setup_keywords:
        kw['classifiers'] = [
            'Development Status :: 4 - Beta',
            'License :: Public Domain',
            'Natural Language :: English',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Security',
            'Topic :: Software Development :: Libraries :: Python Modules'
          ]
    if 'download_url' in distutils.core.setup_keywords:
        kw['download_url'] = "http://www.decalage.info/python/pdfid"


distutils.core.setup(**kw)
