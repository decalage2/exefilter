=begin

= File
	xreftable.rb

= Info
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

  class InvalidXRef < Exception #:nodoc:
  end

  #
  # Class representing a Cross-reference information.
  #
  class XRef
    
    FREE = "f"
    USED = "n"
    LASTFREE = 65535

    @@regexp = /\A(\d{10}) (\d{5}) (n|f)(\r| )\n/
    
    attr_accessor :offset, :generation, :state
    
    #
    # Creates a new XRef.
    # _offset_:: The file _offset_ of the referenced Object.
    # _generation_:: The generation number of the referenced Object.
    # _state_:: The state of the referenced Object (FREE or USED).
    #
    def initialize(offset, generation, state)
    
      @offset, @generation, @state = offset, generation, state
    
    end
    
    def self.parse(stream) #:nodoc:
      
      if stream.scan(@@regexp).nil?
        raise InvalidXRef, "Invalid XRef format"
      end
      
      offset = stream[1].to_i
      generation = stream[2].to_i
      state = stream[3]
      
      XRef.new(offset, generation, state)
    end
    
    #
    # Outputs self into PDF code.
    #
    def to_s
      off = ("0" * (10 - @offset.to_s.length)) + @offset.to_s
      gen = ("0" * (5 - @generation.to_s.length)) + @generation.to_s
      
      "#{off} #{gen} #{@state}" + EOL
    end

    def to_xrefstm_data
      type = (@state == FREE) ? 0 : 1

      [ type, @offset, @generation ].pack("Cnn")
    end
    
    class InvalidSubsection < Exception #:nodoc:
    end
  
    #
    # Class representing a cross-reference subsection.
    # A subsection contains a continute set of XRef.
    #
    class Subsection
      
      @@regexp = Regexp.new("\\A(\\d+) (\\d+)" + WHITESPACES + "(\\r?\\n|\\r\\n?)")
      
      attr_reader :range
      
      #
      # Creates a new XRef subsection.
      # _start_:: The number of the first object referenced in the subsection.
      # _entries_:: An array of XRef.
      #
      def initialize(start, entries = [])
        
        @entries = entries.dup
        @range = Range.new(start, start + entries.size - 1)
        
      end
      
      def self.parse(stream) #:nodoc:
        
        if stream.scan(@@regexp).nil?
          raise InvalidSubsection, "Bad subsection format"
        end
        
        start = stream[1].to_i
        size = stream[2].to_i
        
        xrefs = []
        size.times {
          xrefs << XRef.parse(stream)
        }
        
        XRef::Subsection.new(start, xrefs)
      end
      
      #
      # Returns whether this subsection contains information about a particular object.
      # _no_:: The Object number.
      #
      def has_object?(no)
        @range.include?(no)
      end
      
      #
      # Returns XRef associated with a given object.
      # _no_:: The Object number.
      #
      def [](no)
        @entries[no - @range.begin]
      end
      
      #
      # Processes each XRef in the subsection.
      #
      def each(&b)
        @entries.each(&b)
      end
      
      #
      # Outputs self into PDF code.
      #
      def to_s
        section = "#{@range.begin} #{@range.end - @range.begin + 1}" + EOL
        @entries.each { |xref|
          section << xref.to_s
        }
        
        section
      end
      
    end

    class InvalidSection < Exception #:nodoc:
    end

    #
    # Class representing a Cross-reference table.
    # A section contains a set of XRefSubsection.
    #
    class Section
      
      @@regexp_open = Regexp.new('\A' + WHITESPACES + "xref" + WHITESPACES + "(\\r?\\n|\\r\\n?)")
      @@regexp_sub = Regexp.new("\\A(\\d+) (\\d+)" + WHITESPACES + "(\\r?\\n|\\r\\n?)")
      
      #
      # Creates a new XRef section.
      # _subsections_:: An array of XRefSubsection.
      #
      def initialize(subsections = [])
        @subsections = subsections
      end
      
      def self.parse(stream) #:nodoc:
        
        if stream.skip(@@regexp_open).nil?
          raise InvalidSection, "No xref token found"
        end
        
        subsections = []
        while stream.match?(@@regexp_sub) do
          subsections << XRef::Subsection.parse(stream)
        end

        XRef::Section.new(subsections)
      end
      
      #
      # Appends a new subsection.
      # _subsection_:: A XRefSubsection.
      #
      def <<(subsection)
        @subsections << subsection
      end
      
      #
      # Returns a XRef associated with a given object.
      # _no_:: The Object number.
      #
      def [](no)
        @subsections.each { |s|
          return s[no] if s.has_object?(no)
        }
        nil
      end

      alias :find :[]
      
      #
      # Processes each XRefSubsection.
      #
      def each(&b)
        @subsections.each(&b)
      end
      
      #
      # Outputs self into PDF code.
      #
      def to_s
        "xref" << EOL << @subsections.join
      end
      
    end
    
  end

  #
  # An xref poiting to an Object embedded in an ObjectStream.
  #
  class XRefToCompressedObj

    attr_accessor :objstmno, :index

    def initialize(objstmno, index)
      @objstmno = objstmno
      @index = index
    end

    def to_xrefstm_data
      [ 2, @objstmno, @index ].pack("Cnn")
    end

  end
  
  class InvalidXRefStream < InvalidStream ; end

  #
  # Class representing a XRef Stream.
  #
  class XRefStream < Stream

    XREF_FREE = 0
    XREF_USED = 1
    XREF_COMPRESSED = 2
  
    include Enumerable
    include Configurable

    attr_reader :xrefs
 
    #
    # Xref fields
    #
    field   :Type,          :Type => Name, :Default => :XRef, :Required => true, :Version => "1.5"
    field   :Size,          :Type => Integer, :Required => true
    field   :Index,         :Type => Array
    field   :Prev,          :Type => Integer
    field   :W,             :Type => Array, :Required => true

    #
    # Trailer fields
    #
    field   :Root,          :Type => Dictionary, :Required => true
    field   :Encrypt,       :Type => Dictionary
    field   :Info,          :Type => Dictionary
    field   :ID,            :Type => Array
  
    def initialize(data = "", dictionary = {})
      super(data, dictionary)

      @xrefs = nil
    end

    def pre_build #:nodoc:
      self.W = [ 1, 2, 2 ]
      self.Size = @xrefs.length + 1

      save!

      super
    end

    #
    # Adds an XRef to this Stream.
    #
    def <<(xref)
      load! if @xrefs.nil?

      @xrefs << xref  
    end

    #
    # Iterates over each XRef present in the stream.
    #
    def each(&b)
      load! if @xrefs.nil?

      @xrefs.each(&b)
    end

    #
    # Returns an XRef matching this object number.
    #
    def find(no)
      load! if @xrefs.nil?

      ranges = self.Index || [ 0, @xrefs.length ]

      index = 0
      (ranges.size / 2).times do |i|
        brange = ranges[i*2].to_i
        size = ranges[i*2+1].to_i
        return @xrefs[index + no - brange] if Range.new(brange, brange + size) === no

        index += size
      end

      nil
    end

    private

    def load! #:nodoc:
      widths = self.W

      if not widths.is_a?(Array) or widths.length != 3 or widths.any?{|width| not width.is_a?(Integer) }
        raise InvalidXRefStream, "W field must be an array of 3 integers"
      end

      decode!

      type_w = self.W[0]
      field1_w = self.W[1]
      field2_w = self.W[2]
      
      entrymask = "B#{type_w << 3}B#{field1_w << 3}B#{field2_w << 3}"
      size = @data.size / (type_w + field1_w + field2_w)

      entries = @data.unpack(entrymask * size).map!{|field| field.to_i(2) }

      @xrefs = []
      size.times do |i|
        type,field1,field2 = entries[i*3],entries[i*3+1],entries[i*3+2]
        case type
          when XREF_FREE
            @xrefs << XRef.new(field1, field2, XRef::FREE)
          when XREF_USED
            @xrefs << XRef.new(field1, field2, XRef::USED)
          when XREF_COMPRESSED
            @xrefs << XRefToCompressedObj.new(field1, field2)
        end
      end
    end

    def save! #:nodoc:
      @data = ""

      @xrefs.each do |xref| @data << xref.to_xrefstm_data end
      
      encode!
    end

  end

end
