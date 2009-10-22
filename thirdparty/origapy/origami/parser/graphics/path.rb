=begin

= File
	graphics/path.rb

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

  module Graphics

    module LineCapStyle
      BUTT_CAP              = 0
      ROUND_CAP             = 1
      PROJECTING_SQUARE_CAP = 2
    end

    module LineJoinStyle
      MITER_JOIN = 0
      ROUND_JOIN = 1
      BEVEL_JOIN = 2
    end

    class DashPattern
      attr_accessor :array, :phase

      def initialize(array, phase = 0)
        @array = array
        @phase = phase
      end

      def eql?(dash) #:nodoc
        dash.array == @array and dash.phase == @phase
      end
      
      def hash #:nodoc:
        [ @array, @phase ].hash
      end
    end

    class Path

      module Segment
        attr_accessor :from, :to

        def initialize(from, to)
          @from, @to = from, to
        end
      end

      class Line
        include Segment 
      end
  
      attr_accessor :current_point
      attr_reader :segments

      def initialize
        @segments = []
        @current_point = nil
        @closed = false
      end

      def is_closed?
        @closed
      end

      def close!
        from = @current_point
        to = @segments.first.from
        
        @segments << Line.new(from, to)
        @segments.freeze
        @closed = true
      end

      def add_segment(seg)
        raise GraphicsStateError, "Cannot modify closed subpath" if is_closed?

        @segments << seg
        @current_point = seg.to
      end

    end

    module Instruction

      class D
        include PDF::Instruction
        def initialize(array, phase); super('d', array, phase) end

        def update_state(gs)
          gs.dash_pattern = DashPattern.new(@operands[0], @operands[1])
          self
        end
      end

      class W
        include PDF::Instruction
        def initialize(width); super('w', width) end

        def update_state(gs)
          gs.line_width = @operands[0]
          self
        end
      end

      class JCap
        include PDF::Instruction
        def initialize(cap); super('J', cap) end

        def update_state(gs)
          gs.line_cap = @operands[0]
          self
        end
      end

      class JJoin
        include PDF::Instruction
        def initialize(join); super('j', join) end

        def update_state(gs)
          gs.line_join = @operands[0]
          self
        end
      end

      class M
        include PDF::Instruction
        def initialize(x,y); super('m', x, y) end

        def update_state(gs)
          gs.current_path << (subpath = Path.new)

          subpath.current_point = @operands
          self
        end
      end

      class L
        include PDF::Instruction
        def initialize(x,y); super('l', x, y) end

        def update_state(gs)
          if gs.current_path.empty? 
            raise GraphicsStateError, "No current point is defined"
          end

          subpath = gs.current_path.last

          from = subpath.current_point
          to = @operands
          subpath.add_segment(Path::Line.new(from, to))
          self
        end
      end

      class H
        include PDF::Instruction
        def initialize; super('h') end

        def update_state(gs)
          unless gs.current_path.empty?
            subpath = gs.current_path.last
            subpath.close! unless subpath.is_closed?
          end
          self
        end
      end

      class RE
        include PDF::Instruction
        def initialize(x,y,width,height); super('re', x,y,width,height) end

        def update_state(gs)
          x,y,width,height = @operands
          tx = x + width
          ty = y + height
          gs.current_path << (subpath = Path.new)
          subpath.segments << Path::Line.new([x,y], [tx,y])
          subpath.segments << Path::Line.new([tx,y], [tx, ty])
          subpath.segments << Path::Line.new([tx, ty], [x, ty])
          subpath.close!
          self
        end
      end

      class S
        include PDF::Instruction
        def initialize; super('S') end
      end

      class CloseS
        include PDF::Instruction
        def initialize; super('s') end

        def update_state(gs)
          gs.current_path.last.close!
          self
        end
      end
      
      class F
        include PDF::Instruction
        def initialize; super('f') end
      end

      class FStar
        include PDF::Instruction
        def initialize; super('f*') end
      end

      class B
        include PDF::Instruction
        def initialize; super('B') end
      end

      class BStar
        include PDF::Instruction
        def initialize; super('B*') end
      end 

      class CloseB
        include PDF::Instruction
        def initialize; super('b') end

        def update_state(gs)
          gs.current_path.last.close!
          self
        end
      end

      class CloseBStar
        include PDF::Instruction
        def initialize; super('b*') end
      end 

      class N
        include PDF::Instruction
        def initialize; super('n') end
      end 

    end

  end

end
