=begin

= File
	boolean.rb

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

  class InvalidBoolean < InvalidObject #:nodoc:
  end

  #
  # Class representing a Boolean Object.
  # A Boolean Object can be *true* or *false*.
  #
  class Boolean
  
    include Origami::Object
    
    TOKENS = [ %w{ true false } ] #:nodoc:
  
    @@regexp = Regexp.new('\A' + WHITESPACES + "(#{TOKENS.first.join('|')})")
    
    #
    # Creates a new Boolean value.
    # _value_:: *true* or *false*.
    #
    def initialize(value, indirect = false)
      
      unless value.is_a?(TrueClass) or value.is_a?(FalseClass)
        raise TypeError, "Expected type TrueClass or FalseClass, received #{value.class}."
      end
      
      super(indirect)
      
      @value = (value == nil || value == false) ? false : true
      
    end
    
    def to_s #:nodoc:
      print(@value.to_s)
    end
    
    def self.parse(stream) #:nodoc:
    
      if stream.scan(@@regexp).nil?
        raise InvalidBoolean
      end

      value = stream[2] == "true" ? true : false
        
      Boolean.new(value)
    end
    
    #
    # Converts self into a Ruby boolean, that is TrueClass or FalseClass instance.
    #
    def value
      @value
    end

    def real_type ; Boolean end
    
    def false?
      value == false
    end
    
    def true?
      value == true
    end

  end

end
