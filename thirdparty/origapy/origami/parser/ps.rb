=begin

= File
	ps.rb

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

  module PS
  
    class Text
    
      DEFAULT_SIZE = 12
      DEFAULT_FONT = :F1
      DEFAULT_LINESPACING = 20
    
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
    
      attr_accessor :buffer
      attr_accessor :x, :y
      attr_accessor :word_spacing, :char_spacing, :line_spacing
      attr_accessor :scale, :rise, :rendering
      attr_accessor :font, :size
      
      def initialize(text = "", attr = {})
      
        @x = attr.include?(:x) ? attr[:x] : 0
        @y = attr.include?(:y) ? attr[:y] : 0
        
        @font = attr.include?(:font) ? attr[:font] : DEFAULT_FONT
        @size = attr.include?(:size) ? attr[:size] : DEFAULT_SIZE
        
        @line_spacing = attr.include?(:line_spacing) ? attr[:line_spacing] : DEFAULT_LINESPACING
        
        @word_spacing = attr[:word_spacing]
        @char_spacing = attr[:char_spacing]
        @scale = attr[:scale]
        @rise = attr[:rise]
        @rendering = attr[:rendering]
        
        @buffer = text
        
      end
      
      def to_s
      
        lines = buffer.split("\n").map!{|line| line.to_o.to_s}
        
        text = lines.slice!(0) + " Tj " + lines.join(" ' ") 
        text << " ' " unless lines.empty?
      
        data = "BT\n#{@font.to_o} #{@size} Tf #{@x} #{@y} Td #{@line_spacing} TL\n"
        data << "#{@rendering} Tr " unless @rendering.nil?
        data << "#{@rise} Ts " unless @rise.nil?
        data << "#{@scale} Tz " unless @scale.nil?
        data << "#{@word_spacing} Tw " unless @word_spacing.nil?
        data << "#{@char_spacing} Tc " unless @char_spacing.nil?
        data << "#{text}\nET"
        
        data
      end
      
    end
    
  end

end
