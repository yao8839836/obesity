#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.dom.minidom as Dom
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn import linear_model
import xml.etree.ElementTree as et
import numpy as np
from data.cnews_loader import get_dic

f = open('data/obesity_lda_features.txt', 'r')
content = f.read()
f.close()

lines = content.split('\n')
embedding_vectors = []
for line in lines:
    values = line.split(' ')
    vector = values[0:]
    embedding_vectors.append(vector)
print(embedding_vectors[0])
print(len(embedding_vectors))
print(len(embedding_vectors[0]))

train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
#print(train_dic) 
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')
#print(test_dic)

test_dic_text_rule = get_dic('perl_classifier/output/system_textual_annotation.xml')
test_dic_int_rule = get_dic('perl_classifier/output/system_intuitive_annotation.xml')

doc = Dom.Document() 
root_node = doc.createElement("diseaseset")
doc.appendChild(root_node) 

for key in train_dic:
    train_sub_dic = train_dic[key]
    test_sub_dic = test_dic[key]
    source_node = doc.createElement("diseases")
    source_node.setAttribute("source", key)
    for sub_key in train_sub_dic:
        disease_node = doc.createElement("disease")
        disease_node.setAttribute("name", sub_key)
        train_data_X = []
        train_data_Y = [] 
        train_docs = train_sub_dic[sub_key]
        print(len(train_docs))
        for train_doc in train_docs:
            temp = train_doc.split(',')
            #print(key,sub_key,temp)
            if(key == 'textual'):
                if(temp[1] == 'Y' or temp[1] == 'U'):
                    train_data_X.append(embedding_vectors[int(temp[0])-1])
                    train_data_Y.append(temp[1])
            if(key == 'intuitive'):
                if(temp[1] == 'Y' or temp[1] == 'N'):
                    train_data_X.append(embedding_vectors[int(temp[0])-1])
                    train_data_Y.append(temp[1])
        clf = svm.SVC(decision_function_shape='ovr',class_weight="balanced",kernel='linear')
        #clf = GaussianNB()
        #clf = linear_model.LogisticRegression(C=1e5, class_weight = 'balanced')
        train_data_X = np.array(train_data_X)
        train_data_Y = np.array(train_data_Y)
        clf.fit(train_data_X, train_data_Y)
    
        test_docs = test_sub_dic[sub_key]
        test_data_X = []
        test_data_Y = [] 
        print(len(test_docs))
    
        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_X.append(embedding_vectors[int(temp[0])-1])
            test_data_Y.append(temp[1])
        
        predict_y = clf.predict(test_data_X)
        print(predict_y)
    
        correct_count = 0
        for i in range(len(test_data_Y)):

            doc_id = test_docs[i].split(',')[0]
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", test_docs[i].split(',')[0])
            doc_node.setAttribute("judgment", predict_y[i])
                        
            #合并两者，rule和二分类结果，用规则的Q或N覆盖
            #disease_node.get
            if key == 'textual':
                test_rule = test_dic_text_rule[key]
                test_rule_docs = test_rule[sub_key]
                for test_doc_rule in test_rule_docs:
                    temp = test_doc_rule.split(',')
                    if temp[0] == doc_id and (temp[1] == 'N' or temp[1] == 'Q'):
                        doc_node.setAttribute("judgment", temp[1])
            if key == 'intuitive':
                test_rule = test_dic_int_rule[key]
                test_rule_docs = test_rule[sub_key]
                for test_doc_rule in test_rule_docs:
                    temp = test_doc_rule.split(',')
                    if temp[0] == doc_id and temp[1] == 'Q':
                        doc_node.setAttribute("judgment", temp[1])
            disease_node.appendChild(doc_node) 
    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node)
    
f = open("output/test_predict_lda_removeQN.xml", "w") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close()