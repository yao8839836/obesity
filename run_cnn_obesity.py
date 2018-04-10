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
import run_cnn as cnn


f = open('data/Obesity_data/ObesitySen_remove_familiy_history.dms','r')
content = f.read()
f.close()
corpus_file = open('data/Obesity_data/Obesity_corpus.txt','w')
records = content.strip().split('RECORD #')
corpus = []
for record in records:
    id = record[:record.find('\n')]
    if(record.find('[report_end]') != -1):
        content = record[record.find('\n') + 1: record.find('[report_end]')].strip()
        content = expand_abbr(content)
        content = content.replace('\'s', " 's").replace("'d", " 'd")
        content = content.replace("'s", " 's")
        content = content.replace("can't", "cannot")
        content = content.replace("couldn't", "could not")
        content = content.replace("won't", "will not")
        content = content.replace("wasn't", "was not")
        content = content.replace("hasn't", "has not")
        content = content.replace("don't", "do not")
        content = content.replace("didn't", "did not")
        content = content.replace("doesn't", "does not")
        
        word_list = text.text_to_word_sequence(content, lower=True, split=" ")
        word_list = clean_wds(word_list)
        #filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
        str_to_write = ' '
        str_to_write = str_to_write.join(word_list)
        corpus.append(str_to_write)
        corpus_file.write(str_to_write + '\n')
print(len(corpus))
corpus_file.close()
train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')

# Read Word Vectors
word_vector_file = 'data/mimic3_pp100.txt'
vocab,embd, word_vector_map = loadWord2Vec(word_vector_file)
embedding_dim = len(embd[0])
#embeddings = np.asarray(embd)
cnn.categories, cnn.cat_to_id, cnn.id_to_cat = read_category()

doc = Dom.Document() 
root_node = doc.createElement("diseaseset")
doc.appendChild(root_node) 

class_distribution_file = open('data/class_distribution.txt', 'w')
for key in train_dic:
    train_sub_dic = train_dic[key]
    test_sub_dic = test_dic[key]
    source_node = doc.createElement("diseases")
    source_node.setAttribute("source", key)
    for sub_key in train_sub_dic:
        disease_node = doc.createElement("disease")
        disease_node.setAttribute("name", sub_key)

        cnn.base_dir = 'data/obesity_cnn'
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
        
        counts = [0 for i in cnn.categories]
        for train_doc in train_docs:
            temp = train_doc.split(',')
            index = cnn.categories.index(temp[1])
            counts[index] += 1
        max_count = max(counts)

        class_distribution_file.write(key+'.'+ sub_key + "\t")
        for i in range(len(counts)):
            class_distribution_file.write(str(counts[i]) + " ")
        class_distribution_file.write("\t")
        print(len(train_docs))
        
        for train_doc in train_docs:
            temp = train_doc.split(',')

            train_data_X.append(corpus[int(temp[0])-1])
            train_data_Y.append(temp[1])

            string = corpus[int(temp[0])-1]
            str_to_write = string

            index = cnn.categories.index(temp[1])
            count = counts[index]
            if(random.random() > 0.1):
                train_file.write(temp[1] + '\t' + str_to_write + '\n')
                val_file.write(temp[1] + '\t' + str_to_write + '\n')
                # if(count < max_count):
                #     if(count < 10):
                #         for j in range(10):
                #             train_file.write(temp[1] + '\t' + str_to_write + '\n')
                #     else:
                #         for j in range(max_count/count):
                #             train_file.write(temp[1] + '\t' + str_to_write + '\n')
                # else: 
                #     train_file.write(temp[1] + '\t' + str_to_write + '\n')
            else:
                train_file.write(temp[1] + '\t' + str_to_write + '\n')
                val_file.write(temp[1] + '\t' + str_to_write + '\n')
                # if(count < max_count):
                #     if(count < 10):
                #         for j in range(10):
                #             val_file.write(temp[1] + '\t' + str_to_write + '\n')
                #     else:
                #         for j in range(max_count/count):
                #             val_file.write(temp[1] + '\t' + str_to_write + '\n')
                # else: 
                #     val_file.write(temp[1] + '\t' + str_to_write + '\n')
            all_file.write(temp[1] + '\t' + str_to_write + '\n')

        train_file.close()
        val_file.close()

        test_docs = test_sub_dic[sub_key]
        test_data_X = []
        test_data_Y = [] 
        print(len(test_docs))

        counts = [0 for i in cnn.categories]
        for test_doc in test_docs:
            temp = test_doc.split(',')
            index = cnn.categories.index(temp[1])
            counts[index] += 1

        for i in range(len(counts)):
            class_distribution_file.write(str(counts[i]) + " ")
        class_distribution_file.write("\n")
    
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
        print(len(predict_y))
        print(len(test_data_Y))

        tf.reset_default_graph() 
        
        correct_count = 0
        for i in range(len(test_data_Y)):
            if cnn.id_to_cat[predict_y[i]] == test_data_Y[i]:
                correct_count += 1
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", test_docs[i].split(',')[0])
            doc_node.setAttribute("judgment", cnn.id_to_cat[predict_y[i]])
            disease_node.appendChild(doc_node) 
        accuracy = correct_count * 1.0/ len(test_data_Y)
        print(key + ','+ sub_key + ' : Accuaracy :'+ str(accuracy))
    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node)

        #delete model files
        ds = list(os.listdir('checkpoints/text_word_cnn'))
        for d in ds:
            if os.path.isfile(d):
                os.remove(d)
        #delete train/dev/test data files 
        ds = list(os.listdir(cnn.base_dir))
        for d in ds:
            if os.path.isfile(d):
                os.remove(d)
class_distribution_file.close()
f = open("output/test_predict_cnn_pretrained_word2vec_oversampling_fam_rem_0.1_val.xml", "wb+") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close() 
