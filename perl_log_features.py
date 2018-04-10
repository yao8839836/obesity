import xml.dom.minidom as Dom
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn import linear_model
from data.cnews_loader import get_dic
import xml.etree.ElementTree as et
import numpy as np

## collect all + features
useful_line_list = []
keyword_set = set()
# positive
f = open('data/intuitive/positive_useful.log','r')
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
f = open('data/intuitive/questionable_truly_useful.log','r')
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
f = open('data/intuitive/negated_truly_useful.log','r')
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

        for train_doc in train_docs:
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
            train_data_X.append(feature_vector)
            train_data_Y.append(temp[1])
        #clf = svm.SVC(decision_function_shape='ovr',class_weight="balanced",kernel='linear')
        #clf = GaussianNB()
        clf = linear_model.LogisticRegression(C=1e5, class_weight = 'balanced')
        train_data_X = np.array(train_data_X)
        train_data_Y = np.array(train_data_Y)
        clf.fit(train_data_X, train_data_Y)
    
        test_docs = test_sub_dic[sub_key]
        test_data_X = []
        test_data_Y = []
    
        for test_doc in test_docs:
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
            #print(feature_vector)
            test_data_X.append(feature_vector)
            test_data_Y.append(temp[1])
        
        predict_y = clf.predict(test_data_X)
    
        correct_count = 0
        for i in range(len(test_data_Y)):
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", test_docs[i].split(',')[0])
            doc_node.setAttribute("judgment", predict_y[i])
            disease_node.appendChild(doc_node) 
    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node)
    
f = open("output/test_predict_plus_features_intuitive_LR.xml", "w") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close()