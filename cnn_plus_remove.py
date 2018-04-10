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
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, clean_wds, get_dic
from data.cnews_loader import build_vocab, build_vocab_words, loadWord2Vec, expand_abbr, txt_proc
from data.cnews_loader import read_category_textual, read_category_intuitive, if_has_YNQ, if_list_has_YNQ
import run_cnn as cnn

train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')

test_dic_text_rule = get_dic('perl_classifier/output/system_textual_annotation.xml')
test_dic_int_rule = get_dic('perl_classifier/output/system_intuitive_annotation.xml')

# Read Word Vectors
word_vector_file = 'data/mimic3_pp200.txt'
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

        cnn.base_dir = 'data/plus_remove_less'
        cnn.train_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.train.removeQN.txt')
        cnn.test_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.test.txt')
        cnn.val_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.train.removeQN.txt')
        cnn.all_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.all.txt')
        cnn.vocab_dir = os.path.join(cnn.base_dir, key+'.'+ sub_key +'.vocab.txt')

        test_docs = test_sub_dic[sub_key]
        test_data_Y = [] 
        print(len(test_docs))

        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_Y.append(temp[1])

        print('Configuring CNN model...')

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
            if(cnn.words[i] in word_vector_map): # word_vector_map.has_key(cnn.words[i])
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
        print(key, sub_key)
        print(predict_y)
        print(len(predict_y))
        print(len(test_data_Y))

        tf.reset_default_graph()

        test_doc_list = []
        for i in range(len(test_data_Y)):
            temp = test_docs[i].split(',')
            doc_id = temp[0]
            test_doc_list.append(doc_id)

        YNQ_list = if_list_has_YNQ(key, sub_key, test_doc_list)
        
        for i in range(len(test_data_Y)):

            temp = test_docs[i].split(',')

            doc_id = temp[0]
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", doc_id)

            judgment = cnn.id_to_cat[predict_y[i]]
            #doc_node.setAttribute("judgment", cnn.id_to_cat[predict_y[i]])
            #合并两者，rule和二分类CNN，用规则的Q或N覆盖
            #judgment = temp[1]

            #合并两者，rule和二分类CNN，先判断为QN，再用CNN预测
            #result = if_has_YNQ(key, sub_key, doc_id)
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

            disease_node.appendChild(doc_node)
                    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node)

result_filename = "output/test_predict_cnn_plus_removeQN.xml"
f = open(result_filename, "wb+") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close()

print(result_filename)
os.system('java -jar output/evaluation.jar output/test_groundtruth.xml ' 
+ result_filename)