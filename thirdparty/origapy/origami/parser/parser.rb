=begin

= File
	parser.rb

= Info
	Origami is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Origami is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with Origami.  If not, see <http://www.gnu.org/licenses/>.

=end

require 'strscan'

require 'pdf.rb'
require 'adobe/addressbook.rb'

module Origami
  
  if RUBY_PLATFORM =~ /win32/ 
    require "Win32API"
  
    getStdHandle = Win32API.new("kernel32", "GetStdHandle", ['L'], 'L')
    @@setConsoleTextAttribute = Win32API.new("kernel32", "SetConsoleTextAttribute", ['L', 'N'], 'I')

    @@hOut = getStdHandle.call(-11)
  end

  module Colors #:nodoc;
    if RUBY_PLATFORM =~ /win32/
      BLACK = 0
      BLUE = 1
      GREEN = 2
      CYAN = 3
      RED = 4
      MAGENTA = 5
      YELLOW = 6
      GREY = 7
      WHITE = 8
    else
      GREY = '0;0'
      BLACK = '0;30'
      RED = '0;31'
      GREEN = '0;32'
      BROWN  = '0;33'
      BLUE = '0;34'
      CYAN = '0;36'
      MAGENTA = '0;35'
      #~ :light_gray   => '0;37',
      #~ :dark_gray    => '1;30',
      #~ :light_red    => '1;31',
      #~ :light_green  => '1;32',
      YELLOW = '1;33'
      #~ :light_blue   => '1;34',
      #~ :light_cyan   => '1;36',
      #~ :light_purple => '1;35',
      WHITE  = '1;37'
    end
  end

  def set_fg_color(color, bright = false, fd = STDOUT) #:nodoc:
    if RUBY_PLATFORM =~ /win32/
      if bright then color |= Colors::WHITE end
      @@setConsoleTextAttribute.call(@@hOut, color)
      yield
      @@setConsoleTextAttribute.call(@@hOut, Colors::GREY)
    else
      col, nocol = [color, Colors::GREY].map { |key| "\033[#{key}m" }
      fd << col
      yield
      fd << nocol
    end
  end

  def colorprint(text, color, bright = false, fd = STDOUT) #:nodoc:
    set_fg_color(color, bright, fd) {
      fd << text
    }    
  end

  #
  # Class representing a PDF file parser.
  #
  class Parser
   
    #
    # Do not output debug information.
    #
    VERBOSE_QUIET = 0
    
    #
    # Output some useful information.
    #
    VERBOSE_INFO = 1
    
    #
    # Output debug information.
    #
    VERBOSE_DEBUG = 2
    
    #
    # Output every objects read
    #
    VERBOSE_INSANE = 3
    
    @@file_types = [ PDF, Adobe::AddressBook ]
    
    attr_accessor :options
    
    #
    # Creates a new PDF file Parser.
    # _options_:: A hash of options modifying the parser behavior.
    #
    def initialize(options = {})
      
      #Default options values
      @options = 
      { 
        :verbosity => VERBOSE_INFO, # Verbose level.
        :ignore_errors => true,    # Try to keep on parsing when errors occur.
        :callback => Proc.new {},   # Callback procedure whenever a structure is read.
        :prompt_password => Proc.new { print "Password: "; gets.chomp } #Callback procedure to prompt password when document is encrypted.
      }
     
      @options.update(options)
    end
    
    #
    # Parse the given file and returns a PDF object, or nil if the parsing process failed.
    # _filename_:: The path to the PDF file to parse.
    #
    def parse(file)
      
      # Read PDF file contents
      begin

        if file.respond_to?(:read)
          filename = nil
          data = file.read
        else
          filename = file
          data = File.open(filename, "r").binmode.read
        end
        
        stream = StringScanner.new(data)
        
        info "...Start parsing file ..."
        info "...Reading header..."

        hdr = nil
        @@file_types.each { |fileType|
          begin
            hdr = fileType::Header.parse(stream)
            break
          rescue Exception => e 
            next
          end
        }
        
        case hdr
          when PDF::Header
            pdf = PDF.new(false)
            pdf.header = hdr
            pdf.filename = filename
            @options[:callback].call(pdf.header)
            
            parse_pdf_file(pdf, stream)
            
            info "...End parsing file..."
            info
            
            return pdf
          
          when Adobe::AddressBook::Header
            addrbk = Adobe::AddressBook.new
            addrbk.header = hdr
            addrbk.filename = filename
            @options[:callback].call(addrbk.header)
            
            parse_addressbook(addrbk, stream)
            
            info "...End parsing file..."
            info
            
            return addrbk
          
          else
            raise InvalidHeader, "No file type was recognized"
        end
        
      rescue SystemExit
        raise

      rescue Exception => e
        error "An error occured while parsing."
      
        debug "#{e.message} (#{e.class})"
        #debug e.backtrace.join("\n")
        debug
         
        raise
      end
    
    end
  
    private
    
    def parse_pdf_file(pdf, stream) #:nodoc:
        
        #
        # Parse each revision
        #
        revision = 0
        until stream.eos? do
          
          begin
            
            pdf.add_new_revision unless revision.zero?
            revision = revision.succ
            
            info "...Parsing revision #{pdf.revisions.size}..."
            read_pdf_objects(pdf, stream)
            
            read_xreftable(pdf, stream)
            
            read_trailer(pdf, stream)
            
          rescue SystemExit
            raise
          rescue Exception => e
            error "Cannot read : " + (stream.peek(10) + "...").inspect
            error "Stopped on exception : " + e.message
            
            break
          end
          
        end

        if pdf.is_linearized?
          warn "This file has been linearized."
        end

        #
        # Decrypt encrypted file contents
        #
        if pdf.is_encrypted?
          warn "This document contains encrypted data !"
        
          passwd = ""
          begin
            pdf.decrypt(passwd)
