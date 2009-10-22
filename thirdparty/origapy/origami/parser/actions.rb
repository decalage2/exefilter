=begin

= File
	actions.rb

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

  module Action
    
    #
    # Class representing an action to launch in a PDF.
    #
    class Action < Dictionary
      
      include Configurable

      field   :Type,    :Type => Name, :Default => :Action
      field   :S,       :Type => Name, :Required => true
      field   :Next,    :Type => [ Array, Dictionary ], :Version => "1.2"
     
    end
    
    #
    # Class representing a action going to a destination in the current document.
    #
    class GoTo < Action

      field   :S,       :Type => Name, :Default => :GoTo, :Required => true
      field   :D,       :Type => [ Array, Name, ByteString ], :Required => true

      #
      # Creates a new GoTo Action.
      # _hash_:: A hash of options to set for this jump.
      #
      def initialize(hash = {})
        
        if hash.is_a? Destination
          super(:S => :GoTo, :D => hash)
        else
          super(hash)
        end
        
      end
      
    end
    
    #
    # Class representing an action launching an URL.
    #
    class URI < Action
     
      field   :S,       :Type => Name, :Default => :URI, :Required => true
      field   :URI,     :Type => ByteString, :Required => true
      field   :IsMap,   :Type => Boolean, :Default => false

      #
      # Creates a new URI Action.
      # _uri_:: The URI to launch.
      # _ismap_::
      #
      def initialize(uri, ismap = false)
       
        super(:URI => uri, :IsMap => ismap)
        
      end
    
    end

    #
    # Class representing a JavaScript Action.
    #
    class JavaScript < Action
      
      field   :S,       :Type => Name, :Default => :JavaScript, :Required => true
      field   :JS,      :Type => [ Stream, String ], :Required => true

      #
      # Creates a new JavaScript Action.
      # _script_:: The script to be executed.
      #
      def initialize(script)
       
        super(:JS => script)
        
      end
      
    end

    #
    # Class representing an Action which run a command on the current system.
    #
    class Launch < Action
     
      field   :S,         :Type => Name, :Default => :Launch, :Required => true
      field   :F,         :Type => [ ByteString, Dictionary ]
      field   :Win,       :Type => Dictionary
      field   :Mac,       :Type => Object
      field   :Unix,      :Type => Object
      field   :NewWindow, :Type => Boolean

      #
      # Dictionary for passing parameter to Windows applications during Launch.
      #
      class WindowsLaunchParams < Dictionary
        
        include Configurable
       
        field   :F,         :Type => ByteString, :Required => true
        field   :D,         :Type => ByteString
        field   :O,         :Type => ByteString, :Default => "open"
        field   :P,         :Type => ByteString

      end
    end
    
    #
    # Class representing a Named Action.
    # Named actions are predefined GoTo actions.
    #
    class Named < Action
      
      NEXTPAGE = :NextPage
      PREVPAGE = :PrevPage
      FIRSTPAGE = :FirstPage
      LASTPAGE = :LastPage
      PRINT = :Print
   
      field   :S,         :Type => Name, :Default => :Named, :Required => true
      field   :N,         :Type => Name, :Required => true

      def initialize(type)
        super(:N => type)
      end

    end
    
    #
    # Class representing a GoTo Action to an external file.
    #
    class GoToR < Action

      field   :S,         :Type => Name, :Default => :GoToR, :Required => true
      field   :F,         :Type => [ ByteString, Dictionary ], :Required => true
      field   :D,         :Type => [ Array, Name, ByteString ], :Required => true
      field   :NewWindow, :Type => Boolean, :Version => "1.2"

      #
      # Creates a new GoTo remote Action.
      # _file_:: A FileSpec describing the file.
      # _dest_:: A Destination in the file.
      # _newwindow_:: Specifies whether the file has to be opened in a new window.
      #
      def initialize(file, dest = Destination::GlobalFit.new(0), newwindow = false)
       
        super(:F => file, :D => dest, :NewWindow => newwindow)
        
      end
      
    end
    
    #
    # Class representing a GoTo Action to an embedded pdf file.
    #
    class GoToE < Action
  
      field   :S,         :Type => Name, :Default => :GoToE, :Required => true
      field   :F,         :Type => Dictionary
      field   :D,         :Type => [ Array, Name, ByteString ], :Required => true
      field   :NewWindow, :Type => Boolean
      field   :T,         :Type => Dictionary

      def initialize(filespec, dest, newwindow = false)
       
        super(:F => filespec, :D => dest, :NewWindow => newwindow)
        
      end
      
    end
    
    #
    # A class representing a target for a GoToE to an embedded file.
    #
    class EmbeddedTarget < Dictionary
      
      include Configurable
      
      module Relationship
        PARENT = :P
        CHILD = :C
      end

      field   :R,           :Type => Name, :Required => true
      field   :N,           :Type => ByteString
      field   :P,           :Type => [ Integer, ByteString ]
      field   :A,           :Type => [ Integer, ByteString ]
      field   :T,           :Type => Dictionary
      
    end
    
    #
    # (PDF 1.2) Send data to a uniform resource locator. p703
    #
    class SubmitForm < Action
      
      module Flags
        INCLUDEEXCLUDE       = 1 << 0
        INCLUDENOVALUEFIELDS = 1 << 1
        EXPORTFORMAT         = 1 << 2
        GETMETHOD            = 1 << 3
        SUBMITCOORDINATES    = 1 << 4
        XFDF                 = 1 << 5 
        INCLUDEAPPENDSAVES   = 1 << 6
        INCLUDEANNOTATIONS   = 1 << 7
        SUBMITPDF            = 1 << 8
        CANONICALFORMAT      = 1 << 9
        EXCLNONUSERANNOTS    = 1 << 10
        EXCLFKEY             = 1 << 11
        EMBEDFORM            = 1 << 12
      end
     
      field   :S,           :Type => Name, :Default => :SubmitForm, :Required => true
      field   :F,           :Type => Dictionary
      field   :Fields,      :Type => Array
      field   :Flags,       :Type => Integer, :Default => 0

      def initialize(url, fields = [], flags = 0)
               
        if not url.is_a? FileSpec
          url = FileSpec.new(:FS => :URL, :F => url)
        end
        
        super(:F => url, :Fields => fields, :Flags => flags)
        
      end
      
    end

    class ImportData < Action

      field   :S,           :Type => Name, :Default => :ImportData, :Required => true
      field   :F,           :Type => Dictionary, :Required => true

      def initialize(file)
       
        if not file.is_a? FileSpec
          file = FileSpec.new(:FS => :File, :F => file)
        end
        
        super(:F => file)
        
      end
    
    end
    
  end

end
