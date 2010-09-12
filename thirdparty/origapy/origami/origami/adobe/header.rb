=begin

= File
	adobe/header.rb

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

  module Adobe
  
    class InvalidHeader < Exception #:nodoc:
    end

    class AddressBook
      
      #
      # Class representing a certificate store header.
      #
      class Header

        MAGIC = /\A%PPKLITE-(\d)\.(\d)/
        
        attr_accessor :majorversion, :minorversion
        
        #
        # Creates a file header, with the given major and minor versions.
        # _majorversion_:: Major version.
        # _minorversion_:: Minor version.
        #
        def initialize(majorversion = 2, minorversion = 1)
          
          @majorversion, @minorversion = majorversion, minorversion
          
        end
        
        def self.parse(stream) #:nodoc:
          
          if not stream.scan(MAGIC).nil?
            maj = stream[1].to_i
            min = stream[2].to_i
          else
            raise InvalidHeader, "Invalid header format"
          end
          
          AddressBook::Header.new(maj,min)
        end
        
        #
        # Outputs self into PDF code.
        #
        def to_s
          "%PPKLITE-#{@majorversion}.#{@minorversion}" + EOL
        end
        
        def to_sym #:nodoc:
          "#{@majorversion}.#{@minorversion}".to_sym
        end
        
        def to_f #:nodoc:
          to_sym.to_s.to_f
        end
      
      end

    end
  
  end
  
end
