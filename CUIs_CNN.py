#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as et
import xml.dom.minidom as Dom
import sys
import os
import shutil
import numpy as np
from keras.preprocessing import text
import tensorflow as tf
import random

from cnn_model import TCNNConfig, TextCNN
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, clean_wds, get_dic, if_list_has_YNQ
from data.cnews_loader import build_vocab, build_vocab_words, loadWord2Vec, expand_abbr, txt_proc, if_has_YNQ
import run_cnn as cnn
from rnn_atten import TRNNConfig, TextRNN
#import run_rnn as rnn

f = open('data/CUIs_text_weng.txt','r')
content = f.read()
lines = content.split('\n')
f.close()

corpus = []
for line in lines:
    corpus.append(line)
print(len(corpus))


train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')

test_dic_text_rule = get_dic('perl_classifier/output/system_textual_annotation.xml')
test_dic_int_rule = get_dic('perl_classifier/output/system_intuitive_annotation.xml')

# Read CUI Vectors
word_vector_file = 'data/DeVine_etal_200.txt'
vocab,embd, word_vector_map = loadWord2Vec(word_vector_file)
embedding_dim = len(embd[0])
#embeddings = np.asarray(embd)
cnn.categories, cnn.cat_to_id, cnn.id_to_cat = read_category()

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

        cnn.base_dir = 'data/obesity_rnn'
        cnn.train_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.train.txt')
        cnn.test_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.test.txt')
        cnn.val_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.val.txt')
        cnn.all_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.all.txt')
        cnn.vocab_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.vocab.txt')

        train_data_X = []
        train_data_Y = [] 
        train_docs = train_sub_dic[sub_key]

        all_file = open(cnn.all_dir, 'w')
        train_file = open(cnn.train_dir, 'w')
        val_file = open(cnn.val_dir, 'w')
        
        print(len(train_docs))
        
        for train_doc in train_docs:
            temp = train_doc.split(',')

            string = corpus[int(temp[0])-1]
            str_to_write = string

            index = cnn.categories.index(temp[1])

            if random.random() > 0.1:
                if(key == 'textual'):
                    if(temp[1] == 'Y' or temp[1] == 'U'):
                        train_file.write(temp[1] + '\t' + str_to_write + '\n')
                        val_file.write(temp[1] + '\t' + str_to_write + '\n')
                        all_file.write(temp[1] + '\t' + str_to_write + '\n')

                if(key == 'intuitive'):
                    if(temp[1] == 'Y' or temp[1] == 'N'):
                        train_file.write(temp[1] + '\t' + str_to_write + '\n')
                        val_file.write(temp[1] + '\t' + str_to_write + '\n')
                        all_file.write(temp[1] + '\t' + str_to_write + '\n')
            else:
                if(key == 'textual'):
                    if(temp[1] == 'Y' or temp[1] == 'U'):
                        train_file.write(temp[1] + '\t' + str_to_write + '\n')
                        val_file.write(temp[1] + '\t' + str_to_write + '\n')
                        all_file.write(temp[1] + '\t' + str_to_write + '\n')
                if(key == 'intuitive'):
                    if(temp[1] == 'Y' or temp[1] == 'N'):
                        train_file.write(temp[1] + '\t' + str_to_write + '\n')
                        val_file.write(temp[1] + '\t' + str_to_write + '\n')
                        all_file.write(temp[1] + '\t' + str_to_write + '\n')

        train_file.close()
        val_file.close()

        test_docs = test_sub_dic[sub_key]
        test_data_X = []
        test_data_Y = [] 
        print(len(test_docs))

    
        test_file = open(cnn.test_dir , 'w')
        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_X.append(corpus[int(temp[0])-1])
            test_data_Y.append(temp[1])
            string = corpus[int(temp[0])-1]
            #string = expand_abbr(string)
            str_to_write = string

            test_file.write(temp[1] + '\t' + str_to_write + '\n')
            all_file.write(temp[1] + '\t' + str_to_write + '\n')

        print('Configuring CNN model...')
        test_file.close()
        all_file.close()
        cnn.config = TCNNConfig()
        #if not os.path.exists(cnn.vocab_dir): #if no vocab, build it
        build_vocab_words(cnn.all_dir, cnn.vocab_dir, cnn.config.vocab_size)
        cnn.words, cnn.word_to_id = read_vocab(cnn.vocab_dir)
        cnn.config.vocab_size = len(cnn.words)

        #select a subset of word vectors
        cnn.missing_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.missing.txt')
        missing_words_file = open(cnn.missing_dir, 'w')
        sub_embeddings = np.random.uniform(-0.0, 0.0, (cnn.config.vocab_size , embedding_dim))
        count = 0
        for i in range(0, cnn.config.vocab_size):
            if(cnn.words[i] in word_vector_map): #word_vector_map.has_key(cnn.words[i])
                count = count
                sub_embeddings[i]= word_vector_map.get(cnn.words[i])
            else:
                count = count + 1
                missing_words_file.write(cnn.words[i]+'\n')
        
        print('no embedding: ' + str(1.0 * count/len(cnn.words)))
        print(str(len(sub_embeddings)) + '\t' + str(len(sub_embeddings[0])))
        missing_words_file.close()
        
        print(sub_embeddings[0])
        cnn.embedding_matrix = sub_embeddings
        #print(cnn.embedding_matrix.shape)
        cnn.model = TextCNN(cnn.config)

        cnn.train()
        predict_y = cnn.test()  #predicting results
        print(predict_y)

        tf.reset_default_graph() 

        test_doc_list = []
        for i in range(len(test_data_Y)):
            temp = test_docs[i].split(',')
            doc_id = temp[0]
            test_doc_list.append(doc_id)

        YNQ_list = if_list_has_YNQ(key, sub_key, test_doc_list)

        tf.reset_default_graph() 
        
        for i in range(len(test_data_Y)):

            doc_id = test_docs[i].split(',')[0]
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", doc_id)

            judgment = cnn.id_to_cat[predict_y[i]]

            doc_node.setAttribute("judgment", judgment)

            #result = if_has_YNQ(key, sub_key, doc_id)
            result = YNQ_list[i]
            #print(result)
            if result[0] == 0 and result[1] == 0 and result[2] == 0: # Nothing
                doc_node.setAttribute("judgment", judgment)
            elif result[0] == 0 and result[1] == 0 and result[2] == 1: #Y
                doc_node.setAttribute("judgment", judgment)
            elif result[0] == 0 and result[1] == 1 and result[2] == 0: # N
                doc_node.setAttribute("judgment", 'N')
            elif result[0] == 0 and result[1] == 1 and result[2] == 1: # YN
                doc_node.setAttribute("judgment", judgment)
            elif result[0] == 1 and result[1] == 0 and result[2] == 0: # Q
                doc_node.setAttribute("judgment", 'Q')
            elif result[0] == 1 and result[1] == 0 and result[2] == 1: # QY
                doc_node.setAttribute("judgment", judgment)
            elif result[0] == 1 and result[1] == 1 and result[2] == 0: # QN
                doc_node.setAttribute("judgment", 'N')
            elif result[0] == 1 and result[1] == 1 and result[2] == 1: # QNY
                doc_node.setAttribute("judgment", judgment)

            #doc_node.setAttribute("judgment", judgment) 

            #合并两者，rule和二分类CNN，用规则的Q或N覆盖
            #disease_node.get
            '''if key == 'textual':
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
                        doc_node.setAttribute("judgment", temp[1])'''

            disease_node.appendChild(doc_node) 

        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node)

result_filename = "output/test_predict_cnn_cui_weng_removeQN.xml"
f = open(result_filename, "wb+") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close()

print(result_filename)
os.system('java -jar output/evaluation.jar output/test_groundtruth.xml ' 
+ result_filename)
