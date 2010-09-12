=begin

= File
	graphics/instruction.rb

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

  class InvalidPDFInstructionError < Exception ; end
  class PDF::Instruction
    attr_reader :operator
    attr_accessor :operands

    @@regexp = Regexp.new('([^ \\t\\r\\n\\0\\[\\]<>()%\\/]+)')
    @insns = Hash.new(:operands => [], :proc => lambda{}, :callback => lambda{})

    def initialize(operator, *operands)
      @operator = operator
      @operands = operands.map!{|arg| arg.value}

      if self.class.has_op?(operator)
        opdef = self.class.get_operands(operator)

        if opdef.size != operands.size
          raise InvalidPDFInstructionError, 
            "Numbers of operands mismatch for #{operator}: #{operands.inspect}"
        end
      end
    end

    def update_state(gs)
      self.class.get_proc(@operator)[gs, *operands] if self.class.has_proc?(@operator)
      self
    end

    def render
    end

    def exec(gs)
      update_state(gs)
      self.class.get_callback(@operator)[gs] if self.class.has_callback?(@operator)

      self
    end

    def to_s
      "#{operands.map!{|op| op.to_o.to_s}.join(' ')}#{' ' unless operands.empty?}#{operator}\n"
    end

    class << self
      def insn(operator, *operands, &p)
        @insns[operator] = {}
        @insns[operator][:operands] = operands
        @insns[operator][:proc] = p if block_given?
      end

      def has_op?(operator)
        @insns.has_key? operator
      end

      def has_proc?(operator)
        self.has_op?(operator) and @insns[operator].has_key?(:proc)
      end

      def has_callback?(operator)
        self.has_op?(operator) and @insns[operator].has_key?(:callback)
      end

      def set_callback(operator, &b)
        raise RuntimeError, "Operator `#{operator}' does not exist" unless @insns.has_key?(operator)
        @insns[operator][:callback] = b
      end

      def get_proc(operator)
        @insns[operator][:proc]
      end

      def get_operands(operator)
        @insns[operator][:operands]
      end

      def parse(stream)
        operands = []
        while type = Object.typeof(stream, true)
          operands.unshift type.parse(stream)
        end
        
        if not stream.eos?
          if stream.scan(@@regexp).nil?
            raise InvalidPDFInstructionError, 
              "Operator: #{(stream.peek(10) + '...').inspect}"
          end

          operator = stream[1]
          PDF::Instruction.new(operator, *operands)
        else
          if not operands.empty?
            raise InvalidPDFInstructionError,
              "No operator given for operands: #{operands.join}"
          end
        end
      end
    end

  end
end

