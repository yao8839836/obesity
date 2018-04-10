# coding: utf-8

import sys
from collections import Counter

import numpy as np
import tensorflow.contrib.keras as kr
import xml.etree.ElementTree as et

import re
import os
import csv
import subprocess
import nltk
from datetime import datetime


if sys.version_info[0] > 2:
    is_py3 = True
else:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    is_py3 = False


def native_word(word, encoding='utf-8'):
    """如果在python2下面使用python3训练的模型，可考虑调用此函数转化一下字符编码"""
    if not is_py3:
        return word.encode(encoding)
    else:
        return word


def native_content(content):
    if not is_py3:
        return content.decode('utf-8')
    else:
        return content


def open_file(filename, mode='r'):
    """
    常用文件操作，可在python2和python3间切换.
    mode: 'r' or 'w' for read or write
    """
    if is_py3:
        return open(filename, mode, encoding='utf-8', errors='ignore')
    else:
        return open(filename, mode)


def read_file(filename):
    """读取文件数据，字符"""
    contents, labels = [], []
    with open_file(filename) as f:
        for line in f:
            try:
                label, content = line.strip().split('\t')
                #temp = line.strip().split('\t')
                #label = temp[0]
                #content = temp[1]
                if content:
                    contents.append(list(native_content(content)))
                    labels.append(native_content(label))
                else:
                    print("failed")
            except:
                print("failed")
                pass
    f.close()
    return contents, labels

def read_file_words(filename):
    """读取文件数据,单词"""
    contents, labels = [], []
    with open_file(filename) as f:
        for line in f:
            try:
                temp = line.strip().split('\t')
                label = temp[0]
                content = temp[1]
                if content:
                    contents.append(content.split(' '))
                    #print(len(content.split(' ')))
                    labels.append(native_content(label))
                else:
                    print("failed")
            except:
                print("failed")
                pass
    print('!!!' + str(len(contents)))
    f.close()
    return contents, labels


def build_vocab(train_dir, vocab_dir, vocab_size=5000):
    """根据训练集字符构建词汇表，存储"""
    data_train, _ = read_file(train_dir)

    all_data = []
    for content in data_train:
        all_data.extend(content)

    counter = Counter(all_data)
    count_pairs = counter.most_common(vocab_size - 1)
    words, _ = list(zip(*count_pairs))
    # 添加一个 <PAD> 来将所有文本pad为同一长度
    words = ['<PAD>'] + list(words)
    f = open_file(vocab_dir, mode='w')
    f.write('\n'.join(words) + '\n')
    f.close

def build_vocab_words(train_dir, vocab_dir, vocab_size=5000):
    """根据训练集单词构建词汇表，存储"""
    data_train, _ = read_file_words(train_dir)

    all_data = []
    for content in data_train:
        all_data.extend(content)

    counter = Counter(all_data)
    count_pairs = counter.most_common(vocab_size - 1)
    words, _ = list(zip(*count_pairs))
    # 添加一个 <PAD> 来将所有文本pad为同一长度
    words = ['<PAD>'] + list(words)
    f = open_file(vocab_dir, mode='w')
    f.write('\n'.join(words) + '\n')
    f.close


def read_vocab(vocab_dir):
    """读取词汇表"""
    # words = open_file(vocab_dir).read().strip().split('\n')
    with open_file(vocab_dir) as fp:
        # 如果是py2 则每个值都转化为unicode
        words = [native_content(_.strip()) for _ in fp.readlines()]
    word_to_id = dict(zip(words, range(len(words))))
    return words, word_to_id


def read_category():
    """读取分类目录，固定"""
    categories = ['Y', 'N', 'Q', 'U']

    categories = [native_content(x) for x in categories]

    cat_to_id = dict(zip(categories, range(len(categories))))
    
    id_to_cat = dict(zip(range(len(categories)), categories))

    return categories, cat_to_id, id_to_cat

