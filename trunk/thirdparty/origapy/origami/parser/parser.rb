=begin

= File
	parser.rb

= Info
	Origami is free software: you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Origami is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with Origami.  If not, see <http://www.gnu.org/licenses/>.

=end

require 'strscan'

require 'origami/pdf'
require 'origami/adobe/addressbook'

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

  def Origami.parse(file, options = {})
    
    if file.respond_to?(:read)
      filename = nil
      data = file.read
    else
      filename = file
      data = File.open(filename, "r").binmode.read
    end
    
    stream = StringScanner.new(data)
    
    hdr = nil
    [ PDF, Adobe::AddressBook ].each do |filetype|
      begin
        hdr = filetype::Header.parse(stream)
        break
      rescue Exception => e 
        if filetype == PDF and options[:force] == true
          unless stream.skip_until(/%PDF-/).nil?
            stream.pos = stream.pos - 5
            retry
          end
        end

        next
      end
    end
    
    parser = 
    case hdr
      when PDF::Header
        PDF::LinearParser.new(options)     
      when Adobe::AddressBook::Header
        Adobe::AddressBook::Parser.new(options)
      else
        raise ParsingError, "No file type was recognized"
    end

    parsee = parser.parse(stream)
    
    parsee.filename = filename
    parsee
  end

  class Parser #:nodoc:

    class ParsingError < Exception #:nodoc:
    end
   
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
    
    attr_accessor :options
    
    def initialize(options = {}) #:nodoc:
      
      #Default options values
      @options = 
      { 
        :verbosity => VERBOSE_INFO, # Verbose level.
        :ignore_errors => true,    # Try to keep on parsing when errors occur.
        :callback => Proc.new {},   # Callback procedure whenever a structure is read.
        :prompt_password => Proc.new { print "Password: "; gets.chomp }, #Callback procedure to prompt password when document is encrypted.
        :force => false # Force PDF header detection
      }
     
      @options.update(options)
    end

    def parse(stream)
      data = 
      case stream
        when IO then 
          @filename = stream.path
          StringScanner.new(stream.read)
        when ::String then
          @filename = stream
          StringScanner.new(File.open(stream, "r").binmode.read)
        when StringScanner then
          stream
        else
          raise TypeError
      end
    
      @data = data
      @data.pos = 0
    end
    
    def parse_objects(file) #:nodoc:
      begin
        loop do 
          obj = Object.parse(@data)
          return if obj.nil?

          trace "Read #{obj.type} object#{if obj.type != obj.real_type then " (" + obj.real_type.to_s.split('::').last + ")" end}, #{obj.reference}"
          
          file << obj
                    
          @options[:callback].call(obj)
        end
        
      rescue UnterminatedObjectError => e
        error e.message
        file << e.obj

        @options[:callback].call(e.obj)
        retry

      rescue Exception => e
        error "Breaking on: #{(@data.peek(10) + "...").inspect} at offset 0x#{@data.pos.to_s(16)}"
        error "Last exception: [#{e.class}] #{e.message}"
        debug "-> Stopped reading body : #{file.revisions.last.body.size} indirect objects have been parsed" if file.is_a?(PDF)
        puts e.backtrace    
        abort("Manually fix the file or set :ignore_errors parameter.") if not @options[:ignore_errors]

        debug 'Skipping this indirect object.'
        return if @data.skip_until(/endobj/).nil?
            
        retry
      end
    end
    
    def parse_xreftable(file) #:nodoc:
      begin
        info "...Parsing xref table..."
        file.revisions.last.xreftable = XRef::Section.parse(@data)
        @options[:callback].call(file.revisions.last.xreftable)
      rescue Exception => e
        debug "Exception caught while parsing xref table : " + e.message
        warn "Unable to parse xref table! Xrefs might be stored into an XRef stream."

        @data.pos -= 'trailer'.length unless @data.skip_until(/trailer/).nil?
      end
    end
    
    def parse_trailer(file) #:nodoc:
      begin
        info "...Parsing trailer..."
        trailer = Trailer.parse(@data)

        if file.is_a?(PDF)
          xrefstm = file.get_object_by_offset(trailer.startxref) || 
          (file.get_object_by_offset(trailer.XRefStm) if trailer.has_field? :XRefStm)
        end

        if not xrefstm.nil?
          debug "Found a XRefStream for this revision at #{xrefstm.reference}"
          file.revisions.last.xrefstm = xrefstm
        end

        file.revisions.last.trailer = trailer
        @options[:callback].call(file.revisions.last.trailer)
       
      rescue Exception => e
        debug "Exception caught while parsing trailer : " + e.message
        warn "Unable to parse trailer!"
            
        abort("Manually fix the file or set :ignore_errors parameter.") if not @options[:ignore_errors]

        raise
      end
    end

    private
 
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

  class PDF

    #
    # Create a new PDF linear Parser.
    #
    class LinearParser < Origami::Parser
      def parse(stream)
        super
        
        if @options[:force] == true
          @data.skip_until(/%PDF-/).nil?
          @data.pos = stream.pos - 5
        end

        pdf = PDF.new(false)
        pdf.filename = @filename

        info "...Reading header..."
        pdf.header = PDF::Header.parse(@data)
        @options[:callback].call(pdf.header)
        
        #
        # Parse each revision
        #
        revision = 0
        until @data.eos? do
          
          begin
            
            pdf.add_new_revision unless revision.zero?
            revision = revision.succ
            
            info "...Parsing revision #{pdf.revisions.size}..."
            parse_objects(pdf)
            parse_xreftable(pdf)
            parse_trailer(pdf)
            
          rescue SystemExit
            raise
          rescue Exception => e
            error "Cannot read : " + (@data.peek(10) + "...").inspect
            error "Stopped on exception : " + e.message
            
            break
          end
          
        end

        warn "This file has been linearized." if pdf.is_linearized?

        #
        # Decrypt encrypted file contents
        #
        if pdf.is_encrypted?
          warn "This document contains encrypted data !"
        
          passwd = ""
          begin
            pdf.decrypt(passwd)
          rescue EncryptionInvalidPasswordError
            if passwd.empty?
              passwd = @options[:prompt_password].call
              retry unless passwd.empty?
              raise EncryptionInvalidPasswordError
            end
          end
        end

        pdf
      end
    end
  end

  class Adobe::AddressBook
    class Parser < Origami::Parser
      def parse(stream) #:nodoc:
        super

        addrbk = Adobe::AddressBook.new
        addrbk.filename = @filename

        addrbk.header = Adobe::AddressBook::Header.parse(stream)
        @options[:callback].call(addrbk.header)
        
        parse_objects(addrbk)
        parse_xreftable(addrbk)
        parse_trailer(addrbk)
        book_specialize_entries(addrbk)

        addrbk
      end
      
      def book_specialize_entries(addrbk) #:nodoc:
        addrbk.revisions.first.body.each_pair { |ref, obj|
          
          if obj.is_a?(Dictionary)
            
            if obj[:Type] == :Catalog
              
              o = Adobe::AddressBook::Catalog.new(obj)
              o.generation, o.no, o.file_offset = obj.generation, obj.no, obj.file_offset
              
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
              o.generation, o.no, o.file_offset = obj.generation, obj.no, obj.file_offset
              
              addrbk.revisions.first.body[ref] = o
            elsif obj[:ABEType] == Adobe::AddressBook::Descriptor::CERTIFICATE
              o = Adobe::AddressBook::Certificate.new(obj)
              o.generation, o.no, o.file_offset = obj.generation, obj.no, obj.file_offset
              
              addrbk.revisions.first.body[ref] = o
            end

          end
        }
      end
    end
  end

end
