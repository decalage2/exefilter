################################################################################
#                                                                              #
#                  Origami - Ruby PDF manipulation framework                   #
#                                                                              #
################################################################################

:: DESCRIPTION
==============

Origami is a framework written in Ruby designed to parse, analyze, and forge PDF 
documents.
This is *NOT* a PDF rendering library, it aims at providing a scripting tool for 
generating and analyzing malicious PDF files. As well, it can be used to create 
on-the-fly customized PDFs, or to inject evil code into already existing 
documents.


:: LICENSE
==========

This software is distributed under the GPL license.
See the COPYING file for more details.


:: RELEASE
==========

- Current : Version 1.0.0 Alpha 0 release


:: DEPENDENCIES
===============

- Ruby 1.8 (actually not tested on 1.9)
- Ruby-GTK2 (only for GUI), http://ruby-gnome2.sourceforge.jp/


:: DIRECTORIES
==============

``sources/parser/``
* Core scripts used to parse a PDF file. All objects and features are
  provided here.

``sources/walker/``
* An unfinished GTK interface to analyze a PDF.

``sources/samples/``
* Many samples, mostly sorted to generate specially crafted PDFs.

``sources/scripts/``
* Simple Ruby scripts playing with PDF files.

``sources/tests/``
* Test case units.

``doc/``
* Automated RubyDoc HTML documentation.


:: CONTRIBUTORS
===============

Guillaume Delugré <guillaume@security-labs.org>     - Author
Frédéric Raynal   <fred@security-labs.org>          - Contributor


:: NOTES
========

This is a very first alpha release. It contains many bugs and many incomplete
features. If you encounter a problem, feel free to report it by mail at
<guillaume@security-labs.org>, with a short explanation of what you did and
any necessary PDF documents.

Thanks.

