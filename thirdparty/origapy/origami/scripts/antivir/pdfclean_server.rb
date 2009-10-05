#!/usr/bin/env ruby 

#------------------------------------------------------------------------------

#   - pdfclean.rb: deactivate some "features" of the PDF language. 
#     Actions, trigger events and form actions can be turned off. This
#     is done by swapping the case of these keywords (as PDF language is
#     case sensitive). 

# pdfclean_server.rb is a modified version which acts as a server, waiting for
# PDF filenames to be cleaned on its standard input (indefinite loop).
# The process ends either if the user types "exit" or if an error occurs.
# A client process may use popen() to launch pdfclean_server, send filenames
# and read results using a pipe. The purpose is to use this script from any
# language, not only Ruby.
# See Origapy for a sample client implementation in Python: 
# http://www.decalage.info/python/origapy

# AUTHORS:
# Guillaume Delugre <guillaume@security-labs.org>     - Author
# Frederic Raynal   <fred@security-labs.org>          - Contributor
# Philippe Lagadec  <decalage at laposte.net>         - Contributor

# LICENSE: GPL v3 (see COPYING)
 
# CHANGELOG:
# 2009-07-12 PL: - modified version renamed to pdfclean_server.rb
#                - moved main script into a function                             
#                - loop to read PDF file names from stdin (pipe mode)
#                - parse PDF file here instead of within getop.rb
# 2009-09-30 PL: - added logging with "[CLEANED]" keyword when PDF is actually 
#                  cleaned, to detect it from the client.

# TODO:
# - avoid asking for password when parsing encrypted PDF
# - add a cleaner way to close the input file in clean_pdf (instead of calling GC.start)
# - catch exceptions to avoid exiting the process when a parsing error occurs
# - read options from command-line, to allow setting "type"

#------------------------------------------------------------------------------

$: << "../../parser"
require 'parser.rb'
include Origami

# getopt is not used in this version:
#require 'getopt.rb'

TRIGGER_PATTERNS = [ 'OpenAction', 'AA', 'Names' ]
ACTIONS_PATTERNS = [ 'GoTo', 'GoToE', 'GoToR', 'Launch', 'Thread', 'URI', 'Sound', 'Movie', 'JavaScript', 'Hide', 'Named', 'SetOCGState', 'Rendition', 'Transition', 'Go-To-3D' ]
FORM_PATTERNS = [ 'SubmitForm', 'ResetForm', 'ImportData' ]

def disable_triggers(pdf)

  objects = pdf.ls(*TRIGGER_PATTERNS.map{|str| Regexp.new("^#{str}$") })

  objects.each do |obj|
    dict = obj.parent

    TRIGGER_PATTERNS.each do |pattern|
      name = Name.new(pattern)
      if dict.has_key?(name)
        dict.delete(name)
        dict[pattern.swapcase.to_sym] = obj
        puts "[CLEANED] trigger " + pattern
      end
    end
  end

end

def disable_actions(pdf, actions)

  objects = pdf.grep(*actions.map{|str| Regexp.new("^#{str}$") })

  objects.each do |obj|
    parent = obj.parent

    if parent.is_a?(Dictionary) and actions.include?(parent[:S].value.to_s)
      puts "[CLEANED] action " + parent[:S].value.to_s
      parent[:S] = parent[:S].value.to_s.swapcase.to_sym
    end
  end

end

def disable_main_actions(pdf) ; disable_actions(pdf, ACTIONS_PATTERNS); end
def disable_form_actions(pdf) ; disable_actions(pdf, FORM_PATTERNS); end


def clean_pdf (input_name, output_name, type)
  if not input_name.nil?
    pdf = PDF.read(input_name, :verbose => Parser::VERBOSE_INFO )
  else
    pdf = PDF.new.append_page
  end

  if type == "all" or type == "triggers"
    disable_triggers(pdf)
  end
  
  if type == "all" or type == "main"
    disable_main_actions(pdf)
  end
  
  if type == "all" or type == "forms"
    disable_form_actions(pdf)
  end
  
  pdf.saveas(output_name)
  
  # This is apparently necessary to make sure that input file is closed:
  # (ref: http://blade.nagaokaut.ac.jp/cgi-bin/scat.rb/ruby/ruby-talk/9184)
  pdf = nil
  GC.start
end


#input_name, output_name, type = get_params()
  
# read command from standard input:
while true
  puts "Enter absolute path of PDF file to be cleaned, or 'exit' to quit:" 
  input_file = STDIN.gets
  # remove whitespaces:
  input_file.chop!
  # if command is "exit", terminate:
  if input_file == "exit"
    break
  else
    puts "Enter output file path:" 
    output_file = STDIN.gets
    output_file.chop!
    # else evaluate command, send result to standard output:
    clean_pdf(input_file, output_file, "all")
    # and append [end] so that master knows it's the last line:
    print "<<end>>\n"
    # flush stdout to avoid buffering issues:
    STDOUT.flush
  end
end

