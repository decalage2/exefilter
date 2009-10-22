=begin

= File
	catalog.rb

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

  class PDF

    #
    # Returns the current Catalog Dictionary.
    #
    def Catalog
      get_doc_attr(:Root)
    end
    
    #
    # Sets the current Catalog Dictionary.
    #
    def Catalog=(cat)
      
      unless cat.is_a?(Catalog)
        raise TypeError, "Expected type Catalog, received #{cat.class}"
      end
      
      if @revisions.last.trailer.Root
        delete_object(@revisions.last.trailer.Root)
      end
      
      @revisions.last.trailer.Root = self << cat
    end
 
    #
    # Sets an action to run on document opening.
    # _action_:: An Action Object.
    #
    def onDocumentOpen(action)   
      
      unless action.is_a?(Action::Action)
        raise TypeError, "An Action object must be passed."
      end
      
      unless self.Catalog
        raise InvalidPDF, "A catalog object must exist to add this action."
      end
      
      self.Catalog.OpenAction = action
      
      self
    end
    
    #
    # Sets an action to run on document closing.
    # _action_:: A JavaScript Action Object.
    #
    def onDocumentClose(action)
      
      unless action.is_a?(Action::JavaScript)
        raise TypeError, "An Action::JavaScript object must be passed."
      end
      
      unless self.Catalog
        raise InvalidPDF, "A catalog object must exist to add this action."
      end
      
      self.Catalog.AA ||= CatalogAdditionalActions.new
      self.Catalog.AA.WC = action
      
      self
    end
    
    #
    # Sets an action to run on document printing.
    # _action_:: A JavaScript Action Object.
    #
    def onDocumentPrint(action)
      
      unless action.is_a?(Action::JavaScript)
        raise TypeError, "An Action::JavaScript object must be passed."
      end
      
      unless self.Catalog
        raise InvalidPDF, "A catalog object must exist to add this action."
      end
      
      self.Catalog.AA ||= CatalogAdditionalActions.new
      self.Catalog.AA.WP = action
      
    end

    #
    # Registers an object into a specific Names root dictionary.
    # _root_:: The root dictionary (see Names::Root)
    # _name_:: The value name.
    # _value_:: The value to associate with this name.
    #
    def register(root, name, value)
      
      if self.Catalog.Names.nil?
        self.Catalog.Names = Names.new
      end
      
      value.set_indirect(true)
      
      namesroot = self.Catalog.Names.send(root)
      if namesroot.nil?
        names = NameTreeNode.new({:Names => [] })
        self.Catalog.Names.send((root.id2name + "=").to_sym, (self << names))
        names.Names << name << value
      else
        namesroot.Names << name << value
      end
      
    end
  
  end

  #
  # Class representing the Catalog Dictionary of a PDF file.
  #
  class Catalog < Dictionary
    
    include Configurable

    field   :Type,                :Type => Name, :Default => :Catalog, :Required => true
    field   :Version,             :Type => Name, :Version => "1.4"
    field   :Pages,               :Type => Dictionary, :Required => true
    field   :PageLabels,          :Type => Dictionary, :Version => "1.3"
    field   :Names,               :Type => Dictionary, :Version => "1.2"
    field   :Dests,               :Type => Dictionary, :Version => "1.1"
    field   :ViewerPreferences,   :Type => Dictionary, :Version => "1.2"  
    field   :PageLayout,          :Type => Name, :Default => :SinglePage
    field   :PageMode,            :Type => Name, :Default => :UseNone
    field   :Outlines,            :Type => Dictionary
    field   :Threads,             :Type => Array, :Version => "1.1"
    field   :OpenAction,          :Type => [ Array, Dictionary ], :Version => "1.1"
    field   :AA,                  :Type => Dictionary, :Version => "1.4"
    field   :URI,                 :Type => Dictionary, :Version => "1.1"
    field   :AcroForm,            :Type => Dictionary, :Version => "1.2"
    field   :Metadata,            :Type => Stream, :Version => "1.4"
    field   :StructTreeRoot,      :Type => Dictionary, :Version => "1.3"
    field   :MarkInfo,            :Type => Dictionary, :Version => "1.4"
    field   :Lang,                :Type => String, :Version => "1.4"
    field   :SpiderInfo,          :Type => Dictionary, :Version => "1.3"
    field   :OutputIntents,       :Type => Array, :Version => "1.4"
    field   :PieceInfo,           :Type => Dictionary, :Version => "1.4"
    field   :OCProperties,        :Type => Dictionary, :Version => "1.5"
    field   :Perms,               :Type => Dictionary, :Version => "1.5"
    field   :Legal,               :Type => Dictionary, :Version => "1.5"
    field   :Requirements,        :Type => Array, :Version => "1.7"
    field   :Collection,          :Type => Dictionary, :Version => "1.7"
    field   :NeedsRendering,      :Type => Boolean, :Version => "1.7", :Default => false

    def initialize(hash = {})
      set_indirect(true)

      super(hash)
    end
    
  end
  
  #
  # Class representing additional actions which can be associated with a Catalog.
  #
  class CatalogAdditionalActions < Dictionary
    
    include Configurable
   
    field   :WC,                  :Type => Dictionary, :Version => "1.4"
    field   :WS,                  :Type => Dictionary, :Version => "1.4"
    field   :DS,                  :Type => Dictionary, :Version => "1.4"
    field   :WP,                  :Type => Dictionary, :Version => "1.4"
    field   :DP,                  :Type => Dictionary, :Version => "1.4"
    
  end
  
  #
  # Class representing the Names Dictionary of a PDF file.
  #
  class Names < Dictionary
    
    include Configurable
    
    #
    # Defines constants for Names tree root entries.
    #
    module Root
      DESTS = :Dests
      AP = :AP
      JAVASCRIPT = :JavaScript
      PAGES = :Pages
      TEMPLATES = :Templates
      IDS = :IDS
      URLS = :URLS
      EMBEDDEDFILES = :EmbeddedFiles
      ALTERNATEPRESENTATIONS = :AlternatePresentations
      RENDITIONS = :Renditions
    end

    field   Root::DESTS,        :Type => Dictionary, :Version => "1.2"
    field   Root::AP,           :Type => Dictionary, :Version => "1.3"
    field   Root::JAVASCRIPT,   :Type => Dictionary, :Version => "1.3"
    field   Root::PAGES,        :Type => Dictionary, :Version => "1.3"
    field   Root::TEMPLATES,    :Type => Dictionary, :Version => "1.3"
    field   Root::IDS,          :Type => Dictionary, :Version => "1.3"
    field   Root::URLS,         :Type => Dictionary, :Version => "1.3"
    field   Root::EMBEDDEDFILES,  :Type => Dictionary, :Version => "1.4"
    field   Root::ALTERNATEPRESENTATIONS, :Type => Dictionary, :Version => "1.4"
    field   Root::RENDITIONS,   :Type => Dictionary, :Version => "1.5"
    
  end
  
  #
  # Class representing a node in a Name tree.
  #
  class NameTreeNode < Dictionary
    
    include Configurable
   
    field   :Kids,              :Type => Array
    field   :Names,             :Type => Array
    field   :Limits,            :Type => Array

  end
  
  #
  # Class representing a leaf in a Name tree.
  #
  class NameLeaf < Origami::Array
    
    #
    # Creates a new leaf in a Name tree.
    # _hash_:: A hash of couples, associating a Name with an Reference.
    #
    def initialize(hash = {})
      
      names = []
      hash.each_pair { |k,v|
        names << k.to_o << v.to_o
      }
      
      super(names)
    end
    
  end

  #
  # Class representing the ViewerPreferences Dictionary of a PDF.
  # This dictionary modifies the way the UI looks when the file is opened in a viewer.
  #
  class ViewerPreferences < Dictionary
    
    include Configurable

    field   :HideToolbar,             :Type => Boolean, :Default => false
    field   :HideMenubar,             :Type => Boolean, :Default => false
    field   :HideWindowUI,            :Type => Boolean, :Default => false
    field   :FitWindow,               :Type => Boolean, :Default => false
    field   :CenterWindow,            :Type => Boolean, :Default => false
    field   :DisplayDocTitle,         :Type => Boolean, :Default => false, :Version => "1.4"
    field   :NonFullScreenPageMode,   :Type => Name, :Default => :UseNone
    field   :Direction,               :Type => Name, :Default => :L2R
    field   :ViewArea,                :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :ViewClip,                :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :PrintArea,               :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :PrintClip,               :Type => Name, :Default => :CropBox, :Version => "1.4"
    field   :PrintScaling,            :Type => Name, :Default => :AppDefault, :Version => "1.6"
    field   :Duplex,                  :Type => Name, :Default => :Simplex, :Version => "1.7"
    field   :PickTrayByPDFSize,       :Type => Boolean, :Version => "1.7"
    field   :PrintPageRange,          :Type => Array, :Version => "1.7"
    field   :NumCopies,               :Type => Integer, :Version => "1.7"
    
  end
  
end
