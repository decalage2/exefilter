module Origami

  module Obfuscator

    WHITECHARS = [ " ", "\t", "\r", "\n", "\0" ] 
    OBJECTS = [ Array, Boolean, Dictionary, Integer, Name, Null, Stream, String, Real, Reference ]
    MAX_INT = 0xFFFFFFFF
    PRINTABLE = ("!".."9").to_a + (':'..'Z').to_a + ('['..'z').to_a + ('{'..'~').to_a
    FILTERS = [ :FlateDecode, :RunLengthDecode, :LZWDecode, :ASCIIHexDecode, :ASCII85Decode ]

    def self.junk_spaces(max_size = 3)
      length = rand(max_size) + 1

      ::Array.new(length) { WHITECHARS[rand(WHITECHARS.size)] }.join
    end

    def self.junk_comment(max_size = 15)
      length = rand(max_size) + 1

      junk_comment = ::Array.new(length) { 
        byte = rand(256).chr until (not byte.nil? and byte != "\n" and byte != "\r"); byte 
      }.join
      
      "%#{junk_comment}#{EOL}"
    end

    def self.junk_object(type = nil)

      if type.nil?
        type = OBJECTS[rand(OBJECTS.size)]
      end

      unless type.include?(Origami::Object)
        raise TypeError, "Not a valid object type"
      end

      Obfuscator.send("junk_#{type.to_s.split('::').last.downcase}")
    end

    def self.junk_array(max_size = 5)
      length = rand(max_size) + 1

      ::Array.new(length) {
        obj = Obfuscator.junk_object until (not obj.nil? and not obj.is_a?(Stream)) ; obj
      }.to_o 
    end

    def self.junk_boolean
      Boolean.new(rand(2).zero?)
    end

    def self.junk_dictionary(max_size = 5)
      length = rand(max_size) + 1

      hash = Hash.new
      length.times do 
        obj = Obfuscator.junk_object
        hash[Obfuscator.junk_name] = obj unless obj.is_a?(Stream)
      end
      
      hash.to_o
    end

    def self.junk_integer(max = MAX_INT)
      Integer.new(rand(max + 1))
    end

    def self.junk_name(max_size = 8)
      length = rand(max_size) + 1

      Name.new(::Array.new(length) { PRINTABLE[rand(PRINTABLE.size)] }.join)
    end

    def self.junk_null
      Null.new
    end

    def self.junk_stream(max_data_size = 200)
      
      chainlen = rand(2) + 1
      chain = ::Array.new(chainlen) { FILTERS[rand(FILTERS.size)] }

      length = rand(max_data_size) + 1
      junk_data = ::Array.new(length) { rand(256).chr }.join

      stm = Stream.new
      stm.dictionary = Obfuscator.junk_dictionary(5)
      stm.setFilter(chain)
      stm.data = junk_data

      stm
    end

    def self.junk_string(max_size = 10)
      length = rand(max_size) + 1

      strtype = (rand(2).zero?) ? ByteString : HexaString

      strtype.new(::Array.new(length) { PRINTABLE[rand(PRINTABLE.size)] }.join)
    end

    def self.junk_real
      Real.new(rand * rand(MAX_INT + 1))
    end

    def self.junk_reference(max_no = 300, max_gen = 1)
      no = rand(max_no) + 1
      gen = rand(max_gen)

      Reference.new(no, gen)
    end

  end

  class Dictionary
    
    def to_obfuscated_str
      content = TOKENS.first + Obfuscator.junk_spaces
      self.each_pair { |key, value|
        content << Obfuscator.junk_spaces + 
          key.to_obfuscated_str + Obfuscator.junk_spaces + 
          value.to_obfuscated_str + Obfuscator.junk_spaces
      }

      content << TOKENS.last
      print(content)
    end

  end

  class Array
    def to_obfuscated_str
      content = TOKENS.first + Obfuscator.junk_spaces
      self.each { |entry|
        content << entry.to_o.to_obfuscated_str + Obfuscator.junk_spaces
      }

      content << TOKENS.last

      print(content)
    end
  end

  class Null
    alias :to_obfuscated_str :to_s
  end

  class Boolean
    alias :to_obfuscated_str :to_s
  end

  class Integer
    alias :to_obfuscated_str :to_s
  end

  class Real
    alias :to_obfuscated_str :to_s
  end

  class Reference
    def to_obfuscated_str
      refstr = refno.to_s + Obfuscator.junk_spaces + refgen.to_s + Obfuscator.junk_spaces + "R"

      print(refstr)
    end
  end

  class ByteString
    def to_obfuscated_str
      to_s
    end
  end

  class HexaString
    def to_obfuscated_str
      to_s
    end
  end

  class Name
    def to_obfuscated_str(prop = 2)
      name = (self.value == :" ") ? "" : self.id2name
      
      forbiddenchars = [ " ","#","\t","\r","\n","\0","[","]","<",">","(",")","%","/","\\" ]

      name.gsub!(/./) do |c|
        if rand(prop) == 0 or forbiddenchars.include?(c)
          hexchar = c[0].to_s(base=16)
          hexchar = "0" + hexchar if hexchar.length < 2
          
          '#' + hexchar
        else
          c
        end
      end

      print(TOKENS.first + name)
    end
  end

  class Stream
    def to_obfuscated_str
      content = ""
      
      content << @dictionary.to_obfuscated_str
      content << "stream" + EOL
      content << self.rawdata
      content << EOL << TOKENS.last
      
      print(content)
    end
  end

  class PDF

    def obfuscate_and_saveas(filename, options = {})
      options[:obfuscate] = true
      saveas(filename, options)
    end
  end

  class Trailer

    def to_obfuscated_str
      content = ""
      if self.has_dictionary?
        content << TOKENS.first << EOL << @dictionary.to_obfuscated_str << EOL
      end

      content << XREF_TOKEN << EOL << @startxref.to_s << EOL << TOKENS.last << EOL

      content
    end

  end

end
