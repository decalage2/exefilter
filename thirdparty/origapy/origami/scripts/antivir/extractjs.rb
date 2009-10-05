#!/usr/bin/env ruby 

$: << "../../parser"
require 'parser.rb'
include Origami

if ARGV.size < 1
  puts "Usage: #{__FILE__} <files>"
end

ARGV.each do |file|
  pdf = PDF.read(file, :verbosity => Parser::VERBOSE_QUIET)
  scripts = pdf.ls(/^JS/)
  
  unless scripts.empty?
    colorprint "-" * 80 + "\n", Colors::MAGENTA
    colorprint "* Found the following scripts in #{file} :\n", Colors::MAGENTA
    colorprint "-" * 80 + "\n", Colors::MAGENTA
    scripts.each do |script|
      colorprint case script
        when Stream then script.data # print the uncompressed data stream
        else script.value
      end + "\n", Colors::CYAN
      colorprint "-" * 80 + "\n", Colors::MAGENTA
    end
  end
end

