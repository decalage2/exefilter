=begin

= File
	null.rb

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

module Origami

  class InvalidNull < InvalidObject #:nodoc:
  end
  
  #
  # Class representing  Null Object.
  #
  class Null
    
    include Origami::Object
    
    TOKENS = %w{ null } #:nodoc:
    
    @@regexp = Regexp.new('\A' + WHITESPACES + TOKENS.first)
    
    def initialize(indirect = false)
      super(indirect)
    end
    
    def self.parse(stream) #:nodoc:
      
      if stream.skip(@@regexp).nil?
        raise InvalidNull
      end
      
      Null.new
    end
    
    #
    # Returns *nil*.
    #
    def value
      nil
    end
    
    def to_s #:nodoc:
      print(TOKENS.first)
    end

    def real_type ; Null end
    
  end
  
end
