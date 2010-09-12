=begin

= File
	signature.rb

= Info
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

require 'openssl'

module Origami

  class PDF
    
    #
    # Sign the document with the given key and x509 certificate.
    # _certificate_:: The X509 certificate containing the public key.
    # _key_:: The private key associated with the certificate.
    # _ca_:: Optional CA certificates used to sign the user certificate.
    #
    def sign(certificate, key, ca = [], annotation = nil, location = nil, contact = nil, reason = nil)
      
      unless certificate.is_a?(OpenSSL::X509::Certificate)
        raise TypeError, "A OpenSSL::X509::Certificate object must be passed."
      end
      
      unless key.is_a?(OpenSSL::PKey::RSA)
        raise TypeError, "A OpenSSL::PKey::RSA object must be passed."
      end
      
      unless ca.is_a?(::Array)
        raise TypeError, "Expected an Array of CA certificate."
      end
      
      unless annotation.nil? or annotation.is_a?(Annotation::Widget::Signature)
        raise TypeError, "Expected a Annotation::Widget::Signature object."
      end
      
      def signfield_size(certificate, key, ca = []) #;nodoc:
        datatest = "abcdefghijklmnopqrstuvwxyz"
        OpenSSL::PKCS7.sign(certificate, key, datatest, ca, OpenSSL::PKCS7::DETACHED | OpenSSL::PKCS7::BINARY).to_der.size + 128
      end
      
      digsig = Signature::DigitalSignature.new.set_indirect(true)
     
      if annotation.nil?
        annotation = Annotation::Widget::Signature.new
        annotation.Rect = Rectangle[:llx => 0.0, :lly => 0.0, :urx => 0.0, :ury => 0.0]        
      end
      
      annotation.V = digsig ;
      add_fields(annotation)
      self.Catalog.AcroForm.SigFlags = InteractiveForm::SigFlags::SIGNATURESEXIST | InteractiveForm::SigFlags::APPENDONLY
      
      digsig.Type = :Sig #:nodoc:
      digsig.Contents = HexaString.new("\x00" * signfield_size(certificate, key, ca)) #:nodoc:
      digsig.Filter = Name.new("Adobe.PPKMS") #:nodoc:
      digsig.SubFilter = Name.new("adbe.pkcs7.detached") #:nodoc:
      digsig.ByteRange = [0, 0, 0, 0] #:nodoc:
      
      digsig.Location = HexaString.new(location) if location
      digsig.ContactInfo = HexaString.new(contact) if contact
      digsig.Reason = HexaString.new(reason) if reason
      
      #
      #  Flattening the PDF to get file view.
      #
      self.compile
      
      #
      # Creating an empty Xref table to compute signature byte range.
      #
      rebuild_dummy_xrefs
      
      sigoffset = get_object_offset(digsig.no, digsig.generation) + digsig.sigOffset
      
      digsig.ByteRange[0] = 0 
      digsig.ByteRange[1] = sigoffset
      digsig.ByteRange[2] = sigoffset + digsig.Contents.size
      
      digsig.ByteRange[3] = filesize - digsig.ByteRange[2] until digsig.ByteRange[3] == filesize - digsig.ByteRange[2]
      
      # From that point the file size remains constant
      
      #
      # Correct Xrefs variations caused by ByteRange modifications.
      #
      rebuildxrefs
      
      filedata = self.to_bin
      signable_data = filedata[digsig.ByteRange[0],digsig.ByteRange[1]] + filedata[digsig.ByteRange[2],digsig.ByteRange[3]]
      
      signature = OpenSSL::PKCS7.sign(certificate, key, signable_data, ca, OpenSSL::PKCS7::DETACHED | OpenSSL::PKCS7::BINARY).to_der
      digsig.Contents[0, signature.size] = signature
      
      #
      # No more modification are allowed after signing.
      #
      self.freeze
      
    end
    
    #
    # Returns whether the document contains a digital signature.
    #
    def is_signed?
      
      #~ not self.Catalog.AcroForm.nil? and (self.Catalog.AcroForm[:SigFlags] & InteractiveForm::SigFlags::SIGNATUREEXISTS) != 0
      "todo"
      
    end
    
    #
    # Enable the document Usage Rights.
    # _rights_:: list of rights defined in UsageRights::Rights
    #
    def enable_usage_rights(*rights)
      
      def signfield_size(certificate, key, ca = []) #:nodoc:
        datatest = "abcdefghijklmnopqrstuvwxyz"
        OpenSSL::PKCS7.sign(certificate, key, datatest, ca, OpenSSL::PKCS7::DETACHED | OpenSSL::PKCS7::BINARY).to_der.size + 128
      end
      
      begin
        key = OpenSSL::PKey::RSA.new(File.open('adobe.key','r').binmode.read)
        certificate = OpenSSL::X509::Certificate.new(File.open('adobe.crt','r').binmode.read)
      rescue
        warn "The Adobe private key is necessary to enable usage rights.\nYou do not seem to be Adobe :)... Aborting."
        return nil
      end
      
      digsig = Signature::DigitalSignature.new.set_indirect(true)
      
      self.Catalog.AcroForm ||= InteractiveForm.new
      #self.Catalog.AcroForm.SigFlags = InteractiveForm::SigFlags::APPENDONLY
      
      digsig.Type = :Sig #:nodoc:
      digsig.Contents = HexaString.new("\x00" * signfield_size(certificate, key, [])) #:nodoc:
      digsig.Filter = Name.new("Adobe.PPKLite") #:nodoc:
      digsig.Name = "ARE Acrobat Product v8.0 P23 0002337" #:nodoc:
      digsig.SubFilter = Name.new("adbe.pkcs7.detached") #:nodoc:
      digsig.ByteRange = [0, 0, 0, 0] #:nodoc:
      
      sigref = Signature::Reference.new #:nodoc:
      sigref.Type = :SigRef #:nodoc:
      sigref.TransformMethod = :UR3 #:nodoc:
      sigref.Data = self.Catalog
      
      sigref.TransformParams = UsageRights::TransformParams.new
      sigref.TransformParams.P = true #:nodoc:
      sigref.TransformParams.Type = :TransformParams #:nodoc:
      sigref.TransformParams.V = UsageRights::TransformParams::VERSION
      
      rights.each { |right|
        
        sigref.TransformParams[right.first] ||= []
        sigref.TransformParams[right.first].concat(right[1..-1])
        
      }
      
      digsig.Reference = [ sigref ]
      
      self.Catalog.Perms ||= Perms.new
      self.Catalog.Perms.UR3 = digsig
      
      #
      #  Flattening the PDF to get file view.
      #
      self.compile
      
      #
      # Creating an empty Xref table to compute signature byte range.
      #
      rebuild_dummy_xrefs
      
      sigoffset = get_object_offset(digsig.no, digsig.generation) + digsig.sigOffset
      
      digsig.ByteRange[0] = 0 
      digsig.ByteRange[1] = sigoffset
      digsig.ByteRange[2] = sigoffset + digsig.Contents.size
      
      digsig.ByteRange[3] = filesize - digsig.ByteRange[2] until digsig.ByteRange[3] == filesize - digsig.ByteRange[2]
      
      # From that point the file size remains constant
      
      #
      # Correct Xrefs variations caused by ByteRange modifications.
      #
      rebuildxrefs
      
      filedata = self.to_bin
      signable_data = filedata[digsig.ByteRange[0],digsig.ByteRange[1]] + filedata[digsig.ByteRange[2],digsig.ByteRange[3]]
      
      signature = OpenSSL::PKCS7.sign(certificate, key, signable_data, [], OpenSSL::PKCS7::DETACHED | OpenSSL::PKCS7::BINARY).to_der
      digsig.Contents[0, signature.size] = signature
      
      #
      # No more modification are allowed after signing.
      #
      self.freeze
      
    end
    
    def has_usage_rights?
      
      #~ not self.Catalog.Perms.nil? and (not self.Catalog.Perms.UR3.nil? or not self.Catalog.Perms.UR.nil?)
      "todo"
      
    end

  end
  
  class Perms < Dictionary
    
    include Configurable
   
    field   :DocMDP,          :Type => Dictionary
    field   :UR,              :Type => Dictionary
    field   :UR3,             :Type => Dictionary, :Version => "1.6"

  end

  module Signature

    #
    # Class representing a digital signature.
    #
    class DigitalSignature < Dictionary
      
      include Configurable
  
      field   :Type,            :Type => Name, :Default => :Sig
      field   :Filter,          :Type => Name, :Default => "Adobe.PPKMS".to_sym, :Required => true
      field   :SubFilter,       :Type => Name
      field   :Contents,        :Type => String, :Required => true
      field   :Cert,            :Type => [ Array, String ]
      field   :ByteRange,       :Type => Array
      field   :Reference,       :Type => Array, :Version => "1.5"
      field   :Changes,         :Type => Array
      field   :Name,            :Type => String
      field   :M,               :Type => String
      field   :Location,        :Type => String
      field   :Reason,          :Type => String
      field   :ContactInfo,     :Type => String
      field   :R,               :Type => Integer
      field   :V,               :Type => Integer, :Default => 0, :Version => "1.5"
      field   :Prop_Build,      :Type => Dictionary, :Version => "1.5"
      field   :Prop_AuthTime,   :Type => Integer, :Version => "1.5"
      field   :Prop_AuthType,   :Type => Name, :Version => "1.5"
      
      def pre_build #:nodoc:
        self.M = Origami::Date.now
        self.Prop_Build ||= BuildProperties.new.pre_build
        
        super
      end
      
      def to_s(base = 1)
        
        pairs = self.to_a
        content = TOKENS.first + EOL
        
        pairs.sort_by{ |k| k.to_s }.reverse.each { |pair|
          key, value = pair[0].to_o, pair[1].to_o
            
          content << "\t" * base + key.to_s + " " + (value.is_a?(Dictionary) ? value.to_s(base+1) : value.to_s) + EOL
        }
        
        content << "\t" * (base-1) + TOKENS.last
        
        output(content)
      end
      
      def sigOffset #:nodoc:
        
        base = 1
        pairs = self.to_a
        content = "#{no} #{generation} obj" + EOL + TOKENS.first + EOL
        
        pairs.sort_by{ |k| k.to_s }.reverse.each { |pair|
          
            key, value = pair[0].to_o, pair[1].to_o
            
            if key == :Contents
              content << "\t" * base + key.to_s + " "
              
              return content.size
            else
              content << "\t" * base + key.to_s + " " + (value.is_a?(Dictionary) ? value.to_s(base+1) : value.to_s) + EOL
            end
        }
          
        nil
      end
      
    end
    
    #
    # Class representing a signature which can be embedded in DigitalSignature dictionary.
    # It must be a direct object. 
    #
    class Reference < Dictionary
      
      include Configurable
     
      field   :Type,            :Type => Name, :Default => :SigRef
      field   :TransformMethod, :Type => Name, :Default => :DocMDP, :Required => true
      field   :TransformParams, :Type => Dictionary
      field   :Data,            :Type => Object
      field   :DigestMethod,    :Type => Name, :Default => :MD5
      field   :DigestValue,     :Type => String
      field   :DigestLocation,  :Type => Array

      def initialize(hash = {})
        set_indirect(false)

        super(hash)
      end
    end
    
    class BuildProperties < Dictionary
      
      include Configurable
      
      field   :Filter,          :Type => Dictionary, :Version => "1.5"
      field   :PubSec,          :Type => Dictionary, :Version => "1.5"
      field   :App,             :Type => Dictionary, :Version => "1.5"
      field   :SigQ,            :Type => Dictionary, :Version => "1.7"

      def initialize(hash = {})
        set_indirect(false)

        super(hash)
      end

      def pre_build #:nodoc:
        
        self.Filter ||= BuildData.new
        self.Filter.Name ||= Name.new("Adobe.PPKMS")
        self.Filter.R ||= 0x2001D
        self.Filter.Date ||= Time.now.to_s
        
        self.SigQ ||= SigQData.new
        self.SigQ.Preview ||= false
        self.SigQ.R ||= 0x2001D
        
        self.PubSec ||= BuildData.new
        self.PubSec.NonEFontNoWarn ||= false
        self.PubSec.Date ||= Time.now.to_s
        self.PubSec.R ||= 0x2001D
        
        self.App ||= AppData.new
        self.App.TrustedMode ||= false
        self.App.OS ||= [ :Win ]
        self.App.R ||= 0x70000
        self.App.Name ||= Name.new("Exchange-Pro")
        
        super
      end
      
    end
    
    class BuildData < Dictionary
      
      include Configurable
     
      field   :Name,              :Type => Name,  :Version => "1.5"
      field   :Date,              :Type => String, :Version => "1.5"
      field   :R,                 :Type => Number, :Version => "1.5"
      field   :PreRelease,        :Type => Boolean, :Default => false, :Version => "1.5"
      field   :OS,                :Type => Array, :Version => "1.5"
      field   :NonEFontNoWarn,    :Type => Boolean, :Version => "1.5"
      field   :TrustedMode,       :Type => Boolean, :Version => "1.5"
      field   :V,                 :Type => Number, :Version => "1.5"

      def initialize(hash = {})
        set_indirect(false)

        super(hash)
      end
      
    end
    
    class AppData < BuildData
      field   :REx,               :Type => String, :Version => "1.6"
    end
    
    class SigQData < BuildData
      field   :Preview,           :Type => Boolean, :Default => false, :Version => "1.7"
    end

  end
  
  module UsageRights
    
    module Rights
      
      DOCUMENT_FULLSAVE = [:Document, :FullSave]
      DOCUMENT_ALL = DOCUMENT_FULLSAVE
      
      ANNOTS_CREATE = [:Annots, :Create]
      ANNOTS_DELETE = [:Annots, :Delete]
      ANNOTS_MODIFY = [:Annots, :Modify]
      ANNOTS_COPY = [:Annots, :Copy]
      ANNOTS_IMPORT = [:Annots, :Import]
      ANNOTS_EXPORT = [:Annots, :Export]
      ANNOTS_ONLINE = [:Annots, :Online]
      ANNOTS_SUMMARYVIEW = [:Annots, :SummaryView]
      ANNOTS_ALL = [ :Annots, :Create, :Modify, :Copy, :Import, :Export, :Online, :SummaryView ]
      
      FORM_FILLIN = [:Form, :FillIn]
      FORM_IMPORT = [:Form, :Import]
      FORM_EXPORT = [:Form, :Export]
      FORM_SUBMITSTANDALONE = [:Form, :SubmitStandAlone]
      FORM_SPAWNTEMPLATE = [:Form, :SpawnTemplate]
      FORM_BARCODEPLAINTEXT = [:Form, :BarcodePlaintext]
      FORM_ONLINE = [:Form, :Online]
      FORM_ALL = [:Form, :FillIn, :Import, :Export, :SubmitStandAlone, :SpawnTemplate, :BarcodePlaintext, :Online]
      
      FORMEX_BARCODEPLAINTEXT = [:FormEx, :BarcodePlaintext]
      FORMEX_ALL = FORMEX_BARCODEPLAINTEXT
      
      SIGNATURE_MODIFY = [:Signature, :Modify]
      SIGNATURE_ALL = SIGNATURE_MODIFY
      
      EF_CREATE = [:EF, :Create]
      EF_DELETE = [:EF, :Delete]
      EF_MODIFY = [:EF, :Modify]
      EF_IMPORT = [:EF, :Import]
      EF_ALL = [:EF, :Create, :Delete, :Modify, :Import]
      
      ALL = [ DOCUMENT_ALL, ANNOTS_ALL, FORM_ALL, SIGNATURE_ALL, EF_ALL ]
      
    end
    
    class TransformParams < Dictionary
      
      include Configurable
      
      VERSION = Name.new("2.2")
     
      field   :Type,              :Type => Name, :Default => :TransformParams
      field   :Document,          :Type => Array
      field   :Msg,               :Type => String
      field   :V,                 :Type => Name, :Default => VERSION
      field   :Annots,            :Type => Array
      field   :Form,              :Type => Array
      field   :FormEx,            :Type => Array
      field   :Signature,         :Type => Array
      field   :EF,                :Type => Array, :Version => "1.6"
      field   :P,                 :Type => Boolean, :Default => false, :Version => "1.6"

      def initialize(hash = {})
        set_indirect(false)

        super(hash)
      end

    end
    
  end

end
