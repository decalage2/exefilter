#!/usr/bin/env ruby 

begin
  require 'origami'
rescue LoadError
  ORIGAMIDIR = "#{File.dirname(__FILE__)}/../.."
  $: << ORIGAMIDIR
  require 'origami'
end
include Origami

require 'getopt.rb'
pdf, output_name, type = get_params()

TRIGGER_PATTERNS = [ 'OpenAction', 'AA', 'Names' ]
ACTIONS_PATTERNS = [ 'GoTo', 'GoToE', 'GoToR', 'Launch', 'Thread', 'URI', 'Sound', 'Movie', 'JavaScript', 'Hide', 'Named', 'SetOCGState', 'Rendition', 'Transition', 'Go-To-3D' ]
FORM_PATTERNS = [ 'SubmitForm', 'ResetForm', 'ImportData' ]

def disable_triggers(pdf)

  objects = pdf.ls_no_follow(*TRIGGER_PATTERNS.map{|str| Regexp.new("^#{str}$") })

  objects.each do |obj|
    dict = obj.parent

    TRIGGER_PATTERNS.each do |pattern|
      name = Name.new(pattern)
      if dict.has_key?(name)
        dict.delete(name)
        dict[pattern.swapcase.to_sym] = obj
      end
    end
  end

end

def disable_actions(pdf, actions)

  objects = pdf.grep(*actions.map{|str| Regexp.new("^#{str}$") })

  objects.each do |obj|
    parent = obj.parent

    if parent.is_a?(Dictionary) and parent.has_key?(:S) and actions.include?(parent[:S].value.to_s)
      parent[:S] = parent[:S].value.to_s.swapcase.to_sym
    end
  end

end

def disable_main_actions(pdf) ; disable_actions(pdf, ACTIONS_PATTERNS); end
def disable_form_actions(pdf) ; disable_actions(pdf, FORM_PATTERNS); end


disable_triggers(pdf) if type == "all" or type == "triggers"
disable_main_actions(pdf) if type == "all" or type == "main" 
disable_form_actions(pdf) if type == "all" or type == "forms"

pdf.saveas(output_name)

