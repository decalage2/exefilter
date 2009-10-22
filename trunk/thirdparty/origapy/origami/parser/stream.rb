=begin

= File
	stream.rb

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

require 'strscan'

module Origami

  class InvalidStream < InvalidObject #:nodoc:
  end

  #
  # Class representing a PDF Stream Object.
  # Streams can be used to hold any kind of data, especially binary data.
  #
  class Stream
    
    include Origami::Object
    include Configurable
    
    TOKENS = [ "stream" + WHITECHARS  + "\\r?\\n", "endstream" ] #:nodoc:
   
    @@regexp_open = Regexp.new('\A' + WHITESPACES + TOKENS.first)
    @@regexp_close = Regexp.new(TOKENS.last)

    #
    # Actually only 5 first ones are implemented, other ones are mainly about image data processing (JPEG, JPEG2000 ... )
    #
    @@defined_filters = 
    [ 
      :ASCIIHexDecode, 
      :ASCII85Decode, 
      :LZWDecode, 
      :FlateDecode, 
      :RunLengthDecode,
      # TODO
      :CCITTFaxDecode,
      :JBIG2Decode,
      :DCTDecode,
      :JPXDecode
    ]
    
    attr_accessor :dictionary
     
    field   :Length,          :Type => Integer, :Required => true
    field   :Filter,          :Type => [ Name, Array ]
    field   :DecodeParms,     :Type => [ Dictionary, Array ]
    field   :F,               :Type => Dictionary, :Version => "1.2"
    field   :FFilter,         :Type => [ Name, Array ], :Version => "1.2"
    field   :FDecodeParms,    :Type => [ Dictionary, Array ], :Version => "1.2"
    field   :DL,              :Type => Integer, :Version => "1.5"

    #
    # Creates a new PDF Stream.
    # _data_:: The Stream uncompressed data.
    # _dictionary_:: A hash representing the Stream attributes.
    #
    def initialize(data = "", dictionary = {})
        super()
        
        set_indirect(true)
       
        @dictionary, @data = Dictionary.new(dictionary), data
        @dictionary.parent = self
    end
    
    def pre_build
      encode!
     
      super
    end

    def post_build
     
      unless self.Length.nil?
        self.Length = @rawdata.length
      end
 
      super
    end
    
    def self.parse(stream) #:nodoc:
    
      dictionary = Dictionary.parse(stream)
     
      if not stream.skip(@@regexp_open)
        return dictionary
      end
     
      len = dictionary[:Length]
      if not len.is_a?(Integer)
        rawdata = stream.scan_until(@@regexp_close)
        if rawdata.nil?
          raise InvalidStream, "Stream shall end with a '#{TOKENS.last}' statement"
        end

      else
        rawdata = stream.peek(len)
        stream.pos += len
        if not ( unmatched = stream.scan_until(@@regexp_close) )
          raise InvalidStream, "Stream shall end with a '#{TOKENS.last}' statement"
        end

        rawdata << unmatched
      end
       
      rawdata.chomp!(TOKENS.last)

      stm = if dictionary[:Type] and @@stm_special_types.include?(dictionary[:Type].value)
        @@stm_special_types[dictionary[:Type].value].new("", dictionary.to_h)
      else
        Stream.new("", dictionary.to_h)
      end

      rawdata.chomp! if len.is_a?(Integer) and len < rawdata.length
      stm.rawdata = rawdata

      stm
    end   

    def set_predictor(predictor, colors = 1, bitspercomponent = 8, columns = 1)
      
      filters = @dictionary[:Filter].is_a?(::Array) ? filters : [ @dictionary[:Filter] ]

      if not filters.include?(:FlateDecode) and not filters.include?(:LZWDecode)
        raise InvalidStream, 'Predictor functions can only be used with Flate or LZW filters'
      end

      params = @dictionary[:DecodeParms] ||= Filter::LZW::DecodeParms.new
      params[:Predictor] = predictor
      params[:Colors] = colors if colors != 1
      params[:BitsPerComponent] = bitspercomponent if bitspercomponent != 8
      params[:Columns] = columns if columns != 1

      self
    end

    def value #:nodoc:
      self
    end
 
    #
    # Returns the uncompressed stream content.
    #
    def data
      self.decode! if @data.nil?
      
      @data 
    end
   
    #
    # Sets the uncompressed stream content.
    # _str_:: The new uncompressed data.
    #
    def data=(str)      
      @rawdata = nil
      @data = str
    end
    
    #
    # Returns the raw compressed stream content.
    #
    def rawdata
      self.encode! if @rawdata.nil? 
       
      @rawdata
    end
    
    #
    # Sets the raw compressed stream content.
    # _str_:: the new raw data.
    #
    def rawdata=(str)
      @rawdata = str
      @data = nil
    end
    
    #
    # Uncompress the stream data.
    #
    def decode!
      
      if @rawdata
      
        filters = @dictionary[:Filter]
        
        if filters.nil?
          @data = @rawdata
        elsif filters.type == :Array
          
          @data = @rawdata
          
          filters.each { |filter|
            @data = decodedata(@data, filter)
          }
          
        elsif filters.type == :Name
          
          @data = decodedata(@rawdata, filters)
        else
          raise InvalidStream, "Invalid Filter type parameter"
        end
        
      end
      
      self
    end
    
    #
    # Compress the stream data.
    #
    def encode!
      
      if @data
      
        filters = @dictionary[:Filter]
        
        if filters.nil?
          @rawdata = @data
        elsif filters.is_a?(Array)
          
          @rawdata = @data
          
          filters.to_a.reverse.each { |filter|
            @rawdata = encodedata(@rawdata, filter)
          }
        
        elsif filters.is_a?(Name)
          
          @rawdata = encodedata(@data, filters)
          
        else
          raise InvalidStream, "Invalid filter type parameter"
        end
        
        self.Length = @rawdata.length
      
      end
      
      self
    end
    
    def to_s #:nodoc:
      
      content = ""
      
      content << @dictionary.to_s
      content << "stream" + EOL
      content << self.rawdata
      content << EOL << TOKENS.last
      
      super(content)
    end
    
    def [](key) #:nodoc:
      @dictionary[key]
    end
    
    def []=(key,val) #:nodoc:
      @dictionary[key] = val
    end
    
    def each_key(&b) #:nodoc:
      @dictionary.each_key(&b)
    end
  
    def real_type ; Stream end

    private
    
    def decodedata(data, filter) #:nodoc:
      
      if not @@defined_filters.include? filter.value
        raise InvalidStream, "Unknown filter : #{filter}"
      end

      begin
        params = self.DecodeParms.is_a?(Dictionary) ? self.DecodeParms : {}

        Origami::Filter.const_get(filter.value.to_s.sub(/Decode$/,"")).decode(data, params)
      rescue Exception => e
        raise InvalidStream, "Error while decoding stream : #{e.message}"
      end
    end
    
    def encodedata(data, filter) #:nodoc:
      
      if not @@defined_filters.include? filter.value
        raise InvalidStream, "Unknown filter : #{filter}"
      end
 
      params = self.DecodeParms.is_a?(Dictionary) ? self.DecodeParms : {}
      encoded = Origami::Filter.const_get(filter.value.to_s.sub(/Decode$/,"")).encode(data, params)

      if filter.value == :ASCIIHexDecode or filter.value == :ASCII85Decode
        encoded << Origami::Filter.const_get(filter.value.to_s.sub(/Decode$/,""))::EOD
      end
      
      encoded
    end
    
  end

  #
  # Class representing an external Stream.
  #
  class ExternalStream < Stream

    def initialize(filespec, hash = {})

      hash[:F] = filespec
      super('', hash)
    end

  end
  
  class InvalidObjectStream < InvalidStream  #:nodoc:
  end

  #
  # Class representing a Stream containing other Objects.
  #
  class ObjectStream < Stream
    
    include Enumerable
    
    NUM = 0 #:nodoc:
    OBJ = 1 #:nodoc:
    
    field   :Type,            :Type => Name, :Default => :ObjStm, :Required => true, :Version => "1.5"
    field   :N,               :Type => Integer, :Required => true
    field   :First,           :Type => Integer, :Required => true
    field   :Extends,         :Type => Stream

    #
    # Creates a new Object Stream.
    # _dictionary_:: A hash of attributes to set to the Stream.
    # _rawdata_:: The Stream data.
    #
    def initialize(rawdata = "", dictionary = {})
    
      @objects = nil
     
      super(rawdata, dictionary)
    end
    
    def pre_build #:nodoc:
      
      load! if @objects.nil?

      prolog = ""
      data = ""
      objoff = 0
      @objects.to_a.sort.each { |num,obj|
        
        obj.set_indirect(false)
        obj.objstm_offset = objoff

        prolog << "#{num} #{objoff} "
        objdata = "#{obj.to_s} "
        
        objoff += objdata.size
        data << objdata
        
      }
      
      @data = prolog + data
      
      @dictionary[:N] = @objects.size
      @dictionary[:First] = prolog.size
      
      super
    end
    
    # TODO
    # Adds a new Object to this Stream.
    # _object_:: The Object to append.
    #
    def <<(object)
      
      unless object.generation == 0
        raise InvalidObject, "Cannot store an object with generation > 0 in an ObjectStream"
      end

      if object.is_a?(Stream)
        raise InvalidObject, "Cannot store a Stream in an ObjectStream"
      end

      load! if @objects.nil?
      
      object.no, object.generation = @pdf.alloc_new_object_number if object.no == 0
      
      object.set_indirect(true) # object is indirect
      object.parent = self      # set this stream as the parent
      object.set_pdf(@pdf)      # indirect objects need pdf information
      @objects[object.no] = object
     
      Reference.new(object.no, 0)
    end

    #
    # Deletes Object _no_.
    #
    def delete(no)
      load! if @objects.nil?

      @objects.delete(no)
    end

    #
    # Returns the index of Object _no_.
    #
    def index(no)
      ind = 0
      @objects.to_a.sort.each { |num, obj|
        return ind if num == no

        ind = ind + 1
      }

      nil
    end

    # 
    # Returns a given decompressed object contained in the Stream.
    # _no_:: The Object number.
    #
    def extract(no)
      load! if @objects.nil?
    
      @objects[no]
    end

    #
    # Returns a given decompressed object by index.
    # _index_:: The Object index in the ObjectStream.
    #
    def extract_by_index(index)
      load! if @objects.nil?

      @objects.to_a.sort[index]
    end
  
    #
    # Returns whether a specific object is contained in this stream.
    # _no_:: The Object number.
    #
    def include?(no)
      load! if @objects.nil?
    
      @objects.include?(no)
    end
    
    #
    # Iterates over each object in the stream.
    #
    def each(&b)
      load! if @objects.nil? 
      
      @objects.values.each(&b)
    end
    
    #
    # Returns the array of inner objects.
    #
    def objects
      load! if @objects.nil?
    
      @objects.values
    end
    
    private
    
    def load! #:nodoc:
      
      decode!
      
      data = StringScanner.new(@data)
      nums = []
      offsets = []
      
      @dictionary[:N].to_i.times do
        
        nums << Integer.parse(data).to_i
        offsets << Integer.parse(data)
        
      end
      
      @objects = {}
      nums.size.times do |i|
        
        type = Object.typeof(data)
        if type.nil?
          raise InvalidObjectStream, "Bad embedded object format in object stream"
        end
        
        embeddedobj = type.parse(data)
        embeddedobj.set_indirect(true) # object is indirect
        embeddedobj.no = nums[i]       # object number
        embeddedobj.parent = self      # set this stream as the parent
        embeddedobj.set_pdf(@pdf)      # indirect objects need pdf information
        embeddedobj.objstm_offset = offsets[i]
        @objects[nums[i]] = embeddedobj
        
      end
      
    end

  end
  
  #
  # A class for the Sound stream (section 9.2 p782)
  # TODO: should probably be defined as Encoded Stream ...
  class Sound < Stream
    
    module Encoding
      RAW = :Raw
      SIGNED = :Signed
      MULAW = :muLaw
      ALAW = :aLaw
    end

    field   :Type,            :Type => Name, :Default => :Sound
    field   :R,               :Type => Number
    field   :C,               :Type => Integer, :Default => 1
    field   :B,               :Type => Integer, :Default => 8
    field   :E,               :Type => Name, :Default => Encoding::RAW
    field   :CO,              :Type => Name
    field   :CP,              :Type => Object 
    
  end

end
