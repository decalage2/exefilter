=begin

= File
	fdf.rb

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

require 'object.rb'
require 'name.rb'
require 'dictionary.rb'
require 'reference.rb'
require 'boolean.rb'
require 'numeric.rb'
require 'string.rb'
require 'array.rb'
require 'stream.rb'
require 'trailer.rb'
require 'xreftable.rb'
require 'header.rb'
require 'catalog.rb'
require 'page.rb'
require 'misc.rb'
require 'destinations.rb'
require 'actions.rb'
require 'file.rb'
require 'acroform.rb'
require 'annotations.rb'
require 'signature.rb'
require 'webcapture.rb'

require 'openssl'

module Origami

  class FDF

    #
    # TODO: 
    #
    # add a real parser. This class is currently useless except to
    # create empty FDF and add some items, not to parse old ones. 
    #
    attr_accessor :filename
    
    attr_accessor :header, :bin, :body, :xreftable, :trailer

    def initialize(hdr = "%FDF-1.2", bin="%\x25\xe3\xcf\xd3" body = [], xref = [], trailer="") 
      @header = hdr
      @bin = bin
      @body = body
      @xreftable = xref
      @trailer = traier
    end
    

  end




end