def read_category_textual():
    """读取分类目录，固定"""
    categories = ['Y', 'U']

    categories = [native_content(x) for x in categories]

    cat_to_id = dict(zip(categories, range(len(categories))))
    
    id_to_cat = dict(zip(range(len(categories)), categories))

    return categories, cat_to_id, id_to_cat

def read_category_intuitive():
    """读取分类目录，固定"""
    categories = ['Y', 'N']

    categories = [native_content(x) for x in categories]

    cat_to_id = dict(zip(categories, range(len(categories))))
    
    id_to_cat = dict(zip(range(len(categories)), categories))

    return categories, cat_to_id, id_to_cat


def to_words(content, words):
    """将id表示的内容转换为文字"""
    return ''.join(words[x] for x in content)


def process_file(filename, word_to_id, cat_to_id, max_length=10000):
    """将文件转换为id表示(字符)"""
    contents, labels = read_file(filename)
    print("测试集大小" + str(len(contents)))
    data_id, label_id = [], []
    for i in range(len(contents)):
        data_id.append([word_to_id[x] for x in contents[i] if x in word_to_id])
        label_id.append(cat_to_id[labels[i]])

    # 使用keras提供的pad_sequences来将文本pad为固定长度
    x_pad = kr.preprocessing.sequence.pad_sequences(data_id, max_length)
    y_pad = kr.utils.to_categorical(label_id, num_classes=len(cat_to_id))  # 将标签转换为one-hot表示

    return x_pad, y_pad


def process_file_words(filename, word_to_id, cat_to_id, max_length=10000):
    """将文件转换为id表示"""
    contents, labels = read_file_words(filename)
    print("测试集大小" + str(len(contents)))
    data_id, label_id = [], []
    for i in range(len(contents)):
        data_id.append([word_to_id[x] for x in contents[i] if x in word_to_id])
        label_id.append(cat_to_id[labels[i]])

    # 使用keras提供的pad_sequences来将文本pad为固定长度
    x_pad = kr.preprocessing.sequence.pad_sequences(data_id, max_length)
    y_pad = kr.utils.to_categorical(label_id, num_classes=len(cat_to_id))  # 将标签转换为one-hot表示

    return x_pad, y_pad


def batch_iter(x, y, batch_size=64):
    """生成批次数据"""
    data_len = len(x)
    num_batch = int((data_len - 1) / batch_size) + 1

    indices = np.random.permutation(np.arange(data_len))
    x_shuffle = x[indices]
    y_shuffle = y[indices]

    for i in range(num_batch):
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        yield x_shuffle[start_id:end_id], y_shuffle[start_id:end_id]

def batch_iter_2_x(x1, x2, y, batch_size=64):
    """生成批次数据"""
    data_len = len(x1)
    num_batch = int((data_len - 1) / batch_size) + 1

    indices = np.random.permutation(np.arange(data_len))
    x1_shuffle = x1[indices]
    x2_shuffle = x2[indices]
    y_shuffle = y[indices]

    for i in range(num_batch):
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        yield x1_shuffle[start_id:end_id], x2_shuffle[start_id:end_id], y_shuffle[start_id:end_id]


def loadWord2Vec(filename):
    """读取词向量"""
    vocab = []
    embd = []
    word_vector_map = {}
    file = open(filename,'r')
    for line in file.readlines():
        row = line.strip().split(' ')
        if(len(row) > 2):
            vocab.append(row[0])
            embd.append(row[1:])
            word_vector_map[row[0]] = row[1:]
    print('Loaded Word Vectors!')
    file.close()
    return vocab, embd, word_vector_map

