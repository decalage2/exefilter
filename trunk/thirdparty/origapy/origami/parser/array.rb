=begin

= File
	array.rb

= Info
	This file is part of Origami, PDF manipulation framework for Ruby
	Copyright (C) 2009	Guillaume DelugrÈ <guillaume@security-labs.org>
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

  class InvalidArray < InvalidObject #:nodoc:
  end

  #
  # Class representing an Array Object.
  # Arrays contain a set of Object.
  #
  class Array < ::Array

    include Origami::Object
    
    TOKENS = %w{ [ ] } #:nodoc:
 
    @@regexp_open = Regexp.new('\A' + WHITESPACES + Regexp.escape(TOKENS.first) + WHITESPACES)   
    @@regexp_close = Regexp.new('\A' + WHITESPACES + Regexp.escape(TOKENS.last) + WHITESPACES)    
    #
    # Creates a new PDF Array Object.
    # _data_:: An array of objects.
    #
    def initialize(data = [])
      
      unless data.is_a?(::Array)
        raise TypeError, "Expected type Array, received #{data.class}."
      end
      
      super()

      i = 0
      while i < data.size
        self[i] = data[i].to_o
        i = i + 1
      end
      
    end
    
    def pre_build
      self.map!{|obj| obj.to_o}
      
      super
    end
    
    def self.parse(stream) #:nodoc:
      
      data = []
      
      if not stream.skip(@@regexp_open)
        raise InvalidArray, "No token '#{TOKENS.first}' found"
      end
      
      while stream.skip(@@regexp_close).nil? do
        
        type = Object.typeof(stream)
        if type.nil?
          raise InvalidArray, "Bad embedded object format"
        end
        
        value = type.parse(stream)  
        data << value
      
      end
    
      Array.new(data)
    end
    
    #
    # Converts self into a Ruby array.
    #
    def to_a
      super.map { |item|
        item.is_a?(Origami::Object) ? item.value : item
      }
    end
    
    def to_s #:nodoc:
      content = "#{TOKENS.first} "
      self.each { |entry|
        content << entry.to_o.to_s + ' '
      }
      content << TOKENS.last
      
      super(content)
    end

    def +(other)
      
      a = Origami::Array.new(self.to_a + other.to_a,  is_indirect?)
      a.no, a.generation = @no, @generation
      
      return a
    end

    def <<(item)
      obj = item.to_o
      obj.parent = self

      super(obj)
    end
    
    def []=(key,val)
      key, val = key.to_o, val.to_o
      super(key.to_o,val.to_o)

      val.parent = self

      val
    end
    
    alias value to_a

    def real_type ; Origami::Array end

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
    
    def initialize(lowerleftx, lowerlefty, upperrightx, upperrighty)
      super([ lowerleftx, lowerlefty, upperrightx, upperrighty ])
    end
    
  end

end
