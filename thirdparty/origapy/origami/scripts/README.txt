:: SUBDIRECTORIES
=================

``antivir/``
* Scripts to quickly search for offensive patterns inside PDF documents.
  - detectsig.rb: Search for a signature inside PDF objects (using
    PDF#grep method).

  - extractjs.rb: Search and extract all JS scripts from documents
    (using PDF#ls method).

  - pdfcleanr.rb: deactivate some "features" of the PDF language. 
    Actions, trigger events and form actions can be turned off. This
    is done by swapping the case of these keywords (as PDF language is
    case sensitive).

``embed/``
* Script to attach a file to an existing PDF document. the user is
  then prompted to execute the file at the document opening.


``js/``
* Script to inject a (possibly malicious) JS script into an existing
  PDF document.

``moebius/``
* Torture a PDF document: it jumps from page to page, then jumps back
  onto first page as hitting the last one. Implemented using PDF GoTo
  action (works under Adobe Reader, and should with Foxit too).

``samba/``
* Implementation of a SMB relay attack using PDF. When opened in a
  browser on Windows, the document tries to access a document shared
  on a malicious SMB server (on a LAN). The server will then be able
  to steal user credentials. This script merely forges the malicious
  PDF document.

``crypto/``
* Encrypt contents of a PDF document. If a null password is provided,
  the document will be decrypted automatically at opening.


``exploits/``
* Basic exploits PoC generation.


``scan/``
* A PDF scanner, working either in fast mode, or deep mode.
  -fast: the PDF is read, names are sanitized, then scan is made based
   on regular expressions which can lead to some misleading results,
   but is really fast.

  -deep: in this mode, we use our own PDF parser to get deep into each
   PDF object. This is really slow but the inspection is equivalent to
   the completeness of the parser.

``metadata/``
* Display metadata contained in a document.

