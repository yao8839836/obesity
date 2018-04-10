#!/usr/bin/perl -w

#
#
# Script to transform i2b2 data to FullDoc format
#
# Usage:    TODO
# 
# Author:   Illes Solt
# Created:  06/06/2008
#

## use module

use XML::Simple;
use XML::Parser;
use XML::Writer;
use IO::File;

use Data::Dumper;

require 'judgements.pl';

## globals

# $docsfile = 'obesity_patient_records_training.xml';

my @labelfiles = @ARGV;

# @labelfiles =
# (
#     'obesity_standoff_intuitive_annotations_training.xml',
#     'obesity_standoff_textual_annotations_training.xml',
#     'disease_name_truths.xml',
# );

%disease_short =
(
    'Asthma'	=> 'Ast',
    'CAD'	=> 'CAD',
    'CHF'	=> 'CHF',
    'Depression'	=> 'Dp',
    'Diabetes'	=> 'DM',
    'Gallstones'	=> 'Gs',
    'GERD'	=> 'GER',
    'Gout'	=> 'Gou',
    'Hypercholesterolemia'	=> 'HC',
    'Hypertension'	=> 'HTN',
    'Hypertriglyceridemia'	=> 'HTG',
    'OA'	=> 'OA',
    'Obesity'	=> 'Obe',
    'OSA'	=> 'OSA',
    'PVD'	=> 'PVD',
    'Venous Insufficiency'	=> 'VI',
);
%disease_long =
(
	'Asthma' => 'Asthma',
	'CAD' => 'Atherosclerotic CV disease (CAD)',
	'CHF' => 'Heart failure (CHF)',
	'Depression' => 'Depression',
	'Diabetes' => 'Diabetes mellitus (DM)',
	'Gallstones' => 'Gallstones / Cholecystectomy',
	'GERD' => 'GERD',
	'Gout' => 'Gout',
	'Hypercholesterolemia' => 'Hypercholesterolemia',
	'Hypertension' => 'Hypertension (HTN)',
	'Hypertriglyceridemia' => 'Hypertriglyceridemia',
	'OA' => 'Osteoarthritis (OA)',
	'Obesity' => 'Obesity',
	'OSA' => 'Obstructive sleep apnea (OSA)',
	'PVD' => 'Peripheral vascular disease (PVD)',
	'Venous Insufficiency' => 'Venous insufficiency',
);


## used for coloring the different tag sets
#@colors = ('red', 'blue', 'orange', 'navy', 'green');





######################
## parse judgements XML


## create object


## HoHoH: file per doc per disease per judgement
my %judgements_by_file = ();
foreach my $labelfile (@labelfiles)
{
    my %judgements = %{merge_judgements($labelfile)};
#     print STDERR Dumper(\%judgements);
#     exit;
    $judgements_by_file{$labelfile} = \%judgements;

#    print STDERR  Dumper(\%judgements);
}



## print all doc-judgements

# print Dumper(\%judgements);




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

#<!-- mc tag means judgement == 'Y' (in file: `$labelfile') -->

my $time = scalar(localtime());

