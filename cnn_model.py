# coding: utf-8

import tensorflow as tf
import numpy as np
from sklearn import metrics

class TCNNConfig(object):
    """CNN配置参数"""

    embedding_dim = 200  # 词向量维度
    seq_length = 15  # 序列长度
    num_classes = 4  # 类别数
    num_filters = 256  # 卷积核数目
    kernel_size = 5  # 卷积核尺寸
    vocab_size = 10000  # 词汇表大小

    hidden_dim = 128  # 全连接层神经元

    dropout_keep_prob = 0.8  # dropout保留比例
    learning_rate = 1e-3  # 学习率

    batch_size = 64  # 每批训练大小
    num_epochs = 20  # 总迭代轮次

    print_per_batch = 100  # 每多少轮输出一次结果
    save_per_batch = 10  # 每多少轮存入tensorboard


class TextCNN(object):
    """文本分类，CNN模型"""

    def __init__(self, config):
        self.config = config

        # 三个待输入的数据
        self.input_x = tf.placeholder(tf.int32, [None, self.config.seq_length], name='input_x')
        self.input_y = tf.placeholder(tf.float32, [None, self.config.num_classes], name='input_y')
        self.embeddings_matrix = tf.placeholder(tf.float32, [None, self.config.embedding_dim], name='embedding_matrix')
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob')

        self.cnn()

    def cnn(self):
        """CNN模型"""
        # 词向量映射
        with tf.device('/cpu:0'):
            self.W = tf.Variable(
                tf.random_uniform([self.config.vocab_size, self.config.embedding_dim], -1.0, 1.0),
                name="W")
            #embedding = tf.get_variable('embedding', [self.config.vocab_size, self.config.embedding_dim])
            #embedding = tf.get_variable("embedding", shape=[self.config.vocab_size, self.config.embedding_dim], initializer=tf.constant_initializer(self.embeddings_matrix))
            embedding_inputs = tf.nn.embedding_lookup(self.W, self.input_x)

        with tf.name_scope("cnn"):
            # CNN layer
            #attention = tf.nn.softmax(embedding_inputs)
            #conv = tf.layers.conv1d(attention, self.config.num_filters, self.config.kernel_size, name='conv')

            conv = tf.layers.conv1d(embedding_inputs, self.config.num_filters, self.config.kernel_size, name='conv')
            
            #onv1 = tf.layers.conv1d(embedding_inputs, self.config.num_filters, 3, name='conv1')
            #conv2 = tf.layers.conv1d(embedding_inputs, self.config.num_filters, 3, name='conv2')
            #conv3 = tf.layers.conv1d(embedding_inputs, self.config.num_filters, 3, name='conv3')

            # global max pooling layer
            gmp = tf.reduce_max(conv, reduction_indices=[1], name='gmp')

        with tf.name_scope("score"):
            # 全连接层，后面接dropout以及relu激活
            fc = tf.layers.dense(gmp, self.config.hidden_dim, name='fc1')
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
        #with tf.name_scope("fscore"):
            # macro_f score
            #y_true = np.argmax(self.input_y, 1)
            #y_pred = np.argmax(tf.nn.softmax(self.logits), 1)
            #self.fscore = metrics.f1_score(y_true, y_pred,  average='macro')
            #y_true = tf.argmax(self.input_y, 1)
            #precision, update_op = tf.metrics.streaming_precision(y_true, self.y_pred_cls)
            #recall = tf.metrics.recall(y_true, self.y_pred_cls)
            #for i in range(0, len(precision)):
            #scores = tf.cast(precision, tf.float32)
            #print(scores.shape)
            #self.fscore = tf.reduce_mean(tf.cast(precision, tf.float32))

            #self.fscore = 2 * precision * recall/(precision + recall)
            
            #y_true = tf.argmax(self.input_y, 1)
            #cm = metrics.confusion_matrix(y_true,self.y_pred_cls)
