=begin

= File
	font.rb

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

module Origami

  #
  # Class representing a rendering font in a document.
  #
  class Font < Dictionary
    
    include Configurable
   
    field   :Type,                    :Type => Name, :Default => :Font, :Required => true
    field   :Subtype,                 :Type => Name, :Default => :Type1, :Required => true
    field   :Name,                    :Type => Name
    field   :BaseFont,                :Type => Name, :Default => :Helvetica, :Required => true
    field   :FirstChar,               :Type => Integer
    field   :LastChar,                :Type => Integer
    field   :Widths,                  :Type => Array
    field   :FontDescriptor,          :Type => Dictionary
    field   :Encoding,                :Type => [ Name, Dictionary ], :Default => :MacRomanEncoding
    field   :ToUnicode,               :Type => Stream, :Version => "1.2"
   
    #
    # Type1 Fonts.
    #
    class Type1 < Font

      #
      # 14 standard Type1 fonts.
      #
      module Standard
        
        class TimesRoman < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Times-Roman", :Required => true
        end

        class Helvetica < Type1
          field   :BaseFont,          :Type => Name, :Default => :Helvetica, :Required => true
        end

        class Courier < Type1
          field   :BaseFont,          :Type => Name, :Default => :Courier, :Required => true
        end

        class Symbol < Type1
          field   :BaseFont,          :Type => Name, :Default => :Symbol, :Required => true
        end

        class TimesBold < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Times-Bold", :Required => true
        end

        class HelveticaBold < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Helvetica-Bold", :Required => true
        end

        class CourierBold < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Courier-Bold", :Required => true
        end

        class ZapfDingbats < Type1
          field   :BaseFont,          :Type => Name, :Default => :ZapfDingbats, :Required => true
        end

        class TimesItalic < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Times-Italic", :Required => true
        end

        class HelveticaOblique < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Helvetica-Oblique", :Required => true
        end

        class CourierOblique < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Courier-Oblique", :Required => true
        end

        class TimesBoldItalic < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Times-BoldItalic", :Required => true
        end

        class HelveticaBoldOblique < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Helvetica-BoldOblique", :Required => true
        end

        class CourierBoldOblique < Type1
          field   :BaseFont,          :Type => Name, :Default => :"Courier-BoldOblique", :Required => true
        end

      end
      
      field   :SubType,               :Type => Name, :Default => :Type1, :Required => true

    end

  end
  
  #
  # Class representing a font details in a document.
  #
  class FontDescriptor < Dictionary
    
    include Configurable
    
    FIXEDPITCH = 1 << 1
    SERIF = 1 << 2
    SYMBOLIC = 1 << 3
    SCRIPT = 1 << 4
    NONSYMBOLIC = 1 << 6
    ITALIC = 1 << 7
    ALLCAP = 1 << 17
    SMALLCAP = 1 << 18
    FORCEBOLD = 1 << 19

    field   :Type,                    :Type => Name, :Default => :FontDescriptor, :Required => true
    field   :FontName,                :Type => Name, :Required => true
    field   :FontFamily,              :Type => ByteString, :Version => "1.5"
    field   :FontStretch,             :Type => Name, :Default => :Normal, :Version => "1.5"
    field   :FontWeight,              :Type => Integer, :Default => 400, :Version => "1.5"
    field   :Flags,                   :Type => Integer, :Required => true
    field   :FontBBox,                :Type => Array
    field   :ItalicAngle,             :Type => Number, :Required => true
    field   :Ascent,                  :Type => Number
    field   :Descent,                 :Type => Number
    field   :Leading,                 :Type => Number, :Default => 0
    field   :CapHeight,               :Type => Number
    field   :XHeight,                 :Type => Number, :Default => 0
    field   :StemV,                   :Type => Number
    field   :StemH,                   :Type => Number, :Default => 0
    field   :AvgWidth,                :Type => Number, :Default => 0
    field   :MaxWidth,                :Type => Number, :Default => 0
    field   :MissingWidth,            :Type => Number, :Default => 0
    field   :FontFile,                :Type => Stream
    field   :FontFile2,               :Type => Stream, :Version => "1.1"
    field   :FontFile3,               :Type => Stream, :Version => "1.2"
    field   :CharSet,                 :Type => ByteString, :Version => "1.1"
    
  end
  
  #
  # Class representing a character encoding in a document.
  #
  class Encoding < Dictionary
    
    include Configurable

    field   :Type,                    :Type => Name, :Default => :Encoding
    field   :BaseEncoding,            :Type => Name
    field   :Differences,             :Type => Array
   
  end
 
end