# PL 2009-10-03: disabled password prompt to avoid blocking           
#           rescue EncryptionInvalidPasswordError
#             if passwd.empty?
#               passwd = @options[:prompt_password].call
#               retry unless passwd.empty?
#             end
          end
        end
          
    end
    
    def parse_addressbook(addrbk, stream) #:nodoc:
      
      read_pdf_objects(addrbk, stream)
      
      read_xreftable(addrbk, stream)
      
      read_trailer(addrbk, stream)
      
      book_specialize_entries(addrbk)
      
    end
    
    def read_pdf_objects(pdf, stream) #:nodoc:
    
      begin

        loop do 
          
          obj = Object.parse(stream, pdf)
          return if obj.nil?

          trace "Read #{obj.type} object#{if obj.type != obj.real_type then " (" + obj.real_type.to_s.split('::').last + ")" end}, #{obj.reference}"
          
          pdf << obj
                    
          @options[:callback].call(obj)
        end
        
      rescue Exception => e
        error "Breaking on: #{(stream.peek(10) + "...").inspect} at offset 0x#{stream.pos.to_s(16)}"
        error "Last exception: [#{e.class}] #{e.message}"
        debug "-> Stopped reading body : #{pdf.revisions.last.body.size} indirect objects have been parsed" if pdf.is_a?(PDF)
            
        abort("Manually fix the file or set :ignore_errors parameter.") if not @options[:ignore_errors]

        debug 'Skipping this indirect object.'
        return if stream.skip_until(/endobj/).nil?
            
        retry
      end
      
    end
    
    def read_xreftable(pdf, stream) #:nodoc:
      
      begin
      
        info "...Parsing xref table..."
        pdf.revisions.last.xreftable = XRef::Section.parse(stream)
        @options[:callback].call(pdf.revisions.last.xreftable)
        
      rescue Exception => e
        debug "Exception caught while parsing xref table : " + e.message
        warn "Unable to parse xref table! Xrefs might be stored into an XRef stream."
      end
      
    end
    
    def read_trailer(pdf, stream) #:nodoc:
      
      begin
      
        info "...Parsing trailer..."
        trailer = Trailer.parse(stream)

        xrefstm = pdf.get_object_by_offset(trailer.startxref) || 
          (pdf.get_object_by_offset(trailer.XRefStm) if trailer.has_field? :XRefStm)
       
        if not xrefstm.nil?
          debug "Found a XRefStream for this revision at #{xrefstm.reference}"
          pdf.revisions.last.xrefstm = xrefstm
        end

        pdf.revisions.last.trailer = trailer
        @options[:callback].call(pdf.revisions.last.trailer)
       
      rescue Exception => e
        debug "Exception caught while parsing trailer : " + e.message
        warn "Unable to parse trailer!"
            
        abort("Manually fix the file or set :ignore_errors parameter.") if not @options[:ignore_errors]

        raise
      end
      
    end
   
    def book_specialize_entries(addrbk) #:nodoc:
      
      addrbk.revisions.first.body.each_pair { |ref, obj|
        
        if obj.is_a?(Dictionary)
          
          if obj[:Type] == :Catalog
            
            o = Adobe::AddressBook::Catalog.new(obj)
            o.generation = obj.generation
            o.no = obj.no
            
            if o.PPK.is_a?(Dictionary) and o.PPK[:Type] == :PPK
              o.PPK = Adobe::AddressBook::PPK.new(o.PPK)
              
              if o.PPK.User.is_a?(Dictionary) and o.PPK.User[:Type] == :User
                o.PPK.User = Adobe::AddressBook::UserList.new(o.PPK.User)
              end
              
              if o.PPK.AddressBook.is_a?(Dictionary) and o.PPK.AddressBook[:Type] == :AddressBook
                o.PPK.AddressBook = Adobe::AddressBook::AddressList.new(o.PPK.AddressBook)
              end
            end
            
            addrbk.revisions.first.body[ref] = o
            
          elsif obj[:ABEType] == Adobe::AddressBook::Descriptor::USER
            o = Adobe::AddressBook::User.new(obj)
            o.generation = obj.generation
            o.no = obj.no
            
            addrbk.revisions.first.body[ref] = o
          elsif obj[:ABEType] == Adobe::AddressBook::Descriptor::CERTIFICATE
            o = Adobe::AddressBook::Certificate.new(obj)
            o.generation = obj.generation
            o.no = obj.no
            
            addrbk.revisions.first.body[ref] = o
          end

        end
        
      }
      
    end
 
    def error(str = "") #:nodoc:
      colorprint("[error] #{str}\n", Colors::RED, false, STDERR)
    end

    def warn(str = "") #:nodoc:
      colorprint("[info ] Warning: #{str}\n", Colors::YELLOW, false, STDERR) if @options[:verbosity] >= VERBOSE_INFO
    end

    def info(str = "") #:nodoc:
      (colorprint("[info ] ", Colors::GREEN, false, STDERR); STDERR << "#{str}\n") if @options[:verbosity] >= VERBOSE_INFO
    end
    
    def debug(str = "") #:nodoc:
      (colorprint("[debug] ", Colors::MAGENTA, false, STDERR); STDERR << "#{str}\n") if @options[:verbosity] >= VERBOSE_DEBUG
    end
    
    def trace(str = "") #:nodoc:
      (colorprint("[trace] ", Colors::CYAN, false, STDERR); STDERR << "#{str}\n") if @options[:verbosity] >= VERBOSE_INSANE
    end
    
  end

end
