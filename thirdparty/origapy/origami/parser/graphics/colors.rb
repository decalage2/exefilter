=begin

= File
	graphics/colors.rb

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

begin
  require 'color'
rescue LoadError
end

module Origami

  module Graphics

    module RenderingIntent
      ABSOLUTE_COLORIMETRIC = :AbsoluteColorimetric
      RELATIVE_COLORIMETRIC = :RelativeColorimetric
      SATURATION = :Saturation
      PERCEPTUAL = :Perceptual
    end

    module BlendMode
      NORMAL      = :Normal
      COMPATIBLE  = :Compatible
      MULTIPLY    = :Multiply
      SCREEN      = :Screen
      OVERLAY     = :Overlay
      DARKEN      = :Darken
      LIGHTEN     = :Lighten
      COLORDODGE  = :ColorDodge
      COLORBURN   = :ColorBurn
      HARDLIGHT   = :HardLight
      SOFTLIGHt   = :SoftLight
      DIFFERENCE  = :Difference
      EXCLUSION   = :Exclusion
    end

    module Color

      module Space
        DEVICE_GRAY   = :DeviceGray
        DEVICE_RGB    = :DeviceRGB
        DEVICE_CMYK   = :DeviceCMYK
      end

      class GrayScale
        attr_accessor :g

        def initialize(g)
          @g = g
        end
      end

      class RGB
        attr_accessor :r,:g,:b

        def initialize(r,g,b)
          @r,@g,@b = r,g,b
        end
      end

      class CMYK
        attr_accessor :c,:m,:y,:k

        def initialize(c,m,y,k)
          @c,@m,@y,@k = c,m,y,k
        end
      end

      def Color.to_a(color)
        return color if color.is_a?(::Array)
        
        if (color.respond_to? :r and color.respond_to? :g and color.respond_to? :b) 
          r = (color.respond_to?(:r) ? color.r : color[0]).to_f / 255
          g = (color.respond_to?(:g) ? color.g : color[1]).to_f / 255
          b = (color.respond_to?(:b) ? color.b : color[2]).to_f / 255
          return [r, g, b]

        elsif (color.respond_to? :c and color.respond_to? :m and color.respond_to? :y and color.respond_to? :k)
          c = (color.respond_to?(:c) ? color.c : color[0]).to_f
          m = (color.respond_to?(:m) ? color.m : color[1]).to_f
          y = (color.respond_to?(:y) ? color.y : color[2]).to_f
          k = (color.respond_to?(:k) ? color.k : color[3]).to_f
          return [c,m,y,k]
          
        elsif color.respond_to?:g or (0.0..1.0) === color 
          g = color.respond_to?(:g) ? color.g : color
          return [ g ]

        else
          raise TypeError, "Invalid color : #{color}"
        end
      end
    end

    module Instruction

      class StrokeG
        include PDF::Instruction
        def initialize(color); super('G', color) end

        def update_state(gs)
          gs.stroking_colorspace = Color::Space::DEVICE_GRAY
          gs.stroking_color = @operands
          self
        end
      end

      class G
        include PDF::Instruction
        def initialize(color); super('g', color) end

        def update_state(gs)
          gs.nonstroking_colorspace = Color::Space::DEVICE_GRAY
          gs.nonstroking_color = @operands
          self
        end
      end

      class StrokeRG
        include PDF::Instruction
        def initialize(r,g,b); super('RG', r,g,b) end

        def update_state(gs)
          gs.stroking_colorspace = Color::Space::DEVICE_RGB
          gs.stroking_color = @operands
          self
        end
      end
      
      class RG
        include PDF::Instruction
        def initialize(r,g,b); super('rg', r,g,b) end

        def update_state(gs)
          gs.nonstroking_colorspace = Color::Space::DEVICE_RGB
          gs.nonstroking_color = @operands
          self
        end
      end

      class StrokeK
        include PDF::Instruction
        def initialize(c,m,y,k); super('K', c,m,y,k) end

        def update_state(gs)
          gs.stroking_colorspace = Color::Space::DEVICE_CMYK
          gs.stroking_color = @operands
          self
        end
      end
      
      class K
        include PDF::Instruction
        def initialize(c,m,y,k); super('k', c,m,y,k) end

        def update_state(gs)
          gs.nonstroking_colorspace = Color::Space::DEVICE_CMYK
          gs.nonstroking_color = @operands
          self
        end
      end

    end

  end

end
