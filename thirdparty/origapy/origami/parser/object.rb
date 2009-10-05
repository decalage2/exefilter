=begin

= File
	object.rb

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

class Bignum #:nodoc:
  def to_o
    Origami::Integer.new(self)
  end
end

class Fixnum #:nodoc:
  def to_o
    Origami::Integer.new(self)
  end
end

class Array #:nodoc:
  def to_o
    Origami::Array.new(self)
  end
  
  def shuffle
    sort_by { rand }
  end
  
  def shuffle!
    self.replace shuffle
  end  
end

class Float #:nodoc:
  def to_o
    Origami::Real.new(self)
  end
end

class Hash #:nodoc:
  def to_o
    Origami::Dictionary.new(self)
  end
end

class TrueClass #:nodoc:
  def to_o
    Origami::Boolean.new(true)
  end
end

class FalseClass #:nodoc:
  def to_o
    Origami::Boolean.new(false)
  end
end

class Symbol #:nodoc:
  def to_o
    Origami::Name.new(self)
  end
  
  def value
    self
  end
  
end

class String #:nodoc:
  def to_o
    Origami::ByteString.new(self)
  end

  def is_binary_data?
    ( self.count( "\x00" ) > 0 ) unless empty?
  end
end

#
# Module for parsing/generating PDF files.
#
module Origami

	EOL = "\r\n" #:nodoc:
  DEFINED_TOKENS = "[<\\[(%\\/)\\]>]" #:nodoc:
  WHITESPACES = "([ \\f\\t\\r\\n\\0]|%[^\\n]*\\n)*" #:nodoc:
  
  #
  # Mixin' module for objects which can store their options into an inner Dictionary.
  #
  module Configurable

    DEFAULT_ATTRIBUTES = { :Type => Object, :Version => "1.1" } #:nodoc:

    def self.included(receiver)
      receiver.instance_variable_set(:@fields, Hash.new(DEFAULT_ATTRIBUTES))
      receiver.extend(ClassMethods)
    end

    module ClassMethods
    
      def inherited(subclass)
        subclass.instance_variable_set(:@fields, Marshal.load(Marshal.dump(@fields)))
      end

      def fields
        @fields
      end
      
      def field(name, attributes)
      
        if not @fields.has_key?(name)
          @fields[name] = attributes
        else
          attributes.each_pair { |k,v|
            @fields[name][k] = v
          }
        end
        
        define_field_methods(name)
      end

      def define_field_methods(field) #:nodoc:
        reader = lambda { obj = self[field]; obj.is_a?(Reference) ? obj.solve : obj }
        writer = lambda { |value| self[field] = value }
        set = lambda { |value| self[field] = value; self }
        
        send(:define_method, field.id2name, reader)
        send(:define_method, field.id2name + "=", writer)
        send(:define_method, "set" + field.id2name, set)  
      end
    
      #
      # Returns an array of required fields for the current Object.
      #
      def required_fields #:nodoc:
        fields = []
        @fields.each_pair { |name, attributes|
            fields << name if attributes[:Required] == true
        }
      
        fields
      end

    end

    def pre_build #:nodoc:
      
      set_default_values
      do_type_check
      
      super
    end
    
    #
    # Check if an attribute is set in the current Object.
    # _attr_:: The attribute name.
    #
    def has_field? (field)
      not self[field].nil?
    end

    #
    # Returns the version required by the current Object.
    #
    def version_required #:nodoc:
      
      max = 1.0
      
      self.each_key { |field|
        
        attributes = self.class.fields[field.value]
        if attributes[:Version] and attributes[:Version].to_s.to_f > max
          max = attributes[:Version].to_s.to_f
        end

        localmax = self[field.value].version_required
        if localmax.to_s.to_f > max then max = localmax end
      }
      
      max
    end
  
    def set_default_value(field) #:nodoc:
      if self.class.fields[field][:Default]
        self[field] = self.class.fields[field][:Default]
        self[field].pre_build
      end
    end
    
    def set_default_values #:nodoc:
      self.class.required_fields.each do |field| 
        set_default_value(field) unless has_field?(field) 
      end
    end
    
    def do_type_check #:nodoc:
      
      self.class.fields.each_pair { |field, attributes|
        
        if not self[field].nil? and not attributes[:Type].nil?
          types = attributes[:Type].is_a?(::Array) ? attributes[:Type] : [ attributes[:Type] ]
          puts "Warning: in object #{self.class}, field `#{field.to_s}' has unexpected type #{self[field].class}" if not self[field].is_a?(Reference) and types.all? { |type|
            not self[field].is_a?(type)
          }
        end
      }
      
    end
  
  end
  
  class InvalidObject < Exception #:nodoc:
  end

  #
  # Parent module representing a PDF Object.
  # PDF specification declares a set of primitive object types :
  # * Null
  # * Boolean
  # * Integer
  # * Real
  # * Name
  # * String
  # * Array
  # * Dictionary
  # * Stream
  #
  module Object
    
    TOKENS = %w{ obj endobj } #:nodoc:
    
    @@regexp_obj = Regexp.new('\A' + WHITESPACES + "(\\d+)" + WHITESPACES + "(\\d+)" + WHITESPACES + TOKENS.first + WHITESPACES)
    @@regexp_endobj = Regexp.new('\A' + WHITESPACES + TOKENS.last + WHITESPACES)

    # Streams are processed apart from them
    @@defined_types = [ :Name, :Dictionary, :Array, :Reference, :Real, :Integer, :ByteString, :HexaString, :Boolean, :Null ]
    
    attr_accessor :no, :generation, :file_offset, :objstm_offset
    attr_accessor :parent
    
    #
    # Creates a new PDF Object.
    #
    def initialize(indirect, *cons)
      
      set_indirect(indirect)
      @no, @generation = 0, 0
      
      super(*cons) unless cons.empty?
      
    end
    
    #
    # Sets whether the object is indirect or not.
    # Indirect objects are allocated numbers at build time.
    #
    def set_indirect(dir)
      unless dir == true  or dir == false
        raise TypeError, "The argument must be boolean"
      end
      
      @indirect = dir
      self
    end
    
    #
    # Generic method called just before the object is finalized.
    # At this time, no number nor generation allocation has yet been done.
    #
    def pre_build
      self
    end

    #
    # Generic method called just after the object is finalized.
    # At this time, any indirect object has its own number and generation identifier.
    #
    def post_build
      self
    end
    
    #
    # Compare two objects from their respective numbers.
    #
    def <=>(obj)
      [@no, @generation] <=> [obj.no, obj.generation]
    end
    
    #
    # Returns whether the objects is indirect, which means that it is not embedded into another object.
    #
    def is_indirect?
      @indirect
    end

    #
    # Deep copy of an object.
    #
    def copy
      Marshal.load(Marshal.dump(self))
    end
    
    #
    # Returns an indirect reference to this object, or a Null object is this object is not indirect.
    #
    def reference
      unless self.is_indirect?
        raise InvalidObject, "Cannot reference a direct object"
      end

      ref = Reference.new(@no, @generation)
      ref.parent = self

      ref
    end

    #
    # Returns an array of references pointing to the current object.
    #
    def xrefs
      unless self.is_indirect?
        raise InvalidObject, "Cannot find xrefs to a direct object"
      end

      if self.pdf.nil?
        raise InvalidObject, "Not attached to any PDF"
      end

      thisref = self.reference
      @pdf.objects.find_all{|obj| obj.is_a?(Reference) and obj.eql?(thisref)}
    end

    #
    # Returns the indirect object which contains this object.
    # If the current object is already indirect, returns self.
    #
    def indirect_parent 
      obj = self
      obj = obj.parent until obj.is_indirect?
        
      obj
    end
    
    #
    # Returns self.
    #
    def to_o
      self
    end
    
    #
    # Returns the size of this object once converted to PDF code.
    #
    def size
      to_s.size
    end

    #
    # Returns the PDF which the object belongs to.
    #
    def pdf
      if self.is_indirect? then @pdf
      else
        @parent.pdf
      end
    end

    def set_pdf(pdf)
      if self.is_indirect? then @pdf = pdf
      else
        raise InvalidObject, "You cannot set the PDF parent of a direct object"
      end
    end
    
    class << self

      def typeof(stream) #:nodoc:
        
        @@defined_types.each { |type|
          type = Origami.const_get(type)
        
          token = type::TOKENS.first
          if token.is_a?(::Array)
            token = "(#{token.join('|')})"
          elsif not type.include?(Number) and type != Reference and type != Stream
            token = Regexp.escape(token)
          end
        
          if stream.check(Regexp.new('\A' + WHITESPACES + token, Regexp::MULTILINE))
            return (type == Dictionary ? Stream : type)
          end
        }
        
        nil
      end
        
      def types #:nodoc:
        @@defined_types
      end
      
      def parse(stream, pdf) #:nodoc:
       
        offset = stream.pos

        #
        # End of body ?
        #
        return nil if stream.match?(/xref/) or stream.match?(/startxref/)
 
        if stream.scan(@@regexp_obj).nil?
          raise InvalidObject, "Object shall begin with '$no $gen obj' statement"
        end
          
        no = stream[2].to_i
        gen = stream[4].to_i

        type = typeof(stream) 
        if type.nil?
          raise InvalidObject, "Cannot determine object (no:#{no},gen:#{gen}) type"
        end
          
        begin
          newObj = type.parse(stream)
        rescue Exception => e
          raise InvalidObject, "Failed to parse object (no:#{no},gen:#{gen})\n\t -> [#{e.class}] #{e.message}"
        end

        newObj.set_indirect(true)
        newObj.no = no
        newObj.generation = gen
        newObj.file_offset = offset
          
        if stream.skip(@@regexp_endobj).nil?
          raise InvalidObject, "Object shall end with 'endobj' statement"
        end
          
        newObj
      end
      
    end
    
    def version_required #:nodoc:
      "1.0"
    end
      
    #
    # Returns the symbol type of this Object.
    #
    def type
      self.class.to_s.split("::").last.to_sym
    end
    
    alias real_type type
    
    private
    
    #
    # Outputs this object into PDF code.
    # _data_:: The object data.
    #
    def print(data)
      
      content = ""
      content << "#{no} #{generation} obj" << EOL if self.is_indirect?
      content << data
      content << EOL << "endobj" << EOL if self.is_indirect?
      
      content
    end
    
  end

end
