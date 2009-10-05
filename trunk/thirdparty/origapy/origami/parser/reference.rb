=begin

= File
	reference.rb

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

  class InvalidReference < Exception #:nodoc:
  end

  #
  # Class representing a Reference Object.
  # Reference are like symbolic links pointing to a particular object into the file.
  #
  class Reference
    
    include Origami::Object

    TOKENS = [ "(\\d+)" + WHITESPACES +  "(\\d+)" + WHITESPACES + "R" ] #:nodoc:
    
    @@regexp = Regexp.new('\A' + WHITESPACES + TOKENS.first + WHITESPACES)
    
    attr_accessor :refno, :refgen
    
    def initialize(refno, refgen)
      @refno, @refgen = refno, refgen
    end
    
    def self.parse(stream) #:nodoc:
      
      if stream.scan(@@regexp).nil?
        raise InvalidReference, "Bad reference to indirect objet format"
      end
      
      refno = stream[2].to_i
      refgen = stream[3].to_i
       
      Reference.new(refno,refgen)
    end
    
    def solve
      
      pdfdoc = self.pdf

      if pdfdoc.nil?
        raise InvalidReference, "Not attached to any PDF"
      end
      
      target = pdfdoc.get_object(self)
      
      if target.nil?
        raise InvalidReference, "Cannot resolve reference"
      end

      target
    end
    
    def eql?(ref) #:nodoc
      ref.refno == @refno and ref.refgen == @refgen
    end
    
    def hash #:nodoc:
      self.to_a.hash
    end
    
    def <=>(ref) #:nodoc
      self.to_a <=> ref.to_a
    end
    
    #
    # Returns a Ruby array with the object number and the generation this reference is pointing to.
    #
    def to_a
      [@refno, @refgen]
    end
    
    def to_s #:nodoc:
      print("#{@refno} #{@refgen} R")
    end
    
    #
    # Returns self.
    #
    def value
      self
    end

    def real_type ; Reference end

  end

end
