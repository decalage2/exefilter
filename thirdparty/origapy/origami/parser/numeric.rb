=begin

= File
	numeric.rb

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

require 'delegate'

module Origami

  class InvalidInteger < InvalidObject #:nodoc:
  end

  #
  # Class representing a PDF number (Integer, or Real).
  #
  module Number
    include Origami::Object
    
    def ~
      self.class.new(~self.to_i, is_indirect?)
    end
    
    def |(val)
      self.class.new(self.to_i | val, is_indirect?)
    end
    
    def &(val)
      self.class.new(self.to_i & val, is_indirect?)
    end
    
    def ^(val)
      self.class.new(self.to_i ^ val, is_indirect?)
    end
    
    def <<(val)
      self.class.new(self.to_i << val, is_indirect?)
    end
    
    def >>(val)
      self.class.new(self.to_i >> val, is_indirect?)
    end
    
    def +(val)
      self.class.new(self.to_i + val, is_indirect?)
    end
    
    def -(val)
      self.class.new(self.to_i - val, is_indirect?)
    end
    
    def -@
      self.class.new(-self.to_i, is_indirect?)
    end
    
    def *(val)
      self.class.new(self.to_i * val, is_indirect?)
    end
    
    def /(val)
      self.class.new(self.to_i / val, is_indirect?)
    end
    
    def abs
      self.class.new(self.to_i.abs, is_indirect?)
    end
    
    def **(val)
      self.class.new(self.to_i ** val, is_indirect?)
    end
    
    def to_s
      print(super)
    end
    
    def real_type ; Number end
  end
  
  #
  # Class representing an Integer Object.
  #
  class Integer < DelegateClass(Bignum)
    
    include Number
    
    TOKENS = [ "(\\+|-)?[\\d]+[^.]?" ] #:nodoc:
    
    @@regexp = Regexp.new('\A' + WHITESPACES + "((\\+|-)?[\\d]+)")

    #
    # Creates a new Integer from  a Ruby Fixnum / Bignum.
    # _i_:: The Integer value.
    #
    def initialize(i = 0, indirect = false)
      
      unless i.is_a?(::Integer)
        raise TypeError, "Expected type Fixnum or Bignum, received #{i.class}."
      end
      
      super(indirect, i)
      
    end
      
    def self.parse(stream) #:nodoc:
      if not stream.scan(@@regexp)
        raise InvalidInteger, "Invalid integer format"
      end

      value = stream[2].to_i
      Integer.new(value)
    end
    
    alias value to_i
    
  end
  
  class InvalidReal < InvalidObject #:nodoc:
  end

  #
  # Class representing a Real number Object.
  # PDF real numbers are arbitrary precision numbers, depending on architectures.
  #
  class Real < DelegateClass(Float)
    
    include Number
    
    TOKENS = [ "(\\+|-)?([\\d]*\\.[\\d]+|[\\d]+\\.[\\d]*)" ] #:nodoc:
    
    @@regexp = Regexp.new('\A' + WHITESPACES + "(" + TOKENS.first + ")")
    
    #
    # Creates a new Real from a Ruby Float.
    # _f_:: The new Real value.
    #
    def initialize(f = 0, indirect = false)
      
      unless f.is_a?(Float)
        raise TypeError, "Expected type Float, received #{f.class}."
      end
      
      super(indirect, f)
    
    end
  
    def self.parse(stream) #:nodoc:
      
      if not stream.scan(@@regexp)
        raise InvalidReal, "Invalid real number format"
      end
       
      value = stream[2].to_f
      Real.new(value)
    end
    
    alias value to_f
    
  end

end
