=begin

= File
	file.rb

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

  class PDF

    #
    # Attachs an embedded file to the PDF.
    # _path_:: The path to the file to attach.
    # _options_:: A set of options to configure the attachment. 
    #
    def attach_file(path, options = {})

      #
      # Default options.
      #
      params = 
      {
        :Register => true,                      # Shall the file be registered in the name directory ?
        :EmbeddedName => File.basename(path),   # The inner filename of the attachment.
        :Filter => :FlateDecode                 # The stream filter used to store data.
      }

      params.update(options)
      
      fdata = File.open(path, "r").binmode.read
      
      fstream = EmbeddedFileStream.new
      fstream.data = fdata
      fstream.setFilter(params[:Filter])
      
      name = params[:EmbeddedName]
      fspec = FileSpec.new.setType(:Filespec).setF(name).setEF(FileSpec.new(:F => fstream))
      
      register(Names::Root::EMBEDDEDFILES, name, fspec) if params[:Register] == true

      fspec
    end
 
  end

  #
  # Class used to convert system-dependent pathes into PDF pathes.
  # PDF path specification offers a single form for representing file pathes over operating systems.
  #
  class Filename
    
    class << self
      
      #
      # Converts UNIX file path into PDF file path.
      #
      def Unix(file)
        ByteString.new(file)
      end
      
      #
      # Converts MacOS file path into PDF file path.
      #
      def Mac(file)
        ByteString.new("/" + file.gsub(":", "/"))
      end
      
      #
      # Converts Windows file path into PDF file path.
      #
      def DOS(file)
        path = ""
        # Absolute vs relative path
        if file.include? ":"
          path << "/"
          file.sub!(":","")
        end
        
        file.gsub!("\\", "/")
        ByteString.new(path + file)
      end
      
    end
    
  end
  
  
  #
  # Class representing  a file specification.
  # File specifications can be used to reference external files, as well as embedded files and URIs.
  #
  class FileSpec < Dictionary
    
    include Configurable
   
    field   :Type,          :Type => Name, :Default => :FileSpec
    field   :FS,            :Type => Name, :Default => :URL
    field   :F,             :Type => [ ByteString, Stream ]
    field   :UF,            :Type => String
    field   :DOS,           :Type => ByteString
    field   :Mac,           :Type => ByteString
    field   :Unix,          :Type => ByteString
    field   :ID,            :Type => Array
    field   :V,             :Type => Boolean, :Default => false, :Version => "1.2"
    field   :EF,            :Type => Dictionary, :Version => "1.3"
    field   :RF,            :Type => Dictionary, :Version => "1.3"
    field   :Desc,          :Type => ByteString, :Version => "1.6"
    field   :CI,            :Type => Dictionary, :Version => "1.7"

  end
    
    #
    # Class representing a Uniform Resource Locator (URL)
    #
    class URL < FileSpec
    
      field   :Type,        :Type => Name, :Default => :URL, :Required => true

      def initialize(url)
        super(:F => url)
      end
    end
    
    #
    # A class representing a file outside the current PDF file.
    #
    class ExternalFile < FileSpec
     
      field   :Type,        :Type => Name, :Default => :FileSpec, :Required => true

      #
      # Creates a new external file specification.
      # _dos_:: The Windows path to this file.
      # _mac_:: The MacOS path to this file.
      # _unix_:: The UNIX path to this file.
      #
      def initialize(dos, mac = "", unix = "")
        
        if not mac.empty? or not unix.empty?
          super(:DOS => Filename.DOS(dos), :Mac => Filename.Mac(mac), :Unix => Filename.Unix(unix))
        else
         super(:F => dos)
        end
        
      end

    end
    
    #
    # Class representing the data of an embedded file.
    #
    class EmbeddedFileStream < Stream
     
      include Configurable
      
      field   :Type,          :Type => Name, :Default => :EmbeddedFile
      field   :Subtype,       :Type => Name
      field   :Params,        :Type => Dictionary
      
    end
    
    #
    # Class representing parameters for a EmbeddedFileStream.
    #
    class EmbeddedFileParameters < Dictionary
      
      include Configurable
      
      field   :Size,          :Type => Integer
      field   :CreationDate,  :Type => ByteString
      field   :ModDate,       :Type => ByteString
      field   :Mac,           :Type => Dictionary
      field   :Checksum,      :Type => String
     
    end

end
