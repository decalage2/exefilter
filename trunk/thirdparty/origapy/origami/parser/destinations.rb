=begin

= File
	destinations.rb

= Info
	This file is part of Origami, PDF manipulation framework for Ruby
	Copyright (C) 2009	Guillaume Delugr» <guillaume@security-labs.org>
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

  

  #
  # A destination represents a specified location into the document.
  #
  module Destination
    
    attr_reader :top, :left, :right, :bottom, :zoom
  
    #
    # Class representing a Destination zooming on a part of a document.
    #
    class Zoom < Origami::Array
      
      include Destination
      
      #
      # Creates a new zoom Destination.
      # _pageref_:: A Reference to a Page.
      # _left_, _top_:: Coords in the Page.
      # _zoom_:: Zoom factor.
      #
      def initialize(pageref, left = 0, top = 0, zoom = 0, indirect = false)
        
        @left, @top, @zoom = left, top, zoom
        
        super([pageref, :XYZ, left, top, zoom], indirect)
        
      end
      
    end
    
    #
    # Class representing a Destination showing a Page globally.
    #
    class GlobalFit < Origami::Array
      
      include Destination
      
      #
      # Creates a new global fit Destination.
      # _pageref_:: A Reference to a Page.
      #
      def initialize(pageref,  indirect = false)
        super([pageref, :Fit], indirect)
      end
      
    end
    
    #
    # Class representing a Destination fitting a Page horizontally.
    #
    class HorizontalFit < Origami::Array
      
      include Destination
      
      #
      # Creates a new horizontal fit destination.
      # _pageref_:: A Reference to a Page.
      # _top_:: The vertical coord in the Page.
      #
      def initialize(pageref, top = 0, indirect = false)
        
        @top = top
        super([pageref, :FitH, top], indirect)
        
      end
    
    end

    #
    # Class representing a Destination fitting a Page vertically.
    # _pageref_:: A Reference to a Page.
    # _left_:: The horizontal coord in the Page.
    #
    class VerticalFit < Origami::Array
      
      include Destination
      
      def initialize(pageref, left = 0, indirect = false)
        
        @left = left
        super([pageref, :FitV, left], indirect)
        
      end
      
    end
    
    #
    # Class representing a Destination fitting the view on a rectangle in a Page.
    #
    class RectangleFit < Origami::Array
      
      include Destination
      
      #
      # Creates a new rectangle fit Destination.
      # _pageref_:: A Reference to a Page.
      # _left_, _bottom_, _right_, _top_:: The rectangle to fit in.
      #
      def initialize(pageref, left = 0, bottom = 0, right = 0, top = 0, indirect = false)
        
        @left, @bottom, @right, @top = left, bottom, right, top
        super([pageref, :FitR, left, bottom, right, top], indirect)
        
      end
      
    end
    
    #
    # Class representing a Destination fitting the bounding box of a Page.
    #
    class GlobalBoundingBoxFit < Origami::Array
      
      include Destination
      
      #
      # Creates a new bounding box fit Destination.
      # _pageref_:: A Reference to a Page.
      #
      def initialize(pageref, indirect = false)
        super([pageref, :FitB], indirect)
      end
      
    end
    
    #
    # Class representing a Destination fitting horizontally the bouding box a Page.
    #
    class HorizontalBoudingBoxFit < Origami::Array
      
      include Destination
      
      #
      # Creates a new horizontal bounding box fit Destination.
      # _pageref_:: A Reference to a Page.
      # _top_:: The vertical coord.
      #
      def initialize(pageref, top = 0, indirect = false)
        
        @top = top
        super([pageref, :FitBH, top], indirect)
        
      end
      
    end
    
    #
    # Class representing a Destination fitting vertically the bounding box of a Page.
    #
    class VerticalBoundingBoxFit < Origami::Array
      
      include Destination
      
      #
      # Creates a new vertical bounding box fit Destination.
      # _pageref_:: A Reference to a Page.
      # _left_:: The horizontal coord.
      #
      def initialize(pageref, left = 0, indirect = false)
        
        @left = left
        super([pageref, :FitBV, left], indirect)
      
      end
    
    end
    
  end

end
