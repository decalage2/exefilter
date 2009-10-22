=begin

= File
	dictionary.rb

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

    class InvalidDictionary < InvalidObject #:nodoc:
    end
  
    #
    # Class representing a Dictionary Object.
    # Dictionaries are containers associating a Name to an embedded Object.
    #
    class Dictionary < Hash
      
      include Origami::Object
    
      TOKENS = %w{ << >> } #:nodoc:
      
      @@regexp_open = Regexp.new('\A' + WHITESPACES + Regexp.escape(TOKENS.first) + WHITESPACES)
      @@regexp_close = Regexp.new('\A' + WHITESPACES + Regexp.escape(TOKENS.last) + WHITESPACES)
      #
      # Creates a new Dictionary.
      # _hash_:: The hash representing the new Dictionary.
      #
      def initialize(hash = {})
        
        unless hash.is_a?(Hash)
          raise TypeError, "Expected type Hash, received #{hash.class}."
        end
        
        super()
        
        hash.each_key { |k|
          self[k.to_o] = hash[k].to_o unless k.nil?
        }
        
      end
      
      def self.parse(stream) #:nodoc:
        
        pairs = {}
        
        if stream.skip(@@regexp_open).nil?
          raise InvalidDictionary, "No token '#{TOKENS.first}' found"
        end
          
        while stream.skip(@@regexp_close).nil? do
        
          #unless Object.typeof(stream) == Name
          #  raise InvalidDictionary, "Key value must be declared as name"
          #end
          
          key = Name.parse(stream)
          
          type = Object.typeof(stream)
          if type.nil?
            raise InvalidDictionary, "Cannot determine value type for field #{key.to_s}"
          end

          value = type.parse(stream)
          
          pairs[key.value] = value
        
        end
        
        if pairs[:Type] and @@dict_special_types.include?(pairs[:Type].value)
          return @@dict_special_types[pairs[:Type].value].new(pairs)
        else
          return Dictionary.new(pairs)
        end
        
      end
      
      alias to_h to_hash
      
      def to_s(base = 1)  #:nodoc:
        
        content = TOKENS.first + EOL
        self.each_pair { |key,value|
          content << "\t" * base + key.to_s + " " + (value.is_a?(Dictionary) ? value.to_s(base+1) : value.to_s) + EOL
        }
        
        content << "\t" * (base-1) + TOKENS.last
        
        super(content)
      end
      
      def map!(&b)
        
        self.each_pair { |k,v|
          self[k] = b.call(v)
        }
        
      end

      def merge(dict)
        Dictionary.new(super(dict))
      end
      
      def []=(key,val)
        
        unless key.is_a?(Symbol) or key.is_a?(Name)
          fail "Expecting a Name for a Dictionary entry, found #{key.class} instead."
        end
        
        key = key.to_o
        if not val.nil?
          val = val.to_o
          super(key,val)
        
          val.parent = self

          val
        else
          delete(key)
        end
      end
      
      def [](key)
        super(key.to_o)
      end

      def has_key?(key)
        super(key.to_o)
      end

      def delete(key)
        super(key.to_o)
      end

      alias each each_value

      def real_type ; Dictionary end

      alias value to_h
    
    end #class
 
end # Origami
