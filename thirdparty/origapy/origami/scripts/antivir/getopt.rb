require 'optparse'

class OptParser
    def self.parse(args)
        options = {}
        opts = OptionParser.new do |opts|
            opts.banner = "Usage: #{$0} [options] <arguments>"

            opts.on("-i", "--input PDFFILE", "Input pdf") do |i|
                options[:input] = i
            end

            opts.on("-o", "--output PDFFILE", "Output pdf") do |o|
                options[:output] = o
            end

            opts.on("-t", "--type <all,triggers,actions,forms>", "Type") do |t|
                options[:type] = t
            end

            opts.on_tail("-h", "--help", "Show this message") do
                puts opts
                exit
            end
        end
        opts.parse!(args)

        if not options[:input].nil? and not File.exist? options[:input]
            puts "error: #{options[:input]} doesn't exist"
            puts opts
            exit
        end

        if not options[:output]
            puts "error: need an output pdf file"
            puts opts
            exit
        end

        options[:type] = "all" if %w{all triggers main forms}.include?(options[:type])

        options
    end
end

def get_params
  options = OptParser.parse(ARGV)

  if not options[:input].nil?
    pdf = PDF.read(options[:input], :verbose => Parser::VERBOSE_INFO )
  else
    pdf = PDF.new.append_page
  end

  [ pdf, options[:output], options[:type] ]
end
