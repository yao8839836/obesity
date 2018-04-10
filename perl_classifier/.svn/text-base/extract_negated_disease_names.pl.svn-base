#!/usr/bin/perl -w

#
# Script to extract disease names from i2b2 data
#   and output it in i2b2 ground-truth format
#
# Usage:    $0 > outfile.xml
#    or:    $0 obesity_patient_records_training.xml > outfile.xml
#    or:    $0 < obesity_patient_records_training.xml > outfile.xml
# 
# Author:   Illes Solt
# Created:  08/06/2008
# Changed:  09/06/2008 all-lowercase to avoid slow case-insensitive match
#


my $prefix = 'negation_';

## use module

use XML::Simple;
use XML::Parser;
use XML::Writer;
use IO::File;

use Data::Dumper;
use XML::Quote qw(:all);


## cmdline args

die "Usage: $0 (intuitive|textual)\n" if $#ARGV < 0;
$target = shift(@ARGV);


## globals

require 'judgements.pl';
require 'disease_aliases.pl';


#my $default_judgement = 'U';
my $source = $target;

my $docsfile ='-';

my $outfile = ($#ARGV > -1 && $ARGV[0] ne  '-')
          ? $ARGV[0]
          : 'negated_stripped.xml';

die "$0: No output file specified.\n" unless $outfile;


#print STDERR "$0: Saving stripped docs to '$outfile'\n";
#print STDERR "$0: Echo prefix tokens: $echo_prefixed\n";

$count_tokens = 0;

my @fake_negatives = 
(
	'gram negative',
	'no further',
	'not able to be',
    'no increase',
    'not suspicious',
	'not certain',
	'not clearly',
	'not certain whether',
	'not certain if',
	'not necessarily',
	'not optimal',
	'not rule out',
	'without any further',
	'without difficulty',
	'without further',
	'not correlate',
	'no correlataion',
	
#'no family history', # unstripped family history segments
	'no prior',
);

open(FD_STRIPPED, ">$outfile");
open(FD_LOG, ">$target/negated.log");


#$labelfile = 'obesity_standoff_intuitive_annotations_training.xml';
#$labelfile = 'obesity_standoff_textual_annotations_training.xml';


my %aliases = ();
#my %doc_ids = ();
my %count = (); # count per regex

foreach my $dis (@alias_lists)
{
    my $tag = $dis->[0];
    foreach my $alias (@{$dis})
    {
        $alias = lc($alias);
        $alias =~ s/ /[ _]/g;
        $aliases{$alias} = $tag;
    }
}


my %truths = ();
my $found = 0;

######################
## parse documents XML


my $parser = new XML::Parser(ErrorContext => 2);

my $echo_mode = 0;  # CDATA gets echoed
my $in_topics = 0;  # currently in <TOPICS>
my $in_body = 0;    # currently in <BODY>
my $newline_in_body = 0;    # on a new line in <BODY>
my $current_id = -1;    # current documents ID



## parser init

$parser->setHandlers(
    Char    => \&char_handler,
#   Default => \&default_handler,
    Start   => \&start_handler,
    End     => \&end_handler);


## open output file


open(FD_FILE, ">&STDOUT");
print FD_FILE <<END
<?xml version="1.0" encoding="UTF-8"?>
<diseaseset>
<diseases source="$source">
END
;

## open & parse docs XML file

my $file = $docsfile;
if ($file ne '-')
{
    die "Can't find file \"$file\""
        unless -f $file;

    print STDERR "Processing '$file'...\n";
    $parser->parsefile($file);
}
else
{
    print STDERR "Processing <STDIN>...\n";
    $parser->parse(\*STDIN);
}

while (my ($tag, $judgements) = each(%truths))
{
    print FD_FILE "<disease name=\"$tag\">\n";
    while (my ($doc_id, $judgement) = each(%{$judgements}))
    {
        print FD_FILE "<doc id=\"$doc_id\" judgment=\"$judgement\"/>\n";
    }
    print FD_FILE "</disease>\n";
}

# foreach my $tag (@disease_tags)
# {
#     my $judgements = $truths{$tag};
#     
#     print FD_FILE "  <disease name=\"$tag\">\n";
#     foreach my $doc_id (keys %doc_ids)
#     {
#         my $judgement = $judgements->{$doc_id};
#         print FD_FILE "    <doc id=\"$doc_id\" judgment=\"$judgement\"/>\n";
#     }
#     print FD_FILE "  </disease>\n";
# }


print FD_FILE <<END
</diseases>
</diseaseset>
END
;

close(FD_FILE);


#print STDERR "Found "
#    . sprintf('%4d', exists $count{$_} ? $count{$_} : 0) . " occurences in "
#    . sprintf('%4d', exists $count{$_} ? scalar keys %{$count_docs{$_}} : 0) . " documents of '$_'\n"
#    foreach (sort keys %aliases);

    
print STDERR "$0: $found disease names identified.\n";
#print STDERR "$0: Prefixed tokens: $echo_prefixed\n";


## handler subs

sub char_handler
{
    my ($p, $data) = @_;
    
#    $data =~ s/[<>&'"]/ /g;

    return unless $in_body;
    
    
    
    #print FD_FILE $data if $echo_mode; # && !$in_topics;

    ## NOTE lower case to avoid slow case-insensitive match
    $data = lc($data); 
    $original_line = $data;
    
    undef @lines;
    $_ = $data;
    while (/(\b(?:no|not|denie[sd]|denying|rule[sd] out|neg(?:ative)?|w(?:ithout|-\B|\/o\b)|did not exhibit|declined|(?:\w|\s|-)+ neg(?:ative)?) (?:[^\.\,\;\:\)\(\?\*]+)|non-[a-z-]+)/g) # |non-[a-z-]+(?: [a-z\-]+)?
    {
    	push(@lines, $1);
    }
    
LINES:    foreach $data (@lines) 
    {
    

#	$data =~ s/(?:\b(?:and|when)\b).*//g;
    my $tail = '';
	if ($data =~ s/((?:\b(?:when|given|taken|takes?|from|further|but|taking|during|as|besides|more|who|after|complications? of|because|since|due to|unless|regarding|secondary)\b|\b-\B|\B-\b|\-\-|\*\*).*)//g)
	{$tail = $1;}
	
	foreach my $fake (@fake_negatives)
	{
        next LINES if $data =~ /$fake/;
    }
    
    print FD_LOG "-".sprintf('%-4d %-20s', $current_id, '') . "|  $data  ##  $tail\n\n";
    while (my ($alias, $tag) = each(%aliases))
    {
        my $fake = (exists $fake_aliases{$tag}) ?
            '(?:' . join('|', @{$fake_aliases{$tag}}) . ')|'
            : '';
            
        while ($data =~ m/($fake(?:\b|[0-9])($alias)(?:\b|[0-9]))/g)
        {
            unless (defined $2)
			{
				print FD_LOG "f".sprintf('%-4d %-20s', $current_id, $tag) . "|  $data\n\n";
				next;
			}
        
            $truths{$tag}{$current_id} = 'N';

            $count{$alias}++;
            $count_docs{$alias}{$current_id} = 1;

            $found++;

			print FD_LOG "+".sprintf('%-4d %-20s', $current_id, $tag) . " |  $data\n\n";

            #last if $match_only_first;
        }
    }
	    
	## strip or replace processed segments
	my $replacement = '';
	if ($echo_prefixed)
	{	
		$replacement = $data;
		$count_tokens += (
			$replacement =~ s/(\S+)/$prefix$1/g);
	}
	$original_line =~ s/\Q$data\E/$replacement/;
    }
    
    print FD_STRIPPED xml_quote($original_line)."\n";
}  # End of char_handler

# sub default_handler
# {
#     my ($p, $data) = @_;
# 
#     if ($data =~ /^<!--/)
#     {
#       my $line = $p->current_line;
#       $data =~ s/\n/\n\t/g;
#       print "$line:\t$data\n";
#       $count++;
#     }
# 
# }  # End of default_handler

sub start_handler
{
    my $expat = shift;
    my $element = shift; # element is the name of the tag
    
    if ($element eq 'root')
    {
    print FD_STRIPPED <<END
<?xml version="1.0" encoding="UTF-8"?>
<root>
END
;
    }
    elsif ($element eq 'doc')
    {
        
        my %attrs = ();
        while (@_)
        {
            my $att = shift;
            my $val = shift;
            
            $attrs{$att} = $val;
            #print " $att = $val ";

            if ($att eq 'id')
            {
                $current_id = $val;
                #$doc_ids{$current_id} = 1;
                last;
            }
        }
	print FD_STRIPPED "\n<doc id=\"$current_id\">\n";
        
        
    }
    elsif ($element eq 'text')
    {
	print FD_STRIPPED "\n<text>\n";
    
        #$echo_mode = 1;
        $in_body = 1;
        #print FD_FILE "\n<tx id=\"body\"><p><t>\n";
    }
}

sub end_handler
{
    my $expat = shift;
    my $element = shift;
    
    
    if ($element eq 'root')
    {
	print FD_STRIPPED "\n</root>\n";
    }
    elsif ($element eq "doc")
    {
	print FD_STRIPPED "\n</doc>\n";
#        print FD_FILE "\n</document>\n";
    }
    elsif ($element eq "text")
    {
#        print FD_FILE "\n</t></p></tx>\n";
        
#       print FD_FILE "\n<!-- end of body -->";
	print FD_STRIPPED "\n</text>\n";
        $echo_mode = 0;
        $in_body = 0;
    }

#    print FD_FILE " " if ($element ne "doc" and $element ne "text");
}
