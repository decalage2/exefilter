=begin

= File
	export.rb

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

module Origami

  class PDF
    
    #
    # Exports the document to a dot Graphiz file.
    # _filename_:: The path where to save the file.
    #
    def export_to_graph(filename)
      
      def appearance(object) #:nodoc:
      
        label = object.type.to_s
        case object
          when Catalog
            fontcolor = "red"
            color = "mistyrose"
            shape = "doublecircle"
          when Name, Number
            label = object.value 
            fontcolor = "orange"
            color = "lightgoldenrodyellow"
            shape = "polygon"
           when String
            label = object.value unless (object.is_binary_data? or object.length > 50)
            fontcolor = "red"
            color = "white"
            shape = "polygon"
          when Array
            fontcolor = "green"
            color = "lightcyan"
            shape = "ellipse"
        else
          fontcolor = "blue"
          color = "aliceblue"
          shape = "ellipse"
        end
      
        { :label => label, :fontcolor => fontcolor, :color => color, :shape => shape }
      end
      
      def add_edges(pdf, fd, object) #:nodoc:
        
        if object.is_a?(Array) or object.is_a?(ObjectStream)
          
          object.each { |subobj|
            
            if subobj.is_a?(Reference) then subobj = pdf.indirect_objects[subobj] end
            
            unless subobj.nil?
              fd << "\t#{object.object_id} -> #{subobj.object_id}\n"
            end
          }
          
        elsif object.is_a?(Dictionary)
          
          object.each_pair { |name, subobj|
            
            if subobj.is_a?(Reference) then subobj = pdf.indirect_objects[subobj] end
            
            unless subobj.nil?
              fd << "\t#{object.object_id} -> #{subobj.object_id} [label=\"#{name.value}\",fontsize=7];\n"
            end
          }
          
        end
        
        if object.is_a?(Stream)
          
          object.dictionary.each_pair { |key, value|
          
            if value.is_a?(Reference) then value = pdf.indirect_objects[subobj] end
            
            unless value.nil?
              fd << "\t#{object.object_id} -> #{value.object_id} [label=\"#{key.value}\",fontsize=7];\n"
            end
          }
          
        end
        
      end
      
      graphname = "PDF" if graphname.nil? or graphname.empty?
      
      fd = File.open(filename, "w")
    
      begin
        
        fd << "digraph #{graphname} {\n\n"
        
        objects = self.objects(true).find_all{ |obj| not obj.is_a?(Reference) }
        
        objects.each { |object|
          
          attr = appearance(object)
          
          fd << "\t#{object.object_id} [label=\"#{attr[:label]}\",shape=#{attr[:shape]},color=#{attr[:color]},style=filled,fontcolor=#{attr[:fontcolor]}];\n"
          
          if object.is_a?(Stream)
            
            object.dictionary.each { |value|
            
              unless value.is_a?(Reference)
                attr = appearance(value)
                fd << "\t#{value.object_id} [label=\"#{attr[:label]}\",shape=#{attr[:shape]},color=#{attr[:color]},style=filled,fontcolor=#{attr[:fontcolor]}];\n"
              end
            
            }
            
          end
          
          add_edges(self, fd, object)
        
        }
        
        fd << "\n}"
        
      ensure
        fd.close
      end
      
    end
    
    #
    # Exports the document to a GraphML file.
    # _filename_:: The path where to save the file.
    #
    def export_to_graphml(filename)
      
      def declare_node(id, attr) #:nodoc:
        " <node id=\"#{id}\">\n" <<
        "  <data key=\"d0\">\n" <<
        "    <y:ShapeNode>\n" <<
        "     <y:NodeLabel>#{attr[:label]}</y:NodeLabel>\n" <<
        #~ "     <y:Shape type=\"#{attr[:shape]}\"/>\n" <<
        "    </y:ShapeNode>\n" <<
        "  </data>\n" <<
        " </node>\n"
      end
      
      def declare_edge(id, src, dest, label = nil) #:nodoc:
        " <edge id=\"#{id}\" source=\"#{src}\" target=\"#{dest}\">\n" << 
        "  <data key=\"d1\">\n" <<
        "   <y:PolyLineEdge>\n" <<
        "    <y:LineStyle type=\"line\" width=\"1.0\" color=\"#000000\"/>\n" <<
        "    <y:Arrows source=\"none\" target=\"standard\"/>\n" << 
        "    <y:EdgeLabel>#{label.to_s}</y:EdgeLabel>\n" <<
        "   </y:PolyLineEdge>\n" <<
        "  </data>\n" <<
        " </edge>\n"
      end
      
      def appearance(object) #:nodoc:
      
        label = object.type.to_s
        case object
          when Catalog
            fontcolor = "red"
            color = "mistyrose"
            shape = "doublecircle"
          when Name, Number
            label = object.value 
            fontcolor = "orange"
            color = "lightgoldenrodyellow"
            shape = "polygon"
          when String
            label = object.value unless (object.is_binary_data? or object.length > 50)
            fontcolor = "red"
            color = "white"
            shape = "polygon"
          when Array
            fontcolor = "green"
            color = "lightcyan"
            shape = "ellipse"
        else
          fontcolor = "blue"
          color = "aliceblue"
          shape = "ellipse"
        end
      
        { :label => label, :fontcolor => fontcolor, :color => color, :shape => shape }
      end
      
     def add_edges(pdf, fd, object, id) #:nodoc:
        
        if object.is_a?(Array) or object.is_a?(ObjectStream)
          
          object.each { |subobj|
            
            if subobj.is_a?(Reference) then subobj = pdf.indirect_objects[subobj] end
            
            unless subobj.nil?
              fd << declare_edge("e#{id}", "n#{object.object_id}", "n#{subobj.object_id}")
              id = id + 1
            end
          }
          
        elsif object.is_a?(Dictionary)
          
          object.each_pair { |name, subobj|
            
            if subobj.is_a?(Reference) then subobj = pdf.indirect_objects[subobj] end
            
            unless subobj.nil?
              fd << declare_edge("e#{id}", "n#{object.object_id}", "n#{subobj.object_id}", name.value)
              id = id + 1
            end
          }
          
        end
        
        if object.is_a?(Stream)
          
          object.dictionary.each_pair { |key, value|
          
            if value.is_a?(Reference) then value = pdf.indirect_objects[subobj] end
            
            unless value.nil?
              fd << declare_edge("e#{id}", "n#{object.object_id}", "n#{value.object_id}", key.value)
              id = id + 1
            end
          }
          
        end
        
        id
      end
      
      @@edge_nb = 1
      
      graphname = "PDF" if graphname.nil? or graphname.empty?
      
      fd = File.open(filename, "w")
      
      edge_nb = 1
      begin
        
        fd << '<?xml version="1.0" encoding="UTF-8"?>' << "\n"
        fd << '<graphml xmlns="http://graphml.graphdrawing.org/xmlns/graphml"' << "\n"
        fd << ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' << "\n"
        fd << ' xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/graphml ' << "\n"
        fd << ' http://www.yworks.com/xml/schema/graphml/1.0/ygraphml.xsd"' << "\n"
        fd << ' xmlns:y="http://www.yworks.com/xml/graphml">' << "\n"
        fd << '<key id="d0" for="node" yfiles.type="nodegraphics"/>' << "\n"
        fd << '<key id="d1" for="edge" yfiles.type="edgegraphics"/>' << "\n"
        fd << "<graph id=\"#{graphname}\" edgedefault=\"directed\">\n"
        
        objects = self.objects(true).find_all{ |obj| not obj.is_a?(Reference) }
        
        objects.each { |object|
          
          fd << declare_node("n#{object.object_id}", appearance(object))
          
          if object.is_a?(Stream)
            
            object.dictionary.each { |value|
            
              unless value.is_a?(Reference)
                fd << declare_node(value.object_id, appearance(value))
              end
            }
          end
          
          edge_nb = add_edges(self, fd, object, edge_nb)
        }
        
        fd << '</graph>' << "\n"
        fd << '</graphml>'
        
      ensure
        fd.close
      end
      
    end

  end
  
end
