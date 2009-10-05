=begin

= File
	misc.rb

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
  # Class representing the ViewerPreferences Dictionary of a PDF.
  # This dictionary modifies the way the UI looks when the file is opened in a viewer.
  #
  class ViewerPreferences < Dictionary
    
    include Configurable

    field   :HideToolbar,             :Type => Boolean, :Default => false
    field   :HideMenubar,             :Type => Boolean, :Default => false
    field   :HideWindowUI,            :Type => Boolean, :Default => false
    field   :FitWindow,               :Type => Boolean, :Default => false
    field   :CenterWindow,            :Type => Boolean, :Default => false
    field   :DisplayDocTitle,         :Type => Boolean, :Default => false, :Version => "1.4"
    field   :NonFullScreenPageMode,   :Type => Name, :Default => :UseNone
    field   :Direction,               :Type => Name, :Default => :L2R
    field   :ViewArea,                :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :ViewClip,                :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :PrintArea,               :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :PrintClip,               :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :PrintScaling,            :Type => Name, :Default => :AppDefault, :Version => "1.6"
    field   :Duplex,                  :Type => Name, :Default => :Simplex, :Version => "1.7"
    field   :PickTrayByPDFSize,       :Type => Boolean, :Version => "1.7"
    field   :PrintPageRange,          :Type => Array, :Version => "1.7"
    field   :NumCopies,               :Type => Integer, :Version => "1.7"
    
  end
  
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
 
  #
  # Class representing a location on a page or a bounding box.
  #
  class Rectangle < Array
    
    class << self
      
      def [](coords)
        corners = coords.values_at(:llx, :lly, :urx, :ury)
        
        unless corners.all? { |corner| corner.is_a?(Numeric) }
          raise TypeError, "All coords must be numbers"
        end
        
        Rectangle.new(*corners)
      end
      
    end
    
    def initialize(lowerleftx, lowerlefty, upperrightx, upperrighty, indirect = false)
      
      super([ lowerleftx, lowerlefty, upperrightx, upperrighty ], indirect)
      
    end
    
  end

end
