#!/usr/bin/perl -w

#
# Script to translate medical abbreviataions
#
# Usage:    $0 < infile > outfile
#
# Author:   Illes Solt
# Created:  08/06/2008
#



# //     * a.c. = before meals (from "ante cibum", before meals)
# //     * b.i.d. = twice a day (from "bis in die", twice a day)
# //     * gtt. = drops (from "guttae", drops)
# //     * p.c. = after meals (from "post cibum", after meals)
# //     * p.o. = by mouth, orally (from "per os", by mouth)
# //     * q.d. = once a day (from "quaque die", once a day)
# //     * q.i.d. = four times a day (from "quater in die", 4 times a day)
# //     * q._h.: If a medicine is to be taken every so-many hours (from "quaque", every and the "h" indicating the number of hours)
# //     * q.h. = every hour
# //     * q.2h. = every 2 hours
# //     * q.3h. = every 3 hours
# //     * q.4h. = every 4 hours
# //     * t.i.d. = three times a day (from "ter in die", 3 times a day)
# //     * ut dict. = as directed (from "ut dictum", as directed)

#          qpm = Every Day After Noontime
#          QAM  Quaque die Ante Meridiem (Latin: Every Day Before Noon)
#          qac = before every meal = before meals

#          npo = nothing by mouth
#          PRN Pro Re Nata (Latin: for the existing occasion; as matters are; as needed)
#          QHS   Quaque Hora Somni (Latin: Every Bedtime)
#          QOD  Every Other Day
#          PR   Pro Rata (Latin: in proportion to)


#   iv = intravenous
#   bp = blood pressure
#   hr = heart rate
#   yo = year-old
#   y/o = year-old
#   w/ = with
#   w- = without
#   pt = patient
# [a-z][./][a-z]

#$b = '\b'; # word boundary
$opt_full_period = '(?:\.\B|\b)'; # a greedy optional . char at the end of abbreviataion


# abc => ABC | abc | abc. | a.b.c | a.b.c.
sub standard_abbrev_w_uc($)
{
    my $abbr = shift;

    my $regex = '(?:'. standard_abbrev($abbr) . '|' . boundaries(uc($abbr)) .')';
    return $regex;
}

# abc => ABC | abc | abc. | a.b.c | a.b.c.
sub non_standard_abbrev_w_uc($)
{
    my $abbr = shift;

    my $regex = '(?:'. non_standard_abbrev($abbr) . '|' . boundaries(uc($abbr)) .')';
    return $regex;
}

