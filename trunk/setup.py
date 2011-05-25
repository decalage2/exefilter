"""
Setup script for ExeFilter
"""
# CHANGELOG:
# 2010-05-25: - added short/long descriptions

import distutils.core
import __init__ as thispackage

DESCRIPTION = 'A tool and python framework to analyze files and sanitize active content such as javascript and macros'

LONG_DESCRIPTION = """ExeFilter is an open-source tool and python framework to filter file formats in e-mails, web pages or files.
It detects many common file formats and can remove active content (javascript, macros, etc) according to a configurable policy.
See http://www.decalage.info/exefilter for more information.
"""

kw = {
    'name': "exefilter",
    'version': thispackage.__version__,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'author': thispackage.__author__,
    'author_email': "decalage (a) laposte.net",
    'maintainer': 'Philippe Lagadec',
    'maintainer_email': "decalage (a) laposte.net",
    'url': "http://www.decalage.info/exefilter",
    'license': "CeCILL (open-source GPL compatible)",
    'platforms': ['any'],
    #'py_modules': ['ExeFilter', '__init__'],
    'packages': ['', 'Filtres', 'thirdparty', 'thirdparty.origapy', 'thirdparty.pdfid'],
    }


# If we're running Python 2.3+, add extra information
if hasattr(distutils.core, 'setup_keywords'):
    if 'classifiers' in distutils.core.setup_keywords:
        kw['classifiers'] = [
            'Development Status :: 4 - Beta',
            #'License :: Freely Distributable',
            'Natural Language :: French',
            'Natural Language :: English',
            'Intended Audience :: Developers',
            #'Topic :: Internet :: WWW/HTTP',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules'
          ]
    if 'download_url' in distutils.core.setup_keywords:
        kw['download_url'] = "http://www.decalage.info/exefilter"


distutils.core.setup(**kw)
