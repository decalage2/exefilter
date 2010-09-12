# Setup script for origapy - Philippe Lagadec

import distutils.core

from origapy import __version__, __author__

DESCRIPTION = "A Python module to clean PDF files by disabling active content (javascript, launch, etc), using the Ruby Origami PDF parser."

LONG_DESCRIPTION = open("README.txt").read()

kw = {
    'name': "origapy",
    'version': __version__,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'author': __author__,
    'author_email': "decalage (a) laposte.net",
    'url': "http://www.decalage.info/python/origapy",
    'license': "GPL v3",
    'py_modules': ['origapy'],
    }


# If we're running Python 2.3, add extra information
if hasattr(distutils.core, 'setup_keywords'):
    if 'classifiers' in distutils.core.setup_keywords:
        kw['classifiers'] = [
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Ruby',
            'Topic :: Software Development :: Libraries :: Python Modules'
          ]
    if 'download_url' in distutils.core.setup_keywords:
        kw['download_url'] = "http://www.decalage.info/python/origapy"

distutils.core.setup(**kw)
