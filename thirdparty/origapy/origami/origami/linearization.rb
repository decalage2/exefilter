=begin

= File
	linearization.rb

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

  class PDF

    #
    # Returns whether the current document is linearized.
    #
    def is_linearized?
      begin
        obj = @revisions.first.body.values.sort_by{|obj| obj.file_offset}.first
      rescue
        return false
      end

      obj.is_a?(Dictionary) and obj.has_key? :Linearized
    end   

    #
    # Tries to delinearize the document if it has been linearized.
    # This operation is xrefs destructive, should be fixed in the future to merge tables.
    #
    def delinearize!
      raise RuntimeError, 'Not a linearized document' unless is_linearized?
      
      #
      # Saves the catalog location.
      #
      catalog_ref = self.Catalog.reference

      lin_dict = @revisions.first.body.values.first
      hints = lin_dict[:H]
  
      #
      # Removes hint streams used by linearization.
      #
      if hints.is_a?(::Array)
        if hints.length > 0 and hints[0].is_a?(Integer)
          hint_stream = get_object_by_offset(hints[0])
          delete_object(hint_stream.reference) if hint_stream.is_a?(Stream)
        end

        if hints.length > 2 and hints[2].is_a?(Integer)
          overflow_stream = get_object_by_offset(hints[2])
          delete_object(overflow_stream.reference) if overflow_stream.is_a?(Stream)
        end
      end

      #
      # Fix: Should be merged instead.
      #
      remove_xrefs

      #
      # Remove the linearization revision.
      #
      remove_revision(0)

      #
      # Restore the Catalog.
      #
      @revisions.last.trailer ||= Trailer.new
      @revisions.last.trailer.dictionary ||= Dictionary.new
      @revisions.last.trailer.dictionary[:Root] = catalog_ref

      self
    end

  end

  #
  # Class representing a linearization dictionary.
  #
  class Linearization < Dictionary

    include Configurable

    field   :Linearized,   :Type => Real, :Default => 1.0, :Required => true
    field   :L,            :Type => Integer, :Required => true
    field   :H,            :Type => Array, :Required => true
    field   :O,            :Type => Integer, :Required => true
    field   :E,            :Type => Integer, :Required => true
    field   :N,            :Type => Integer, :Required => true
    field   :T,            :Type => Integer, :Required => true
    field   :P,            :Type => Integer, :Default => 0

    def initialize(hash = {})
      super(hash, true)
    end

  end

  class InvalidHintTableError < Exception #:nodoc:
  end

  module HintTable

    module ClassMethods
      
      def header_item_size(number, size)
        @header_items_size[number] = size
      end

      def get_header_item_size(number)
        @header_items_size[number]
      end

      def entry_item_size(number, size)
        @entry_items_size[number] = size
      end

      def get_entry_item_size(number)
        @entry_items_size[number] 
      end

      def nb_header_items
        @header_items_size.size
      end

      def nb_entry_items
        @entry_items_size.size
      end

    end

    def self.included(receiver)
      receiver.instance_variable_set(:@header_items_size, {})
      receiver.instance_variable_set(:@entry_items_size, {})
      receiver.extend(ClassMethods)
    end

    attr_accessor :header_items
    attr_accessor :entries

    def initialize
      @header_items = {}
      @entries = []
    end

    def to_s
      
      data = ""

      nitems = self.class.nb_header_items
      for no in (1..nitems)
        unless @header_items.include?(no)
          raise InvalidHintTableError, "Missing item #{no} in header section of #{self.class}"
        end

        value = @header_items[no]
        item_size = self.class.get_header_item_size(no)
        
        item_size = ((item_size + 7) >> 3) << 3
        item_data = value.to_s(2)
        item_data = "0" * (item_size - item_data.size) + item_data

        data << [ item_data ].pack("B*")
      end
      
      i = 0
      nitems = self.class.nb_entry_items
      @entries.each do |entry|
        for no in (1..items)
          unless entry.include?(no)
            raise InvalidHintTableError, "Missing item #{no} in entry #{i} of #{self.class}"
          end

          value = entry[no]
          item_size = self.class.get_entry_item_size(no)
          
          item_size = ((item_size + 7) >> 3) << 3
          item_data = value.to_s(2)
          item_data = "0" * (item_size - item_data.size) + item_data

          data << [ item_data ].pack("B*")
        end

        i = i + 1
      end

      data
    end

    class PageOffsetTable
      include HintTable

      header_item_size  1,  32
      header_item_size  2,  32
      header_item_size  3,  16
      header_item_size  4,  32
      header_item_size  5,  16
      header_item_size  6,  32
      header_item_size  7,  16
      header_item_size  8,  32
      header_item_size  9,  16
      header_item_size  10,  16
      header_item_size  11,  16
      header_item_size  12,  16
      header_item_size  13,  16

      entry_item_size   1,  16
      entry_item_size   2,  16
      entry_item_size   3,  16
      entry_item_size   4,  16
      entry_item_size   5,  16
      entry_item_size   6,  16
      entry_item_size   7,  16
    end

    class SharedObjectTable
      include HintTable

      header_item_size  1,  32
      header_item_size  2,  32
      header_item_size  3,  32
      header_item_size  4,  32
      header_item_size  5,  16
      header_item_size  6,  32
      header_item_size  7,  16

      entry_item_size   1,  16
      entry_item_size   2,  1
      entry_item_size   3,  128
      entry_item_size   4,  16
    end

  end

  class InvalidHintStreamObjectError < InvalidStreamObjectError #:nodoc:
  end

  class HintStream < Stream

    attr_accessor :page_offset_table
    attr_accessor :shared_objects_table
    attr_accessor :thumbnails_table
    attr_accessor :outlines_table
    attr_accessor :threads_table
    attr_accessor :named_destinations_table
    attr_accessor :interactive_forms_table
    attr_accessor :information_dictionary_table
    attr_accessor :logical_structure_table
    attr_accessor :page_labels_table
    attr_accessor :renditions_table
    attr_accessor :embedded_files_table

    field   :S,             :Type => Integer, :Required => true # SHared objects
    field   :T,             :Type => Integer  # Thumbnails
    field   :O,             :Type => Integer  # Outlines
    field   :A,             :Type => Integer  # Threads
    field   :E,             :Type => Integer  # Named destinations
    field   :V,             :Type => Integer  # Interactive forms
    field   :I,             :Type => Integer  # Information dictionary
    field   :C,             :Type => Integer  # Logical structure
    field   :L,             :Type => Integer  # Page labels
    field   :R,             :Type => Integer  # Renditions
    field   :B,             :Type => Integer  # Embedded files

    def pre_build
      if @page_offset_table.nil?
        raise InvalidHintStreamObjectError, "No page offset hint table"
      end

      if @shared_objects_table.nil?
        raise InvalidHintStreamObjectError, "No shared objects hint table"
      end

      @data = ""
      save_table(@page_offset_table)
      save_table(@shared_objects_table,         :S)
      save_table(@thumbnails_table,             :T)
      save_table(@outlines_table,               :O)
      save_table(@threads_table,                :A)
      save_table(@named_destinations_table,     :E)
      save_table(@interactive_forms_table,      :V)
      save_table(@information_dictionary_table, :I)
      save_table(@logical_structure_table,      :C)
      save_table(@page_labels_table,            :L)
      save_table(@renditions_table,             :R)
      save_table(@embedded_files_table,         :B)
      
      super
    end

    private

    def save_table(table, name = nil)
      unless table.nil?
        self[name] = @data.size if name
        @data << table.to_s
      end
    end

  end

end