def expand_abbr(txt):
    txt = re.sub(' a/w ', ' admitted with ', txt)
    txt = re.sub(' b/c ', ' because ', txt)
    txt = re.sub(' c/b ', ' complicated by ', txt)
    txt = re.sub(' c/o ', ' complains of ', txt)
    txt = re.sub(' c/w ', ' consistent with ', txt)
    txt = re.sub(' d/c ', ' discharge ', txt)
    txt = re.sub(' d/t ', ' due to ', txt)
    txt = re.sub(' f/u ', ' follow up ', txt)
    txt = re.sub(' h/o ', ' history of ', txt)
    txt = re.sub(' o/n ', ' overnight ', txt)
    txt = re.sub(' r/o ', ' rule out ', txt)
    txt = re.sub(' s/p ', ' status post ', txt)
    txt = re.sub(' t/c ', ' to consider ', txt)
    txt = re.sub(' w/ ', ' with ', txt)
    txt = re.sub(' w/o ', ' without ', txt)
    txt = re.sub(' w/out ', ' without ', txt)
    txt = re.sub(' w/u ', ' workup ', txt)
    return txt

def alphabet_pct(txt):
    tlen = len(txt) + 0.001 # prevent empty line exception
    alphabet = re.sub(r'[^A-Za-z\s.,;:()\[\]{}\-/+?]', "", txt)
    pct = len(alphabet) / tlen
    return pct

def txt_proc(txt, senb=False, alphabet_pct_thr=None):
    txt = re.sub(r'\[\*\*.*?\*\*\]', "", txt)
    txt = re.sub(r'([^\n])\n([^\nA-Z])', r'\1 \2', txt)
    if alphabet_pct_thr != None:
        txts = txt.split('\n')
        ftxts = []
        for txt in txts:
            if alphabet_pct(txt) > alphabet_pct_thr:
                ftxts.append(txt)
        txt = '\n'.join(ftxts) + '\n'
    txt = re.sub(r'(?i) \S*(year-old|y/o|yo|y\.o\.) ', ' ', txt)
    txt = expand_abbr(txt) # should disable this and try again with semrel todo
    txt = re.sub(r'(\S{3,})[/\-](\S{3,})', r'\1 \2', txt)
    
    if senb:
        txt = re.sub(r'\.(  |$)', r' .\n', txt) # sentence breaker
    #txt = re.sub(r'\.', "", txt) # p.o.
    txt = re.sub(r'[^A-Za-z0-9\s,.;:()\[\]{}\-/+?]', " ", txt)
    #txt = re.sub(r'\.$', '', txt) # include .
    txt = re.sub(r'([A-Za-z])([.,;:()\[\]{}\+?])', r'\1 \2', txt) # / - ignored for now
    txt = re.sub(r'([.,;:()\[\]{}\+?])([A-Za-z])', r'\1 \2', txt)
    # txt = re.sub(r'(\s|^)[0-9]+(\s|$)', r'\1\2', txt)
    txt = re.sub(' {2,}', ' ', txt)
    txt = re.sub('\n{2,}', '\n', txt)
    return txt.lower()

def mimicWEmCorp(fncsv, fn, textcn='text', sent_det=False, alphabet_pct_thr=None):
    if sent_det:
        sent_detector = nltk.data.load('/n/data1/hms/dbmi/zaklab/yluo/nltk_data/tokenizers/punkt/english.pickle')
    # write mimic word embedding corpus
    fcsv = open(fncsv, 'r')
    f = open(fn, 'w')
    reader = csv.reader(fcsv, delimiter=',', quotechar="\"")
    lc = 0
    for row in reader:
        if lc == 0:
            cols = row
            txtid = cols.index(textcn)
        else:
            if sent_det:
                txts = sent_detector.tokenize(row[txtid])
                for txt in txts:
                    txt = txt_proc(txt, alphabet_pct_thr=alphabet_pct_thr)
                    f.write('%s\n' % (txt.strip()))
            else:
                txt = row[txtid].lower()
                txt = txt_proc(txt, senb=True, alphabet_pct_thr=alphabet_pct_thr)
                f.write('%s\n' % (txt))
        lc += 1
    fcsv.close()
    f.close()
    return

