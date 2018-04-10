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

from cnn_2inputs import TCNNConfig, TextCNN
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, clean_wds, get_dic, if_list_has_YNQ
from data.cnews_loader import build_vocab, build_vocab_words, loadWord2Vec, expand_abbr, txt_proc, if_has_YNQ
import run_cnn_combined as cnn
#from rnn_atten import TRNNConfig, TextRNN
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

test_dic_text_rule = get_dic('perl_classifier/output/prod_134_0_2.xml')
test_dic_int_rule = get_dic('perl_classifier/output/prod_134_0_5.xml')

# Read CUI Vectors
entity_vector_file = 'data/DeVine_etal_200.txt'
entity_vocab, entity_embd, entity_vector_map = loadWord2Vec(entity_vector_file)
entity_embedding_dim = len(entity_embd[0])
#embeddings = np.asarray(embd)
# Read Word Vectors
word_vector_file = 'data/mimic3_pp200.txt'
word_vocab, word_embd, word_vector_map = loadWord2Vec(word_vector_file)
word_embedding_dim = len(word_embd[0])
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

        cnn.entity_base_dir = 'data/obesity_cnn'
        cnn.entity_train_dir = os.path.join(cnn.entity_base_dir, key+'.'+ sub_key +'.train.txt')
        cnn.entity_test_dir = os.path.join(cnn.entity_base_dir, key+'.'+ sub_key +'.test.txt')
        cnn.entity_val_dir = os.path.join(cnn.entity_base_dir, key+'.'+ sub_key +'.val.txt')
        cnn.entity_all_dir = os.path.join(cnn.entity_base_dir, key+'.'+ sub_key +'.all.txt')
        cnn.entity_vocab_dir = os.path.join(cnn.entity_base_dir, key+'.'+ sub_key +'.vocab.txt')

        cnn.base_dir = 'data/plus_remove_less'
        cnn.train_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.train.removeQN.txt')
        cnn.test_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.test.txt')
        cnn.val_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.train.removeQN.txt')
        cnn.all_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.all.txt')
        cnn.vocab_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.vocab.txt')

        train_data_X = []
        train_data_Y = [] 
        train_docs = train_sub_dic[sub_key]

        all_file = open(cnn.entity_all_dir, 'w')
        train_file = open(cnn.entity_train_dir, 'w')
        val_file = open(cnn.entity_val_dir, 'w')
        
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

        test_file = open(cnn.entity_test_dir , 'w')
        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_X.append(corpus[int(temp[0])-1])
            test_data_Y.append(temp[1])
            string = corpus[int(temp[0])-1]
            str_to_write = string

            test_file.write(temp[1] + '\t' + str_to_write + '\n')
            all_file.write(temp[1] + '\t' + str_to_write + '\n')

        test_file.close()
        all_file.close()

        print('Configuring CNN model...')

        cnn.config = TCNNConfig()
        build_vocab_words(cnn.all_dir, cnn.vocab_dir, cnn.config.vocab_size)
        cnn.words, cnn.word_to_id = read_vocab(cnn.vocab_dir)
        cnn.config.vocab_size = len(cnn.words)

        #select a subset of word vectors
        cnn.missing_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.missing.txt')
        missing_words_file = open(cnn.missing_dir, 'w')
        word_embeddings = np.random.uniform(-0.0, 0.0, (cnn.config.vocab_size , word_embedding_dim))
        count = 0
        for i in range(0, cnn.config.vocab_size):
            if(cnn.words[i] in word_vector_map): #word_vector_map.has_key(cnn.words[i])
                word_embeddings[i]= word_vector_map.get(cnn.words[i])
            else:
                count = count + 1
                missing_words_file.write(cnn.words[i]+'\n')
        
        print('no embedding: ' + str(1.0 * count/len(cnn.words)))
        print(str(len(word_embeddings)) + '\t' + str(len(word_embeddings[0])))
        missing_words_file.close()
        
        print(word_embeddings[0])

        build_vocab_words(cnn.entity_all_dir, cnn.entity_vocab_dir, cnn.config.entity_vocab_size)
        cnn.entities, cnn.entity_to_id = read_vocab(cnn.entity_vocab_dir)
        cnn.config.entity_vocab_size = len(cnn.entities)

        #select a subset of entity vectors
        entity_embeddings = np.random.uniform(-0.0, 0.0, (cnn.config.entity_vocab_size , entity_embedding_dim))
        count = 0
        for i in range(0, cnn.config.entity_vocab_size):
            if(cnn.entities[i] in entity_vector_map): #word_vector_map.has_key(cnn.words[i])
                entity_embeddings[i]= entity_vector_map.get(cnn.entities[i])
            else:
                count = count + 1
        print('no embedding: ' + str(1.0 * count/len(cnn.entities)))
        print(str(len(entity_embeddings)) + '\t' + str(len(entity_embeddings[0])))

        #cnn.embedding_matrix = word_embeddings
        #print(cnn.embedding_matrix.shape)
        cnn.model = TextCNN(cnn.config, word_embeddings, entity_embeddings)

        cnn.train()
        predict_y = cnn.test()  #predicting results
        print(key, sub_key)
        print(predict_y)

        tf.reset_default_graph() 

        test_doc_list = []
        for i in range(len(test_data_Y)):
            temp = test_docs[i].split(',')
            doc_id = temp[0]
            test_doc_list.append(doc_id)

        YNQ_list = if_list_has_YNQ(key, sub_key, test_doc_list)

        for i in range(len(test_data_Y)):

            doc_id = test_docs[i].split(',')[0]
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", doc_id)

            judgment = cnn.id_to_cat[predict_y[i]]
            #合并两者，rule和二分类CNN，先判断为QN，再用CNN预测
            #result = if_has_YNQ(key, sub_key, doc_id)
            doc_node.setAttribute("judgment", judgment)
            result = YNQ_list[i]
            
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

result_filename = "output/test_predict_cnn_plus_cui_removeQN.xml"
f = open(result_filename, "wb+") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close()

print(result_filename)
os.system('java -jar output/evaluation.jar output/test_groundtruth.xml ' 
+ result_filename)