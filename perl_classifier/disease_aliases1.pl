#!/bin/perl -W

## controls echo output
## prints prefixed words if set
$echo_prefixed = 0;

## Match only the first occurence of a disease per line
#$match_only_first = 1;

## optimize for specific targets
#$target = 'textual';
#$target = 'intuitive';


@alias_lists =
(
    ['Asthma', ],   # asztma
    ['CAD',         # szívkoszorúér betegség [elmeszesedés]
#        'coronary (?:(?:artery|heart)? ?disease|atherosclerosis)',
#        'coronary (?:atherosclerosis)',  # remove is better
        'coronary angioplasty',
        'Percutaneous coronary intervention',
        'PCI', # FIXME intuitive
        'Atherosclerotic disease',
        'chd',
        'coronary artery bypass',
        'coronary artery disease' #added
#        'LAD',
        ],
    ['CHF',         # kongesztív szívbetegség
        '(?:congestive )?(?:heart|cardiac) failure',
        'CCF',
        'dchf',
        '(?:dilated|(?:non-?)?ischa?emic) cardiomyopathy',
#       'cardiomyopathy',
#		'CMP',
#        'Pulmonary edema',
        ],
    ['Depression',                                # depresszió
        'depressive?',
        ],
    ['Diabetes',                                    # cukorbetegség
        'DM',
        'N?IDDM',  # = diabetes mellitus
        'diabetic',
         ],
    ['Gallstones',                                  # epekő (nem betegség
        'gall ?stones?',
        'Cholelithiasis',
#        'pancreatitis', # NOTE epekő következménye
        'biliary colic', # NOTE tünet
        'Cholecystectomy', # NOTE műtét
        'Gallbladder removal',  # NOTE műtét
        'CCY',
        'gallbladder (?:[a-z-\/]+ )*stones',
#        'pancreatic duct',
        #,'Cholestasis', # NOTE epekő következménye
        ],
    ['GERD',                                        # reflux
        'reflux (?:disease|disorder|esophagitis)',
        '(?:gastro(?:-o)?)?esophageal reflux',
        'G-?E Reflux',
        'gord',
        's esophagitis', # barretts's esophagitis
#        'reflux',
        ],
    ['Gout',
    	'gouty',
        'metabolic arthritis',
	],                    # köszvény
    ['Hypercholesterolemia',                        # hypercholesterinaemia
        'hyperchol\w*',
        '(?:high|elev(?:ated)?|increased) (?:chol(?:esterol)?|lipids?)',
        '(?:chol(?:esterol)?|lipids?)(?:\w|-| )+(?:high|elev(?:ated)?|increased)',
#         'hyperlipi?demia',   # NOTE utal rá
#         'hyperlipoproteinemia' , # NOTE utal rá
#         'dyslipidemia', # NOTE általánosabb
        'hyperli?pi?d\w*',   # NOTE utal rá
#        'hyperlipoproteinemia' , # NOTE utal rá
#        'dyslipidemia', # NOTE általánosabb
        'dysli?pi?d\w+', # NOTE általánosabb

        ],
    ['Hypertension',                                # magasvérnyomás
        'htn',
#        'elevated bp',
        ],
    ['Hypertriglyceridemia',                        # u.a.
        'Hyper(?:tri)?glycerid[a-z]*',
        'hyper tg',
        '(?:high|elev(?:ated)?|increased) trig(?:lyceride)?s',
        't(?:g|rig(?:lyceride)?s?) (?:[a-z0-9\-\/]+ )*(?:high|elev(?:ated)?|increased)',
        ],
    ['OA',                                  # rheumatoid arthritis
        '(?:Osteo)?arthritis',
        'degenerative (arthritis|joint disease)',
        'DJD',
        ],
    ['Obesity',                                   # elhízás
       'obes\w+',
#        'weight gain', # tul sok FP
        ],
    ['OSA',
        '(obstructive )?sleep apnea', ],           # alvási apnoe [horkolás]
    ['PVD', # Végtagi érelmeszesedés [verőérszűkület]
        'Peripheral (?:vascular|arterial)(?: occlusive)? Disease',
        'peripherovascular disease',
       'peripheral arterial disease',
#        'PAD',
         'Peripheral Vascular Disease',
         'peripheral arterial disease',
        ],
    ['Venous Insufficiency',       #visszér betegség
        'venostasis',   # NOTE alfaj
        '(veno)?stasis dermatitis',   # NOTE alfaj
        'venous (?:stasis|return)',
        ],
        
);

