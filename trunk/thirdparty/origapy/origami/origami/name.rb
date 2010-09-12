=begin

= File
	name.rb

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

module Origami

  REGULARCHARS = "([^ \\t\\r\\n\\0\\[\\]<>()%\\/]|#[a-fA-F0-9][a-fA-F0-9])*" #:nodoc:

  class InvalidNameObjectError < InvalidObjectError #:nodoc:
  end

  #
  # Class representing a Name Object.
  # Name objects are strings which identify some PDF file inner structures.
  #
  class Name #< DelegateClass(Symbol)
    
    include Origami::Object
    
    TOKENS = %w{ / } #:nodoc:
    
    @@regexp = Regexp.new('\A' + WHITESPACES + TOKENS.first + "(" + REGULARCHARS + ")" + WHITESPACES) #:nodoc
    
    #
    # Creates a new Name.
    # _name_:: A symbol representing the new Name value.
    #
    def initialize(name = "")
      
      unless name.is_a?(Symbol) or name.is_a?(::String)
        raise TypeError, "Expected type Symbol or String, received #{name.class}."
      end
      
      @value = name.to_s
      
      super()
    end

    def value
      @value.to_sym
    end

    def ==(object) #:nodoc:
      @value.to_sym == object
    end
    
    def eql?(object) #:nodoc:
      object.is_a?(Name) and self.to_s == object.to_s
    end
    
    def hash #:nodoc:
      @value.hash
    end
    
    def to_s #:nodoc:
      super(TOKENS.first + Name.expand(@value))
    end
    
    def self.parse(stream) #:nodoc:
      
      if stream.scan(@@regexp).nil?
        raise InvalidNameObjectError, "Bad name format"
      else
        value = stream[2]
        
        Name.new(value.include?('#') ? contract(value) : value)
      end
      
    end
    
    def self.contract(name) #:nodoc:
     
      i = 0
      while i < name.length

        if name[i,1] == "#"
          digits = name[i+1, 2]
          
          unless /^[A-Za-z0-9]{2}$/ === digits
            raise InvalidNameObjectError, "Irregular use of # token"
          end
          
          char = digits.hex.chr
          
          if char == "\0"
            raise InvalidNameObjectError, "Null byte forbidden inside name definition"
          end
          
          name[i, 3] = char
        end
          
        i = i + 1
      end

      name
    end
    
    def self.expand(name) #:nodoc:
      
      forbiddenchars = /[ #\t\r\n\0\[\]<>()%\/]/
      
      name.gsub!(forbiddenchars) { |c|
        hexchar = c[0].to_s(base=16)
        hexchar = "0" + hexchar if hexchar.length < 2
        
        "#" + hexchar
      }
      
      name
    end
    
    def real_type ; Name end

  end

end
