import xml.etree.ElementTree as et
import xml.dom.minidom as Dom
import sys
import os
import shutil
import numpy as np
from keras.preprocessing import text
import tensorflow as tf
import random

from rnn_atten import TRNNConfig, TextRNN
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, clean_wds, get_dic
from data.cnews_loader import build_vocab, build_vocab_words, loadWord2Vec, expand_abbr, txt_proc
import run_rnn as rnn

train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')

# Read Word Vectors
word_vector_file = 'data/mimic3_pp100.txt'
vocab,embd, word_vector_map = loadWord2Vec(word_vector_file)
embedding_dim = len(embd[0])
#embeddings = np.asarray(embd)
rnn.categories, rnn.cat_to_id, rnn.id_to_cat = read_category()

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

        rnn.base_dir = 'data/plus_features_short_text'
        rnn.train_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.train.intuitive.txt')
        rnn.test_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.test.intuitive.txt')
        rnn.val_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.train.intuitive.txt')
        rnn.all_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.all.intuitive.txt')
        rnn.vocab_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.vocab.txt')

        test_docs = test_sub_dic[sub_key]
        test_data_Y = [] 
        print(len(test_docs))

        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_Y.append(temp[1])
        print('Configuring RNN model...')

        rnn.config = TRNNConfig()
        #if not os.path.exists(cnn.vocab_dir): #if no vocab, build it
        build_vocab_words(rnn.all_dir, rnn.vocab_dir, rnn.config.vocab_size)
        rnn.words, rnn.word_to_id = read_vocab(rnn.vocab_dir)
        rnn.config.vocab_size = len(rnn.words)

        #select a subset of word vectors
        rnn.missing_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.missing.txt')
        missing_words_file = open(rnn.missing_dir, 'w')
        sub_embeddings = np.random.uniform(-0.0, 0.0, (rnn.config.vocab_size , embedding_dim))
        count = 0
        for i in range(0, rnn.config.vocab_size):
            if(rnn.words[i] in word_vector_map): #word_vector_map.has_key(cnn.words[i])
                count = count
                sub_embeddings[i]= word_vector_map.get(rnn.words[i])
            else:
                count = count + 1
                missing_words_file.write(rnn.words[i]+'\n')
        
        print('no embedding: ' + str(1.0 * count/len(rnn.words)))
        print(str(len(sub_embeddings)) + '\t' + str(len(sub_embeddings[0])))
        missing_words_file.close()
        
        print(sub_embeddings[0])
        #rnn.embedding_matrix = sub_embeddings
        #print(cnn.embedding_matrix.shape)
        rnn.model = TextRNN(rnn.config, sub_embeddings)

        rnn.train()
        predict_y = rnn.test()  #predicting results
        print(predict_y)
        print(len(predict_y))
        print(len(test_data_Y))

        tf.reset_default_graph() 
        
        correct_count = 0
        for i in range(len(test_data_Y)):
            if rnn.id_to_cat[predict_y[i]] == test_data_Y[i]:
                correct_count += 1
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", test_docs[i].split(',')[0])
            doc_node.setAttribute("judgment", rnn.id_to_cat[predict_y[i]])
            disease_node.appendChild(doc_node) 
        accuracy = correct_count * 1.0/ len(test_data_Y)
        print(key + ','+ sub_key + ' : Accuaracy :'+ str(accuracy))
    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node)

f = open("test_predict_rnn_plus_intuitive_atten_pretrain.xml", "wb+") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close() 
