
# coding: utf-8

# In[1]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn import svm
import xml.etree.ElementTree as et



def get_turples(string):
    #get turples from xml
    train_labels = et.parse(string)
    root = train_labels.getroot()
    turples = []
    dic = {}
    for child in root:
        #print(child.attrib)
        for sub_child in child:
            key = child.attrib['source'] + ',' +sub_child.attrib['name']
            value = []
            #print(sub_child.attrib)
            for sub_sub_child in sub_child:
                #print(sub_sub_child.attrib)
                #print(child.attrib['source'], sub_child.attrib['name'], 
                #      sub_sub_child.attrib['id'],sub_sub_child.attrib['judgment'])
                turples.append((sub_sub_child.attrib['id'], child.attrib['source'],
                                sub_child.attrib['name'],sub_sub_child.attrib['judgment']))
                value.append(sub_sub_child.attrib['id']+','+sub_sub_child.attrib['judgment'])
                dic[key]= value
    return turples, dic

f = open('data/Obesity_data/Obesity1.dms','r')
content = f.read()
f.close()

#print (len(str))
#records_str = ''.join(str)
#records = records_str.split('[report_end]')
#print (len(records))
records = content.strip().split('RECORD #')
print (len(records))

corpus = []
for record in records:
    id = record[:record.find('\n')]
    if(record.find('[report_end]') != -1):
        #print(id)
        corpus.append(record[record.find('\n') + 1: record.find('[report_end]')].strip())
#print(corpus[0])
print(len(corpus))

tfidf_vec = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english') 
tfidf_matrix = tfidf_vec.fit_transform(corpus)
tfidf_matrix_array = tfidf_matrix.toarray()
print(tfidf_matrix_array.shape)
stop_words = tfidf_vec.get_stop_words()

#print(stop_words)
#print(tfidf_vec.get_feature_names())
#print(tfidf_vec.vocabulary_)
#print(tfidf_matrix)
#print(s)
#records = str.split('[report_end] RECORD')=

#print(dic)
train_turples, train_dic = get_turples('data/Obesity_data/train_groundtruth.xml')
print(train_dic) 

test_turples, test_dic = get_turples('data/Obesity_data/test_groundtruth.xml')
print(test_dic) 


f = open('results.txt','w')
for key in train_dic:
    #print(key)
    train_data_X = []
    train_data_Y = [] 
    train_docs = train_dic[key]
    for train_doc in train_docs:
        temp = train_doc.split(',')
        train_data_X.append(tfidf_matrix_array[int(temp[0])-1])
        #print(tfidf_matrix[int(temp[0])-1])
        train_data_Y.append(temp[1])
    clf = svm.SVC()
    #print(train_data_X)
    clf.fit(train_data_X, train_data_Y)
    test_docs = test_dic[key]
    test_data_X = []
    test_data_Y = [] 
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
    accuracy = correct_count * 1.0/ len(test_data_Y)
    print('Accuaracy :'+ str(accuracy))
    f.write(key + '  '+ 'Accuaracy :'+ str(accuracy) +'\n')
f.close()

