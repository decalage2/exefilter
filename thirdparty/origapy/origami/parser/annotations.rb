=begin

= File
	annotations.rb

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

  module Annotation
  
    module Triggerable
      
      def onMouseOver(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.E = action
        
      end
      
      def onMouseOut(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.X = action
        
      end
      
      def onMouseDown(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.D = action
        
      end
      
      def onMouseUp(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.U = action
        
      end
      
      def onFocus(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.Fo = action
        
      end
      
      def onBlur(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.Bl = action
        
      end
      
      def onPageOpen(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.PO = action
        
      end
      
      def onPageClose(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.PC = action
        
      end

      def onPageVisible(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.PV = action
        
      end
      
      def onPageInvisible(action)        
        
        unless action.is_a?(Action::Action)
          raise TypeError, "An Action object must be passed."
        end
        
        self.AA ||= AdditionalActions.new
        self.AA.PI = action
        
      end

    end
    
    #
    # Annotation flags
    #
    module Flags
      INVISIBLE = 1 << 0
      HIDDEN = 1 << 1
      PRINT = 1 << 2
      NOZOOM = 1 << 3
      NOROTATE = 1 << 4
      NOVIEW = 1 << 5
      READONLY = 1 << 6
      LOCKED = 1 << 7
      TOGGLENOVIEW = 1 << 8
      LOCKEDCONTENTS = 1 << 9
    end

    module Markup

      def self.included(receiver)
        receiver.field    :T,             :Type => String, :Version => "1.1"
        receiver.field    :Popup,         :Type => Dictionary, :Version => "1.3"
        receiver.field    :CA,            :Type => Number, :Default => 1.0, :Version => "1.4"
        receiver.field    :RC,            :Type => [String, Stream], :Version => "1.5"
        receiver.field    :CreationDate,  :Type => String, :Version => "1.5"
        receiver.field    :IRT,           :Type => Dictionary, :Version => "1.5"
        receiver.field    :Subj,          :Type => String, :Version  => "1.5"
        receiver.field    :RT,            :Type => Name, :Default => :R, :Version => "1.6"
        receiver.field    :IT,            :Type => Name, :Version => "1.6"
        receiver.field    :ExData,        :Type => Dictionary, :Version => "1.7"
      end

    end

    #
    # Class representing an annotation.
    # Annotations are objects which user can interact with.
    #
    class Annotation < Dictionary
      
      include Configurable
      
      field   :Type,            :Type => Name, :Default => :Annot
      field   :Subtype,         :Type => Name, :Default => :Text, :Required => true
      field   :Rect,            :Type => Array, :Default => [ 0 , 0 , 0 , 0 ], :Required => true
      field   :Contents,        :Type => String
      field   :P,               :Type => Dictionary, :Version => "1.3"
      field   :NM,              :Type => String, :Version => "1.4"
      field   :M,               :Type => ByteString, :Version => "1.1"
      field   :F,               :Type => Integer, :Default => 0, :Version => "1.1"
      field   :AP,              :Type => Dictionary, :Version => "1.2"
      field   :AS,              :Type => Name, :Version => "1.2"
      field   :Border,          :Type => Array, :Default => [ 0 , 0 , 1 ]
      field   :C,               :Type => Array, :Version => "1.1"
      field   :StructParent,    :Type => Integer, :Version => "1.3"
      field   :OC,              :Type => Dictionary, :Version => "1.5"

      def set_normal_appearance(apstm)
        self.AP ||= AppearanceDictionary.new
        self.AP[:N] = apstm

        self
      end

      def set_rollover_appearance(apstm)
        self.AP ||= AppearanceDictionary.new
        self.AP[:R] = apstm

        self
      end

      def set_down_appearance(apstm)
        self.AP ||= AppearanceStream.new
        self.AP[:D] = apstm

        self
      end

    end

    class AppearanceDictionary < Dictionary

      include Configurable

      field   :N,               :Type => [ Stream, Dictionary ], :Required => true
      field   :R,               :Type => [ Stream, Dictionary ]
      field   :D,               :Type => [ Stream, Dictionary ]

    end

    class AppearanceStream < Graphics::FormXObject ; end
    
    class BorderStyle < Dictionary
      
      include Configurable
      
      SOLID = :S
      DASHED = :D
      BEVELED = :B
      INSET = :I
      UNDERLINE = :U

      field   :Type,            :Type => Name, :Default => :Border
      field   :W,               :Type => Number, :Default => 1
      field   :S,               :Type => Name, :Default => SOLID
      field   :D,               :Type => Array, :Default => [ 3 ]

    end
    
    class AppearanceCharacteristics < Dictionary
      
      include Configurable
      
      module CaptionStyle
        CAPTIONONLY = 0
        ICONONLY = 1
        CAPTIONBELOW = 2
        CAPTIONABOVE = 3
        CAPTIONRIGHT = 4
        CAPTIONLEFT = 5
        CAPTIONOVERLAID = 6
      end
    
      field   :R,               :Type => Integer, :Default => 0
      field   :BC,              :Type => Array
      field   :BG,              :Type => Array
      field   :CA,              :Type => String
      field   :RC,              :Type => String
      field   :AC,              :Type => String
      field   :I,               :Type => Stream
      field   :RI,              :Type => Stream
      field   :IX,              :Type => Stream
      field   :IF,              :Type => Dictionary
      field   :TP,              :Type => Integer, :Default => CaptionStyle::CAPTIONONLY
      
    end
    
    class Shape < Annotation

      include Markup

      field   :Subtype,         :Type => Name, :Default => :Square, :Required => true
      field   :BS,              :Type => Dictionary
      field   :IC,              :Type => Array
      field   :BE,              :Type => Dictionary, :Version => "1.5"
      field   :RD,              :Type => Array, :Version => "1.5"
      
    end
    
    class Square < Shape
    end
    
    class Circle < Shape
   
      field   :Subtype,         :Type => Name, :Default => :Circle, :Required => true
      
    end

    #
    # Text annotation
    #
    class Text < Annotation

      include Markup

      module TextName
        COMMENT      = :C
        KEY          = :K
        NOTE         = :N
        HELP         = :H
        NEWPARAGRAPH = :NP
        PARAGRAPH    = :P
        INSERT       = :I
      end

      field   :Subtype,         :Type => Name, :Default => :Text, :Required => true
      field   :Open,            :Type => Boolean, :Default => false
      field   :Name,            :Type => Name, :Default => TextName::NOTE
      field   :State,           :Type => String, :Version => "1.5"
      field   :StateModel,      :Type => String, :Version => "1.5"

      def pre_build
         
        model = self.StateModel
        state = self.State
        
        case model
        when "Marked"
          state = "Unmarked" if state.nil?
        when "Review"
          state = "None" if state.nil?
        end

        super
      end

    end

    #
    # FreeText Annotation
    #
    class FreeText < Annotation

      include Markup

      module Intent
        FREETEXT            = :FreeText
        FREETEXTCALLOUT     = :FreeTextCallout
        FREETEXTTYPEWRITER  = :FreeTextTypeWriter
      end

      field   :Subtype,         :Type => Name, :Default => :FreeText, :Required => true
      field   :DA,              :Type => String, :Default => "/F1 10 Tf 0 g", :Required => true
      field   :Q,               :Type => Integer, :Default => Field::TextAlign::LEFT, :Version => "1.4"
      field   :RC,              :Type => [String, Stream], :Version => "1.5"
      field   :DS,              :Type => String, :Version => "1.5"
      field   :CL,              :Type => Array, :Version => "1.6"
      field   :IT,              :Type => Name, :Default => Intent::FREETEXT, :Version => "1.6"
      field   :BE,              :Type => Dictionary, :Version => "1.6"
      field   :RD,              :Type => Array, :Version => "1.6"
      field   :BS,              :Type => Dictionary, :Version => "1.6"
      field   :LE,              :Type => Name, :Default => :None, :Version => "1.6"

    end
    
    #
    # Class representing an link annotation.
    #
    class Link < Annotation
      
      #
      # The annotationís highlighting mode, the visual effect to be used when the mouse button is pressed or held down inside its active area.
      #
      module Highlight
        # No highlighting
        NONE = :N
        
        # Invert the contents of the annotation rectangle. 
        INVERT = :I
        
        # Invert the annotationís border. 
        OUTLINE = :O
        
        # Display the annotation as if it were being pushed below the surface of the page
        PUSH = :P
      end

      field   :Subtype,             :Type => Name, :Default => :Link, :Required => true
      field   :A,                   :Type => Dictionary, :Version => "1.1"
      field   :Dest,                :Type => [ Array, Name, ByteString ]
      field   :H,                   :Type => Name, :Default => Highlight::INVERT, :Version => "1.2"
      field   :AP,                  :Type => Dictionary, :Version => "1.3"
      field   :QuadPoints,          :Type => Array, :Version => "1.6"
      
    end
    
    #
    # Class representing a file attachment annotation.
    #
    class FileAttachment < Annotation
      
      include Markup

      # Icons to be displayed for file attachment.
      module Icons
        GRAPH       = :Graph
        PAPERCLIP   = :Paperclip
        PUSHPIN     = :PushPin
        TAG         = :Tag
      end

      field   :Subtype,             :Type => Name, :Default => :FileAttachment, :Required => true
      field   :FS,                  :Type => Dictionary, :Required => true
      field   :Name,                :Type => Name, :Default => Icons::PUSHPIN
      
    end
    
    #
    # Class representing a screen Annotation.
    # A screen annotation specifies a region of a page upon which media clips may be played. It also serves as an object from which actions can be triggered.
    #
    class Screen < Annotation
      
      include Triggerable

      field   :Subtype,             :Type => Name, :Default => :Screen, :Required => true
      field   :T,                   :Type => String
      field   :MK,                  :Type => Dictionary
      field   :A,                   :Type => Dictionary, :Version => "1.1"
      field   :AA,                  :Type => Dictionary, :Version => "1.2"
     
    end


    class Sound < Annotation

      include Markup
      
      module Icons
        SPEAKER = :Speaker
        MIC     = :Mic
      end

      field   :Subtype,             :Type => Name, :Default => :Sound, :Required => true
      field   :Sound,               :Type => Stream, :Required => true
      field   :Name,                :Type => Name, :Default => Icons::SPEAKER

    end
    
    module Widget
    
      module Highlight
        # No highlighting
        NONE    = :N
        
        # Invert the contents of the annotation rectangle. 
        INVERT  = :I
        
        # Invert the annotationís border. 
        OUTLINE = :O
        
        # Display the annotation as if it were being pushed below the surface of the page
        PUSH    = :P
        
        # Same as P.
        TOGGLE  = :T
        
      end
  
      #
      # Class representing a widget Annotation.
      # Interactive forms use widget annotations to represent the appearance of fields and to manage user interactions. 
      #
      class Widget < Annotation
        
        include Field
        include Triggerable
   
        field   :Subtype,           :Type => Name, :Default => :Widget, :Required => true
        field   :H,                 :Type => Name, :Default => Highlight::INVERT
        field   :MK,                :Type => Dictionary
        field   :A,                 :Type => Dictionary, :Version => "1.1"
        field   :AA,                :Type => Dictionary, :Version => "1.2"
        field   :BS,                :Type => Dictionary, :Version => "1.2"
        
        def onActivate(action)        
          
          unless action.is_a?(Action::Action)
            raise TypeError, "An Action object must be passed."
          end
          
          self.A = action
        end
      
      end
      
      class Button < Widget
        
        module Flags
          NOTOGGLETOOFF = 1 << 14
          RADIO = 1 << 15
          PUSHBUTTON = 1 << 16
          RADIOSINUNISON = 1 << 26
        end
       
        field   :FT,                :Type => Name, :Default => Field::Type::BUTTON, :Required => true
        
      end
      
      class PushButton < Button
        
        def pre_build
          
          self.Ff ||= 0
          self.Ff |= Button::Flags::PUSHBUTTON
          
          super
        end
        
      end
      
      class CheckBox < Button
        
        def pre_build
          
          self.Ff ||= 0
          
          self.Ff &= ~Button::Flags::RADIO
          self.Ff &= ~Button::Flags::PUSHBUTTON
          
          super
        end
        
      end
      
      class Radio < Button
        
        def pre_build
          
          self.Ff ||= 0
          
          self.Ff &= ~Button::Flags::PUSHBUTTON
          self.Ff |= Button::Flags::RADIO
          
          super
        end
        
      end
      
      class Text < Widget
        
        module Flags
          MULTILINE       = 1 << 12
          PASSWORD        = 1 << 13
          FILESELECT      = 1 << 20
          DONOTSPELLCHECK = 1 << 22
          DONOTSCROLL     = 1 << 23
          COMB            = 1 << 24
          RICHTEXT        = 1 << 25
        end
        
        field   :FT,          :Type => Name, :Default => Field::Type::TEXT, :Required => true
        field   :MaxLen,      :Type => Integer

      end
      
      class Choice < Widget
        
        module Flags
          COMBO = 1 << 17
          EDIT = 1 << 18
          SORT = 1 << 19
          MULTISELECT = 1 << 21
          DONOTSPELLCHECK = 1 << 22
          COMMITONSELCHANGE = 1 << 26
        end

        field   :FT,          :Type => Name, :Default => Field::Type::CHOICE, :Required => true
        field   :Opt,         :Type => Array
        field   :TI,          :Type => Integer, :Default => 0
        field   :I,           :Type => Array, :Version => "1.4"
        
      end
      
      class ComboBox < Choice
        
        def pre_build
          
          self.Ff ||= 0
          self.Ff |= Choice::Flags::COMBO
          
          super
        end
        
      end
      
      class ListBox < Choice
        
        def pre_build
          
          self.Ff ||= 0
          self.Ff &= ~Choice::Flags::COMBO 
          
        end
        
      end
      
      class Signature < Widget

        field   :FT,          :Type => Name, :Default => Field::Type::SIGNATURE
        field   :Lock,        :Type => Dictionary, :Version => "1.5"
        field   :SV,          :Type => Dictionary, :Version => "1.5"
        
      end
    
    end
    
    #
    # Class representing additional actions which can be associated with an annotation having an AA field.
    #
    class AdditionalActions < Dictionary
      
      include Configurable
      
      field   :E,             :Type => Dictionary, :Version => "1.2" # Mouse Enter
      field   :X,             :Type => Dictionary, :Version => "1.2" # Mouse Exit
      field   :D,             :Type => Dictionary, :Version => "1.2" # Mouse Down
      field   :U,             :Type => Dictionary, :Version => "1.2" # Mouse Up
      field   :Fo,            :Type => Dictionary, :Version => "1.2" # Focus
      field   :Bl,            :Type => Dictionary, :Version => "1.2" # Blur
      field   :PO,            :Type => Dictionary, :Version => "1.2" # Page Open
      field   :PC,            :Type => Dictionary, :Version => "1.2" # Page Close
      field   :PV,            :Type => Dictionary, :Version => "1.2" # Page Visible
      field   :PI,             :Type => Dictionary, :Version => "1.2" # Page Invisible
      
    end
    
  end

end
