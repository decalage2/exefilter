=begin

= File
	string.rb

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

if RUBY_VERSION < '1.9'
  class Fixnum
    def ord; self; end
  end
end

module Origami

  #
  # Module common to String objects.
  #
  module String
    
    module Encoding
      class EncodingError < Exception #:nodoc:
      end

      module PDFDocEncoding

        CHARMAP =
        [
          "\x00\x00", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd",
          "\xff\xfd", "\x00\x09", "\x00\x0a", "\xff\xfd", "\x00\x0c", "\x00\x0d", "\xff\xfd", "\xff\xfd",
          "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd", "\xff\xfd",
          "\x02\xd8", "\x02\xc7", "\x02\xc6", "\x02\xd9", "\x02\xdd", "\x02\xdb", "\x02\xda", "\x02\xdc",
          "\x00\x20", "\x00\x21", "\x00\x22", "\x00\x23", "\x00\x24", "\x00\x25", "\x00\x26", "\x00\x27",
          "\x00\x28", "\x00\x29", "\x00\x2a", "\x00\x2b", "\x00\x2c", "\x00\x2d", "\x00\x2e", "\x00\x2f",
          "\x00\x30", "\x00\x31", "\x00\x32", "\x00\x33", "\x00\x34", "\x00\x35", "\x00\x36", "\x00\x37",
          "\x00\x38", "\x00\x39", "\x00\x3a", "\x00\x3b", "\x00\x3c", "\x00\x3d", "\x00\x3e", "\x00\x3f",
          "\x00\x40", "\x00\x41", "\x00\x42", "\x00\x43", "\x00\x44", "\x00\x45", "\x00\x46", "\x00\x47",
          "\x00\x48", "\x00\x49", "\x00\x4a", "\x00\x4b", "\x00\x4c", "\x00\x4d", "\x00\x4e", "\x00\x4f",
          "\x00\x50", "\x00\x51", "\x00\x52", "\x00\x53", "\x00\x54", "\x00\x55", "\x00\x56", "\x00\x57",
          "\x00\x58", "\x00\x59", "\x00\x5a", "\x00\x5b", "\x00\x5c", "\x00\x5d", "\x00\x5e", "\x00\x5f",
          "\x00\x60", "\x00\x61", "\x00\x62", "\x00\x63", "\x00\x64", "\x00\x65", "\x00\x66", "\x00\x67",
          "\x00\x68", "\x00\x69", "\x00\x6a", "\x00\x6b", "\x00\x6c", "\x00\x6d", "\x00\x6e", "\x00\x6f",
          "\x00\x70", "\x00\x71", "\x00\x72", "\x00\x73", "\x00\x74", "\x00\x75", "\x00\x76", "\x00\x77",
          "\x00\x78", "\x00\x79", "\x00\x7a", "\x00\x7b", "\x00\x7c", "\x00\x7d", "\x00\x7e", "\xff\xfd",
          "\x20\x22", "\x20\x20", "\x20\x21", "\x20\x26", "\x20\x14", "\x20\x13", "\x01\x92", "\x20\x44",
          "\x20\x39", "\x20\x3a", "\x22\x12", "\x20\x30", "\x20\x1e", "\x20\x1c", "\x20\x1d", "\x20\x18",
          "\x20\x19", "\x20\x1a", "\x21\x22", "\xfb\x01", "\xfb\x02", "\x01\x41", "\x01\x52", "\x01\x60",
          "\x01\x78", "\x01\x7d", "\x01\x31", "\x01\x42", "\x01\x53", "\x01\x61", "\x01\x7e", "\xff\xfd",
          "\x20\xac", "\x00\xa1", "\x00\xa2", "\x00\xa3", "\x00\xa4", "\x00\xa5", "\x00\xa6", "\x00\xa7",
          "\x00\xa8", "\x00\xa9", "\x00\xaa", "\x00\xab", "\x00\xac", "\xff\xfd", "\x00\xae", "\x00\xaf",
          "\x00\xb0", "\x00\xb1", "\x00\xb2", "\x00\xb3", "\x00\xb4", "\x00\xb5", "\x00\xb6", "\x00\xb7",
          "\x00\xb8", "\x00\xb9", "\x00\xba", "\x00\xbb", "\x00\xbc", "\x00\xbd", "\x00\xbe", "\x00\xbf",
          "\x00\xc0", "\x00\xc1", "\x00\xc2", "\x00\xc3", "\x00\xc4", "\x00\xc5", "\x00\xc6", "\x00\xc7",
          "\x00\xc8", "\x00\xc9", "\x00\xca", "\x00\xcb", "\x00\xcc", "\x00\xcd", "\x00\xce", "\x00\xcf",
          "\x00\xd0", "\x00\xd1", "\x00\xd2", "\x00\xd3", "\x00\xd4", "\x00\xd5", "\x00\xd6", "\x00\xd7",
          "\x00\xd8", "\x00\xd9", "\x00\xda", "\x00\xdb", "\x00\xdc", "\x00\xdd", "\x00\xde", "\x00\xdf",
          "\x00\xe0", "\x00\xe1", "\x00\xe2", "\x00\xe3", "\x00\xe4", "\x00\xe5", "\x00\xe6", "\x00\xe7",
          "\x00\xe8", "\x00\xe9", "\x00\xea", "\x00\xeb", "\x00\xec", "\x00\xed", "\x00\xee", "\x00\xef",
          "\x00\xf0", "\x00\xf1", "\x00\xf2", "\x00\xf3", "\x00\xf4", "\x00\xf5", "\x00\xf6", "\x00\xf7", 
          "\x00\xf8", "\x00\xf9", "\x00\xfa", "\x00\xfb", "\x00\xfc", "\x00\xfd", "\x00\xfe", "\x00\xff"
        ]

        def PDFDocEncoding.to_utf16be(pdfdocstr)

          utf16bestr = "#{UTF16BE::MAGIC}"
          pdfdocstr.each_byte do |byte|
            utf16bestr << CHARMAP[byte]
          end

          utf16bestr
        end

        def PDFDocEncoding.to_pdfdoc(str)
          str
        end

      end

      module UTF16BE

        MAGIC = "\xFE\xFF"

        def UTF16BE.to_utf16be(str)
          str
        end

        def UTF16BE.to_pdfdoc(str)
          pdfdoc = []
          i = 2

          while i < str.size
            char = PDFDocEncoding::CHARMAP.index(str[i,2])
            raise EncodingError, "Can't convert UTF16-BE character to PDFDocEncoding" if char.nil?
            pdfdoc << char
            i = i + 2
          end

          pdfdoc.pack("C*")
        end

      end

    end

    include Origami::Object

    attr_accessor :encoding
    
    def real_type ; Origami::String end

    def initialize(str) #:nodoc:
      infer_encoding  
      super(str)
    end

    #
    # Convert String object to an UTF8 encoded Ruby string.
    #
    def to_utf8
      require 'iconv'

      infer_encoding
      i = Iconv.new("UTF-8", "UTF16")
        utf8str = i.iconv(self.encoding.to_utf16be(self.value))
      i.close

      utf8str
    end

    #
    # Convert String object to an UTF16-BE encoded Ruby string.
    #
    def to_utf16be
      infer_encoding
      self.encoding.to_utf16be(self.value)
    end

    #
    # Convert String object to a PDFDocEncoding encoded Ruby string.
    #
    def to_pdfdoc
      infer_encoding
      self.encoding.to_pdfdoc(self.value)
    end

    def infer_encoding #:nodoc:
      @encoding = 
      if self.value[0,2] == Encoding::UTF16BE::MAGIC
        Encoding::UTF16BE
      else
        Encoding::PDFDocEncoding
      end
    end
  end

  class InvalidHexaStringObjectError < InvalidObjectError #:nodoc:
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
    def initialize(str = "")
      
      unless str.is_a?(::String)
        raise TypeError, "Expected type String, received #{str.class}."
      end
      
      super(str)
    end
    
    def self.parse(stream) #:nodoc:
        
      if stream.skip(@@regexp_open).nil?
        raise InvalidHexaStringObjectError, "Hexadecimal string shall start with a '#{TOKENS.first}' token"
      end
        
      hexa = stream.scan_until(@@regexp_close)
      if hexa.nil?
        raise InvalidHexaStringObjectError, "Hexadecimal string shall end with a '#{TOKENS.last}' token"
      end

      decoded = Filter::ASCIIHex.decode(hexa.chomp!(TOKENS.last))
        
      HexaString.new(decoded)
    end
    
    def to_s #:nodoc:
      super(TOKENS.first + Filter::ASCIIHex.encode(value) + TOKENS.last)
    end

    #
    # Converts self to ByteString
    #
    def to_raw
      ByteString.new(self.value)
    end

    def value
      self.decrypt! if self.is_a?(Encryption::EncryptedString) and not @decrypted

      to_str
    end
  end
 
  class InvalidByteStringObjectError < InvalidObjectError #:nodoc:
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
    def initialize(str = "")
      
      unless str.is_a?(::String)
        raise TypeError, "Expected type String, received #{str.class}."
      end
      
      super(str)
    end

    def self.parse(stream) #:nodoc:
      
      if not stream.skip(@@regexp_open)
        raise InvalidByteStringObjectError, "No literal string start token found"
      end
      
      result = ""
      depth = 0
      while depth != 0 or stream.peek(1) != TOKENS.last do

        if stream.eos?
          raise InvalidByteStringObjectError, "Non-terminated string"
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
        raise InvalidByteStringObjectError, "Byte string shall be terminated with '#{TOKENS.last}'"
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
      super(TOKENS.first + self.expand + TOKENS.last)
    end

    #
    # Converts self to HexaString
    #
    def to_hex
      HexaString.new(self.value)
    end
    
    def value
      self.decrypt! if self.is_a?(Encryption::EncryptedString) and not @decrypted

      to_str
    end
  end

  #
  # Class representing a Date string.
  # _Not used_
  # _Not tested_
  #
  class Date < ByteString #:nodoc:

    REGEXP_TOKEN = "(D:)?(\\d{4})(\\d{2})?(\\d{2})?(\\d{2})?(\\d{2})?(\\d{2})?(?:([\\+-Z])(?:(\\d{2})')?(?:(\\d{2})')?)?"
    
    def initialize(year, month = nil, day = nil, hour = nil, minute = nil, second = nil, ut_sign = nil, ut_hours = nil, ut_min = nil)

      year_str = '%04d' % year
      month_str = month.nil? ? '01' : '%02d' % month
      day_str = day.nil? ? '01' : '%02d' % day 
      hour_str = '%02d' % hour
      minute_str = '%02d' % minute
      second_str = '%02d' % second
      
      date_str = "D:#{year_str}#{month_str}#{day_str}#{hour_str}#{minute_str}#{second_str}"
      date_str << "#{ut_sign}#{'%02d' % ut_hours}'#{'%02d' % ut_min}" unless ut_sign.nil?

      super(date_str)
    end
    
    def self.parse(stream) #:nodoc:
      
      dateReg = Regexp.new('\A' + REGEXP_TOKEN)
      
      raise InvalidDate if stream.scan(dateReg).nil?
        
      year  = stream[2].to_i
      month = stream[3] and stream[3].to_i
      day   = stream[4] and stream[4].to_i
      hour  = stream[5] and stream[5].to_i
      min   = stream[6] and stream[6].to_i
      sec   = stream[7] and stream[7].to_i
      ut_sign   = stream[8]
      ut_hours  = stream[9] and stream[9].to_i
      ut_min    = stream[10] and stream[10].to_i
        
      Origami::Date.new(year, month, day, hour, min, sec, ut_sign, ut_hours, ut_min)
    end
    
    #
    # Returns current Date String in UTC time.
    #
    def self.now
      now = Time.now.getutc
      year  = now.strftime("%Y").to_i
      month = now.strftime("%m").to_i
      day   = now.strftime("%d").to_i
      hour  = now.strftime("%H").to_i
      min   = now.strftime("%M").to_i
      sec   = now.strftime("%S").to_i

      Origami::Date.new(year, month, day, hour, min, sec, 'Z', 0, 0)
    end
    
  end

end
