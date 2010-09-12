=begin

= File
	metadata.rb

= Info
	This file is part of Origami, PDF manipulation framework for Ruby
	Copyright (C) 2010	Guillaume Delugré <guillaume@security-labs.org>
	All right reserved.
	
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

require 'rexml/document'

module Origami

  class PDF

    #
    # Returns true if the document has a document information dictionary.
    #
    def has_document_info?
      has_attr? :Info 
    end

    #
    # Returns true if the document has a catalog metadata stream.
    #
    def has_metadata?
      self.Catalog.has_key? :Metadata 
    end

    #
    # Returns the document information dictionary if present.
    #
    def get_document_info
      get_doc_attr :Info
    end

    #
    # Returns a Hash of the information found in the metadata stream
    #
    def get_metadata
      metadata_stm = self.Catalog.Metadata

      if metadata_stm.is_a?(Stream)
        doc = REXML::Document.new(metadata_stm.data)

        info = {}

        doc.elements.each('*/*/rdf:Description') do |description|
          
          description.attributes.each_attribute do |attr|
            case attr.prefix
              when 'pdf','xap','pdf'
                info[attr.name] = attr.value
            end
          end

          description.elements.each('*') do |element|
            value = (element.elements['.//rdf:li'] || element).text
            info[element.name] = value.to_s
          end

        end

        return info
      end
    end

  end

  #
  # Class representing an information Dictionary, containing title, author, date of creation and the like.
  #
  class Metadata < Dictionary
    
    include Configurable

    field   :Title,                   :Type => String, :Version => "1.1"
    field   :Author,                  :Type => String
    field   :Subject,                 :Type => String, :Version => "1.1"
    field   :Keywords,                :Type => String, :Version => "1.1"
    field   :Creator,                 :Type => String
    field   :Producer,                :Type => String
    field   :CreationDate,            :Type => ByteString
    field   :ModDate,                 :Type => ByteString, :Version => "1.1"
    field   :Trapped,                 :Type => Name, :Default => :Unknown, :Version => "1.3"
       
  end
  
  #
  # Class representing a metadata Stream.
  # This stream can contain the same information as the Metadata dictionary, but is storing in XML data.
  #
  class MetadataStream < Stream
    
    include Configurable
   
    field   :Type,                    :Type => Name, :Default => :Metadata, :Required => true
    field   :Subtype,                 :Type => Name, :Default =>:XML, :Required => true
    
  end

end
