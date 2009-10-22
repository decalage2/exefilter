=begin

= File
	graphics/instruction.rb

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

  module PDF::Instruction
    attr_accessor :operator
    attr_accessor :operands

    def initialize(operator, *operands)
      @operator = operator
      @operands = operands
    end

    def to_s
      "#{operands.map!{|op| op.to_o.to_s}.join(' ')}#{' ' unless operands.empty?}#{operator}\n"
    end

    def update_state(gs); self end
  end

end

