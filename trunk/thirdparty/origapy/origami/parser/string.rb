=begin

= File
	string.rb

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

module Origami

  #
  # Module common to String objects.
  #
  module String
    
    include Origami::Object
    
    def real_type ; Origami::String end

  end

  class InvalidHexaString < Exception #:nodoc:
  end
  
  #
  # Class representing an hexadecimal-writen String Object.
  #
  class HexaString < ::String
    
    include String
    
    TOKENS = %w{ < > } #:nodoc:
    
    @@regexp_open = Regexp.new('\A' + WHITESPACES + TOKENS.first)
    @@regexp_close = Regexp.new(TOKENS.last)

    #
    # Creates a new PDF hexadecimal String.
    # _str_:: The string value.
    #
    def initialize(str = "", indirect = false)
      
      unless str.is_a?(::String)
        raise TypeError, "Expected type String, received #{str.class}."
      end
      
      super(indirect, str)
    
    end
    
    def self.parse(stream) #:nodoc:
        
      if stream.skip(@@regexp_open).nil?
        raise InvalidHexaString, "Hexadecimal string shall start with a '#{TOKENS.first}' token"
      end
        
      hexa = stream.scan_until(@@regexp_close)
      if hexa.nil?
        raise InvalidHexaString, "Hexadecimal string shall end with a '#{TOKENS.last}' token"
      end

      decoded = Filter::ASCIIHex.decode(hexa.chomp!(TOKENS.last))
        
      HexaString.new(decoded)
    end
    
    def to_s #:nodoc:
      print(TOKENS.first + Filter::ASCIIHex.encode(super) + TOKENS.last)
    end

    #
    # Converts self to ByteString
    #
    def to_raw
      ByteString.new(self.value)
    end
    
    alias value to_str
    
  end
 
=begin
  class InvalidUTF16BEString < Exception #:nodoc:
  end
  
  #
  # Class representing a UTF16 Big Endian encoded String Object.
  #
  class UTF16BEString < ByteString
    
    #
    # Creates a new UTF16BE encoded String.
    # _str_:: The ASCII representation of the new String.
    # _Not used_
    # _Not tested_
    #
    def initialize(str = "", no = 0, generation = 0)
      
      super(ascii2utf16(str), no, generation)
      
    end
    
    private
    
    def ascii2utf16(str) #:nodoc:
      
      utf16_str = "\xFE\xFF"
      str.each_byte { |c|
        utf16_str << "\0" + c.chr
      }
      
      utf16_str
    end
    
  end
  
  class InvalidDate < InvalidByteString #:nodoc:
  end
 
  #
  # Class representing a Date string.
  # _Not used_
  # _Not tested_
  #
  class Date < ByteString
    
    attr_accessor :year, :month, :day, :hour, :minute, :second, :timezone
    
    TOKENS = [ "(D:)?(\\d{4})((\\d{2})((\\d{2})((\\d{2})((\\d{2})((\\d{2}))?)?)?(([-+Z])(\\d{2})'(\\d{2})')?)?)?" ]
    
    def initialize(year, month = nil, day = nil, hour = nil, minute = nil, second = nil, timezone = nil, indirect = false)
      
      @year, @month, @day = year, month, day
      @hour, @minute, @second, @timezone = hour, minute, second, timezone
      
      super("D:#{year}#{month}#{day}#{hour}#{minute}#{second}#{timezone}", indirect)
      
    end
    
    def self.parse(stream)
      
      dateReg = Regexp.new('\A' + TOKENS.first)
      
      if stream.scan(dateReg).nil?
        raise InvalidDate
      end
        
      year = stream[2]
      month = stream[4]
      day = stream[6]
      hour = stream[8]
      min = stream[10]
      sec = stream[12]
      tz = stream[13]
        
      Origami::Date.new(year, month, day, hour, min, sec, tz)
    end
    
    def self.now
      d = Time.now
      Origami::Date.new(d.strftime("%Y"), d.strftime("%m"), d.strftime("%d"), d.strftime("%H"), d.strftime("%M"), d.strftime("%S"))
    end
    
  end
=end

  class InvalidByteString < Exception #:nodoc:
  end

  #
  # Class representing an ASCII String Object.
  #
  class ByteString < ::String
    
    include String
    
    TOKENS = %w{ ( ) } #:nodoc:
    
    @@regexp_open = Regexp.new('\A' + WHITESPACES + Regexp.escape(TOKENS.first))
    @@regexp_close = Regexp.new(Regexp.escape(TOKENS.last))
    
    #
    # Creates a new PDF String.
    # _str_:: The string value.
    #
    def initialize(str = "", indirect = false)
      
      unless str.is_a?(::String)
        raise TypeError, "Expected type String, received #{str.class}."
      end
      
      super(indirect, str)
    end

    def self.parse(stream) #:nodoc:
      
      if not stream.skip(@@regexp_open)
        raise InvalidByteString, "No literal string start token found"
      end
      
      result = ""
      depth = 0
      while depth != 0 or stream.peek(1) != TOKENS.last do

        if stream.eos?
          raise InvalidByteString, "Non-terminated string"
        end

        c = stream.get_byte
        case c
        when "\\"
          if stream.match?(/\A\d{1,3}/)
            oct = stream.peek(3).oct.chr
            stream.pos += 3
            result << oct
          elsif stream.match?(/\A((\r?\n)|(\r\n?))/)
            
            stream.skip(/\A((\r?\n)|(\r\n?))/)
            next
            
          else
            flag = stream.get_byte
            case flag
            when "n" then result << "\n"
            when "r" then result << "\r"
            when "t" then result << "\t"
            when "b" then result << "\b"
            when "f" then result << "\f"
            when "(" then result << "("
            when ")" then result << ")"
            when "\\" then result << "\\"
            when "\r"
              if str.peek(1) == "\n" then stream.pos += 1 end
            when "\n"
            else
              result << flag
            end
          end
            
        when "(" then
          depth = depth + 1
          result << c
        when  ")" then
          depth = depth - 1
          result << c
        else
          result << c
        end

      end

      if not stream.skip(@@regexp_close)
        raise InvalidByteString, "Byte string shall be terminated with '#{TOKENS.last}'"
      end

      ByteString.new(result)
    end

    def expand #:nodoc:
      
      extended = self.gsub("\\", "\\\\\\\\")
      extended.gsub!(/\)/, "\\)")
      extended.gsub!("\n", "\\n")
      extended.gsub!("\r", "\\r")
      extended.gsub!(/\(/, "\\(")
      
      extended
    end
    
    def to_s #:nodoc:
      print(TOKENS.first + self.expand + TOKENS.last)
    end

    #
    # Converts self to HexaString
    #
    def to_hex
      HexaString.new(self.value)
    end
    
    alias value to_str
    
  end
  
end
