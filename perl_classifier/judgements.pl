#!/usr/bin/perl -w

#
#
# Routines to handle i2b2 ground truth XML files
#
# Usage:    require $0;
# 
# Author:   Illes Solt
# Created:  08/06/2008
#

## use module

use XML::Simple;
use Data::Dumper;

## globals

@disease_tags =
(
    'Asthma',
    'CAD',
    'CHF',
    'Depression',
    'Diabetes',
    'Gallstones',
    'GERD',
    'Gout',
    'Hypercholesterolemia',
    'Hypertension',
    'Hypertriglyceridemia',
    'OA',
    'Obesity',
    'OSA',
    'PVD',
    'Venous Insufficiency',
);

%dummy = ();

$global_truth = \%dummy;


######################
## parse judgements XML

## create object


## parse an i2b2-style XML of doc judgements
## returns a HoH: doc per disease per judgement
sub parse_judgements($)
{
    my $file = shift;
    
    my %judgements = ();
    
    ## read XML file

    die "Can't find file \"$file\""
        unless -f $file;

    print STDERR "Processing '$file'...\n";

    my $xml = new XML::Simple;
    my $data = $xml->XMLin($file);



    ## parse judgements

    my $diseases = $data->{'diseases'}->{'disease'};

    foreach my $dis (keys %{$diseases})
    {
    #    print "$dis\n";
        my $jdgs = $diseases->{$dis}->{'doc'};
        foreach $doc (keys %{$jdgs})
        {
            $jdg = $jdgs->{$doc}->{'judgment'};
            #print "$doc \t $jdg\n";
            $judgements{$doc}{$dis} = $jdg;
        }
    };
    return \%judgements;
};

sub parse_global_truth($)
{
    my $file = shift;
    $global_truth = merge_judgements($file);

    return $global_truth;
}

sub merge_judgements(@)
{
    #my $only_source = shift;
    my $arg = $_[0];

    my @files = ref($arg) eq 'ARRAY' ? @$arg : @_;
    
    my %judgements = (); # HoHoHoH: source / disease / doc / judgement
    
    ## read XML file

    my $count_total = 0;


    my %jdg_dis_count = (); # H: disease / count
    $jdg_dis_count{$_} = 0 foreach (@disease_tags); 

    my %jdg_dis_owr_count = (); # H: disease / overwrite count
    $jdg_dis_owr_count{$_} = 0 foreach (@disease_tags); 

    my %jdg_dis_miss_count = (); # H: disease / missing count
    $jdg_dis_miss_count{$_} = 0 foreach (@disease_tags); 

    my %jdg_count = (); # H: jdg / count
    $jdg_count{$_} = 0 foreach (@{['Y','N','Q','U']}); 
    
    foreach my $file (@files)
    {
        my $count = 0;
        my $count_ovr = 0;
        my $count_mod = 0;

        die "Can't find file \"$file\""
            unless -f $file;

        print STDERR "Processing '$file'...\n";

        my $xml = new XML::Simple;
        my $data = $xml->XMLin($file, 'ForceArray' => 1);


        ## parse judgements

        foreach my $diseases (@{$data->{'diseases'}})
        {
            my $src = $diseases->{'source'};

            #next if $src ne $only_source;
            
            my $disease = $diseases->{'disease'};
            foreach my $dis (keys %$disease)
            {
            #    print "$dis\n";
                my $jdgs = $disease->{$dis}->{'doc'};
                foreach $doc (keys %{$jdgs})
                {
                    $jdg = $jdgs->{$doc}->{'judgment'};

                    $jdg_count{$jdg}++;
                    $jdg_dis_count{$dis}++;


                    my $old_jdg
                        = exists $judgements{$src}{$dis}{$doc}
                        ? $judgements{$src}{$dis}{$doc}
                        : undef;

                   my $global_jdg
                        = exists $global_truth->{$src}->{$dis}->{$doc}
                        ? $global_truth->{$src}->{$dis}->{$doc}
                        : undef;
                    
                    $count++;
                    $count_ovr++ if (defined $old_jdg);
                    $count_mod++ if (defined $old_jdg && ($old_jdg ne $jdg));
                    $jdg_dis_owr_count{$dis}++ if (defined $old_jdg && ($old_jdg ne $jdg));
                    
                    print STDERR 'MOD ' . sprintf("%4d", $doc) . "  $old_jdg -> $jdg : $dis\n" 
						if (defined $old_jdg && ($old_jdg ne $jdg));

                    if (defined $old_jdg && defined $global_jdg
                        && $old_jdg eq $global_jdg
                        && $jdg ne $global_jdg)
                    {
                        print STDERR sprintf("Doc %4d: %-20s", $doc, $dis) . " modified from global truth '$old_jdg' to '$jdg' by file '$file'\n"
                    }
                    
                    #print STDERR "Modified $doc $dis $jdg\n" if (exists $judgements{$src}{$dis}{$doc} && ($judgements{$src}{$dis}{$doc} ne $jdg));
                    #print "$doc \t $jdg\n";
                    
                    $judgements{$src}{$dis}{$doc} = $jdg;
                }
            }
        }
        my $count_new = ($count-$count_ovr);
        print STDERR "Found $count annotations ($count_new new, $count_ovr owr, $count_mod mod) in file.\n";
        
        $count_total += $count_new;
    }
#    print STDERR "Judgments found: " . Dumper(\%jdg_count) . "\n";

#    print STDERR "\n== Jdgs ==\n";
#    print STDERR "$_,\t$jdg_dis_count{$_}\n" foreach sort @disease_tags;

#    print STDERR "\n== Overwrites ==\n";
#    print STDERR "$_,\t$jdg_dis_owr_count{$_}\n" foreach sort @disease_tags;

#    print STDERR "Found $count_total annotations total.\n";

    return \%judgements;
};

