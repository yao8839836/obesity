from data.cnews_loader import get_dic

test_dic = get_dic('perl_classifier/output/perl_annotation6.xml')

test_dic_text_rule = get_dic('perl_classifier/output/prod_134_0_2.xml')
test_dic_int_rule = get_dic('perl_classifier/output/prod_134_0_5.xml')

#positive
f = open('perl_classifier/textual/positive_useful.log','r')
content = f.read()
f.close()
tplines = content.split('\n')

f = open('perl_classifier/intuitive/positive_useful.log','r')
content = f.read()
f.close()
iplines = content.split('\n')

# questionalble
f = open('perl_classifier/textual/questionable_truly_useful.log','r')
content = f.read()
f.close()
tqlines = content.split('\n')

f = open('perl_classifier/intuitive/questionable_truly_useful.log','r')
content = f.read()
f.close()
iqlines = content.split('\n')

# negated
f = open('perl_classifier/textual/negated_truly_useful.log','r')
content = f.read()
f.close()
tnlines = content.split('\n')

f = open('perl_classifier/intuitive/negated_truly_useful.log','r')
content = f.read()
f.close()
inlines = content.split('\n')


for key in test_dic:

    test_sub_dic = test_dic[key]

    for sub_key in test_sub_dic:

        test_docs = test_sub_dic[sub_key]

        for test_doc in test_docs:
            temp = test_doc.split(',')
            doc_id = temp[0]
            label = temp[1]

            if key == 'textual':
                test_rule = test_dic_text_rule[key]
                test_rule_docs = test_rule[sub_key]
                for test_doc_rule in test_rule_docs:
                    temp1 = test_doc_rule.split(',')
                    if temp1[0] == doc_id and temp1[1] != label:
                        
                        for line in tplines:
                            doc = line[1: line.find(' ')].strip()
                            disease = line[line.find(' ') + 1 : line.find('|')].strip()
                            if doc == doc_id and disease == sub_key:
                                keyword =  line[line.find('|') + 1 : ].strip()
                                print(key, sub_key, doc_id, keyword, 
                                'paper: ', temp1[1], 'perl: ' , label)
                        for line in tqlines:
                            doc = line[1: line.find(' ')].strip()
                            disease = line[line.find(' ') + 1 : line.find('|')].strip()
                            if doc == doc_id and disease == sub_key:
                                keyword =  line[line.find('|') + 1 : ].strip()
                                print(key, sub_key, doc_id, keyword, 
                                'paper: ', temp1[1], 'perl: ' , label)
                        for line in tnlines:
                            doc = line[1: line.find(' ')].strip()
                            disease = line[line.find(' ') + 1 : line.find('|')].strip()
                            if doc == doc_id and disease == sub_key:
                                keyword =  line[line.find('|') + 1 : ].strip()
                                print(key, sub_key, doc_id, keyword, 
                                'paper: ', temp1[1], 'perl: ' , label)

            if key == 'intuitive':
                test_rule = test_dic_int_rule[key]
                test_rule_docs = test_rule[sub_key]
                for test_doc_rule in test_rule_docs:
                    temp1 = test_doc_rule.split(',')
                    if temp1[0] == doc_id and temp1[1] != label:
                        
                        for line in iplines:
                            doc = line[1: line.find(' ')].strip()
                            disease = line[line.find(' ') + 1 : line.find('|')].strip()
                            if doc == doc_id and disease == sub_key:
                                keyword =  line[line.find('|') + 1 : ].strip()
                                print(key, sub_key, doc_id, keyword, 
                                'paper: ', temp1[1], 'perl: ' , label)
                        for line in iqlines:
                            doc = line[1: line.find(' ')].strip()
                            disease = line[line.find(' ') + 1 : line.find('|')].strip()
                            if doc == doc_id and disease == sub_key:
                                keyword =  line[line.find('|') + 1 : ].strip()
                                print(key, sub_key, doc_id, keyword, 
                                'paper: ', temp1[1], 'perl: ' , label)
                        for line in inlines:
                            doc = line[1: line.find(' ')].strip()
                            disease = line[line.find(' ') + 1 : line.find('|')].strip()
                            if doc == doc_id and disease == sub_key:
                                keyword =  line[line.find('|') + 1 : ].strip()
                                print(key, sub_key, doc_id, keyword, 
                                'paper: ', temp1[1], 'perl: ' , label)


