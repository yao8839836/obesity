#!/usr/bin/perl -W -n 

# strip family sections from original (!) i2b2 data
# be careful with xml files
# needs newlines to work properly

BEGIN
{
        die "Usage: $0 logdir\n" if $#ARGV < 0;
        $logdir = shift(@ARGV);

	
	## strip operation
	open(FD_STRIP, ">$logdir/family.log");
	open(FD_OUT, '>&STDOUT');

	
	## test it like this:
	# open(FD_STRIP, '>&STDOUT');
	# open(FD_OUT, '>/dev/null');
	
	$f = 0;
	$count = 0;
	$skipped = 0;
} 

if (/^(.*)(FAMILY(?:\s*[A-Z]+)?\s*)/) # family related stuff begins
{
	
	print FD_OUT $1;
	print FD_STRIP $2; 
	
	$_ =~ s/^$&//;
	
	$f=1;
	$count++;
	$skipped++;
	
}

if ($f && (! /^(?:(?:MEDICAL )?HISTORY|ALLERG)/) && /^((?:[^\.]+\.)*?)( *[A-Z]{2}[A-Z :]{2,}(?:.|\n)*)/) # next section begins (not FAMILY\nHISTORY)
{
	print FD_STRIP $1;
#print FD_STRIP "\t###\t$2\n";
	print FD_OUT $2;
	
	$skipped++ if $1;
	
	$f=0; 
}
elsif ($f)
{	
	print FD_STRIP;
	$skipped++;
}
else
{
	print FD_OUT; 
}

END{
	print STDERR "$0: stripped $count FAMILY* sections ($skipped) lines)\n";
}
