=begin

= File
	trailer.rb

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

require 'digest/md5'

module Origami

  class PDF
   
    private

    def has_attr?(attr) #:nodoc:
      not get_doc_attr(attr).nil?
    end

    def get_doc_attr(attr) #:nodoc: 

      @revisions.reverse_each do |rev|
        if rev.trailer.has_dictionary? and not rev.trailer.dictionary[attr].nil?
          return rev.trailer.send(attr)
        else
          xrefstm = get_object_by_offset(rev.trailer.startxref)
          if xrefstm.is_a?(XRefStream) and xrefstm.has_field?(attr)
            return xrefstm.send(attr)
          end
        end
      end

      nil
    end

    def get_trailer_info #:nodoc:
     
      #
      # First look for a standard trailer dictionary
      #
      if @revisions.last.trailer.has_dictionary?
        @revisions.last.trailer

      #
      # Otherwise look for a xref stream.
      # 
      else
        xrefstm = get_object_by_offset(@revisions.last.trailer.startxref)
        xrefstm if xrefstm.is_a?(XRefStream)
      end
    end
    
    def gen_id
      fileInfo = get_trailer_info
      if fileInfo.nil?
        raise InvalidPDFError, "Cannot access trailer information"
      end

      id = Digest::MD5.hexdigest( rand.to_s )
      fileInfo.ID = [ id, id ]
    end

  end

  class InvalidTrailerError < Exception #:nodoc:
  end

  #
  # Class representing a PDF file Trailer.
  #
  class Trailer
    
    include Configurable
    
    TOKENS = %w{ trailer %%EOF } #:nodoc:
    XREF_TOKEN = "startxref" #:nodoc:
    
    @@regexp_open = Regexp.new('\A' + WHITESPACES + TOKENS.first + WHITESPACES)
    @@regexp_xref = Regexp.new('\A' + WHITESPACES + XREF_TOKEN + WHITESPACES + "(\\d+)" + WHITESPACES + TOKENS.last + WHITESPACES)
    
    attr_accessor :pdf
    attr_accessor :startxref
    attr_reader :dictionary

    field   :Size,      :Type => Integer, :Required => true
    field   :Prev,      :Type => Integer
    field   :Root,      :Type => Dictionary, :Required => true
    field   :Encrypt,   :Type => Dictionary
    field   :Info,      :Type => Dictionary
    field   :ID,        :Type => Array
    field   :XRefStm,   :Type => Integer

    #
    # Creates a new Trailer.
    # _startxref_:: The file _offset_ to the XRef::Section.
    # _dictionary_:: A hash of attributes to set in the Trailer Dictionary.
    #
    def initialize(startxref = 0, dictionary = {})
     
      @startxref, self.dictionary = startxref, dictionary.nil? ? nil : Dictionary.new(dictionary)
    end
    
    def self.parse(stream) #:nodoc:
     
      if stream.skip(@@regexp_open)
        dictionary = Dictionary.parse(stream)
      else 
        dictionary = nil
      end
      
      if not stream.scan(@@regexp_xref)
        raise InvalidTrailerError, "Cannot get startxref value"
      end

      startxref = stream[3].to_i
        
      Trailer.new(startxref, dictionary.nil? ? nil : dictionary.to_h)
    end
    
    def [](key)
      @dictionary[key] if has_dictionary?
    end
    
    def []=(key,val)
      @dictionary[key] = val
    end

    def dictionary=(dict)
      dict.parent = self if dict
      @dictionary = dict
    end
    
    def has_dictionary?
      not @dictionary.nil?
    end
    
    #
    # Outputs self into PDF code.
    #
    def to_s
      
      content = ""
      if self.has_dictionary?
        content << TOKENS.first << EOL << @dictionary.to_s << EOL
      end
      
      content << XREF_TOKEN << EOL << @startxref.to_s << EOL << TOKENS.last << EOL
                    
      content
    end
    
  end

end
