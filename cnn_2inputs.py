# coding: utf-8

import tensorflow as tf
import numpy as np
from sklearn import metrics

class TCNNConfig(object):
    """CNN配置参数"""

    embedding_dim = 200  # 词向量维度
    word_seq_length = 15  # 词序列长度
    entity_seq_length = 356  # 实体序列长度
    num_classes = 4  # 类别数
    num_filters = 256  # 卷积核数目
    kernel_size = 5  # 卷积核尺寸
    vocab_size = 10000  # 词汇表大小
    entity_vocab_size = 10000  # 实体词汇表大小 

    hidden_dim = 128  # 全连接层神经元

    dropout_keep_prob = 0.8  # dropout保留比例
    learning_rate = 1e-3  # 学习率

    batch_size = 64  # 每批训练大小
    num_epochs = 30  # 总迭代轮次

    print_per_batch = 100  # 每多少轮输出一次结果
    save_per_batch = 10  # 每多少轮存入tensorboard


class TextCNN(object):
    """文本分类，CNN模型"""

    def __init__(self, config, word_vectors, entity_vectors):
        self.config = config
        self.word_vectors = word_vectors
        self.entity_vectors = entity_vectors
        # 待输入的数据
        self.input_words = tf.placeholder(tf.int32, [None, self.config.word_seq_length], name='input_words')
        self.input_entities = tf.placeholder(tf.int32, [None, self.config.entity_seq_length], name='input_entities')

        self.input_y = tf.placeholder(tf.float32, [None, self.config.num_classes], name='input_y')
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob')

        self.cnn()

    def cnn(self):
        """CNN模型"""
        # 词向量映射
        with tf.device('/cpu:0'):
            word_embedding = tf.Variable(self.word_vectors, name='word_vectors', dtype= tf.float32)
            entity_embedding = tf.Variable(self.entity_vectors, name='entity_vectors', dtype= tf.float32)

            embedding_input_words = tf.nn.embedding_lookup(word_embedding, self.input_words)
            embedding_input_entities = tf.nn.embedding_lookup(entity_embedding, self.input_entities)

        with tf.name_scope("cnn"):

            conv1 = tf.layers.conv1d(embedding_input_words, self.config.num_filters, self.config.kernel_size, name='conv1')

            # global max pooling layer
            self.gmp1 = tf.reduce_max(conv1, reduction_indices=[1], name='gmp1')

            conv2 = tf.layers.conv1d(embedding_input_entities, self.config.num_filters, self.config.kernel_size, name='conv2')

            self.gmp2 = tf.reduce_max(conv2, reduction_indices=[1], name='gmp2')

            self.gmp = tf.concat([self.gmp1, self.gmp2], 1, name= 'gmp')
            

        with tf.name_scope("score"):
            # 全连接层，后面接dropout以及relu激活
            fc = tf.layers.dense(self.gmp, self.config.hidden_dim, name='fc1')
            fc = tf.contrib.layers.dropout(fc, self.keep_prob)
            fc = tf.nn.relu(fc)

            # 分类器
            self.logits = tf.layers.dense(fc, self.config.num_classes, name='fc2')
            self.y_pred_cls = tf.argmax(tf.nn.softmax(self.logits), 1)  # 预测类别

        with tf.name_scope("optimize"):
            # 损失函数，交叉熵
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=self.logits, labels=self.input_y)
            self.loss = tf.reduce_mean(cross_entropy)
            # 优化器
            self.optim = tf.train.AdamOptimizer(learning_rate=self.config.learning_rate).minimize(self.loss)

        with tf.name_scope("accuracy"):
            # 准确率
            correct_pred = tf.equal(tf.argmax(self.input_y, 1), self.y_pred_cls)
            self.acc = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
