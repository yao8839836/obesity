
import xml.etree.ElementTree as et
import xml.dom.minidom as Dom
import sys
import os
import numpy as np
from keras.preprocessing import text
import tensorflow as tf

from rnn_model import TRNNConfig, TextRNN
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, build_vocab, build_vocab_words
from data.cnews_loader import build_vocab, build_vocab_words, loadWord2Vec, expand_abbr, txt_proc, get_dic, clean_wds
import run_rnn as rnn

f = open('data/Obesity_data/ObesitySen_remove_familiy_history.dms','r')
content = f.read()
f.close()
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
print(len(corpus))


train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')

# Read Word Vectors
word_vector_file = 'data/mimic3_pp100.txt'
vocab,embd, word_vector_map = loadWord2Vec(word_vector_file)
embedding_dim = len(embd[0])

doc = Dom.Document() 
root_node = doc.createElement("diseaseset")
doc.appendChild(root_node) 

f = open('results.txt','w')
for key in train_dic:
    train_sub_dic = train_dic[key]
    test_sub_dic = test_dic[key]
    source_node = doc.createElement("diseases")
    source_node.setAttribute("source", key)
    for sub_key in train_sub_dic:
        disease_node = doc.createElement("disease")
        disease_node.setAttribute("name", sub_key)

        rnn.base_dir = 'data/obesity_rnn'
        rnn.train_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.train.txt')
        rnn.test_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.test.txt')
        rnn.val_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.train.txt')
        rnn.vocab_dir = os.path.join(rnn.base_dir, key+'.'+ sub_key +'.vocab.txt')

        train_data_X = []
        train_data_Y = [] 
        train_docs = train_sub_dic[sub_key]
        train_file = open(rnn.train_dir, 'w')

        print(len(train_docs))
        for train_doc in train_docs:
            temp = train_doc.split(',')
            #print(key,sub_key,temp)
            train_data_X.append(corpus[int(temp[0])-1])
            train_data_Y.append(temp[1])
            string = corpus[int(temp[0])-1].replace('\n', '').replace('\t', '')

            train_file.write(temp[1] + '\t' + string + '\n')

        test_docs = test_sub_dic[sub_key]
        test_data_X = []
        test_data_Y = [] 
        print(len(test_docs))
        train_file.close()
    
        test_file = open(rnn.test_dir, 'w')
        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_X.append(corpus[int(temp[0])-1])
            test_data_Y.append(temp[1])
            string = corpus[int(temp[0])-1].replace('\n', '').replace('\t', '')
   
            test_file.write(temp[1] + '\t' + string + '\n')

        print('Configuring RNN model...')
        test_file.close()
        rnn.config = TRNNConfig()
        #if not os.path.exists(rnn.vocab_dir): #if no vocab, build it
        build_vocab_words(rnn.train_dir, rnn.vocab_dir, rnn.config.vocab_size)
        rnn.categories, rnn.cat_to_id, rnn.id_to_cat = read_category()
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
        
        rnn.model = TextRNN(rnn.config)

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
        f.write(key + ','+ sub_key + ' : Accuaracy :'+ str(accuracy) +'\n')
    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node) 
    
f.close()
f = open("output/test_predict_rnn_gru_remove_fam.xml", "w") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close() 
