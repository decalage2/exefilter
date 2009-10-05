=begin

= File
	linearization.rb

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

  class PDF

    #
    # Returns whether the current document is linearized.
    #
    def is_linearized?
      obj = @revisions.first.body.values.first
      
      obj.is_a?(Dictionary) and obj.has_key? :Linearized
    end   

  end

  #
  # Class representing a linearization dictionary.
  #
  class Linearization < Dictionary

    include Configurable

    field   :Linearized,   :Type => Real, :Default => 1.0, :Required => true
    field   :L,            :Type => Integer, :Required => true
    field   :H,            :Type => Array, :Required => true
    field   :O,            :Type => Integer, :Required => true
    field   :E,            :Type => Integer, :Required => true
    field   :N,            :Type => Integer, :Required => true
    field   :T,            :Type => Integer, :Required => true
    field   :P,            :Type => Integer, :Default => 0

    def initialize(hash = {})
      super(hash, true)
    end

  end

end