# lowercase!
# no active parens '(' in regex! only '(?:' allowed
%fake_aliases = (
    'Depression' => [
        'resp(?:iratory)? depr[a-z]*',
        's(?:t|cd) (?:segment )?depr[a-z]*',
        ],
    'Diabetes' => [
	'(?:gestional|chemical) diabetes',
	'diabetic diet',
	],

    'OA' => [
        '(?:rheumatoid|septic|psoriatic|idiopathic) arthritis',
        ],
    'Asthma' => [
#        'asthma flare',
        'cardiac asthma',
        ],
    'Hypertension' => [
    	'pulmonary hypertension',
    	],
    	
);

@intuitive_alias_lists =
(
    [ 'Depression' ,
        '(?:prozac|zoloft|wellbutrin|plaxil|lexapro|effexor|cymbalta|elavil|celexa|desyrel|Pamelor|Tofranil)',
        '(?:ssri|snri)s?',
        'antidepressants?',
        ],
    [ 'Hypertension',
        '(?:ACE inhibitors|antihypertensive)s?',
        '(?:Angiotensin|b(?:eta)?(?: |-)blocker)',
        ],
    [ 'GERD',
        'ESOPHAGITIS',
        '(?:carafate|Sucralfate)',
        
        ],

   [ 'CAD',
        'Cardiac catheterization',
        ],
    [ 'Hypercholesterolemia',
        '[a-z]+statins?',
        ],
#     [ 'Hypertriglyceridemia',
#         'fibrates?',
#         '(?:Bezafibrate|Bezalip|Ciprofibrate|Modalim|Clofibrate|Gemfibrozil|Lopid|Fenofibrate|Tricor)',
#         ],
    [ 'Obesity',
        'Pannicul(?:ectomy|itis)',
        ],
    [ 'OA',
        'LUMBAR DIS[kc] DISEASE',
        'hip replacement',
        'knee replacement',
        ],
    [ 'Gout',
        'Allopurinol',
        ],
    [ 'Venous Insufficiency',
        '(?:lower extremity|leg) ulcers',
        ],
#     [ 'Hypertriglyceridemia',
#         'hyperglycerida?emia',   # NOTE általánosabb
#         ],

);

# triglycerides: 200
# cholesterol: 150

# Fibrates prescribed commonly are:
# Bezafibrate (e.g. Bezalip)
# Ciprofibrate (e.g. Modalim)
# Clofibrate (largely obsolete due to side-effect profile, e.g. gallstones)
# Gemfibrozil (e.g. Lopid)
# Fenofibrate (e.g. TriCor)

# The proton pump inhibitor Omeprazole. 
#  The proton pump inhibitor Omeprazole.
# Clinically used proton pump inhibitors:
# Omeprazole (brand names: Losec, Prilosec, Zegerid)
# Lansoprazole (brand names: Prevacid, Zoton, Inhibitol)
# Esomeprazole (brand names: Nexium)
# Pantoprazole (brand names: Protonix, Somac, Pantoloc, Pantozol, Zurcal)
# Rabeprazole (brand names: Rabecid, Aciphex, Pariet)

chomp($target);
$target = lc($target);

die("Wrong target: `$target' should be `intuitive' or `textual'.\n")
    if ($target ne 'intuitive' && $target ne 'textual');


push(@alias_lists, @intuitive_alias_lists)
    if ($target eq 'intuitive');

1;
