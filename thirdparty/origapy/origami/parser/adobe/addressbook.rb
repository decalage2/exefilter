=begin

= File
	adobe/addressbook.rb

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

require 'adobe/header.rb'
require 'object.rb'
require 'name.rb'
require 'dictionary.rb'
require 'reference.rb'
require 'boolean.rb'
require 'numeric.rb'
require 'string.rb'
require 'array.rb'
require 'trailer.rb'
require 'xreftable.rb'

require 'openssl'

module Origami

  module Adobe
    
   
    #
    # Class representing an Adobe Reader certificate store.
    #
    class AddressBook
      
      class Revision #:nodoc;
      
        attr_accessor :pdf
        attr_accessor :body, :xreftable, :trailer
        
        def initialize(adbk)
          
          @pdf = adbk
          @body = {}
          @xreftable = nil
          @trailer = nil
          
        end

        def trailer=(trl)
          trl.pdf = @pdf
          @trailer = trl
        end
        
      end

      attr_accessor :filename
      attr_accessor :header, :revisions
      
      def initialize #:nodoc:
        
        @header = AddressBook::Header.new
        @revisions = [ Revision.new(self) ]
        @revisions.first.trailer = Trailer.new
        
      end
      
      def objects
        
        def append_subobj(root, objset)
          
          if objset.find{ |o| o.object_id == root.object_id }.nil?
            
            objset << root
            
            if root.is_a?(Array) or root.is_a?(Dictionary)
              root.each { |subobj| append_subobj(subobj, objset) unless subobj.is_a?(Reference) }
            end
          
          end
          
        end
        
        objset = []
        @revisions.first.body.values.each { |object|
          unless object.is_a?(Reference)
            append_subobj(object, objset)
          end
        }
        
        objset
      end
      
      def <<(object)
        
        object.set_indirect(true)
        
        if object.no.zero?
        maxno = 1
          while get_object(maxno) do maxno = maxno.succ end
          
          object.generation = 0
          object.no = maxno
        end
        
        @revisions.first.body[object.reference] = object
        
        object.reference
      end
      
      def Catalog
        get_object(@trailer.Root)
      end
      
      def saveas(filename)
        
        bin = ""
        bin << @header.to_s

        lastno, brange = 0, 0
          
        xrefs = [ XRef.new(0, XRef::LASTFREE, XRef::FREE) ]
        xrefsection = XRef::Section.new
 
        @revisions.first.body.values.sort.each { |obj|
          if (obj.no - lastno).abs > 1
            xrefsection << XRef::Subsection.new(brange, xrefs)
            brange = obj.no
            xrefs.clear
          end
          
          xrefs << XRef.new(bin.size, obj.generation, XRef::USED)
          lastno = obj.no

          bin << obj.to_s
        }
        
        xrefsection << XRef::Subsection.new(brange, xrefs)
        
        @xreftable = xrefsection
        @trailer ||= Trailer.new
        @trailer.Size = rev.body.size + 1
        @trailer.startxref = bin.size

        bin << @xreftable.to_s
        bin << @trailer.to_s

        fd = File.open(filename, "w").binmode
          fd << bin 
        fd.close
        
        show_entries
      end
      
      #
      # Prints registered users in the address book
      #
      def show_users
        
        puts "----------"
        puts "Users list"
        puts "----------"
        
        @revisions.first.body.values.each { |obj| if obj.is_a?(User) then obj.show; puts end }
        
        nil
      end
      
      #
      # Prints registered certificates in the addressbook
      #
      def show_certs
        puts "-----------------"
        puts "Certificates list"
        puts "-----------------"
        
        @revisions.first.body.values.each { |obj| if obj.is_a?(Certificate) then obj.show; puts end }
        
        nil
      end
      
      #
      # Prints certificate with the specified id
      #
      def show_cert(id)
        certs = @revisions.first.body.values.find_all { |obj| obj.is_a?(Certificate) and obj.ID == id }
        
        certs.each { |cert| cert.show; puts }
        
        nil
      end
      
      #
      # Returns a Certificate dictionary corresponding to the specified id
      #
      def get_cert(id)
        
        @revisions.first.body.values.find { |obj| obj.is_a?(Certificate) and obj.ID == id }
        
      end
      
      def show_user(id)
        users = @revisions.first.body.values.find_all { |obj| obj.is_a?(User) and obj.ID == id }
        
        users.each { |user| cert.show; puts }
        
        nil
      end
      
      #
      # Prints users and certificates registered in the address book
      #
      def show_entries
        show_users
        show_certs
        
        puts "End of address book."
      end
      
      #
      # Add a certificate into the address book
      #
      def add_certificate(certfile, attributes, viewable = false, editable = false)
        
        cert = Certificate.new
        cert.Cert = OpenSSL::X509::Certificate.new(certfile).to_der
        cert.ID = self.Catalog.PPK.AddressBook.NextID
        self.Catalog.PPK.AddressBook.NextID += 1
        cert.Trust = attributes
        cert.Viewable = viewable
        cert.Editable = editable
        
        self.Catalog.PPK.AddressBook.Entries.push(self << cert)
        
        show_certs
      end
      
      alias to_s show_entries
      alias to_str show_entries
      
      class Catalog < Dictionary
        
        include Configurable

        field   :Type,      :Type => Name, :Default => :Catalog, :Required => true
        field   :PPK,       :Type => Dictionary, :Required => true
        
        def initialize(hash = {}) #:nodoc:
          super(hash, true)
        end
        
      end
      
      class PPK < Dictionary
        
        include Configurable

        field   :Type,        :Type => Name, :Default => :PPK, :Required => true
        field   :User,        :Type => Dictionary, :Required => true
        field   :AddressBook, :Type => Dictionary, :Required => true
        field   :V,           :Type => Integer, :Default => 0x10001, :Required => true
        
        def initialize(hash = {}) #:nodoc:
          super(hash, false)
        end
        
      end
      
      class UserList < Dictionary
        
        include Configurable

        field   :Type,        :Type => Name, :Default => :User, :Required => true
        
        def initialize(hash = {})
          super(hash, false)
        end
        
      end
      
      class AddressList < Dictionary
        
        include Configurable

        field   :Type,        :Type => Name, :Default => :AddressBook, :Required => true
        field   :NextID,      :Type => Integer
        field   :Entries,     :Type => Array, :Default => [], :Required => true
        
        def initialize(hash = {}) #:nodoc:
          super(hash, false)
        end
        
      end
      
      module Descriptor
        
        CERTIFICATE = 1
        USER = 2

        def self.included(receiver) #:nodoc:
          receiver.field    :ID,        :Type => Integer, :Required => true
          receiver.field    :ABEType,   :Type => Integer, :Default => Descriptor::CERTIFICATE, :Required => true
        end
        
        def initialize(hash = {}) #:nodoc:
          super(hash, true)
        end
        
      end
      
      class User < Dictionary
        
        include Configurable
        include Descriptor

        field   :ABEType,       :Type => Integer, :Default => Descriptor::USER, :Required => true
        field   :Name,          :Type => String, :Required => true
        field   :Encrypt,       :Type => Integer
        field   :Certs,         :Type => Array, :Default => [], :Required => true
        
        def show
          puts "ID: #{self.ID}"
          puts "Name: #{self.Name}"
          puts "Certificates: " + self.Certs.join(", ")
        end
        
      end
      
      class Certificate < Dictionary
        
        include Configurable
        include Descriptor
        
        module Flags
          
          CAN_CERTIFY = 1 << 1
          ALLOW_DYNAMIC_CONTENT = 1 << 2
          UNKNOWN_1 = 1 << 3
          ALLOW_HIGH_PRIV_JS = 1 << 4
          UNKNOWN_2 = 1 << 5
          IS_ROOT_CA = 1 << 6
          
          #~ FULL_TRUST = 1 << 1 | 1 << 2 | 1 << 3 | 1 << 4 | 1 << 5 | 1 << 6
          FULL_TRUST = 8190
        end

        field   :ABEType,       :Type => Integer, :Default => Descriptor::CERTIFICATE, :Required => true
        field   :Usage,         :Type => Integer, :Default => 1, :Required => true
        field   :Viewable,      :Type => Boolean, :Default => true
        field   :Editable,      :Type => Boolean, :Default => true
        field   :Cert,          :Type => String, :Required => true
        field   :Trust,         :Type => Integer, :Default => Flags::UNKNOWN_2, :Required => true
        
        def show
          puts "ID: #{self.ID}"
          puts "Viewable: #{self.Viewable}"
          puts "Editable: #{self.Editable}"
          puts "Trust attributes: #{self.Trust}"
        end
        
      end
       
      def get_object(no, generation = 0) #:nodoc:
         
        case no
        when Reference
          target = no
        when ::Integer
          target = Reference.new(no, generation)
        when Origami::Object
          return no
        end
       
        @revisions.first.body[target]
      end
      
      private
      
      def rebuildxrefs #:nodoc:
        
        startxref = @header.to_s.size
        
        @revisions.first.body.values.each { |object|
          startxref += object.to_s.size
        }
          
        @xreftable = buildxrefs(@revisions.first.body)
        
        @trailer ||= Trailer.new
        @trailer.Size = @revisions.first.body.size + 1
        @trailer.startxref = startxref
        
        self
      end
      
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
     
      def get_object_offset(no,generation) #:nodoc:

        bodyoffset = @header.to_s.size
        
        objectoffset = bodyoffset
          
        @revisions.first.body.values.each { |object|
          if object.no == no and object.generation == generation then return objectoffset
          else
            objectoffset += object.to_s.size
          end
        }
        
        nil
      end
      
    end
    
  end
  
end
