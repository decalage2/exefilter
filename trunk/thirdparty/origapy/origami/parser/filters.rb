=begin

= File
	filters.rb

= Info
	This file is part of Origami, PDF manipulation framework for Ruby
	Copyright (C) 2009	Guillaume Delugré <guillaume@security-labs.org>
	All right reserved.
	
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

require 'zlib'

module Origami

  #
  # Filters are algorithms used to encode data into a PDF Stream.
  #
  module Filter

    class PredictorError < Exception #:nodoc:
    end
    
    module Predictor
      
      NONE = 1
      TIFF = 2
      PNG_NONE = 10
      PNG_SUB = 11
      PNG_UP = 12
      PNG_AVERAGE = 13
      PNG_PAETH = 14
      PNG_OPTIMUM = 15

      def self.do_pre_prediction(data, predictor = NONE, colors = 1, bpc = 8, columns = 1)
      
        return data if predictor == NONE

        unless (1..4) === colors.to_i
          raise PredictorError, "Colors must be between 1 and 4"
        end

        unless [1,2,4,8,16].include?(bpc.to_i)
          raise PredictorError, "BitsPerComponent must be in 1, 2, 4, 8 or 16"
        end

        # components per line
        nvals = columns * colors

        # bytes per pixel
        bpp = (colors * bpc + 7) >> 3

        # bytes per row
        bpr = (nvals * bpc + 7) >> 3

        unless data.size % bpr == 0
          raise PredictorError, "Invalid data size"
        end

        if predictor == TIFF
          raise PredictorError, "TIFF prediction not yet supported"
        elsif predictor >= 10 # PNG
          do_png_pre_prediction(data, predictor, bpp, bpr)
        else
          raise PredictorError, "Unknown predictor"
        end
     end

      def self.do_post_prediction(data, predictor = NONE, colors = 1, bpc = 8, columns = 1)

        return data if predictor == NONE

        unless (1..4) === colors
          raise PredictorError, "Colors must be between 1 and 4"
        end

        unless [1,2,4,8,16].include?(bpc)
          raise PredictorError, "BitsPerComponent must be in 1, 2, 4, 8 or 16"
        end

        # components per line
        nvals = columns * colors

        # bytes per pixel
        bpp = (colors * bpc + 7) >> 3

        # bytes per row
        bpr = ((nvals * bpc + 7) >> 3) + bpp

        unless data.size % bpr == 0
          raise PredictorError, "Invalid data size"
        end

        if predictor == TIFF
          raise PredictorError, "TIFF prediction not yet supported"
        elsif predictor >= 10 # PNG
          do_png_post_prediction(data, bpp, bpr)
        else
          raise PredictorError, "Unknown predictor"
        end
      end

      def self.do_png_post_prediction(data, bpp, bpr)

        result = ""
        uprow = thisrow = "\0" * bpr
        ncols = data.size / bpr
        
        ncols.times do |col|

          line = data[col * bpr, bpr]
          predictor = 10 + line[0]

          for i in (bpp..bpr-1)

            up = uprow[i]
            left = thisrow[i-bpp]
            upleft = uprow[i-bpp]

            case predictor
              when PNG_NONE
                thisrow = line 
              when PNG_SUB
                thisrow[i] = ((line[i] + left) & 0xFF).chr
              when PNG_UP
                thisrow[i] = ((line[i] + up) & 0xFF).chr
              when PNG_AVERAGE
                thisrow[i] = ((line[i] + ((left + up) / 2)) & 0xFF).chr
              when PNG_PAETH
                p = left + up - upleft
                pa, pb, pc = (p - left).abs, (p - up).abs, (p - upleft).abs

                thisrow[i] = ((line[i] + 
                case [ pa, pb, pc ].min
                  when pa then left
                  when pb then up
                  when pc then upleft
                end
                ) & 0xFF).chr
            else
              puts "Unknown PNG predictor : #{predictor}"
              thisrow = line
            end
            
          end

          result << thisrow[bpp..-1]
          uprow = thisrow
        end
  
        result
      end

      def self.do_png_pre_prediction(data, predictor, bpp, bpr)
        
        result = ""
        ncols = data.size / bpr

        line = "\0" * bpp + data[-bpr, bpr]
        
        (ncols-1).downto(0) do |col|

          uprow = col.zero? ? ("\0" * (bpr+bpp)) : ("\0" * bpp + data[(col-1)*bpr,bpr])
          (bpr+bpp-1).downto(bpp) do |i|

            up = uprow[i]
            left = line[i-bpp]
            upleft = uprow[i-bpp]

            case predictor
              when PNG_SUB
                line[i] = ((line[i] - left) & 0xFF).chr
              when PNG_UP
                line[i] = ((line[i] - up) & 0xFF).chr
              when PNG_AVERAGE
                line[i] = ((line[i] - ((left + up) / 2)) & 0xFF).chr
              when PNG_PAETH
                p = left + up - upleft
                pa, pb, pc = (p - left).abs, (p - up).abs, (p - upleft).abs

                line[i] = ((line[i] - 
                case [ pa, pb, pc ].min
                  when pa then left
                  when pb then up
                  when pc then upleft
                end
                ) & 0xFF).chr
              when PNG_NONE
            else
              puts "Unknown PNG predictor : #{predictor}"
            end
            
          end
          
          line[0] = (predictor - 10).chr
          result = line + result
          
          line = uprow
        end
  
        result
      end

    end
    
    module ClassMethods
      #
      # Decodes the given data.
      # _stream_:: The data to decode.
      #
      def decode(stream, params = {})
        self.new(params).decode(stream)
      end
      
      #
      # Encodes the given data.
      # _stream_:: The data to encode.
      #
      def encode(stream, params = {})
        self.new(params).encode(stream)
      end
    end

    def initialize(parameters= nil)
      @params = parameters
    end
    
    def self.included(receiver)
      receiver.extend(ClassMethods)
    end
  
    class InvalidASCIIHexString < Exception #:nodoc:
    end
    
    #
    # Class representing a filter used to encode and decode data written into hexadecimal.
    #
    class ASCIIHex
      
      include Filter
      
      EOD = ">"  #:nodoc:
      
      #
      # Encodes given data into upcase hexadecimal representation.
      # _stream_:: The data to encode.
      #
      def encode(stream)
        stream.unpack("H2" * stream.size).join.upcase
      end
      
      #
      # Decodes given data writen into upcase hexadecimal representation.
      # _string_:: The data to decode.
      #
      def decode(string)
        
        input = string.include?(?>) ? string[0..string.index(?>) - 1] : string
        
        digits = input.delete(" \f\t\r\n\0").split(//)
        
        if not digits.all? { |d| d =~ /[a-fA-F0-9>]/ }
          raise InvalidASCIIHexString, input
        end
        
        digits << "0" unless digits.size % 2 == 0
        
        bytes = []
        for i in 0..digits.size/2-1 do bytes << digits[2*i].to_s + digits[2*i+1].to_s end
        
        bytes.pack("H2" * (digits.size / 2))
      end
      
    end
    
    class InvalidASCII85String < Exception #:nodoc:
    end
    
    #
    # Class representing a filter used to encode and decode data written in base85 encoding.
    #
    class ASCII85
      
      include Filter
      
      EOD = "~>" #:nodoc:
      
      #
      # Encodes given data into base85.
      # _stream_:: The data to encode.
      #
      def encode(stream)
        
        i = 0
        code = ""
        input = stream.dup
        
        while i < input.size do
          
          if input.length - i < 4
            addend = 4 - (input.length - i)
            input << "\0" * addend
          else
            addend = 0
          end
          
          inblock = (input[i] * 256**3 + input[i+1] * 256**2 + input[i+2] * 256 + input[i+3])
          outblock = ""
          
          5.times do |p|
            c = inblock / 85 ** (4 - p)
            outblock << (?! + c).chr
            
            inblock -= c * 85 ** (4 - p)
          end
          
          if outblock == "!!!!!" and addend == 0 then outblock = "z" end
          
          if addend != 0
            outblock = outblock[0,(4 - addend) + 1]
          end
          
          code << outblock
          
          i = i + 4
        end

        code
      end
      
      #
      # Decodes the given data encoded in base85.
      # _string_:: The data to decode.
      #
      def decode(string)
        
        input = (string.include?(EOD) ? string[0..string.index(EOD) - 1] : string).delete(" \f\t\r\n\0")
        
        i = 0
        result = ""
        while i < input.size do
          
          if input.length - i < 5
          then
            if input.length - i == 1 then raise InvalidASCII85String, "Invalid length" end
            
            addend = 5 - (input.length - i)
            input << "u" * addend
          else
            addend = 0
          end
          
          if input[i] == ?z
            inblock = 0
          else
            
            inblock = 0
            outblock = ""
            
            # Checking if this string is in base85
            5.times { |j|
              if input[i+j] > ?u or input[i+j] < ?!
                raise InvalidASCII85String, string
              else
                inblock += (input[i+j] - ?!) * 85 ** (4 - j)
              end
            }
          
            if inblock > 2**32 - 1
              raise InvalidASCII85String, "Invalid value"
            end
          
          end
        
          4.times do |p|
            c = inblock / 256 ** (3 - p)
            outblock << c.chr
            
            inblock -= c * 256 ** (3 - p)
          end
          
          if addend != 0
            outblock = outblock[0, 4 - addend]
          end
        
          result << outblock
          
          i = i + 5
        end
        
        result
      end
      
    end
    
    class InvalidLZWData < Exception #:nodoc:
    end
    
    #
    # Class representing a filter used to encode and decode data with LZW compression algorithm.
    #
    class LZW
      
      include Filter

      class DecodeParms < Dictionary

        include Configurable

        field   :Predictor,         :Type => Integer, :Default => 1
        field   :Colors,            :Type => Integer, :Default => 1
        field   :BitsPerComponent,  :Type => Integer, :Default => 8
        field   :Columns,           :Type => Integer, :Default => 1
        field   :EarlyChange,       :Type => Integer, :Default => 1

      end
 
      EOD = 257 #:nodoc:
      CLEARTABLE = 256 #:nodoc:
      
      #
      # Creates a new LZW Filter.
      # _parameters_:: A hash of filter options (ignored).
      #
      def initialize(parameters = DecodeParms.new)
        super(parameters)
      end
      
      #
      # Encodes given data using LZW compression method.
      # _stream_:: The data to encode.
      #
      def encode(string)
  
        if not @params[:Predictor].nil?
          colors =  @params.has_key?(:Colors) ? @params[:Colors].to_i : 1
          bpc =     @params.has_key?(:BitsPerComponent) ? @params[:BitsPerComponent].to_i : 8
          columns = @params.has_key?(:Columns) ? @params[:Columns].to_i : 1

          string = Predictor.do_pre_prediction(string, @params[:Predictor].to_i, colors, bpc, columns)
        end       
        
        codesize = 9
        result = byte2binary(CLEARTABLE)
        table = clear({})
        
        s = ''        
        string.each_byte do |byte|
          char = byte.chr
          
          case table.size
          when 512 then codesize = 10
          when 1024 then codesize = 11
          when 2048 then codesize = 12
          when 4096
            codesize = 9
            result << byte2binary(CLEARTABLE,codesize)
            clear table
            redo
          end
         
          it = s + char
          if table.has_key?(it)
            s = it
          else
            result << byte2binary(table[s], codesize)
            table[it] = table.size
            s = char
          end
        end
         
        result << byte2binary(table[s], codesize)
        result << byte2binary(EOD,codesize)
        
        binary2string(result)
      end
      
      #
      # Decodes given data using LZW compression method.
      # _stream_:: The data to decode.
      #
      def decode(string)
       
        result = ""
        bstring = string2binary(string)
        codesize = 9
        table = clear({})
        prevbyte = nil

        until bstring.empty? do
          
          byte = binary2byte(bstring, codesize)

          case table.size
          when 510 then codesize = 10
          when 1022 then codesize = 11
          when 2046 then codesize = 12
          when 4094
            if byte != CLEARTABLE
            then
              raise InvalidLZWData, "LZW table is full and no clear flag was set"
            end
          end

          if byte == CLEARTABLE
            codesize = 9
            code = EOD
            clear table
            prevbyte = nil
            redo
          elsif byte == EOD
            break
          else
            if prevbyte.nil?
              prevbyte = byte
              result << table.index(byte)
              redo
            else
              if table.has_value?(byte)
                entry = table.index(byte)
              else
                entry = table.index(prevbyte)
                entry += entry[0,1]
              end

              result << entry
              table[table.index(prevbyte) + entry[0,1]] = table.size
              prevbyte = byte
            end
          end
        end
 
        if not @params[:Predictor].nil?
          colors =  @params.has_key?(:Colors) ? @params[:Colors].to_i : 1
          bpc =     @params.has_key?(:BitsPerComponent) ? @params[:BitsPerComponent].to_i : 8
          columns = @params.has_key?(:Columns) ? @params[:Columns].to_i : 1

          result = Predictor.do_post_prediction(result, @params[:Predictor].to_i, colors, bpc, columns)
        end

        result
      end
      
      private

      def binary2string(bin)
        bin << "0" * (bin.size % 8)
        [bin].pack("B*")
      end

      def string2binary(string)
        string.unpack("B*")[0]
      end

      def byte2binary(byte, output_size = 9)
        s = byte.to_s(2)
        ("0" * (output_size - s.size)) + s
      end

      def binary2byte(bstring, codesize)
        if bstring.size < codesize
          raise InvalidLZWData, "Unterminated data"
        end

        bstring.slice!(0,codesize).to_i(2)
      end
      
      def clear(table) #:nodoc:
        table.clear
        256.times { |i|
          table[i.chr] = i
        }
        
        table[CLEARTABLE] = CLEARTABLE
        table[EOD] = EOD
        
        table
      end
      
    end
    
    #
    # Class representing a Filter used to encode and decode data with zlib/Flate compression algorithm.
    #
    class Flate
      
      include Filter
      
      EOD = 257 #:nodoc:
 
      class DecodeParms < Dictionary

        include Configurable

        field   :Predictor,         :Type => Integer, :Default => 1
        field   :Colors,            :Type => Integer, :Default => 1
        field   :BitsPerComponent,  :Type => Integer, :Default => 8
        field   :Columns,           :Type => Integer, :Default => 1

      end
      
      #
      # Create a new Flate Filter.
      # _parameters_:: A hash of filter options (ignored).
      #
      def initialize(parameters = DecodeParms.new)
        super(parameters)
      end
      
      #
      # Encodes data using zlib/Deflate compression method.
      # _stream_:: The data to encode.
      #
      def encode(stream)

        if not @params[:Predictor].nil?
          colors =  @params.has_key?(:Colors) ? @params[:Colors].to_i : 1
          bpc =     @params.has_key?(:BitsPerComponent) ? @params[:BitsPerComponent].to_i : 8
          columns = @params.has_key?(:Columns) ? @params[:Columns].to_i : 1

          stream = Predictor.do_pre_prediction(stream, @params[:Predictor].to_i, colors, bpc, columns)
        end

        Zlib::Deflate.deflate(stream, Zlib::BEST_COMPRESSION)
      end
      
      #
      # Decodes data using zlib/Inflate decompression method.
      # _stream_:: The data to decode.
      #
      def decode(stream)
        
        uncompressed = Zlib::Inflate.inflate(stream)
        
        if not @params[:Predictor].nil?
          colors =  @params.has_key?(:Colors) ? @params[:Colors].to_i : 1
          bpc =     @params.has_key?(:BitsPerComponent) ? @params[:BitsPerComponent].to_i : 8
          columns = @params.has_key?(:Columns) ? @params[:Columns].to_i : 1

          uncompressed = Predictor.do_post_prediction(uncompressed, @params[:Predictor].to_i, colors, bpc, columns)
        end

        uncompressed
      end
      
    end
    
    class InvalidRunLengthData < Exception #:nodoc:
    end
    
    #
    # Class representing a Filter used to encode and decode data using RLE compression algorithm.
    #
    class RunLength
      
      include Filter
      
      EOD = 128 #:nodoc:
      
      #
      # Encodes data using RLE compression method.
      # _stream_:: The data to encode.
      #
      def encode(stream)

        result = ""
        i = 0

        while i < stream.size
          
          #
          # How many identical bytes coming?
          #
          length = 1
          while i+1 < stream.size and length < EOD and stream[i] == stream[i+1]
            length = length + 1
            i = i + 1
          end

          #
          # If more than 1, then compress them.
          #
          if length > 1
            result << (257 - length).chr << stream[i,1]

          #
          # Otherwise how many different bytes to copy ?
          #
          else
            j = i
            while j+1 < stream.size and (j - i + 1) < EOD and stream[j] != stream[j+1]
              j = j + 1
            end

            length = j - i
            result << length.chr << stream[i, length+1]

            i = j
          end

          i = i + 1
        end

        result << EOD
      end


      #
      # Decodes data using RLE decompression method.
      # _stream_:: The data to decode.
      #
      def decode(stream)
        
        i = 0
        result = ""
        
        if not stream.include?(EOD) then raise InvalidRunLengthData, "No end marker" end
        
        until stream[i] == EOD do
        
          length = stream[i]
          if length < EOD
            result << stream[i + 1, length + 1]
            i = i + length + 2
          else
            result << stream[i + 1,1] * (257 - length)
            i = i + 2
          end
          
        end
        
        result
      end

    end
    
    #
    # Class representing  a Filter used to encode and decode data with CCITT-facsimile compression algorithm.
    #
    class CCITTFax
      
      include Filter
      
      class DecodeParms < Dictionary

        include Configurable

        field   :K,           :Type => Integer, :Default => 0
        field   :EndOfLine,   :Type => Boolean, :Default => false
        field   :EncodedByteAlign,  :Type => Boolean, :Default => false
        field   :Columns,     :Type => Integer, :Default => 1728
        field   :Rows,        :Type => Integer, :Default => 0
        field   :EndOfBlock,  :Type => Boolean, :Default => true
        field   :BlackIs1,    :Type => Boolean, :Default => false
        field   :DamagedRowsBeforeError,  :Type => :Integer, :Default => 0

      end

      #
      # Creates a new CCITT Fax Filter.
      #
      def initialize(parameters = DecodeParms.new)
        super(parameters)  
      end
      
      #
      # Not supported.
      #
      def encode(stream)
        raise NotImplementedError, "#{self.class} is not (yet?) supported"
      end
      
      #
      # Not supported.
      #
      def decode(stream)
        puts "#{self.class} : Not yet supported"
        nil
      end
      
    end
    
    #
    # Class representing a Filter used to encode and decode data with JBIG2 compression algorithm.
    #
    class JBIG2
      
      include Filter
     
      class DecodeParms < Dictionary
        
        include Configurable

        field   :JBIG2Globals,    :Type => Stream

      end

      def initialize(parameters = DecodeParms.new)
        super(parameters)
      end

      #
      # Not supported.
      #
      def encode(stream)
        raise NotImplementedError, "#{self.class} is not (yet?) supported"
      end
      
      #
      # Not supported.
      #
      def decode(stream)
        puts "#{self.class} : Not yet supported"
        nil
      end
      
    end
    
    #
    # Class representing a Filter used to encode and decode data with DCT (JPEG) compression algorithm.
    #
    class DCT
      
      include Filter
      
      class DecodeParms < Dictionary

        include Configurable

        field   :ColorTransform,    :Type => Integer

      end

      def initialize(parameters = DecodeParms.new)
        super(parameters)
      end

      #
      # Not supported.
      #
      def encode(stream)
        raise NotImplementedError, "#{self.class} is not (yet?) supported"
      end
      
      #
      # Not supported.
      #
      def decode(stream)
        puts "#{self.class} : Not yet supported"
        nil
      end
      
    end
    
    #
    # Class representing a Filter used to encode and decode data with JPX compression algorithm.
    #
    class JPX
      
      include Filter
      
      #
      # Not supported.
      #
      def encode(stream)
        raise NotImplementedError, "#{self.class} is not (yet?) supported"
      end
      
      #
      # Not supported.
      #
      def decode(stream)
        puts "#{self.class} : Not yet supported"
        nil
      end
      
    end
    
  end

end
