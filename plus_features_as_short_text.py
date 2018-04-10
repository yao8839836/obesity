from data.cnews_loader import get_dic
import xml.etree.ElementTree as et
import numpy as np

## collect all + features
useful_line_list = []
keyword_set = set()
# positive
f = open('data/textual/positive_useful.log','r')
content = f.read()
f.close()
lines = content.split('\n')

for line in lines:
    doc_id = line[1: line.find(' ')].strip()
    disease = line[line.find(' ') + 1 : line.find('|')].strip()
    keyword =  line[line.find('|') + 1 : ].strip()
    string = doc_id + ',' + disease + ',' + keyword
    print(string)
    useful_line_list.append(string)
    keyword_set.add(keyword)

# questionalble
f = open('data/textual/questionable_truly_useful.log','r')
content = f.read()
f.close()
lines = content.split('\n')

for line in lines:
    doc_id = line[1: line.find(' ')].strip()
    disease = line[line.find(' ') + 1 : line.find('|')].strip()
    keyword =  line[line.find('|') + 1 : ].strip()
    string = doc_id + ',' + disease + ',' + keyword
    print(string)
    useful_line_list.append(string)
    keyword_set.add(keyword)

# negated
f = open('data/textual/negated_truly_useful.log','r')
content = f.read()
f.close()
lines = content.split('\n')

for line in lines:
    doc_id = line[1: line.find(' ')].strip()
    disease = line[line.find(' ') + 1 : line.find('|')].strip()
    keyword =  line[line.find('|') + 1 : ].strip()
    string = doc_id + ',' + disease + ',' + keyword
    print(string)
    useful_line_list.append(string)
     
    keyword_set.add(keyword)
    

keyword_list = list(keyword_set)
feature_length = len(keyword_list)
print(feature_length)
print(keyword_list)

train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')

for key in train_dic:
    train_sub_dic = train_dic[key]
    test_sub_dic = test_dic[key]

    for sub_key in train_sub_dic:

        f_all = open('data/plus_features_short_text/'+key+"."+sub_key+".all.textual.txt", 'w')

        train_docs = train_sub_dic[sub_key]
        f = open('data/plus_features_short_text/'+key+"."+sub_key+".train.textual.txt", 'w')

        for train_doc in train_docs:
            phrase_list = []
            temp = train_doc.split(',')
            feature_vector = [0 for i in range(feature_length)]
            for line in useful_line_list:
                string = line.split(',')
                doc_id = string[0]
                disease = string[1]
                keyword = string[2]
                if(sub_key == disease and doc_id == temp[0]):
                    #sub_key == disease and 
                    feature_vector[keyword_list.index(keyword)] = 1
            for i in range(feature_length):
                if(feature_vector[i] != 0):
                    phrase_list.append(keyword_list[i])
            string = ' '.join(phrase_list)
            if string == '':
                string = '0'
            f.write(temp[1] + '\t' + string + '\n')
            ''' if temp[1] == 'N' or temp[1] == 'Q':
                for i in range(10):
                    f.write(temp[1] + '\t' + string + '\n') '''
                    
            f_all.write(temp[1] + '\t' + string + '\n')
        f.close()
                    
 
        test_docs = test_sub_dic[sub_key]
        f = open('data/plus_features_short_text/'+key+"."+sub_key+".test.textual.txt", 'w')

        for test_doc in test_docs:
            phrase_list = []
            temp = test_doc.split(',')
            feature_vector = [0 for i in range(feature_length)]
            for line in useful_line_list:
                string = line.split(',')
                doc_id = string[0]
                disease = string[1]
                keyword = string[2]
                if(sub_key == disease and doc_id == temp[0]):
                    #sub_key == disease and 
                    feature_vector[keyword_list.index(keyword)] = 1
            for i in range(feature_length):
                if(feature_vector[i] != 0):
                    phrase_list.append(keyword_list[i])
            string = ' '.join(phrase_list)
            if string == '':
                string = '0'
            f.write(temp[1] + '\t' + string + '\n')
            f_all.write(temp[1] + '\t' + string + '\n') 
        f.close()
        f_all.close()