=begin

= File
	graphics.rb

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

  module Graphics

    #
    # Generic Graphic state
    # 4.3.4 Graphics State Parameter Dictionaries p219
    #
    class  ExtGState < Dictionary
      
      include Configurable

      field   :Type,          :Type => Name, :Default => :ExtGState, :Required => true
      field   :LW,            :Type => Integer, :Version => "1.3"
      field   :LC,            :Type => Integer, :Version => "1.3"
      field   :LJ,            :Type => Integer, :Version => "1.3"
      field   :ML,            :Type => Number, :Version => "1.3"
      field   :D,             :Type => Array, :Version => "1.3"
      field   :RI,            :Type => Name, :Version => "1.3"
      field   :OP,            :Type => Boolean
      field   :op,            :Type => Boolean, :Version => "1.3"
      field   :OPM,           :Type => Number, :Version => "1.3"
      field   :Font,          :Type => Array, :Version => "1.3"
      field   :BG,            :Type => Object
      field   :BG2,           :Type => Object, :Version => "1.3"
      field   :UCR,           :Type => Object
      field   :UCR2,          :Type => Object, :Version => "1.3"
      field   :TR,            :Type => Object
      field   :TR2,           :Type => Object, :Version => "1.3" 
      field   :HT,            :Type => [ Dictionary, Name, Stream ]
      field   :FL,            :Type => Number, :Version => "1.3"
      field   :SM,            :Type => Number, :Version => "1.3"
      field   :SA,            :Type => Boolean
      field   :BM,            :Type => [ Name, Array ], :Version => "1.4"
      field   :SMask,         :Type => [ Dictionary, Array ], :Version => "1.4"
      field   :CA,            :Type => Number
      field   :ca,            :Type => Number, :Version => "1.4"
      field   :AIS,           :Type => Boolean, :Version => "1.4"
      field   :TK,            :Type => Boolean, :Version => "1.4"

    end # class ExtGState
    
    class XObject < Stream

      field   :Type,          :Type => Name, :Default => :XObject
      field   :Subtype,       :Type => Name, :Default => :Form, :Required => true
      field   :FormType,      :Type => Integer, :Default => 1
      field   :Resources,     :Type => Dictionary, :Default => Resources.new
      field   :BBox,          :Type => Array, :Required => true
      field   :Matrix,        :Type => Array, :Default => [ 1 , 0 , 0 , 1 , 0 , 0 ]

    end

  end #module Graphics 

end
