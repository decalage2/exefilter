=begin

= File
	encryption.rb

= Info
	This file is part of Origami, PDF manipulation framework for Ruby
	Copyright (C) 2009	Guillaume DelugrÈ <guillaume@security-labs.org>
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

require 'digest/md5'
require 'digest/sha2'

module Origami

  class EncryptionError < Exception #:nodoc:
  end

  class EncryptionInvalidPasswordError < EncryptionError #:nodoc:
  end

  class EncryptionNotSupportedError < EncryptionError #:nodoc:
  end

  class PDF
  
    #
    # Returns whether the PDF file is encrypted.
    #
    def is_encrypted?
      has_attr? :Encrypt
    end
   
    #
    # Decrypts the current document (only RC4 40..128 bits).
    # TODO: AESv2, AESv3, lazy decryption
    # _passwd_:: The password to decrypt the document.
    #
    def decrypt(passwd = "")
    
      unless self.is_encrypted?
        raise EncryptionError, "PDF is not encrypted"
      end
     
      encrypt_dict = get_doc_attr(:Encrypt)
      handler = Encryption::Standard::Dictionary.new(encrypt_dict.copy)

      unless handler.Filter == :Standard
        raise EncryptionNotSupportedError, "Unknown security handler : '#{handler.Filter.to_s}'"
      end

      case handler.V.to_i
        when 1,2 then str_algo = stm_algo = Encryption::ARC4
        when 4
          if handler[:CF].is_a?(Dictionary)
            cfs = handler[:CF]
            
            if handler[:StrF].is_a?(Name) and cfs[handler[:StrF]].is_a?(Dictionary)
              cfdict = cfs[handler[:StrF]]
              
              str_algo =
              if cfdict[:CFM] == :V2 then Encryption::ARC4
              elsif cfdict[:CFM] == :AESV2 then Encryption::AES
              elsif cfdict[:CFM] == :None then Encryption::Identity
              else
                Encryption::Identity
              end
            else
              str_algo = Encryption::Identity
            end

            if handler[:StmF].is_a?(Name) and cfs[handler[:StmF]].is_a?(Dictionary)
              cfdict = cfs[handler[:StmF]]

              stm_algo =
              if cfdict[:CFM] == :V2 then Encryption::ARC4
              elsif cfdict[:CFM] == :AESV2 then Encryption::AES
              elsif cfdict[:CFM] == :None then Encryption::Identity
              else
                Encryption::Identity
              end
            else
              stm_algo = Encryption::Identity
            end

          else
            str_algo = stm_algo = Encryption::Identity
          end
      else
        raise EncryptionNotSupportedError, "Unsupported encryption version : #{handler.V}"
      end

      id = get_doc_attr(:ID)
      if id.nil? or not id.is_a?(Array)
        raise EncryptionError, "Document ID was not found or is invalid"
      else
        id = id.first
      end

      if not handler.is_owner_password?(passwd, id) and not handler.is_user_password?(passwd, id)
        raise EncryptionInvalidPasswordError
      end

      encryption_key = handler.compute_encryption_key(passwd, id)

      #self.extend(Encryption::EncryptedDocument)
      #self.encryption_dict = encrypt_dict
      #self.encryption_key = encryption_key
      #self.stm_algo = self.str_algo = algorithm

      encrypt_metadata = (handler.EncryptMetadata != false)
      #
      # Should be fixed to exclude only the active XRefStream
      #
      encrypted_objects = self.objects(false).find_all{ |obj|

        (obj.is_a?(String) and 
          not obj.indirect_parent.is_a?(XRefStream) and 
          not obj.equal?(encrypt_dict[:U]) and 
          not obj.equal?(encrypt_dict[:O])) or 
        
        (obj.is_a?(Stream) and 
          not obj.is_a?(XRefStream) and
          (not obj.equal?(self.Catalog.Metadata) or encrypt_metadata))
      }
     
      encrypted_objects.each { |obj|
        no = obj.indirect_parent.no
        gen = obj.indirect_parent.generation

        k = encryption_key + [no].pack("I")[0..2] + [gen].pack("I")[0..1]
        key_len = (k.length > 16) ? 16 : k.length

        case obj
          when String
            k << "sAlT" if str_algo == Encryption::AES
          when Stream
            k << "sAlT" if stm_algo == Encryption::AES
        end

        key = Digest::MD5.digest(k)[0, key_len]

        case obj
          when String then obj.replace(str_algo.decrypt(key, obj.value))
          when Stream then obj.rawdata = stm_algo.decrypt(key, obj.rawdata) 
        end
      }

      self
    end
   
    #
    # Encrypts the current document with the provided passwords.
    # The document will be encrypted at writing-on-disk time.
    # _userpasswd_:: The user password.
    # _ownerpasswd_:: The owner password.
    # _options_:: A set of options to configure encryption.
    #
    def encrypt(userpasswd, ownerpasswd, options = {})
    
      if self.is_encrypted?
        raise EncryptionError, "PDF is already encrypted"
      end

      #
      # Default encryption options.
      #
      params = 
      {
        :Algorithm => :RC4,         # :RC4 or :AES
        :KeyLength => 128,          # Key size in bits
        :EncryptMetadata => true,    # Metadata shall be encrypted?
        :Permissions => Encryption::Standard::Permissions::ALL    # Document permissions
      }

      params.update(options)

      case params[:Algorithm]
      when :RC4
        algorithm = Encryption::ARC4
        if (40..128) === params[:KeyLength] and params[:KeyLength] % 8 == 0
          if params[:KeyLength] > 40
            version = 2
            revision = 3
          else
            version = 1
            revision = 2
          end
        else
          raise EncryptionError, "Invalid key length"
        end
      when :AES
        algorithm = Encryption::AES
        if params[:KeyLength] == 128 
          version = revision = 4
        else
          raise EncryptionError, "Invalid key length"
        end
      else
        raise EncryptionNotSupportedError, "Algorithm not supported : #{params[:Algorithm]}"
      end
     
      id = (get_doc_attr(:ID) || gen_id).first

      handler = Encryption::Standard::Dictionary.new
      handler.Filter = :Standard #:nodoc:
      handler.V = version
      handler.R = revision
      handler.Length = params[:KeyLength]
      handler.P = params[:Permissions] 
      
      if revision == 4
        handler.EncryptMetadata = params[:EncryptMetadata]
        handler.CF = Dictionary.new
        cryptfilter = Encryption::CryptFilterDictionary.new
        cryptfilter.AuthEvent = :DocOpen
        cryptfilter.CFM = :AESV2
        cryptfilter.Length = params[:KeyLength] >> 3

        handler.CF[:StdCF] = cryptfilter
        handler.StmF = handler.StrF = :StdCF
      end
      
      handler.set_owner_password(userpasswd, ownerpasswd)
      handler.set_user_password(userpasswd, id)
      
      encryption_key = handler.compute_encryption_key(userpasswd, id)

      fileInfo = get_trailer_info
      fileInfo[:Encrypt] = self << handler

      self.extend(Encryption::EncryptedDocument)
      self.encryption_dict = handler
      self.encryption_key = encryption_key
      self.stm_algo = self.str_algo = algorithm

      self
    end
  
  end

  #
  # Module to provide support for encrypting and decrypting PDF documents.
  #
  module Encryption

    module EncryptedDocument

      attr_writer :encryption_key
      attr_writer :encryption_dict
      attr_writer :stm_algo
      attr_writer :str_algo

      def physicalize

        def build(obj, revision, embedded = false) #:nodoc:
     
          if obj.is_a?(ObjectStream)
            obj.each { |subobj|
              build(subobj, revision, true)
            }
          end

          obj.pre_build

          case obj
          when String
            if not obj.equal?(@encryption_dict[:U]) and not obj.equal?(@encryption_dict[:O]) and not embedded 
              obj.extend(EncryptedString)
              obj.encryption_key = @encryption_key
              obj.algorithm = @str_algo
            end

          when Stream
            obj.extend(EncryptedStream)
            obj.encryption_key = @encryption_key
            obj.algorithm = @stm_algo

          when Dictionary, Array

              obj.map! { |subobj|
                if subobj.is_indirect?
                  if get_object(subobj.reference)
                    subobj.reference
                  else
                    ref = add_to_revision(subobj, revision)
                    build(subobj, revision, embedded)
                    ref
                  end
                else
                  subobj
                end
              }
              
              obj.each { |subobj|
                build(subobj, revision, embedded)
              }    
          end

          obj.post_build
          
        end
       
        all_indirect_objects.each { |obj, revision|
            build(obj, revision)          
        }
        
        self
      end
      
    end

    #
    # Module for encrypted PDF objects.
    #
    module EncryptedObject #:nodoc

      attr_writer :encryption_key
      attr_writer :algorithm

      def post_build
        encrypt!

        super
      end

      private 

      def compute_object_key
        no = self.indirect_parent.no
        gen = self.indirect_parent.generation
        k = @encryption_key + [no].pack("I")[0..2] + [gen].pack("I")[0..1]
       
        key_len = (k.length > 16) ? 16 : k.length        
        k << "sAlT" if @algorithm == Encryption::AES
 
        Digest::MD5.digest(k)[0, key_len]
      end

    end

    #
    # Module for encrypted String.
    #
    module EncryptedString

      include EncryptedObject

      private

      def encrypt!
        key = compute_object_key
        
        encrypted_data = 
        if @algorithm == ARC4 or @algorithm == Identity
          @algorithm.encrypt(key, self.value)
        else
          iv = ::Array.new(16) { rand(255) }.pack('C*')
          @algorithm.encrypt(key, iv, self.value)
        end

        self.replace(encrypted_data)
        self.freeze
      end

    end

    #
    # Module for encrypted Stream.
    #
    module EncryptedStream
      
      include EncryptedObject

      private

      def encrypt!
        encode!

        key = compute_object_key

        @rawdata = 
        if @algorithm == ARC4 or @algorithm == Identity
          @algorithm.encrypt(key, self.rawdata)
        else
          iv = ::Array.new(16) { rand(255) }.pack('C*')
          @algorithm.encrypt(key, iv, @rawdata)
        end

        @rawdata.freeze
        self.freeze
      end

    end

    #
    # Identity transformation.
    #
    module Identity

      def Identity.encrypt(key, data)
        data
      end

      def Identity.decrypt(key, data)
        data
      end

    end

    #
    # Pure Ruby implementation of the aRC4 symmetric algorithm
    #
    class ARC4
    
      #
      # Encrypts data using the given key
      #
      def ARC4.encrypt(key, data)
     
        ARC4.new(key).encrypt(data)
        
      end
      
      #
      # Decrypts data using the given key
      #
      def ARC4.decrypt(key, data)

        ARC4.new(key).decrypt(data)
      
      end
      
      #
      # Creates and initialises a new aRC4 generator using given key
      #
      def initialize(key)
        
        @state = init(key)
        
      end
      
      #
      # Encrypt/decrypt data with the aRC4 encryption algorithm
      #
      def cipher(data)
      
        output = ""
        i, j = 0, 0
        data.each_byte do |byte|
          i = i.succ & 0xFF
          j = (j + @state[i]) & 0xFF
          
          @state[i], @state[j] = @state[j], @state[i]
          
          output << (@state[@state[i] + @state[j] & 0xFF] ^ byte).chr
        end
      
        output
      end
      
      alias encrypt cipher
      alias decrypt cipher
      
      private
      
      def init(key) #:nodoc:
        
        state = (0..255).to_a
        
        j = 0
        256.times do |i|
          j = ( j + state[i] + key[i % key.size] ) & 0xFF
          state[i], state[j] = state[j], state[i]
        end
        
        state
      end

    end

    #
    # Pure Ruby implementation of the AES symmetric algorithm.
    # Using mode CBC.
    # TO BE DONE
    #
    class AES #:nodoc:
      
      NROWS = 4
      NCOLS = 4
      BLOCKSIZE = NROWS * NCOLS

      ROUNDS = 
      {
        16 => 10,
        24 => 12,
        32 => 14
      }

      #
      # Rijndael S-box
      #
      SBOX = 
      [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
      ]

      #
      # Inverse of the Rijndael S-box
      #
      RSBOX = 
      [
        0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
        0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
        0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
        0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
        0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
        0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
        0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
        0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
        0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
        0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
        0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
        0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
        0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
        0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
        0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
      ]

      RCON = 
      [
        0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a,
        0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39,
        0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a,
        0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8,
        0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef,
        0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc,
        0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b,
        0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3,
        0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94,
        0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20,
        0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35,
        0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f,
        0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04,
        0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63,
        0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd,
        0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb
      ]

      attr_writer :iv

      def AES.encrypt(key, iv, data)
        AES.new(key, iv).encrypt(data)
      end

      def AES.decrypt(key, data)
        AES.new(key).decrypt(data)
      end
      
      def initialize(key, iv = nil)
        unless key.size == 16 or key.size == 24 or key.size == 32
          raise EncryptionError, "Key must have a length of 128, 192 or 256 bits."
        end

        if not iv.nil? and iv.size != BLOCKSIZE
          raise EncryptionError, "Initialization vector must have a length of #{BLOCKSIZE} bytes."
        end

        @key = key
        @iv = iv
      end

      def encrypt(data)

        if @iv.nil?
          raise EncryptionError, "No initialization vector has been set."
        end
        
        padlen = BLOCKSIZE - (data.size % BLOCKSIZE)
        data << (padlen.chr * padlen)

        cipher = []
        cipherblock = []
        nblocks = data.size / BLOCKSIZE

        first_round = true
        nblocks.times do |n|
          plainblock = data[n * BLOCKSIZE, BLOCKSIZE].unpack("C*")

          if first_round
            BLOCKSIZE.times do |i| plainblock[i] ^= @iv[i] end
          else
            BLOCKSIZE.times do |i| plainblock[i] ^= cipherblock[i] end
          end

          first_round = false
          cipherblock = aesEncrypt(plainblock)
          cipher.concat(cipherblock)
        end

        @iv + cipher.pack("C*")
      end 

      def decrypt(data)
        
        unless data.size % BLOCKSIZE == 0
          puts data.size
          hexprint data
          raise EncryptionError, "Data must be 16-bytes padded"
        end

        @iv = data.slice!(0, BLOCKSIZE)

        plain = []
        plainblock = []
        prev_cipherblock = []
        nblocks = data.size / BLOCKSIZE

        first_round = true
        nblocks.times do |n|
          cipherblock = data[n * BLOCKSIZE, BLOCKSIZE].unpack("C*")

          plainblock = aesDecrypt(cipherblock)

          if first_round
            BLOCKSIZE.times do |i| plainblock[i] ^= @iv[i] end
          else
            BLOCKSIZE.times do |i| plainblock[i] ^= prev_cipherblock[i] end
          end

          first_round = false
          prev_cipherblock = cipherblock
          plain.concat(plainblock)
        end
      
        padlen = plain[-1]
        unless (1..16) === padlen
          raise EncryptionError, "Incorrect padding byte"
        end

        padlen.times do 
          pad = plain.pop
          raise EncryptionError, "Incorrect padding byte" if pad != padlen
        end

        plain.pack("C*")
      end

      private

      def rol(row, n = 1) #:nodoc
        n.times do row.push row.shift end ; row
      end

      def ror(row, n = 1) #:nodoc:
        n.times do row.unshift row.pop end ; row
      end

      def galoisMult(a, b) #:nodoc:
        p = 0

        8.times do 
          p ^= a if b[0] == 1
          highBit = a[7]
          a <<= 1
          a ^= 0x1b if highBit == 1
          b >>= 1
        end

        p % 256
      end

      def scheduleCore(word, iter) #:nodoc:
        rol(word)
        word.map! do |byte| SBOX[byte] end
        word[0] ^= RCON[iter]

        word
      end

      def transpose(m)
        [
          m[NROWS * 0, NROWS],
          m[NROWS * 1, NROWS],
          m[NROWS * 2, NROWS],
          m[NROWS * 3, NROWS]
        ].transpose.flatten
      end

      #
      # AES round methods.
      #

      def createRoundKey(expandedKey, round = 0) #:nodoc:
        transpose(expandedKey[round * BLOCKSIZE, BLOCKSIZE])
      end

      def addRoundKey(roundKey) #:nodoc:
        BLOCKSIZE.times do |i| @state[i] ^= roundKey[i] end 
      end

      def subBytes #:nodoc:
        BLOCKSIZE.times do |i| @state[i] = SBOX[ @state[i] ] end
      end

      def rsubBytes #:nodoc:
        BLOCKSIZE.times do |i| @state[i] = RSBOX[ @state[i] ] end
      end

      def shiftRows #:nodoc:
        NROWS.times do |i|
          @state[i * NCOLS, NCOLS] = rol(@state[i * NCOLS, NCOLS], i)
        end
      end

      def rshiftRows #:nodoc:
        NROWS.times do |i|
          @state[i * NCOLS, NCOLS] = ror(@state[i * NCOLS, NCOLS], i)
        end
      end

      def mixColumnWithField(column, field)
        p = field
 
        column[0], column[1], column[2], column[3] =
          galoisMult(column[0], p[0]) ^ galoisMult(column[3], p[1]) ^ galoisMult(column[2], p[2]) ^ galoisMult(column[1], p[3]),
          galoisMult(column[1], p[0]) ^ galoisMult(column[0], p[1]) ^ galoisMult(column[3], p[2]) ^ galoisMult(column[2], p[3]),
          galoisMult(column[2], p[0]) ^ galoisMult(column[1], p[1]) ^ galoisMult(column[0], p[2]) ^ galoisMult(column[3], p[3]),
          galoisMult(column[3], p[0]) ^ galoisMult(column[2], p[1]) ^ galoisMult(column[1], p[2]) ^ galoisMult(column[0], p[3])
     end

      def mixColumn(column) #:nodoc:
        mixColumnWithField(column, [ 2, 1, 1, 3 ])
      end

      def rmixColumn(column)
        mixColumnWithField(column, [ 14, 9, 13, 11 ])
      end

      def mixColumns #:nodoc:
        NCOLS.times do |c|
          column = []
          NROWS.times do |r| column << @state[c + r * NCOLS] end
          mixColumn(column)
          NROWS.times do |r| @state[c + r * NCOLS] = column[r] end
        end
      end

      def rmixColumns #:nodoc:
        NCOLS.times do |c|
          column = []
          NROWS.times do |r| column << @state[c + r * NCOLS] end
          rmixColumn(column)
          NROWS.times do |r| @state[c + r * NCOLS] = column[r] end
        end
      end

      def expandKey(key) #:nodoc:

        key = key.unpack("C*")
        size = key.size
        expandedSize = 16 * (ROUNDS[key.size] + 1)
        rconIter = 1
        expandedKey = key[0, size]

        while expandedKey.size < expandedSize
          temp = expandedKey[-4, 4]

          if expandedKey.size % size == 0
            scheduleCore(temp, rconIter)
            rconIter = rconIter.succ 
          end

          temp.map! do |b| SBOX[b] end if size == 32 and expandedKey.size % size == 16

          temp.each do |b| expandedKey << (expandedKey[-size] ^ b) end
        end

        expandedKey
      end

      def aesRound(roundKey) #:nodoc:
        subBytes
        #puts "after subBytes: #{@state.inspect}"
        shiftRows
        #puts "after shiftRows: #{@state.inspect}"
        mixColumns
        #puts "after mixColumns: #{@state.inspect}"
        addRoundKey(roundKey)
        #puts "roundKey = #{roundKey.inspect}"
        #puts "after addRoundKey: #{@state.inspect}"
      end

      def raesRound(roundKey) #:nodoc:
        addRoundKey(roundKey)
        rmixColumns
        rshiftRows
        rsubBytes
      end

      def aesEncrypt(block) #:nodoc:
        @state = transpose(block)
        expandedKey = expandKey(@key)
        rounds = ROUNDS[@key.size]

        aesMain(expandedKey, rounds)
      end

      def aesDecrypt(block) #:nodoc:
        @state = transpose(block)
        expandedKey = expandKey(@key)
        rounds = ROUNDS[@key.size]

        raesMain(expandedKey, rounds)
      end

      def aesMain(expandedKey, rounds) #:nodoc:
        #puts "expandedKey: #{expandedKey.inspect}" 
        roundKey = createRoundKey(expandedKey)
        addRoundKey(roundKey)

        for i in 1..rounds-1
          roundKey = createRoundKey(expandedKey, i)
          aesRound(roundKey)
        end

        roundKey = createRoundKey(expandedKey, rounds)
        subBytes
        shiftRows
        addRoundKey(roundKey)

        transpose(@state)
      end

      def raesMain(expandedKey, rounds) #:nodoc:
       
        roundKey = createRoundKey(expandedKey, rounds)
        addRoundKey(roundKey)
        rshiftRows
        rsubBytes
        
        (rounds - 1).downto(1) do |i|
          roundKey = createRoundKey(expandedKey, i)
          raesRound(roundKey)
        end

        roundKey = createRoundKey(expandedKey)
        addRoundKey(roundKey)

        transpose(@state)
      end

    end
  
    #
    # Class representing a crypt filter Dictionary
    #
    class CryptFilterDictionary < Dictionary

      include Configurable

      field   :Type,          :Type => Name, :Default => :CryptFilter
      field   :CFM,           :Type => Name, :Default => :None
      field   :AuthEvent,     :Type => Name, :Default => :DocOpen
      field   :Length,        :Type => Integer

    end

    #
    # Common class for encryption dictionaries.
    #
    class EncryptionDictionary < Dictionary
      
      include Configurable

      field   :Filter,        :Type => Name, :Default => :Standard, :Required => true
      field   :SubFilter,     :Type => Name, :Version => "1.3"
      field   :V,             :Type => Integer, :Default => 0
      field   :Length,        :Type => Integer, :Default => 40, :Version => "1.4"
      field   :CF,            :Type => Dictionary, :Version => "1.5"
      field   :StmF,          :Type => Name, :Default => :Identity, :Version => "1.5"
      field   :StrF,          :Type => Name, :Default => :Identity, :Version => "1.5"
      field   :EFF,           :Type => Name, :Version => "1.6"

    end
    
    #
    # The standard security handler for PDF encryption.
    #
    module Standard
    
      PADDING = "\x28\xBF\x4E\x5E\x4E\x75\x8A\x41\x64\x00\x4E\x56\xFF\xFA\x01\x08\x2E\x2E\x00\xB6\xD0\x68\x3E\x80\x2F\x0C\xA9\xFE\x64\x53\x69\x7A" #:nodoc:
    
      #
      # Permission constants for encrypted documents.
      #
      module Permissions
        RESERVED = 1 << 6 | 1 << 7 | 0xFFFFF000
        PRINT = 1 << 2 | RESERVED
        MODIFY_CONTENTS = 1 << 3 | RESERVED
        COPY_CONTENTS = 1 << 4 | RESERVED
        MODIFY_ANNOTATIONS = 1 << 5 | RESERVED
        FILLIN_FORMS = 1 << 8 | RESERVED
        EXTRACT_CONTENTS = 1 << 9 | RESERVED
        ASSEMBLE_DOC = 1 << 10 | RESERVED
        HIGH_QUALITY_PRINT = 1 << 11 | RESERVED
        
        ALL = PRINT | MODIFY_CONTENTS | COPY_CONTENTS | MODIFY_ANNOTATIONS | FILLIN_FORMS | EXTRACT_CONTENTS | ASSEMBLE_DOC | HIGH_QUALITY_PRINT
      end
    
      #
      # Class defining a standard encryption dictionary.
      # 
      class Dictionary < EncryptionDictionary
    
        field   :R,             :Type => Number, :Required => true
        field   :O,             :Type => String, :Required => true
        field   :U,             :Type => String, :Required => true
        field   :P,             :Type => Integer, :Default => 0, :Required => true
        field   :EncryptMetadata, :Type => Boolean, :Default => true, :Version => "1.5"
        
        #
        # Computes the key that will be used to encrypt/decrypt the document.
        #
        def compute_encryption_key(password, fileid)
          
          padded = pad_password(password)

          padded << self.O
          padded << [ self.P ].pack("i")
          
          padded << fileid
          
          encrypt_metadata = self.EncryptMetadata != false
          padded << "\xFF\xFF\xFF\xFF" if self.R >= 4 and not encrypt_metadata

          key = Digest::MD5.digest(padded)

          50.times { key = Digest::MD5.digest(key[0, self.Length / 8]) } if self.R >= 3

          if self.R == 2
            key[0, 5]
          elsif self.R >= 3
            key[0, self.Length / 8]
          end
           
        end
        
        #
        # Set owner password.
        #
        def set_owner_password(userpassword, ownerpassword = nil)
          
          key = compute_owner_encryption_key(userpassword, ownerpassword)
          upadded = pad_password(userpassword)
          
          owner_key = ARC4.encrypt(key, upadded)
          19.times { |i| owner_key = ARC4.encrypt(xor(key,i+1), owner_key) } if self.R >= 3
          
          self.O = owner_key
        end
        
        #
        # Set user password.
        #
        def set_user_password(userpassword, fileid = nil)
          
          self.U = compute_user_password(userpassword, fileid)
        end
        
        #
        # Checks user password.
        #
        def is_user_password?(pass, fileid)
          
          if self.R == 2 
            compute_user_password(pass, fileid) == self.U
          elsif self.R >= 3
            compute_user_password(pass, fileid)[0, 16] == self.U[0, 16]
          end
          
        end
        
        #
        # Checks owner password.
        #
        def is_owner_password?(pass, fileid)
        
          key = compute_owner_encryption_key(pass)

          if self.R == 2
            user_password = ARC4.decrypt(key, self.O)
          elsif self.R >= 3
            user_password = ARC4.decrypt(xor(key, 19), self.O)
            19.times { |i| user_password = ARC4.decrypt(xor(key, 18-i), user_password) }
          end
          
          is_user_password?(user_password, fileid)
        end
        
        private
        
        def compute_owner_encryption_key(userpassword, ownerpassword = nil) #:nodoc:

          opadded = pad_password(ownerpassword || userpassword)
          
          hash = Digest::MD5.digest(opadded)
          50.times { hash = Digest::MD5.digest(hash) } if self.R >= 3
          
          if self.R == 2
            hash[0, 5]
          elsif self.R >= 3
            hash[0, self.Length / 8]
          end

        end
        
        def compute_user_password(userpassword, fileid) #:nodoc:
        
          key = compute_encryption_key(userpassword, fileid)
          
          if self.R == 2
            user_key = ARC4.encrypt(key, PADDING)
          elsif self.R >= 3
            upadded = PADDING + fileid
            hash = Digest::MD5.digest(upadded)
            
            user_key = ARC4.encrypt(key, hash)
            
            19.times { |i| user_key = ARC4.encrypt(xor(key,i+1), user_key) }
            
            user_key.ljust(32, "\xFF")
          end
        
        end
        
        def xor(str, byte) #:nodoc:
          str.split(//).map!{|c| (c[0] ^ byte).chr }.join
        end
        
        def pad_password(password) #:nodoc:
          password[0,32].ljust(32, PADDING)
        end
      
      end
    
    end
  
  end

end

def hexprint(str)
  hex = "" 
  str.each_byte do |b|
    digit = b.to_s(16)
    digit = "0" + digit if digit.size == 1 
    hex << digit
  end
 
  puts hex.upcase
end