print FD_FILE <<END
<html>
<head>
<style type="text/css">

    .drugbank_id    { color: #008888; padding-left: 0.5em; }
    .drug_name      { background-color: #ddffff; }
    
    .mc_tag         { color: red; }
    .mc_tag_source  { font-style: italic; padding-top:  0.5em; color: #888888; }
    
    .tag_line       { color: navy; }
    
    .judgement_Y    { color: red; }
    .judgement_N    { color: black; }
    .judgement_U    { color: gray; }
    .judgement_Q    { color: fuchsia; }
    .judgement_-    { color: black; }
    
    .zone_name      { font-weight: bold; background-color: #ffffdd; }
    
    .doctor_name    { background-color: #ffddee; }
    .patient_name   { background-color: #eeddff; }

    td              { text-align: center; }
    
    .disease_tag 		{ color: blue; text-decoration: underline; }
    .disease_tag:hover	{ color: red; }
    
    
</style>
</head>
<body>
<p>Generated on $time</p>
<hr/>
END
;

## open & parse docs XML file


# $file = $docsfile;
# die "Can't find file \"$file\""
#     unless -f $file;

# print STDERR "Processing '$file'...\n";
#$parser->parsefile($file);
print STDERR "Processing <STDIN>...\n";
$parser->parse(\*STDIN);

print FD_FILE "\n</body></html>\n";
close(FD_FILE);



## handler subs

sub char_handler
{
    my ($p, $data) = @_;

    if ($echo_mode)
    {
    
    #    $data =~ s/[<>&'"]/ /g;
        ## match zone names
        if ($data =~ /^([A-Z\.,\+-][A-Z0-9\.,\+\/() -]*[:;])(.*)/)
        {
            print FD_FILE "<span class=\"zone_name\">$1</span>$2";
        }
        ## match tag line
        elsif ($data =~ /^[0-9]+ \|/)
        {
            print FD_FILE "<span class=\"tag_line\">$data</span>";
        }
        else
        {
            print FD_FILE $data if $echo_mode; # && !$in_topics;
        }
    }
    
    
#    $newline_in_body = ($in_body and $data eq "\n");

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
    
    if ($element eq 'doc')
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
                last;
            }
        }
        
#        my $name = sprintf("reuters_%05d", $current_id);
#        my $filename = "$name.fd.xml";
        
#        open(FD_FILE, ">&STDOUT");
        
#        my $name = sprintf("i2b2_%04d", $current_id);
        print FD_FILE "\n<h1>Document id: $current_id</h1>\n";

        if (@labelfiles)
        {
    #        print FD_FILE Dumper($judgements{$current_id});
            print FD_FILE "<table cellspacing=\"1\" border=\"1\">\n";

        
            ## print header
            print FD_FILE "<tr><td/><th>Target</th>\n";
            foreach my $dis (@disease_tags)
            {
#                 my $abbr = substr $dis, 0, 3;
                my $abbr = $disease_short{$dis};
                my $desc = $disease_long{$dis};
                print FD_FILE "<td><span class=\"disease_tag\" title=\"$desc\">$abbr</span></td>\n";
            }
            print FD_FILE "</tr>\n";


            
            #my @tag_colors = @colors;
            while (my ($labelfile, $all_judgements)
                = each(%judgements_by_file))
            {
                while (my ($target, $judgements) 
                        = each(%{$all_judgements})) 
                        {
                #print FD_FILE Dumper(%{%$judgements});
#                $this_doc_judgements = $judgements->{$current_id};
                #print FD_FILE Dumper($this_doc_judgements);

    #            print FD_FILE "<table><tr><th colspan=\"2\">\n";
    #            print FD_FILE "<span class=\"mc_tag_source\">$labelfile</span><br/>\n";
    #            while (($dis, $jdg) = each(%{$this_doc_judgements}))
    #            {

                #my $color = shift @tag_colors;
                #print FD_FILE "<tr style=\"color: $color;\">\n";
                print FD_FILE "<tr>\n";
                
    #            foreach my $dis (sort keys %{$this_doc_judgements})
                print FD_FILE "<td><span class=\"source\" title=\"$labelfile\">$labelfile</span></td><td class=\"target\">$target</td>\n";
                foreach my $dis (@disease_tags)
                {
                    my $jdg = exists $judgements->{$dis}->{$current_id}
                            ? $judgements->{$dis}->{$current_id}
                            : '-';

    #                print FD_FILE "<span class=\"mc_tag\">$dis</span><br/>\n"
                    print FD_FILE "<td><span class=\"judgement_$jdg\" >" . ($jdg ne '' ? $jdg : '?') .  "</span></td>\n";
    #                    if ($jdg eq 'Y');
                }
                print FD_FILE "</tr>\n";
                }
            }
            print FD_FILE "</table>\n";
        }
    }
    elsif ($element eq 'text')
    {
        $echo_mode = 1;
        $in_body = 1;
        print FD_FILE "\n<hr/>\n<pre>\n";
    }
}

sub end_handler
{
    my $expat = shift;
    my $element = shift;
    
    
    if ($element eq "doc")
    {
        print FD_FILE "\n<hr/>\n";
    }
    elsif ($element eq "text")
    {
        print FD_FILE "\n</pre>\n";
        
#       print FD_FILE "\n<!-- end of body -->";
        $echo_mode = 0;
        $in_body = 0;
    }

#    print FD_FILE " " if ($element ne "doc" and $element ne "text");
}




# access XML data
#print "$data->{diseseaseset} is $data->{age} years old and works in the $data->{department} section\n";

if (0) {
for (;;)
{
	undef $!;
	unless (defined( $line = <STDIN> )) # read line
	{
		die $! if $!;
		last; # reached EOF
	}
	
	# remove spaces
	chomp($line);
	@buffer = ($line);
	@tokens = ();
	$unknown = 0;
	
	while ($#buffer != -1)
	{
		$input = shift(@buffer);


		if ($input eq "")
		{
			next;
		}
		# words
		elsif ($input =~ /^[a-z]+$/i)
		{
			push(@tokens, $input);
		}
		# words with apostrophe
		elsif ($input =~ /^([a-z]+)'[s]?$/i)
		{
			push(@tokens, $1);
		}
		# words followed by punctuation (except period '.')
		elsif ($input =~ /^([a-z]+)([:;,])$/i)
		{
			push(@tokens, $1);
			push(@tokens, $2);
		}
		# hyphenated word groups (e.g. band-like)
		elsif ($input =~ /^([a-z]+(-[a-z]+)+)$/i)
		{
			push(@tokens, $1);
		}
		# punctuation
		elsif ($input =~ /^[,;:\/]+$/)
		{
			push(@tokens, "*punct*");
		}
		# separators
		elsif ($input =~ /^[.\(\)\|*#^]+$/)
		{
			push(@tokens, ".");
		}
		# split on '/;:()*' (non-empty LHS)
		elsif ($input =~ /(.+)([\/;:\(\)*])(.*)/)
		{
			unshift(@buffer, $3);
			unshift(@buffer, $2);
			unshift(@buffer, $1);
		}
		# split on '/;:()*' (non-empty RHS)
		elsif ($input =~ /(.*)([\/;:\(\)*])(.+)/)
		{
			unshift(@buffer, $3);
			unshift(@buffer, $2);
			unshift(@buffer, $1);
		}
		# strip double-quotes
		elsif ($input =~ /\"/)
		{
			$input =~ s/"//g;
			unshift(@buffer, $input);
		}
		# medical abbreviations (e.g.: "a.b.c")
		elsif ($input =~ /^(([a-z]\.)+[a-z])$/i)
		{
			push(@tokens, $1);
		}
		# sequences followed by period, or colon (probably at end of the sentence)
		elsif ($input =~ /^(.+)([.,;])$/i)
		{
			unshift(@buffer, $2);
			unshift(@buffer, $1);
		}
		# numbers
		elsif ($input =~ /^[0-9]+$/)
		{
			push(@tokens, "*num*");
		}
		# more advanced numbers
		elsif ($input =~ /^[-+]?[0-9]*\.?[0-9]+$/)
		{
			push(@tokens, "*num*");
		}
		# percentages
		elsif ($input =~ /^[0-9]+%$/)
		{
			push(@tokens, "*pct*");
		}
		# more advanced percentages
		elsif ($input =~ /^[-+]?[0-9]*\.?[0-9]+%$/)
		{
			push(@tokens, "*pct*");
		}
		# uknown string
		else 
		{
			#push(@tokens, '*unknown*');
			push(@tokens, $input);
			$unknown = 1;
		}

		#print_pair($line, lc($parsed));
	}
	#	print_pair($line, lc(join("  ", @tokens))) if $unknown;

	print lc(join(" ", @tokens)) . " ";
}
};
