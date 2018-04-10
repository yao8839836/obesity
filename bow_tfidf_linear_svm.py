from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn import linear_model
import xml.etree.ElementTree as et
import xml.dom.minidom as Dom

def get_dic(string):
    #get dict from xml
    train_labels = et.parse(string)
    root = train_labels.getroot()
    dic = {}
    for child in root:
        key = child.attrib['source']
        sub_dic = {}
        for sub_child in child:
            sub_key =  sub_child.attrib['name']
            value = []
            for sub_sub_child in sub_child:
                value.append(sub_sub_child.attrib['id']+','+sub_sub_child.attrib['judgment'])
            sub_dic[sub_key]= value
        dic[key] = sub_dic    
    return dic

f = open('data/Obesity_data/Obesity1.dms','r')
content = f.read()
f.close()

f = open('data/Obesity_data/records.xml','w')
doc = Dom.Document() 
root_node = doc.createElement("root")
doc.appendChild(root_node) 
docs_node = doc.createElement("docs")
root_node.appendChild(docs_node)

records = content.strip().split('RECORD #')
corpus = []
for record in records:


    if(record.find('[report_end]') != -1):
        record_content = record[record.find('\n') + 1: record.find('[report_end]')].strip()
        corpus.append(record_content)

        id = record[:record.find('\n')]
        doc_node = doc.createElement("doc")
        doc_node.setAttribute("id", id)
        text_node =  doc.createTextNode("text")
        text_node.text = record_content
        doc_node.appendChild(text_node)
        docs_node.appendChild(doc_node)
print(len(corpus))
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close() 


tfidf_vec = TfidfVectorizer(max_df=0.95, min_df=2,
                                   max_features=5000) 
tfidf_matrix = tfidf_vec.fit_transform(corpus)
print(tfidf_matrix)
tfidf_matrix_array = tfidf_matrix.toarray()
print(tfidf_matrix_array[0])
print(len(tfidf_matrix_array[0]))

stop_words = tfidf_vec.get_stop_words()
print(stop_words)

train_dic = get_dic('data/Obesity_data/train_groundtruth.xml')
#print(train_dic) 
test_dic = get_dic('data/Obesity_data/test_groundtruth.xml')
#print(test_dic) 


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
        train_data_X = []
        train_data_Y = [] 
        train_docs = train_sub_dic[sub_key]
        print(len(train_docs))
        for train_doc in train_docs:
            temp = train_doc.split(',')
            #print(key,sub_key,temp)
            train_data_X.append(tfidf_matrix_array[int(temp[0])-1])
            train_data_Y.append(temp[1])
        clf = svm.SVC(decision_function_shape='ovr',class_weight="balanced",kernel='linear')
        #clf = GaussianNB()
        #clf = linear_model.LogisticRegression(C=1e5, class_weight = 'balanced')
        clf.fit(train_data_X, train_data_Y)
    
        test_docs = test_sub_dic[sub_key]
        test_data_X = []
        test_data_Y = [] 
        print(len(test_docs))
    
        for test_doc in test_docs:
            temp = test_doc.split(',')
            test_data_X.append(tfidf_matrix_array[int(temp[0])-1])
            test_data_Y.append(temp[1])
        
        predict_y = clf.predict(test_data_X)
        print(predict_y)
    
        correct_count = 0
        for i in range(len(test_data_Y)):
            if predict_y[i] == test_data_Y[i]:
                correct_count += 1
            doc_node = doc.createElement("doc")
            doc_node.setAttribute("id", test_docs[i].split(',')[0])
            doc_node.setAttribute("judgment", predict_y[i])
            disease_node.appendChild(doc_node) 
        accuracy = correct_count * 1.0/ len(test_data_Y)
        print(key + ','+ sub_key + ' : Accuaracy :'+ str(accuracy))
        f.write(key + ','+ sub_key + ' : Accuaracy :'+ str(accuracy) +'\n')
    
        source_node.appendChild(disease_node) 
        root_node.appendChild(source_node) 
    
f.close()
f = open("output/test_predict.xml", "w") 
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close() 