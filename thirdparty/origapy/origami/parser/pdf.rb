=begin

= File
	pdf.rb

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

require 'object.rb'
require 'null.rb'
require 'name.rb'
require 'dictionary.rb'
require 'reference.rb'
require 'boolean.rb'
require 'numeric.rb'
require 'string.rb'
require 'array.rb'
require 'stream.rb'
require 'filters.rb'
require 'trailer.rb'
require 'xreftable.rb'
require 'header.rb'
require 'functions.rb'
require 'catalog.rb'
require 'font.rb'
require 'page.rb'
require 'graphics.rb'
require 'destinations.rb'
require 'outline.rb'
require 'actions.rb'
require 'file.rb'
require 'acroform.rb'
require 'annotations.rb'
require 'signature.rb'
require 'webcapture.rb'
require 'metadata.rb'
require 'export.rb'
require 'webcapture.rb'
require 'encryption.rb'
require 'linearization.rb'
require 'obfuscation.rb'

module Origami

  VERSION = "1.0.0-beta1"
  REVISION = "$Revision: rev 711/devel, 2009/08/28 14:19:40 darko $" #:nodoc:
  
  @@dict_special_types = 
  { 
    :Catalog => Catalog, 
    :Pages => PageTreeNode, 
    :Page => Page, 
    :Filespec => FileSpec, 
    :Action => Action::Action,
    :Font => Font,
    :FontDescriptor => FontDescriptor,
    :Encoding => Encoding,
    :Annot => Annotation::Annotation,
    :Border => Annotation::BorderStyle,
    :Outlines => Outline,
    :Sig => Signature::DigitalSignature,
    :SigRef => Signature::Reference,
    :SigFieldLock => Field::SignatureLock,
    :SV => Field::SignatureSeedValue,
    :SVCert => Field::CertificateSeedValue,
    :ExtGState => Graphics::ExtGState
  }
  
  @@stm_special_types =
  {
    :ObjStm => ObjectStream, 
    :EmbeddedFile => EmbeddedFileStream,
    :Metadata => MetadataStream,
    :XRef => XRefStream
  }

  class InvalidPDF < Exception #:nodoc:
  end
	
  #
  # Main class representing a PDF file and its inner contents.
  # A PDF file contains a set of Revision.
  #
  class PDF
  
    #
    # Class representing a particular revision in a PDF file.
    # Revision contains :
    # * A Body, which is a sequence of Object.
    # * A XRef::Section, holding XRef information about objects in body.
    # * A Trailer.
    #
    class Revision
      
      attr_accessor :pdf
      attr_accessor :body, :xreftable, :xrefstm, :trailer
      
      def initialize(pdf)
        
        @pdf = pdf
        @body = {}
        @xreftable = nil
        @xrefstm = nil
        @trailer = nil
        
      end

      def trailer=(trl)
        trl.pdf = @pdf
        @trailer = trl
      end

      def has_xreftable?
        not @xreftable.nil?
      end

      def has_xrefstm?
        not @xrefstm.nil?
      end
      
    end

    attr_accessor :filename
    attr_accessor :header, :revisions
    
    class << self
      
      #
      # Read and parse a PDF file from disk.
      #
      def read(filename, options = {:verbosity => Parser::VERBOSE_INSANE})
        Parser.new(options).parse(filename)
      end
      
      #
      # Deserializes a PDF dump.
      #
      def deserialize(filename)
        
        Zlib::GzipReader.open(filename) { |gz|
          pdf = Marshal.load(gz.read)
        }
        
        pdf
      end
      
    end
    
    #
    # Creates a new PDF instance.
    # _init_structure_:: If this flag is set, then some structures will be automatically generated while manipulating this PDF. Set it if you are creating a new PDF file, this _must_ _not_ be used when parsing an existing file.
    #
    def initialize(init_structure = true)

      @header = PDF::Header.new
      @revisions = []
      
      add_new_revision
      
      @revisions.first.trailer = Trailer.new

      init if init_structure
    end
    
   
    #
    # Serializes the current PDF
    #
    def serialize(filename)
        Zlib::GzipWriter.open(filename) { |gz|
          gz.write Marshal.dump(self)
        }
        
        self
    end
    
    #
    # Returns the virtual file size as it would be taking on disk.
    #
    def filesize
      self.to_bin(:rebuildxrefs => false).size
    end
    
    #
    # Saves the current file as its current filename.
    #
    def save(file, params = {})
      
      options = 
      {
        :delinearize => false,
        :recompile => true,
      }
      options.update(params)

      if file.respond_to?(:write)
        fd = file
      else
        fd = File.open(file, 'w').binmode
      end
      
      self.delinearize! if options[:delinearize] == true and is_linearized?
      self.compile if options[:recompile] == true

      fd.write self.to_bin(options)
        
      fd.close unless file.respond_to?(:write)
      
      self
    end
    
    #
    # Sets the current filename to the argument given, then save it.
    # _filename_:: The path where to save this PDF.
    #
    def saveas(filename, params = {})
      
      if self.frozen?
        params[:recompile] = params[:rebuildxrefs] = false
        save(filename, params)
      else 
        @filename = filename
        save(filename, params)
      end
      
      self
    end
    
    #
    # Saves the file up to given revision number.
    # This can be useful to visualize the modifications over different incremental updates.
    # _revision_:: The revision number to save.
    # _filename_:: The path where to save this PDF.
    #
    def save_upto(revision, filename)
      saveas(filename, :up_to_revision => revision)  
    end

    #
    # Returns an array of Objects whose content is matching _pattern_.
    #
    def grep(*patterns)

      patterns.map! do |pattern|
        pattern.is_a?(::String) ? Regexp.new(Regexp.escape(pattern)) : pattern
      end

      unless patterns.all? { |pattern| pattern.is_a?(Regexp) }
        raise TypeError, "Expected a String or Regexp"
      end

      result = []
      objects.each do |obj|
        case obj
          when String, Name
            result << obj if patterns.any?{|pattern| obj.value.to_s.match(pattern)}
          when Stream
            result << obj if patterns.any?{|pattern| obj.data.match(pattern)}
        end
      end

      result
    end

    #
    # Returns an array of Objects whose name (in a Dictionary) is matching _pattern_.
    #
    def ls(*patterns)
    
      if patterns.empty?
        return objects
      end

      result = []

      patterns.map! do |pattern|
        pattern.is_a?(::String) ? Regexp.new(Regexp.escape(pattern)) : pattern
      end

      objects.each do |obj|
        if obj.is_a?(Dictionary)
          obj.each_pair do |name, obj|
            if patterns.any?{ |pattern| name.value.to_s.match(pattern) }
              result << ( obj.is_a?(Reference) ? obj.solve : obj )
            end
          end
        end
      end

      result
    end

    #
    # Returns an array of objects matching specified block.
    #
    def find(params = {}, &b)
      
      options =
      {
        :only_indirect => false
      }
      options.update(params)
      
      objset = (options[:only_indirect] == true) ? 
        self.indirect_objects.values : self.objects

      objset.find_all(&b)
    end
    
    #
    # Returns an array of objects embedded in the PDF body.
    # _include_objstm_:: Whether it shall return objects embedded in object streams.
    # Note : Shall return to an iterator for Ruby 1.9 comp.
    #
    def objects(include_objstm = true)
      
      def append_subobj(root, objset, inc_objstm)
        
        if objset.find{ |o| root.equal?(o) }.nil?
          
          objset << root

          if root.is_a?(Dictionary)
            root.each_pair { |name, value|
              append_subobj(name, objset, inc_objstm)
              append_subobj(value, objset, inc_objstm)
            }
          elsif root.is_a?(Array) or (root.is_a?(ObjectStream) and inc_objstm == true)
            root.each { |subobj| append_subobj(subobj, objset, inc_objstm) }
          end
        
        end
        
      end
      
      objset = []
      @revisions.each { |revision|
        revision.body.each_value { |object|
            append_subobj(object, objset, include_objstm)
        }
      }
      
      objset
    end
    
    #
    # Return an hash of indirect objects.
    # Updated objects appear only once.
    #
    def indirect_objects
      @revisions.inject({}) do |set, rev| set.merge(rev.body) end
    end
 
    #
    # Returns an array of all present indirect objects with their associated revision.
    #
    def all_indirect_objects #:nodoc:
      @revisions.inject([]) do |set,rev|
        objset = rev.body.values
        set.concat(objset.zip(::Array.new(objset.length, rev))) 
      end
    end
    
    #
    # Adds a new object to the PDF file.
    # If this object has no version number, then a new one will be automatically computed and assignated to him.
    # It returns a Reference to this Object.
    # _object_:: The object to add.
    #
    def <<(object)
       
      add_to_revision(object, @revisions.last)
      
    end
    
    #
    # Adds a new object to a specific revision.
    # If this object has no version number, then a new one will be automatically computed and assignated to him.
    # It returns a Reference to this Object.
    # _object_:: The object to add.
    # _revision_:: The revision to add the object to.
    #
    def add_to_revision(object, revision)
     
      object.set_indirect(true)
      object.set_pdf(self)
      
      object.no, object.generation = alloc_new_object_number if object.no == 0
      
      revision.body[object.reference] = object
      
      object.reference
    end

    #
    # Returns a new number/generation for future object.
    #
    def alloc_new_object_number
      
      no = 1
      no = no + 1 while get_object(no)

      objset = indirect_objects

      no = 
      if objset.size == 0 then 1
      else 
        indirect_objects.keys.max.refno + 1
      end

      [ no, 0 ]
    end
    
    #
    # This method is meant to recompute, verify and correct main PDF structures, in order to output a proper file.
    # * Allocates objects references.
    # * Sets some objects missing required values.
    #
    def compile
      
      #
      # A valid document must have at least one page.
      #
      append_page if pages.empty?
     
      #
      # Allocates object numbers and creates references.
      # Invokes object finalization methods.
      #
      physicalize
            
      #
      # Sets the PDF version header.
      #
      pdf_version = version_required
      @header.majorversion = pdf_version.to_s[0,1].to_i
      @header.minorversion = pdf_version.to_s[2,1].to_i
      
      self
    end
    
    #
    # Returns the final binary representation of the current document.
    # _rebuildxrefs_:: Computes xrefs while writing objects (default true).
    # _obfuscate_:: Do some basic syntactic object obfuscation.
    #
    def to_bin(params = {})
   
      has_objstm = self.indirect_objects.values.any?{|obj| obj.is_a?(ObjectStream)}

      options =
      {
        :rebuildxrefs => true,
        :obfuscate => false,
        :use_xrefstm => has_objstm,
        :use_xreftable => (not has_objstm),
        :up_to_revision => @revisions.size
        #todo linearize
      }
      options.update(params)

      options[:up_to_revision] = @revisions.size if options[:up_to_revision] > @revisions.size

      # Reset to default params if no xrefs are chosen (hybrid files not supported yet)
      if options[:use_xrefstm] == options[:use_xreftable]
        options[:use_xrefstm] = has_objstm
        options[:use_xreftable] = (not has_objstm)
      end

      # Get trailer dictionary
      trailer_info = get_trailer_info
      if trailer_info.nil?
        raise InvalidPDF, "No trailer information found"
      end
      trailer_dict = trailer_info.dictionary
 
      prev_xref_offset = nil
      xrefstm_offset = nil
      xreftable_offset = nil
    
      # Header
      bin = ""
      bin << @header.to_s
      
      # For each revision
      @revisions[0, options[:up_to_revision]].each do |rev|
        
        if options[:rebuildxrefs] == true
          lastno_table, lastno_stm = 0, 0
          brange_table, brange_stm = 0, 0
          
          xrefs_stm = [ XRef.new(0, XRef::LASTFREE, XRef::FREE) ]
          xrefs_table = [ XRef.new(0, XRef::LASTFREE, XRef::FREE) ]

          if options[:use_xreftable] == true
            xrefsection = XRef::Section.new
          end

          if options[:use_xrefstm] == true
            xrefstm = rev.xrefstm || XRefStream.new
            add_to_revision(xrefstm, rev) unless xrefstm == rev.xrefstm
          end
        end
       
        objset = rev.body.values
        
        objset.find_all{|obj| obj.is_a?(ObjectStream)}.each do |objstm|
          objset |= objstm.objects
        end if options[:rebuildxrefs] == true and options[:use_xrefstm] == true

        objset.sort # process objects in number order
        
        # For each object
        objset.sort.each { |obj|
         
          if options[:rebuildxrefs] == true
           
            # Adding subsections if needed
            if options[:use_xreftable] and (obj.no - lastno_table).abs > 1
              xrefsection << XRef::Subsection.new(brange_table, xrefs_table)

              xrefs_table.clear
              brange_table = obj.no
            end
            if options[:use_xrefstm] and (obj.no - lastno_stm).abs > 1
              xrefs_stm.each do |xref| xrefstm << xref end
              xrefstm.Index ||= []
              xrefstm.Index << brange_stm << xrefs_stm.length

              xrefs_stm.clear
              brange_stm = obj.no
            end

            # Process embedded objects
            if options[:use_xrefstm] and obj.parent != obj and obj.parent.is_a?(ObjectStream)
              index = obj.parent.index(obj.no)
             
              xrefs_stm << XRefToCompressedObj.new(obj.parent.no, index)
              
              lastno_stm = obj.no
            else
              xrefs_stm << XRef.new(bin.size, obj.generation, XRef::USED)
              xrefs_table << XRef.new(bin.size, obj.generation, XRef::USED)

              lastno_table = lastno_stm = obj.no
            end

          end
         
          if obj.parent == obj or not obj.parent.is_a?(ObjectStream)
           
            # Finalize XRefStm
            if options[:rebuildxrefs] == true and options[:use_xrefstm] == true and obj == xrefstm
              xrefstm_offset = bin.size
   
              xrefs_stm.each do |xref| xrefstm << xref end

              xrefstm.W = [ 1, (xrefstm_offset.to_s(2).size + 7) >> 3, 2 ]
              xrefstm.Index ||= []
              xrefstm.Index << brange_stm << xrefs_stm.size
   
              xrefstm.dictionary = xrefstm.dictionary.merge(trailer_dict) 
              xrefstm.Prev = prev_xref_offset

              rev.trailer.dictionary = nil

              add_to_revision(xrefstm, rev)

              xrefstm.pre_build
              xrefstm.post_build
            end

            bin << (options[:obfuscate] == true ? obj.to_obfuscated_str : obj.to_s)
          end
        }
      
        rev.trailer ||= Trailer.new
        
        # XRef table
        if options[:rebuildxrefs] == true
 
          if options[:use_xreftable] == true
            table_offset = bin.size
            
            xrefsection << XRef::Subsection.new(brange_table, xrefs_table)
            rev.xreftable = xrefsection
 
            rev.trailer.dictionary = trailer_dict
            rev.trailer.Size = objset.size + 1
            rev.trailer.Prev = prev_xref_offset

            rev.trailer.XRefStm = xrefstm_offset if options[:use_xrefstm] == true
          end

          startxref = options[:use_xreftable] == true ? table_offset : xrefstm_offset
          rev.trailer.startxref = prev_xref_offset = startxref

        end # end each rev
        
        # Trailer

        bin << rev.xreftable.to_s if options[:use_xreftable] == true
        bin << (options[:obfuscate] == true ? rev.trailer.to_obfuscated_str : rev.trailer.to_s)
        
      end
      
      bin
    end
    
    #
    # Compute and update XRef::Section for each Revision.
    #
    def rebuildxrefs
      
      size = 0
      startxref = @header.to_s.size
      
      @revisions.each { |revision|
      
        revision.body.each_value { |object|
          startxref += object.to_s.size
        }
        
        size += revision.body.size
        revision.xreftable = buildxrefs(revision.body.values)
        
        revision.trailer ||= Trailer.new
        revision.trailer.Size = size + 1
        revision.trailer.startxref = startxref
        
        startxref += revision.xreftable.to_s.size + revision.trailer.to_s.size
      }
      
      self
    end
    
    #
    # Ends the current Revision, and starts a new one.
    #
    def add_new_revision
      
      root = @revisions.last.trailer[:Root] unless @revisions.empty?

      @revisions << Revision.new(self)
      @revisions.last.trailer = Trailer.new
      @revisions.last.trailer.Root = root

      self
    end

    #
    # Removes a whole document revision.
    # _index_:: Revision index, first is 0.
    #
    def remove_revision(index)
      if index < 0 or index > @revisions.size
        raise IndexError, "Not a valid revision index"
      end

      if @revisions.size == 1
        raise InvalidPDF, "Cannot remove last revision"
      end

      @revisions.delete_at(index)
      self
    end
    
    #
    # Looking for an object present at a specified file offset.
    #
    def get_object_by_offset(offset) #:nodoc:
      self.indirect_objects.values.find { |obj| obj.file_offset == offset }
    end   

    #
    # Remove an object.
    #
    def delete_object(no, generation = 0)
      
      case no
        when Reference
          target = no
        when ::Integer
          target = Reference.new(no, generation)
      else
        raise TypeError, "Invalid parameter type : #{no.class}" 
      end
      
      @revisions.each do |rev|
        rev.body.delete(target)
      end

    end

    #
    # Search for an indirect object in the document.
    # _no_:: Reference or number of the object.
    # _generation_:: Object generation.
    #
    def get_object(no, generation = 0, use_xrefstm = true) #:nodoc:
       
      case no
        when Reference
          target = no
        when ::Integer
           target = Reference.new(no, generation)
        when Origami::Object
          return no
      else
        raise TypeError, "Invalid parameter type : #{no.class}" 
      end
      
      set = self.indirect_objects
     
      #
      # Search through accessible indirect objects.
      #
      if set.include?(target)
        set[target]
      elsif use_xrefstm == true
        # Look into XRef streams.

        if @revisions.last.has_xrefstm?

          xrefstm = @revisions.last.xrefstm

          done = []
          while xrefstm.is_a?(XRefStream) and not done.include?(xrefstm)
            xref = xrefstm.find(target.refno)
            #
            # We found a matching XRef.
            #
            if xref.is_a?(XRefToCompressedObj)
              objstm = get_object(xref.objstmno, 0, false)

              object = objstm.extract_by_index(xref.index)
              if object.is_a?(Origami::Object) and object.no == target.refno
                return object
              else
                return objstm.extract(target.refno)
              end
            elsif xrefstm.has_field?(:Prev)
              done << xrefstm
              xrefstm = get_object_by_offset(xrefstm.Prev)
              redo
            else
              break
            end
          end

        end

        #
        # Lastly search directly into Object streams (might be very slow).
        #
        stream = set.values.find_all{|obj| obj.is_a?(ObjectStream)}.find do |objstm| objstm.include?(target.refno) end
        stream && stream.extract(target.refno)
      end
      
    end

    alias :[] :get_object
  
    #
    # Converts a logical PDF view into a physical view ready for writing.
    #
    def physicalize
     
      #
      # Indirect objects are added to the revision and assigned numbers.
      #
      def build(obj, revision) #:nodoc:

        #
        # Finalize any subobjects before building the stream.
        #
        if obj.is_a?(ObjectStream)
          obj.each { |subobj|
            build(subobj, revision)
          }
        end
  
        obj.pre_build

        if obj.is_a?(Dictionary) or obj.is_a?(Array)
            
            obj.map! { |subobj|
              if subobj.is_indirect?
                if get_object(subobj.reference)
                  subobj.reference
                else
                  ref = add_to_revision(subobj, revision)
                  build(subobj, revision)
                  ref
                end
              else
                subobj
              end
            }
            
            obj.each { |subobj|
              build(subobj, revision)
            }
            
        elsif obj.is_a?(Stream)
          build(obj.dictionary, revision)
        end

        obj.post_build
        
      end
      
      all_indirect_objects.each { |obj, revision|
          build(obj, revision)          
      }
      
      self
    end

    #
    # Cleans the document from its references.
    # Indirects objects are made direct whenever possible.
    # TODO: Circuit-checking to avoid infinite induction
    #
    def logicalize #:nodoc:

      fail "Not yet supported"

      processed = []
      
      def convert(root) #:nodoc:

        replaced = []
        if root.is_a?(Dictionary) or root.is_a?(Array)
          
          root.each { |obj|
            convert(obj)
          }

          root.map! { |obj|
            if obj.is_a?(Reference)
              target = obj.solve
              # Streams can't be direct objects
              if target.is_a?(Stream)
                obj
              else
                replaced << obj
                target
              end
            else
              obj
            end
          }
          
        end

        replaced
      end

      @revisions.each { |revision|
        revision.body.each_value { |obj|
          processed.concat(convert(obj))
        }
      }

    end
    
    ##########################
    private
    ##########################
    
    #
    # Instanciates basic structures required for a valid PDF file.
    #
    def init
      
      catalog = (self.Catalog ||= Catalog.new)
      
      catalog.Pages = PageTreeNode.new.set_indirect(true)      
      
      @revisions.last.trailer.Root = catalog.reference
   
      self   
    end
    
    def version_required #:nodoc:
      
      max = 1.0
      @revisions.each { |revision|
        revision.body.each_value { |object|
          ver = object.version_required.to_s.to_f
          max = ver if ver > max 
        }
      }
      
      max.to_s.to_sym
    end
    
    #
    # Compute and update XRef::Section for each Revision.
    #
    def rebuild_dummy_xrefs #:nodoc
      
      def build_dummy_xrefs(objects)
        
        lastno = 0
        brange = 0
        
        xrefs = [ XRef.new(0, XRef::LASTFREE, XRef::FREE) ]

        xrefsection = XRef::Section.new
        objects.sort.each { |object|
          if (object.no - lastno).abs > 1
            xrefsection << XRef::Subsection.new(brange, xrefs)
            brange = object.no
            xrefs.clear
          end
          
          xrefs << XRef.new(0, 0, XRef::FREE)

          lastno = object.no
        }
        
        xrefsection << XRef::Subsection.new(brange, xrefs)
        
        xrefsection
      end
      
      size = 0
      startxref = @header.to_s.size
      
      @revisions.each { |revision|
      
        revision.body.each { |object|
          startxref += object.to_s.size
        }
        
        size += revision.body.size
        revision.xreftable = build_dummy_xrefs(revision.body.values)
        
        revision.trailer ||= Trailer.new
        revision.trailer.Size = size + 1
        revision.trailer.startxref = startxref
        
        startxref += revision.xreftable.to_s.size + revision.trailer.to_s.size
      }
      
      self
    end
    
    #
    # Build a xref section from a set of objects.
    #
    def buildxrefs(objects) #:nodoc:
      
      lastno = 0
      brange = 0
      
      xrefs = [ XRef.new(0, XRef::LASTFREE, XRef::FREE) ]
      
      xrefsection = XRef::Section.new
      objects.sort.each { |object|
        if (object.no - lastno).abs > 1
          xrefsection << XRef::Subsection.new(brange, xrefs)
          brange = object.no
          xrefs.clear
        end
        
        xrefs << XRef.new(get_object_offset(object.no, object.generation), object.generation, XRef::USED)

        lastno = object.no
      }
      
      xrefsection << XRef::Subsection.new(brange, xrefs)
      
      xrefsection
    end
    
    def delete_revision(ngen) #:nodoc:
      @revisions.delete_at[ngen]
    end
    
    def get_revision(ngen) #:nodoc:
      @revisions[ngen].body
    end
    
    def get_object_offset(no,generation) #:nodoc:

      objectoffset = @header.to_s.size
      
      @revisions.each { |revision|
        
        revision.body.values.sort.each { |object|
          if object.no == no and object.generation == generation then return objectoffset
          else
            objectoffset += object.to_s.size
          end
        }
        
        objectoffset += revision.xreftable.to_s.size
        objectoffset += revision.trailer.to_s.size
        
      }
      
      nil
    end

	end

end

