=begin

= File
	graphics/xobject.rb

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

  #
  # A class representing a Stream containing the contents of a Page.
  #
  class ContentStream < Stream
    
    DEFAULT_SIZE = 12
    DEFAULT_FONT = :F1
    DEFAULT_LEADING = 20
    DEFAULT_STROKE_COLOR = Graphics::Color::GrayScale.new(0.0)
    DEFAULT_FILL_COLOR = Graphics::Color::GrayScale.new(1.0)
    DEFAULT_LINECAP = Graphics::LineCapStyle::BUTT_CAP
    DEFAULT_LINEJOIN = Graphics::LineJoinStyle::MITER_JOIN
    DEFAULT_DASHPATTERN = Graphics::DashPattern.new([], 0)
    DEFAULT_LINEWIDTH = 1.0

    attr_reader :instructions
    
    def initialize(rawdata = "", dictionary = {})
    
      @instructions = nil
      @gs = Graphics::State.new

      super(rawdata, dictionary)
    end

    def instructions
      load! if @instructions.nil?

      @instructions
    end

    #
    # Draw a straight line from the point at coord _from_, to the point at coord _to_.
    #
    def draw_line(from, to, attr = {})
      draw_polygon([from, to], attr)
    end

    #
    # Draw a polygon from a array of coordinates.
    #
    def draw_polygon(coords = [], attr = {})
      load! if @instructions.nil?

      stroke_color  = attr[:stroke_color] || DEFAULT_STROKE_COLOR
      fill_color    = attr[:fill_color] || DEFAULT_FILL_COLOR
      line_cap      = attr[:line_cap] || DEFAULT_LINECAP
      line_join     = attr[:line_join] || DEFAULT_LINEJOIN
      line_width    = attr[:line_width] || DEFAULT_LINEWIDTH
      dash_pattern  = attr[:dash] || DEFAULT_DASHPATTERN

      stroke        = attr[:stroke].nil? ? true : attr[:stroke]
      fill          = attr[:fill].nil? ? false : attr[:fill]

      stroke = true if fill == false and stroke == false 

      set_fill_color(fill_color) if fill
      set_stroke_color(stroke_color) if stroke
      set_line_width(line_width)
      set_line_cap(line_cap)
      set_line_join(line_join)
      set_dash_pattern(dash_pattern)
   
      if @gs.text_state.is_in_text_object?
        @instructions << PDF::Instruction.new('ET').update_state(@gs)
      end

      unless coords.size < 1
        x,y = coords.slice!(0)
        @instructions << PDF::Instruction.new('m',x,y).update_state(@gs)

        coords.each do |px,py|
          @instructions << PDF::Instruction.new('l',px,py).update_state(@gs)
        end

        @instructions << (i =
          if stroke and not fill
            PDF::Instruction.new('s')
          elsif fill and not stroke
            PDF::Instruction.new('f')
          elsif fill and stroke
            PDF::Instruction.new('b')
          end
        )

        i.update_state(@gs)
      end

      self
    end

    #
    # Draw a rectangle at position (_x_,_y_) with defined _width_ and _height_.
    #
    def draw_rectangle(x, y, width, height, attr = {})
      load! if @instructions.nil?

      stroke_color  = attr[:stroke_color] || DEFAULT_STROKE_COLOR
      fill_color    = attr[:fill_color] || DEFAULT_FILL_COLOR
      line_cap      = attr[:line_cap] || DEFAULT_LINECAP
      line_join     = attr[:line_join] || DEFAULT_LINEJOIN
      line_width    = attr[:line_width] || DEFAULT_LINEWIDTH
      dash_pattern  = attr[:dash] || DEFAULT_DASHPATTERN

      stroke        = attr[:stroke].nil? ? true : attr[:stroke]
      fill          = attr[:fill].nil? ? false : attr[:fill]

      stroke = true if fill == false and stroke == false 

      set_fill_color(fill_color) if fill
      set_stroke_color(stroke_color) if stroke
      set_line_width(line_width)
      set_line_cap(line_cap)
      set_line_join(line_join)
      set_dash_pattern(dash_pattern)

      if @gs.text_state.is_in_text_object?
        @instructions << PDF::Instruction.new('ET').update_state(@gs)
      end

      @instructions << PDF::Instruction.new('re', x,y,width,height).update_state(@gs)
  
      @instructions << (i =
        if stroke and not fill
          PDF::Instruction.new('S')
        elsif fill and not stroke
          PDF::Instruction.new('f')
        elsif fill and stroke
          PDF::Instruction.new('B')
        end
      )

      i.update_state(@gs)
      
      self
    end

    #
    # Adds text to the content stream with custom formatting attributes.
    # _text_:: Text to write.
    # _attr_:: Formatting attributes.
    #
    def write(text, attr = {})
      load! if @instructions.nil?

      x,y       = attr[:x], attr[:y] 
      font      = attr[:font] || DEFAULT_FONT
      size      = attr[:size] || DEFAULT_SIZE
      leading   = attr[:leading] || DEFAULT_LEADING
      color     = attr[:color] || attr[:fill_color] || DEFAULT_STROKE_COLOR
      stroke_color = attr[:stroke_color] || DEFAULT_STROKE_COLOR
      line_width    = attr[:line_width] || DEFAULT_LINEWIDTH
      word_spacing  = attr[:word_spacing]
      char_spacing  = attr[:char_spacing]
      scale     = attr[:scale]
      rise      = attr[:rise]
      rendering = attr[:rendering]

      @instructions << PDF::Instruction.new('ET').update_state(@gs) if (x or y) and @gs.text_state.is_in_text_object?

      unless @gs.text_state.is_in_text_object? 
        @instructions << PDF::Instruction.new('BT').update_state(@gs)
      end

      set_text_font(font, size)
      set_text_pos(x, y) if x or y
      set_text_leading(leading) if leading
      set_text_rendering(rendering) if rendering
      set_text_rise(rise) if rise
      set_text_scale(scale) if scale
      set_text_word_spacing(word_spacing) if word_spacing
      set_text_char_spacing(char_spacing) if char_spacing
      set_fill_color(color)
      set_stroke_color(stroke_color) 
      set_line_width(line_width)

      write_text_block(text)
     
      self
    end

    def paint_shading(shade)
      load! if @instructions.nil?
      @instructions << PDF::Instruction.new('sh', shade).update_state(@gs)

      self
    end

    def set_text_font(fontname, size)
      load! if @instructions.nil?
      if fontname != @gs.text_state.font or size != @gs.text_state.font_size
        @instructions << PDF::Instruction.new('Tf', fontname, size).update_state(@gs)
      end

      self
    end

    def set_text_pos(tx,ty)
      load! if @instructions.nil?
      @instructions << PDF::Instruction.new('Td', tx, ty).update_state(@gs)
      
      self
    end

    def set_text_leading(leading)
      load! if @instructions.nil?
      if leading != @gs.text_state.leading
        @instructions << PDF::Instruction.new('TL', leading).update_state(@gs)
      end

      self
    end

    def set_text_rendering(rendering)
      load! if @instructions.nil?
      if rendering != @gs.text_state.rendering_mode
        @instructions << PDF::Instruction.new('Tr', rendering).update_state(@gs)
      end

      self
    end

    def set_text_rise(rise)
      load! if @instructions.nil?
      if rise != @gs.text_state.text_rise
        @instructions << PDF::Instruction.new('Ts', rise).update_state(@gs)
      end
      
      self
    end

    def set_text_scale(scaling)
      load! if @instructions.nil?
      if scale != @gs.text_state.scaling
        @instructions << PDF::Instruction.new('Tz', scaling).update_state(@gs)
      end

      self
    end

    def set_text_word_spacing(word_spacing)
      load! if @instructions.nil?
      if word_spacing != @gs.text_state.word_spacing
        @instructions << PDF::Instruction.new('Tw', word_spacing).update_state(@gs)
      end
      
      self
    end

    def set_text_char_spacing(char_spacing)
      load! if @instructions.nil?
      if char_spacing != @gs.text_state.char_spacing
        @instructions << PDF::Instruction.new('Tc', char_spacing).update_state(@gs)
      end

      self
    end

    def set_fill_color(color)
      load! if @instructions.nil?
      
      @instructions << ( i =
        if (color.respond_to? :r and color.respond_to? :g and color.respond_to? :b) or (color.is_a?(::Array) and color.size == 3)
          r = (color.respond_to?(:r) ? color.r : color[0]).to_f / 255
          g = (color.respond_to?(:g) ? color.g : color[1]).to_f / 255
          b = (color.respond_to?(:b) ? color.b : color[2]).to_f / 255
          PDF::Instruction.new('rg', r, g, b) if @gs.nonstroking_color != [r,g,b]

        elsif (color.respond_to? :c and color.respond_to? :m and color.respond_to? :y and color.respond_to? :k) or (color.is_a?(::Array) and color.size == 4)
          c = (color.respond_to?(:c) ? color.c : color[0]).to_f
          m = (color.respond_to?(:m) ? color.m : color[1]).to_f
          y = (color.respond_to?(:y) ? color.y : color[2]).to_f
          k = (color.respond_to?(:k) ? color.k : color[3]).to_f
          PDF::Instruction.new('k', c, m, y, k) if @gs.nonstroking_color != [c,m,y,k]
          
        elsif color.respond_to?:g or (0.0..1.0) === color 
          g = color.respond_to?(:g) ? color.g : color
          PDF::Instruction.new('g', g) if @gs.nonstroking_color != [ g ]

        else
          raise TypeError, "Invalid color : #{color}"
        end
      )

      i.update_state(@gs) if i
      self 
    end
    
    def set_stroke_color(color)
      load! if @instructions.nil?
      
      @instructions << ( i =
        if (color.respond_to? :r and color.respond_to? :g and color.respond_to? :b) or (color.is_a?(::Array) and color.size == 3)
          r = (color.respond_to?(:r) ? color.r : color[0]).to_f / 255
          g = (color.respond_to?(:g) ? color.g : color[1]).to_f / 255
          b = (color.respond_to?(:b) ? color.b : color[2]).to_f / 255
          PDF::Instruction.new('RG', r, g, b) if @gs.stroking_color != [r,g,b]

        elsif (color.respond_to? :c and color.respond_to? :m and color.respond_to? :y and color.respond_to? :k) or (color.is_a?(::Array) and color.size == 4)
          c = (color.respond_to?(:c) ? color.c : color[0]).to_f
          m = (color.respond_to?(:m) ? color.m : color[1]).to_f
          y = (color.respond_to?(:y) ? color.y : color[2]).to_f
          k = (color.respond_to?(:k) ? color.k : color[3]).to_f
          PDF::Instruction.new('K', c, m, y, k) if @gs.stroking_color != [c,m,y,k]
          
        elsif color.respond_to?:g or (0.0..1.0) === color 
          g = color.respond_to?(:g) ? color.g : color
          PDF::Instruction.new('G', g) if @gs.stroking_color != [ g ]

        else
          raise TypeError, "Invalid color : #{color}"
        end
      )

      i.update_state(@gs) if i
      self 
    end

    def set_dash_pattern(pattern)
      load! if @instructions.nil?
      unless @gs.dash_pattern.eql? pattern
        @instructions << PDF::Instruction.new('d', pattern.array, pattern.phase).update_state(@gs)
      end

      self
    end

    def set_line_width(width)
      load! if @instructions.nil?
      if @gs.line_width != width
        @instructions << PDF::Instruction.new('w', width).update_state(@gs)
      end

      self
    end

    def set_line_cap(cap)
      load! if @instructions.nil?
      if @gs.line_cap != cap
        @instructions << PDF::Instruction.new('J', cap).update_state(@gs)
      end

      self
    end
    
    def set_line_join(join)
      load! if @instructions.nil?
      if @gs.line_join != join
        @instructions << PDF::Instruction.new('j', join).update_state(@gs)
      end

      self
    end

    def pre_build #:nodoc:
      load! if @instructions.nil?
      if @gs.text_state.is_in_text_object?
        @instructions << PDF::Instruction.new('ET').update_state(@gs)
      end

      @data = @instructions.join
      
      super
    end

    private

    def load!
      decode!

      code = StringScanner.new self.data
      @instructions = []
      @instructions << PDF::Instruction.parse(code) until code.eos?
      
      self
    end

    def write_text_block(text)
      
      lines = text.split("\n").map!{|line| line.to_s}
      
      @instructions << PDF::Instruction.new('Tj', lines.slice!(0)).update_state(@gs)
      lines.each do |line|
        @instructions << PDF::Instruction.new("'", line).update_state(@gs)
      end
      
    end
    
  end #class ContentStream

  module Graphics

    module XObject
      def self.included(receiver)
        receiver.field  :Type,    :Type => Name, :Default => :XObject
      end
    end

    class FormXObject < ContentStream
      include XObject

      field   :Subtype,       :Type => Name, :Default => :Form, :Required => true
      field   :FormType,      :Type => Integer, :Default => 1
      field   :BBox,          :Type => Array, :Required => true
      field   :Matrix,        :Type => Array, :Default => [1, 0, 0, 1, 0, 0]
      field   :Resources,     :Type => Dictionary, :Version => "1.2"
      field   :Group,         :Type => Dictionary, :Version => "1.4"
      field   :Ref,           :Type => Dictionary, :Version => "1.4"
      field   :Metadata,      :Type => Stream, :Version => "1.4"
      field   :PieceInfo,     :Type => Dictionary, :Version => "1.3"
      field   :LastModified,  :Type => String, :Version => "1.3"
      field   :StructParent,  :Type => Integer, :Version => "1.3"
      field   :StructParents, :Type => Integer, :Version => "1.3"
      field   :OPI,           :Type => Dictionary, :Version => "1.2"
      field   :OC,            :Type => Dictionary, :Version => "1.5"
      field   :Name,          :Type => Name
      field   :Measure,       :Type => Dictionary, :Version => "1.7", :ExtensionLevel => 3
      field   :PtData,        :Type => Dictionary, :Version => "1.7", :ExtensionLevel => 3

      def pre_build
        self.Resources = Resources.new.pre_build unless has_field?(:Resources)

        super
      end

    end

    class ImageXObject < Stream
      include XObject

      field   :Subtype,           :Type => Name, :Default => :Image, :Required => true
      field   :Width,             :Type => Integer, :Required => true
      field   :Height,            :Type => Integer, :Required => true
      field   :ColorSpace,        :Type => [ Name, Array ]
      field   :BitsPerComponent,  :Type => Integer
      field   :Intent,            :Type => Name, :Version => "1.1"
      field   :ImageMask,         :Type => Boolean, :Default => false
      field   :Mask,              :Type => [ Stream, Array ], :Version => "1.3"
      field   :Decode,            :Type => Array
      field   :Interpolate,       :Type => Boolean, :Default => false
      field   :Alternates,        :Type => Array, :Version => "1.3"
      field   :SMask,             :Type => Stream, :Version => "1.4"
      field   :SMaskInData,       :Type => Integer, :Default => 0, :Version => "1.5"
      field   :Name,              :Type => Name
      field   :StructParent,      :Type => Integer, :Version => "1.3"
      field   :ID,                :Type => String, :Version => "1.3"
      field   :OPI,               :Type => Dictionary, :Version => "1.2"
      field   :Metadata,          :Type => Stream, :Version => "1.4"
      field   :OC,                :Type => Dictionary, :Version => "1.5"
      field   :Measure,           :Type => Dictionary, :Version => "1.7", :ExtensionLevel => 3
      field   :PtData,            :Type => Dictionary, :Version => "1.7", :ExtensionLevel => 3

    end

    class ReferenceDictionary < Dictionary
      include Configurable

      field   :F,             :Type => Dictionary, :Required => true
      field   :Page,          :Type => [Integer, String], :Required => true
      field   :ID,            :Tyoe => Array
    end

  end

end