# period at all positions OR period only at the end OR no period
# abc => abc | abc. | a.b.c | a.b.c.
sub standard_abbrev($)
{
    my $abbr = shift;

    my @letters = split(//, $abbr);
    my $regex = shift @letters;
    $regex = $regex.'(?:'.join('', @letters).'|';
    $regex = $regex.'\.'.$_
        foreach (@letters);
    $regex = $regex.')';
    return boundaries_period($regex);
}

# period optional at all positions independently
# abc => abc | abc | a.bc | ...
sub non_standard_abbrev($)
{
    my $abbr = shift;

    my @letters = split(//, $abbr);
    my $regex = join('\.?', @letters);
    
    return boundaries_period($regex);
}


# surround regex with boundaries
# (boundary only works for alpha chars, e.g. not '.', see: perl \b)
sub boundaries($)
{
    my $regex = shift;
    return '\b'.$regex.'\b';
}


# surround regex with boundaries (optional period at the end)
sub boundaries_period($)
{
    my $regex = shift;
    return '\b'.$regex.$opt_full_period;
}

# cat obesity_patient_records_training.xml | grep -o -i -E '(q\.? *)?[1-9][0-9]* *h(rs?)?(\.| |$)' | sort -u
sub hours($) { return boundaries_period('(?:(?:[qQ]\.?|every|Every|EVERY) *)' . shift(@_) . ' *[hH](?:[rR][sS]?|ours|OURS)?');}

# order does matter !
@abbrevs =
(
    # npo |...
    {'npo' =>   standard_abbrev('npo')}, # TODO npo (= pt gets no food) OK?
    
    # AM 
    {'a.m.' =>   boundaries('AM')},

    # nka | ... | NKA
    {'No known allergies' =>   standard_abbrev_w_uc('nka')},

    
    # QAC | qac | ... | q ac | ...
    {'before every meal' =>   '(?:' . standard_abbrev_w_uc('qac') . '|' . non_standard_abbrev('q ac') . ')'},
    
    # ac | ...
    {'before meals' =>   standard_abbrev_w_uc('ac')},

    # QPC | qpc | ... | q pc | ...
    {'after every meal' =>   '(?:' . standard_abbrev_w_uc('qpc') . '|' . non_standard_abbrev('q pc') . ')'},
    
    # pc | ...
    {'after meals' =>   standard_abbrev_w_uc('pc')},


    # gtt | gtt.
    {'drops' =>   boundaries_period('gtt')},

    # po | p.o | p.o. | per mouth | per os | orally
    {'orally' =>   '(?:' . standard_abbrev_w_uc('po') . '|' . boundaries_period('P O') . '|' . boundaries_period('(?:oral|orally|per\s(?:mouth|os))') . ')'},

    # bid | b.i.d | b.i.d.| bid.
    {'twice a day' => standard_abbrev_w_uc('bid')},
    
    # tid | t.i.d | t.i.d.| tid.
    {'three times a day' => standard_abbrev_w_uc('tid')},
    
    # qid | q.i.d | q.i.d.| qid.
    {'four times a day' => standard_abbrev_w_uc('qid')},
    
    # qpm | ... | QPM | q. p.m. | q p.m.
    {'every afternoon' => '(?:'.standard_abbrev_w_uc('qpm').'|\bq\.? p\.m\.\B)'},
    
    # qam | ... | QAM | q. a.m. | q a.m.
    {'every day before noon' => '(?:'.standard_abbrev_w_uc('qam').'|\bq\.? a\.m\.\B)'},
    
    # qod | ...
    {'every other day' => standard_abbrev_w_uc('qod')},

    
    # prn | ...
    {'as needed' => standard_abbrev_w_uc('prn') },


    # pt | pt. | Pt | Pt.
    # NOTE: 'PT' is/maybe 'physical therapy'
    {'patient' =>   boundaries_period('(?:pt|Pt)')},
    
    # PT
    {'physical therapy' =>   boundaries('PT')},
    
    # iv | ... | IV
    {'intravenous' => standard_abbrev_w_uc('iv')},
    
    # im | ... | IM
    {'intramuscular' => standard_abbrev_w_uc('im')},

    # inh | ... | INH
    {'inhaled' => standard_abbrev_w_uc('inh')},
    
    # sl | ... | SL
    {'sublingual' => standard_abbrev_w_uc('sl')},
    
    # ou | ... | OU
    {'each eye' => standard_abbrev_w_uc('ou')},
    
    # subcu | subq 
    {'subcutaneously' =>   boundaries_period('(?:sub(?:cu|-?q)|sc|SC)')},
    
    # NA
    # NOTE: not to confuse with 'Na' = natrium
    {'nasal' => boundaries('NA')},


    # q##h | ...
    # cat obesity_patient_records_training.xml | grep -o -E 'q\.? *[1-9][0-9]* *h\.?'
    {'every 2 hours' =>   hours(2)},
    {'every 3 hours' =>   hours(3)},
    {'every 4 hours' =>   hours(4)},
    {'every 6 hours' =>   hours(6)},
    {'every 8 hours' =>   hours(8)},
    {'every 10 hours' =>   hours(10)},
    {'every 12 hours' =>   hours(12)},
    {'every 24 hours' =>   hours(24)},
    {'every 48 hours' =>   hours(48)},
    {'every 72 hours' =>   hours(72)},
    

    # PCP
    {'primary care physician'   => boundaries('PCP')    },
    
    # h/o
    {'history of'   => boundaries('(?:h\/o|H\/O)')    },
    
    # s/p
    {'history of'   => boundaries('(?:s\/p|S\/P)')    },
# 
#     # Psych | psych | PSYCH
#     {'psychiatrist'   => boundaries_period('([pP]sych|PSYCH)')    },

#    neuro

    # w- | w/o
    {'without'  =>   '\bw(?:-\B|\/o\b)'},
    {'without '  =>   '\bw-\b'},
    
    # w | w/ | w\[a-z]+
    {'with'     =>   '\bw(?:\/\B|$)'},
    {'with '    =>   '\bw(?: |\/\b)'},
    
    
    # yo | y/o | y.o.
    {'year-old' => '(?:'.boundaries('y/o').'|'.standard_abbrev('yo').')'},
    {' year-old' => '\By\.o'.$opt_full_period}, # handle '72y.o.'
    
    # hr | ...
    {'heart rate'   => standard_abbrev('hr')},
    
    # bp | ...
    {'blood pressure' => standard_abbrev('bp')},
    
    # qd | ... | q d | ... | qdaily
    {'every day'        => '(?:' . standard_abbrev_w_uc('qd') . '|' . non_standard_abbrev('q d') . '|' . boundaries('(?:qdaily|qD)') . ')'},
    
    # qmonth
    {'every month'  => boundaries('qmonth')},
    
    # qhs | ...
    {'every bedtime' => '(?:' . boundaries('qHS') . '|' . non_standard_abbrev_w_uc('qhs') . ')'},
    
    
    # hs | ...
    {'bedtime' => standard_abbrev('hs')},
    
    # biw | ...
    {'biweekly' => standard_abbrev('biw')},
    
    # qh | ...
    {'every hour' => standard_abbrev('qh')},
    
    # qo | ...
    {'every other' => standard_abbrev('qo')},
    
    # er | ...
    {'emergency room' => standard_abbrev('er')},


    
    
    # ed | ...
    #{'emergency department' => standard_abbrev('ed')},

    # NOTE: should be after every abbrev with 'q'
    # q | q. | q.[a-z] 
    {'every '   => '(?:\bq\.? |^q\.\b)'},
    {' every '   => ' q\.\b'},
    {' every'   => ' q$'},

    
    

);

## use module

use Data::Dumper;   $Data::Dumper::Sortkeys = 1;


## parse input

open(FD_FILE, ">&STDOUT");

my $replacements = 0;

## read input
for (;;)
{
    undef $!;
    unless (defined( $line = <STDIN> )) ## read line
    {
        die $! if $!;
        last; ## reached EOF
    }
    
    ## remove spaces from end
    chomp($line);

    ## do all applicable replacements
    foreach $abbrev (@abbrevs)
    {
        my ($resolv, $regex) = %$abbrev;
        
        $replacements +=
            ($line =~ s/$regex/$resolv/g);
    }

    ## echo
    print FD_FILE "$line\n"
}

print STDERR "$0: $replacements abbreviataions replaced.\n";


