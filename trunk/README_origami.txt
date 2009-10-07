How to use ExeFilter with Origami:

Origami is a Ruby framework to parse and edit PDF documents. It includes the
pdfclean script which can sanitize PDF files by disabling all active content
(javascript, launch, etc).
See http://www.security-labs.org/origami/

The Origami engine has been integrated into ExeFilter since version 1.1.2,
because Origami is much more effective than the builtin PDF filter.
However, this option is disabled by default because it requires the Ruby
interpreter, and the parser is not complete yet.

A policy file enabling origami is provided if you want to test this new engine. 
Use the -p option to enable it.

Sample usage:

ExeFilter.py source_path -d destination_path -p policy_origami.ini 


A few PDF samples may be found in the folder 
thirdparty/origapy/origami/scripts/antivir


Requirements:
- install Ruby interpreter if not already present
- make sure it is accessible from everywhere thanks to the PATH variable