=begin

= File
	name.rb

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

require 'delegate'

module Origami

  REGULARCHARS = "([^ \\t\\r\\n\\0\\[\\]<>()%\\/]|#[a-fA-F0-9][a-fA-F0-9])*" #:nodoc:

  class InvalidName < InvalidObject #:nodoc:
  end

  #
  # Class representing a Name Object.
  # Name objects are strings which identify some PDF file inner structures.
  #
  class Name < DelegateClass(Symbol)
    
    include Origami::Object
    
    TOKENS = %w{ / } #:nodoc:
    
    @@regexp = Regexp.new('\A' + WHITESPACES + TOKENS.first + "(" + REGULARCHARS + ")" + WHITESPACES) #:nodoc
    
    #
    # Creates a new Name.
    # _name_:: A symbol representing the new Name value.
    #
    def initialize(name = "", indirect = false)
      
      unless name.is_a?(Symbol) or name.is_a?(::String)
        raise TypeError, "Expected type Symbol or String, received #{name.class}."
      end
      
      value = (name.to_s.empty?) ? :" " : name.to_sym
      
      super(indirect, value)
      
    end

    def set(value)
      initialize(value, @indirect)
    end
    
    def value
      self.to_sym
    end
    
    def eql?(object) #:nodoc:
      object.is_a?(Name) and self.id2name == object.id2name
    end
    
    def hash #:nodoc:
      self.value.hash
    end
    
    def to_s #:nodoc:
      
      name = (self.value == :" ") ? "" : self.id2name
      
      print(TOKENS.first + Name.expand(name))
    end
    
    def self.parse(stream) #:nodoc:
      
      if stream.scan(@@regexp).nil?
        raise InvalidName, "Bad name format"
      else
        value = stream[2]

        Name.new(contract(value))
      end
      
    end
    
    def self.contract(name) #:nodoc:
      
      name.length.times { |i|
        if i >= name.length then break end
        
        if name[i].chr == "#"
          digits = name[i+1, 2]
          
          if digits.length != 2
            raise InvalidName, "Irregular use of # token"
          end
          
          digits.each_byte { |d|
            if not ("a".."z") === d.chr and not ("A".."Z") === d.chr and not ( "0".."9" ) === d.chr
              raise InvalidName, "Irregular use of # token"
            end
          }
          
          char = digits.hex.chr
          
          if char == "\0"
            raise InvalidName, "Null byte forbidden inside name definition"
          end
          
          name[i, 3] = char
          
        end
        
      }
      
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
