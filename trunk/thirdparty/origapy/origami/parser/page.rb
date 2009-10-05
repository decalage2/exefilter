=begin

= File
	page.rb

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

  class PDF

    def append_page(page = Page.new, *more)
    
      pages = [ page ].concat(more)
      
      fail "Expecting Page type, instead of #{page.class}" unless pages.all?{|page| page.is_a?(Page)}
      
      treeroot = self.Catalog.Pages
      
      treeroot.Kids ||= [] #:nodoc:
      treeroot.Kids.concat(pages)
      treeroot.Count = treeroot.Kids.length
      
      pages.each do |page| 
        page.Parent = treeroot
      end
      
      self
    end

    #
    # Returns an array of Page
    #
    def pages
      
      return [] if not self.Catalog or not self.Catalog.Pages
      
      root = self.Catalog.Pages
      return [] if root.nil?

      root.solve if root.is_a?(Reference) 

      root.children
    end

  end
  
  #
  # Class representing a Resources Dictionary for a Page.
  #
  class Resources < Dictionary
    
    include Configurable

    field   :ExtGState,   :Type => Dictionary
    field   :ColorSpace,  :Type => Dictionary
    field   :Pattern,     :Type => Dictionary
    field   :Shading,     :Type => Dictionary, :Version => "1.3"
    field   :XObject,     :Type => Dictionary
    field   :Font,        :Type => Dictionary
    field   :ProcSet,     :Type => Array
    field   :Properties,  :Type => Dictionary, :Version => "1.2"
    
    def pre_build
      
      unless self.Font
        fnt = Font.new.set_indirect(true).pre_build
        fnt.Name = :F1
        
        self.Font = { :F1 => fnt }
      end
      
      super
    end
    
  end

  #
  # Class representing a node in a Page tree.
  #
  class PageTreeNode < Dictionary
    
    include Configurable
   
    field   :Type,          :Type => Name, :Default => :Pages, :Required => true
    field   :Parent,        :Type => Dictionary
    field   :Kids,          :Type => Array, :Default => [], :Required => true
    field   :Count,         :Type => Integer, :Default => 0, :Required => true

    def pre_build #:nodoc:
      self.Count = self.children.length     
         
      set_indirect(true)
      super
    end

    #
    # Returns an array of Page inheriting this tree node.
    #
    def children
      pageset = []
     
      unless self.Count.nil?
        self.Count.value.times { |n|
          if n < self.Kids.length
            node = self.Kids[n].is_a?(Reference) ? self.Kids[n].solve : self.Kids[n]
            case node
            when PageTreeNode then pageset.concat(node.children) 
            when Page then pageset << node
            end
          end      
        }
      end
      
      pageset
    end
      
    def << (pageset)
        
      pageset = [pageset] unless pageset.is_a?(Enumerable)
      fail "Cannot add anything but Page and PageTreeNode to this node" unless pageset.all? { |item| item.is_a?(Page) or item.is_a?(PageTreeNode) }

      self.Kids ||= Array.new
      self.Kids.concat(pageset)
      self.Count = self.Kids.length
        
      pageset.each do |node| 
        node.Parent = self 
      end
        
    end
      
  end
    
  #
  # Class representing a Page in the PDF document.
  #
  class Page < Dictionary
    
    include Configurable
   
    field   :Type,                  :Type => Name, :Default => :Page, :Required => true
    field   :Parent,                :Type => Dictionary, :Required => true
    field   :LastModified,          :Type => String, :Version => "1.3"
    field   :Resources,             :Type => Dictionary, :Required => true 
    field   :MediaBox,              :Type => Array, :Default => Rectangle[ :llx => 0, :lly => 0, :urx => 795, :ury => 842 ], :Required => true
    field   :CropBox,               :Type => Array
    field   :BleedBox,              :Type => Array, :Version => "1.3"
    field   :TrimBox,               :Type => Array, :Version => "1.3"
    field   :ArtBox,                :Type => Array, :Version => "1.3"
    field   :BoxColorInfo,          :Type => Dictionary, :Version => "1.4"
    field   :Contents,              :Type => [ Stream, Array ]
    field   :Rotate,                :Type => Integer, :Default => 0
    field   :Group,                 :Type => Dictionary, :Version => "1.4"
    field   :Thumb,                 :Type => Stream
    field   :B,                     :Type => Array, :Version => "1.1"
    field   :Dur,                   :Type => Integer, :Version => "1.1"
    field   :Trans,                 :Type => Dictionary, :Version => "1.1"
    field   :Annots,                :Type => Array
    field   :AA,                    :Type => Dictionary, :Version => "1.2"
    field   :Metadata,              :Type => Stream, :Version => "1.4"
    field   :PieceInfo,             :Type => Dictionary, :Version => "1.2"
    field   :StructParents,         :Type => Integer, :Version => "1.3"
    field   :ID,                    :Type => String
    field   :PZ,                    :Type => Number
    field   :SeparationInfo,        :Type => Dictionary, :Version => "1.3"
    field   :Tabs,                  :Type => Name, :Version => "1.5"
    field   :TemplateAssociated,    :Type => Name, :Version => "1.5"
    field   :PresSteps,             :Type => Dictionary, :Version => "1.5"
    field   :UserUnit,              :Type => Number, :Default => 1.0, :Version => "1.6"
    field   :VP,                    :Type => Dictionary, :Version => "1.6"

    #
    # Creates a new document Page.
    # _hash_:: A hash of attributes to set to this Page.
    #
    def initialize(hash = {}, indirect = true)
     
      super(hash, indirect)
      
    end

    def pre_build
      unless self.Resources
        self.Resources = Resources.new.pre_build
      end

      super
    end

    #
    # Add an Annotation to the Page.
    #
    def add_annot(annotation)
      
      unless annotation.is_a?(Annotation::Annotation)
        raise TypeError, "An Annotation object must be passed."
      end
      
      self.Annots ||= Array.new
      self.Annots << annotation
      
      annotation.P = self if is_indirect?
      
    end
    
    def onOpen(action)
      
      unless action.is_a?(Action::Action)
        raise TypeError, "An Action object must be passed."
      end
      
      self.AA ||= PageAdditionalActions.new
      self.AA.O = action
      
      self
    end
    
    def onClose(action)
      
      unless action.is_a?(Action::Action)
        raise TypeError, "An Action object must be passed."
      end
      
      self.AA ||= PageAdditionalActions.new
      self.AA.C = action
      
    end
    
  end
  
  #
  # Class representing additional actions which can be associated to a Page.
  #
  class PageAdditionalActions < Dictionary
    
    include Configurable
   
    field   :O,   :Type => Dictionary, :Version => "1.2" # Page Open
    field   :C,   :Type => Dictionary, :Version => "1.2" # Page Close
    
  end
  
end