sub filter_judgements(@)
{
    my $only_source = shift;
    my $judgements = shift;

    if (exists $judgements->{$only_source})
    {
        return { $only_source => $judgements->{$only_source} };
    }
    else
    {
        return { $only_source => () };
    }
}

sub parse_judgements2(@) # HoHoHoH: source / disease / doc / judgement
{
    #my @files = @{ shift @_ };
    my $file = shift;
    
    my %judgements = (); # HoHoHoH: source / disease / doc / judgement
    
    ## read XML file

#     my $count_total = 0;

    #foreach my $file (@files)
    #{
        my $count = 0;

#         my $count_ovr = 0;
#         my $count_mod = 0;

        die "Can't find file \"$file\""
            unless -f $file;

        print STDERR "Processing '$file'...\n";

        my $xml = new XML::Simple;
        my $data = $xml->XMLin($file, 'ForceArray' => 1);


        ## parse judgements

        foreach my $diseases (@{$data->{'diseases'}})
        {
            my $src  = $diseases->{'source'};
            my $disease = $diseases->{'disease'};
            
            foreach my $dis (keys %$disease)
            {
            #    print "$dis\n";
                my $jdgs = $disease->{$dis}->{'doc'};
                foreach $doc (keys %{$jdgs})
                {
                    $jdg = $jdgs->{$doc}->{'judgment'};
                    
                    $count++;
                    #print "$doc \t $jdg\n";
                    
                    $judgements{$src}{$dis}{$doc} = $jdg;
                }
            }
        }
        print STDERR "Found $count annotations in file.\n";
        
    #        $count_total += $count_new;
    #}
    #print STDERR "Output contains $count_total '$only_source' annotations total.\n";

    return \%judgements;
    
#    return 1;
};


sub print_judgements(%) # # HoHoHoH: source / disease / doc / judgement
{
    my $arg = shift;
    
    open(FD_FILE, ">&STDOUT");
    print FD_FILE <<END
<?xml version="1.0" encoding="UTF-8"?>
<diseaseset>
END
;
    foreach my $src (sort keys %$arg)
    {
        my $judgements = $arg->{$src};
        
        print FD_FILE "<diseases source=\"$src\">\n";
#         while (my ($dis, $jdgs) = each(%$judgements))
#         {
        foreach my $dis (sort keys %$judgements)
        {
            my $jdgs = $judgements->{$dis};
            
            print FD_FILE "<disease name=\"$dis\">\n";
#             while (my ($doc, $jdg) = each(%$jdgs))
#             {
            foreach my $doc (sort {$a <=> $b} keys %$jdgs)
            {
                my $jdg = $jdgs->{$doc};
                
                print FD_FILE "<doc id=\"$doc\" judgment=\"$jdg\"/>\n";
            }
            print FD_FILE "</disease>\n";
        }
        print FD_FILE "</diseases>\n";
    }

    print FD_FILE <<END
</diseaseset>
END
;
}

# print judgements using ground judgements as a pattern
# default judgement assigned where non-existenet judgement encountered
sub project_judgements(@)
{
    my $ground_judgements = shift; # HoHoHoH: source / disease / doc / judgement
    my $res_judgements    = shift; # HoHoHoH: source / disease / doc / judgement
    my $default_jdg = shift;

    my $count_total = 0;
    my $count_missing = 0;

    my %jdg_dis_miss_count = (); # H: disease / missing count
    $jdg_dis_miss_count{$_} = 0 foreach (@disease_tags); 


    my %projected = ();

    print_stat($res_judgements);

    
    while (my ($src, $judgements) = each(%$ground_judgements))
    {
        while (my ($dis, $jdgs) = each(%$judgements))
        {
            while (my ($doc, $jdg) = each(%$jdgs))
            {
                my $res_jdg;
                if (exists $res_judgements->{$src}->{$dis}->{$doc})
                {
                    $res_jdg  = $res_judgements->{$src}->{$dis}->{$doc};
                }
                else
                {
                    $res_jdg = $default_jdg;
                    $count_missing++;
                    $jdg_dis_miss_count{$dis}++;
                }
                $count_total++;

                $projected{$src}{$dis}{$doc} = $res_jdg;
            }
        }
    }

#    print STDERR "\n== Missing ==\n";
#    print STDERR "$_,\t$jdg_dis_miss_count{$_}\n" foreach sort @disease_tags;

    print STDERR "Projected to $count_total annotations (missing $count_missing were marked '$default_jdg').\n";
#    print_stat(\%projected);

    return \%projected;
}

sub print_stat($)
{
    my $ground_judgements = shift;
    
    my %count_jdg = ();
    while (my ($src, $judgements) = each(%$ground_judgements))
    {
        while (my ($dis, $jdgs) = each(%$judgements))
        {
            while (my ($doc, $jdg) = each(%$jdgs))
            {
                $count_jdg{$src}{$jdg}++;
            }
        }
    }
    print STDERR Dumper(\%count_jdg);
}




## return true
1;