def include_wd(wd):
    ans = re.search(r'[A-Za-z]', wd) != None or wd in '/:;()[]{}-+?'
    ans &= not 'year-old' in wd and 'y/o' != wd and 'yo' != wd and 'y.o.' != wd
    ans &= not '&' in wd and not '**' in wd
    ans &= re.search(r'[0-9]', wd) == None 
    ans &= re.search(r'^[^A-Za-z].+', wd) == None # cannot start with nonletter
    return ans;

def clean_wds(wdsin, hstop={}, strict=True):
    wdsout = []
    for wd in wdsin:
        if not strict or include_wd(wd):
            wd = re.sub('"', '', wd)
            wd = removeNonAscii(wd)
            if not wd in hstop: # if not hstop.has_key(wd):
                if strict and ('-' in wd and '-' != wd):
                    for swd in wd.split('-'):
                        if len(swd)>1:
                            wdsout.append(swd)
                else: 
                    if strict and len(wd)>1:
                        wd = re.sub('[^A-Za-z]*$', '', wd)
                    if len(wd)>0:
                        wdsout.append(wd)
    return wdsout;
    
def removeNonAscii(s): 
    """
    s should be a utf-8 encoded string
    """
    return "".join(i for i in s if ord(i)<128)

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


def if_has_YNQ(source, dis, doc):

    result = [0, 0, 0]
    #Q features
    f = open('data/'+source+'/questionable_truly_useful.log','r')
    content = f.read()
    f.close()
    lines = content.split('\n')

    for line in lines:
        doc_id = line[1: line.find(' ')].strip()
        disease = line[line.find(' ') + 1 : line.find('|')].strip()
        if disease == dis and doc_id == doc:
            result[0] = 1
            break

    #N features
    f = open('data/'+source+'/negated_truly_useful.log','r')
    content = f.read()
    f.close()
    lines = content.split('\n')

    for line in lines:
        doc_id = line[1: line.find(' ')].strip()
        disease = line[line.find(' ') + 1 : line.find('|')].strip()
        if disease == dis and doc_id == doc:
            result[1] = 1
            break
    
    #Y feature
    f = open('data/'+source+'/positive_useful.log','r')
    content = f.read()
    f.close()
    lines = content.split('\n')

    for line in lines:
        doc_id = line[1: line.find(' ')].strip()
        disease = line[line.find(' ') + 1 : line.find('|')].strip()
        if disease == dis and doc_id == doc:
            result[2] = 1
            break

    return result

def if_list_has_YNQ(source, dis, doc_list):

    
    #Q features
    f = open('perl_classifier/'+source+'/questionable_truly_useful.log','r')
    content = f.read()
    f.close()
    qlines = content.split('\n')

    #N features
    f = open('perl_classifier/'+source+'/negated_truly_useful.log','r')
    content = f.read()
    f.close()
    nlines = content.split('\n')

    #Y feature
    f = open('perl_classifier/'+source+'/positive_useful.log','r')
    content = f.read()
    f.close()
    plines = content.split('\n')

    result_list = []

    for doc in doc_list:
    
        result = [0, 0, 0]

        for line in qlines:
            doc_id = line[1: line.find(' ')].strip()
            disease = line[line.find(' ') + 1 : line.find('|')].strip()
            if disease == dis and doc_id == doc:
                result[0] = 1
                break

        for line in nlines:
            doc_id = line[1: line.find(' ')].strip()
            disease = line[line.find(' ') + 1 : line.find('|')].strip()
            if disease == dis and doc_id == doc:
                result[1] = 1
                break    

        for line in plines:
            doc_id = line[1: line.find(' ')].strip()
            disease = line[line.find(' ') + 1 : line.find('|')].strip()
            if disease == dis and doc_id == doc:
                result[2] = 1
                break
        result_list.append(result)
    return result_list