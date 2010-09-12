=begin

= File
	webcapture.rb

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

module Origami
  
  module Webcapture
  
    class SpiderInfo < Dictionary
      
      include Configurable

      field   :V,         :Type => Real, :Default => 1.0, :Version => "1.3", :Required => true
      field   :C,         :Type => Array
    
    end
    
    class Command < Dictionary
      
      module Flags
        SAMESITE = 1 << 1
        SAMEPATH = 1 << 2
        SUBMIT = 1 << 3
      end

      include Configurable

      field   :URL,       :Type => String, :Required => true
      field   :L,         :Type => Integer, :Default => 1
      field   :F,         :Type => Integer, :Default => 0
      field   :P,         :Type => [ String, Stream ]
      field   :CT,        :Type => String, :Default => "application/x-www-form-urlencoded"
      field   :H,         :Type => String
      field   :S,         :Type => Dictionary
        
    end
      
      class CommandSettings < Dictionary
        
        include Configurable
   
        field   :G,       :Type => Dictionary
        field   :C,       :Type => Dictionary
        
      end

      class SourceInformation < Dictionary

        include Configurable
        
        module SubmissionType
          NOFORM   = 0
          GETFORM  = 1
          POSTFORM = 2
        end

        field   :AU,      :Type => [ String, Dictionary ], :Required => true
        field   :TS,      :Type => String
        field   :E,       :Type => String
        field   :S,       :Type => Integer, :Default => 0
        field   :C,       :Type => Dictionary
        
      end
   
  end

end



