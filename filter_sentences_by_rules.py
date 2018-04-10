
# coding: utf-8

# In[15]:


abbrev = []
alias_lists =[
    ['Asthma', ],   # asztma
    ['CAD',         # szívkoszorúér betegség [elmeszesedés]
        'coronary (?:(?:artery|heart)? ?disease|atherosclerosis)',
#        'coronary (?:atherosclerosis)', 
        'coronary angioplasty',
        'Percutaneous coronary intervention',
        'PCI', # FIXME intuitive
        'Atherosclerotic disease',
        'chd',
        'coronary artery bypass',
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
#        'peripheral arterial disease',
#        'PAD',
        ],
    ['Venous Insufficiency',       #visszér betegség
        'venostasis',   # NOTE alfaj
        '(veno)?stasis dermatitis',   # NOTE alfaj
        'venous (?:stasis|return)',
        ],
]
print(alias_lists)


# In[16]:


intuitive_alias_lists = [
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

    ]
print(intuitive_alias_lists)


# In[17]:


fake_negatives = [
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
]
print(fake_negatives)


# In[18]:


negatives = ['(\b(?:no|not|denie[sd]|denying|rule[sd] out|neg(?:ative)?|w(?:ithout|-\B|\/o\b)|did not exhibit|declined|(?:\w|\s|-)+ neg(?:ative)?) (?:[^\.\,\;\:\)\(\?\*]+)|non-[a-z-]+)',
            '((?:\b(?:when|given|taken|takes?|from|further|but|taking|during|as|besides|more|who|after|complications? of|because|since|due to|unless|regarding|secondary)\b|\b-\B|\B-\b|\-\-|\*\*).*)']


# In[ ]:


questionalble = ['((?:(?:\b(?:not certain if|versus|vs|rule out|be ruled out|r\/o|presumed|suggest(?:\b|[^i]|i[^v])|possib|scree?n for|question|consider|whether or not|may have|study for))(?:[^\.\,;:)(\?]+))|\?(?: ?[a-z\/\-]+){1,4}|(?:[a-z\-\/]+ )+(?:versus|vs|screen)[a-z -]+)',
                '^(.+?)((?:\b(?:no |and|when|with|given|if|besides|because|related|component|from|since|secondary|regard|due|disposing)\b|\b-\B|\B-\b|\-\-|\*\*).*)/$1']


# In[ ]:


#
import re
f = open('data/Obesity_data/ObesitySen_copy.dms','r')
content = f.read()
f.close()

records = content.strip().split('RECORD #')
corpus = []
f = open('data/Obesity_data/ObesitySen_filtered.dms', "w") 
for record in records:
    id = record[:record.find(' ')]
    if(record.find('[report_end]') != -1):
        content = record[record.find(' ') + 1: record.find('[report_end]')].strip()
        sentences = content.split('\n')
        #print(sentences)
        print(content[:20] + '\t' + id)
        f.write('RECORD #'+id)
        for sentence in sentences:
                sentence = sentence.lower()
            mark = 0
            for alias_list in alias_lists:
                for alias_name in alias_list:
                    if(len(re.findall(alias_name, sentence))>0):
                        mark = 1
            for alias_list in intuitive_alias_lists:
                for alias_name in alias_list:
                    if(len(re.findall(alias_name, sentence))>0):
                        mark = 1
            for fake_negative in fake_negatives:
                if(len(re.findall(fake_negative, sentence))>0):
                    mark = 1            
            for negtive in negatives:
                if(len(re.findall(negtive, sentence))>0):
                    mark = 1
            for q in questionalble:
                if(len(re.findall(q, sentence))>0):
                    mark = 1
            if(mark == 1):
                print(sentence)
                f.write(sentence + '\n')
        f.write('[report_end]'+'\n')   
print(len(corpus))
f.close()

