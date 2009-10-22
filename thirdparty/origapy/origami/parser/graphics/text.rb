=begin

= File
	graphics/text.rb

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
  
  module Text

    OPERATORS =
    [
      'Tc', 'Tw', 'Tz', 'TL', 'Tf', 'Tr', 'Ts', # Text state
      'BT', 'ET', # Text objects
      'Td', 'TD', 'Tm', 'T*', # Positioning
      'Tj', "'", '"', 'TJ' # Showing
    ]
    
    module Rendering
      FILL                      = 0
      STROKE                    = 1
      FILL_AND_STROKE           = 2
      INVISIBLE                 = 3
      FILL_AND_CLIP             = 4
      STROKE_AND_CLIP           = 5
      FILL_AND_STROKE_AND_CLIP  = 6
      CLIP                      = 7
    end

    class TextStateError < Exception #:nodoc:
    end

    class State

      attr_accessor :char_spacing, :word_spacing, :scaling, :leading
      attr_accessor :font, :font_size
      attr_accessor :rendering_mode
      attr_accessor :text_rise, :text_knockout

      attr_accessor :text_matrix, :text_line_matrix, :text_rendering_matrix

      def initialize
        self.reset
      end

      def reset
        
        @char_spacing = 0
        @word_spacing = 0
        @scaling = 100
        @leading = 0
        @font = nil
        @font_size = nil
        @rendering_mode = Rendering::FILL
        @text_rise = 0
        @text_knockout = true

        #
        # Text objects
        #

        @text_object = false
        @text_matrix = 
        @text_line_matrix = 
        @text_rendering_matrix = nil

      end

      def is_in_text_object?
        @text_object
      end

      def begin_text_object
        if is_in_text_object?
          raise TextStateError, "Cannot start a text object within an existing text object."
        end

        @text_object = true
        @text_matrix = 
        @text_line_matrix = 
        @text_rendering_matrix = Matrix.identity(3)
      end

      def end_text_object
        unless is_in_text_object?
          raise TextStateError, "Cannot end text object : no previous text object has begun."
        end

        @text_object = false
        @text_matrix = 
        @text_line_matrix = 
        @text_rendering_matrix = nil
      end

    end #class State
    
    module Instruction
      
      class Tc 
        include PDF::Instruction
        def initialize(charSpace); super("Tc", charSpace) end

        def update_state(gs)
          gs.text_state.char_spacing = @operands[0]
          self
        end
      end

      class Tw 
        include PDF::Instruction
        def initialize(wordSpace); super("Tw", wordSpace) end

        def update_state(gs)
          gs.text_state.word_spacing = @operands[0]
          self
        end
      end

      class Tz
        include PDF::Instruction
        def initialize(scale); super("Tz", scale) end

        def update_state(gs)
          gs.text_state.scaling = @operands[0]
          self
        end
      end

      class TL
        include PDF::Instruction
        def initialize(leading); super("TL", leading) end

        def update_state(gs)
          gs.text_state.leading = @operands[0]
          self
        end
      end

      class Tf 
        include PDF::Instruction
        def initialize(font, size); super("Tf", font, size) end
      
        def update_state(gs)
          gs.text_state.font = @operands[0]
          gs.text_state.font_size = @operands[1]
          self
        end
      end

      class Tr
        include PDF::Instruction
        def initialize(render); super("Tr", render) end

        def update_state(gs)
          gs.text_state.rendering_mode = @operands[0]
          self
        end
      end

      class Ts
        include PDF::Instruction
        def initialize(rise); super("Ts", rise) end

        def update_state(gs)
          gs.text_state.text_rise = @operands[0]
          self
        end
      end

      class BT
        include PDF::Instruction
        def initialize; super("BT") end

        def update_state(gs)
          gs.text_state.begin_text_object
          self
        end
      end

      class ET
        include PDF::Instruction
        def initialize; super("ET") end

        def update_state(gs)
          gs.text_state.end_text_object
          self
        end
      end

      class Td
        include PDF::Instruction
        def initialize(tx, ty); super("Td", tx, ty) end

        def update_state(gs)
          unless gs.text_state.is_in_text_object?
            raise TextStateError, "Must be in a text object to use operator : #{@operator}"
          end

          tx, ty = @operands[0], @operands[1]

          gs.text_state.text_matrix =
          gs.text_state.text_line_matrix =
          Matrix.rows([[1,0,0],[0,1,0],[tx, ty, 1]]) * gs.text_state.text_line_matrix
          self
        end
      end

      class TD 
        include PDF::Instruction
        def initialize(tx, ty); super("TD", tx, ty) end

        def update_state(gs)
          unless gs.text_state.is_in_text_object?
            raise TextStateError, "Must be in a text object to use operator : #{@operator}"
          end

          tx, ty = @operands

          gs.text_state.leading = -ty

          gs.text_state.text_matrix =
          gs.text_state.text_line_matrix =
          Matrix.rows([[1,0,0],[0,1,0],[tx,ty,1]]) * gs.text_state.text_line_matrix
          self
        end
      end

      class Tm
        include PDF::Instruction
        def initialize(a,b,c,d,e,f); super("Tm",a,b,c,d,e,f) end

        def update_state(gs)
          unless gs.text_state.is_in_text_object?
            raise TextStateError, "Must be in a text object to use operator : #{@operator}"
          end

          a,b,c,d,e,f = @operands

          gs.text_state.text_matrix =
          gs.text_state.text_line_matrix = 
          Matrix.rows([[a,b,0],[c,d,0],[e,f,1]])
          self
        end
      end

      class TStar
        include PDF::Instruction
        def initialize; super("T*") end

        def update_state(gs)
          unless gs.text_state.is_in_text_object?
            raise TextStateError, "Must be in a text object to use operator : #{@operator}"
          end

          tx, ty = 0, -gs.text_state.leading

          gs.text_state.text_matrix =
          gs.text_state.text_line_matrix =
          Matrix.rows([[1,0,0],[0,1,0],[tx, ty, 1]]) * gs.text_state.text_line_matrix
          self
        end
      end

      class Tj 
        include PDF::Instruction
        def initialize(string); super("Tj", string) end
      end

      class Quote
        include PDF::Instruction
        def initialize(string); super("'", string) end
      end

      class DQuote 
        include PDF::Instruction
        def initialize(aw, ac, string); super('"', aw, ac, string) end
      end

      class TJ
        include PDF::Instruction
        def initialize(array); super("TJ", array) end
      end

    end # module Instruction
    
  end #module Text

end
