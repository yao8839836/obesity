#!/usr/bin/perl -W -n

# strip family sections from i2b2 data
# be careful with xml files

#my $echo_prefixed = 1;

# with, of, is, significant-for,

BEGIN{

	# test it like this:
	#open(TEST, '>&STDERR');
#	open(TEST, '>&STDOUT');
#
        die "Usage: $0 log_dir\n" if $#ARGV < 0;
        $logdir = shift(@ARGV);


#	$f = 0; # in family section
	$count = 0;
#	$token_count = 0;
	
	open(FD_LOG, ">>$logdir/family.log");
}

$original_line = $_;

while (/(?:(?:[a-z \n\?]*family history (with|of|is|significant)[^.:;<>]+)|\bf(?:am ?)?hx?:[a-z0-9 ,\-\/\n\?]+)/ig)
{
	my $match = $&;
	my $segment = $match;
	my $pre = '';
	
	#print "$2\n";
#	my $pre = $1;
#my $segment = $2;
	
	print STDERR "$0: found  '$segment'\n";
	print FD_LOG "$segment\n\n";
	
#	$original_line =~ s/\Q$match\E/$pre\n$begin_mark\n$segment\n$end_mark\n/;
	$original_line =~ s/\Q$match\E/$pre/;
}

print $original_line;

END{
	print STDERR "$0: stripped $count 'family history' segments\n";
}
