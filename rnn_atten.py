#!/usr/bin/python
# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
from tensorflow.contrib.rnn import GRUCell
from tensorflow.python.ops.rnn import bidirectional_dynamic_rnn as bi_rnn

class TRNNConfig(object):
    """RNN配置参数"""

    # 模型参数
    embedding_dim = 100      # 词向量维度
    seq_length = 77        # 序列长度
    num_classes = 4        # 类别数
    vocab_size = 10000      # 词汇表大小

    num_layers= 2           # 隐藏层层数
    hidden_dim = 150        # 隐藏层神经元
    rnn = 'lstm'             # lstm 或 gru
    attention_size = 50

    dropout_keep_prob = 0.8 # dropout保留比例
    learning_rate = 1e-3    # 学习率

    batch_size = 64         # 每批训练大小
    num_epochs = 30          # 总迭代轮次

    print_per_batch = 100    # 每多少轮输出一次结果
    save_per_batch = 10      # 每多少轮存入tensorboard


class TextRNN(object):
    """文本分类，RNN模型"""
    def __init__(self, config, word_embedding):
        self.config = config
        self.word_embedding = word_embedding

        # 三个待输入的数据
        self.input_x = tf.placeholder(tf.int32, [None, self.config.seq_length], name='input_x')
        self.input_y = tf.placeholder(tf.float32, [None, self.config.num_classes], name='input_y')
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob')
        #self.seq_len_vector = tf.placeholder(tf.int32, [None], name='seq_len_vector')

        self.rnn()

    def rnn(self):
        """rnn模型"""

        # 词向量映射
        with tf.device('/cpu:0'):
            embedding = tf.get_variable('embedding', initializer = self.word_embedding)
            embedding_inputs = tf.nn.embedding_lookup(embedding, self.input_x)
            embedding_inputs = tf.cast(embedding_inputs,tf.float32)
        with tf.name_scope("rnn"):
            # 多层rnn网络
            #cells = [dropout() for _ in range(self.config.num_layers)]
            #rnn_cell = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)
            #_outputs, _ = tf.nn.dynamic_rnn(cell=rnn_cell, inputs=embedding_inputs, dtype=tf.float32)
            #last = _outputs[:, -1, :]  # 取最后一个时序输出作为结果
            
            # (Bi-)RNN layer(-s)
            rnn_outputs, _ = bi_rnn(GRUCell(self.config.hidden_dim), GRUCell(self.config.hidden_dim),
                        inputs=embedding_inputs, dtype=tf.float32)
            #tf.summary.histogram('RNN_outputs', rnn_outputs)
        # Attention layer
        with tf.name_scope('Attention_layer'):
            attention_output, alphas = attention(rnn_outputs, self.config.attention_size, 
                    return_alphas=True)
            tf.summary.histogram('alphas', alphas)
            # Dropout
            drop = tf.nn.dropout(attention_output, self.keep_prob)


        with tf.name_scope("score"):
            # 全连接层，后面接dropout以及relu激活
            W = tf.Variable(tf.truncated_normal([self.config.hidden_dim * 2, self.config.num_classes], stddev=0.1))  # Hidden size is multiplied by 2 for Bi-RNN
            b = tf.Variable(tf.constant(0., shape=[self.config.num_classes]))
            self.logits = tf.nn.xw_plus_b(drop, W, b)
            #fc = tf.contrib.layers.dropout(fc, self.keep_prob)
            #fc = tf.nn.relu(fc)

            # 分类器
            #self.logits = tf.layers.dense(fc, self.config.num_classes, name='fc2')
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


def attention(inputs, attention_size, time_major=False, return_alphas=False):
    """
    Attention mechanism layer which reduces RNN/Bi-RNN outputs with Attention vector.

    The idea was proposed in the article by Z. Yang et al., "Hierarchical Attention Networks
     for Document Classification", 2016: http://www.aclweb.org/anthology/N16-1174.
    Variables notation is also inherited from the article
    
    Args:
        inputs: The Attention inputs.
            Matches outputs of RNN/Bi-RNN layer (not final state):
                In case of RNN, this must be RNN outputs `Tensor`:
                    If time_major == False (default), this must be a tensor of shape:
                        `[batch_size, max_time, cell.output_size]`.
                    If time_major == True, this must be a tensor of shape:
                        `[max_time, batch_size, cell.output_size]`.
                In case of Bidirectional RNN, this must be a tuple (outputs_fw, outputs_bw) containing the forward and
                the backward RNN outputs `Tensor`.
                    If time_major == False (default),
                        outputs_fw is a `Tensor` shaped:
                        `[batch_size, max_time, cell_fw.output_size]`
                        and outputs_bw is a `Tensor` shaped:
                        `[batch_size, max_time, cell_bw.output_size]`.
                    If time_major == True,
                        outputs_fw is a `Tensor` shaped:
                        `[max_time, batch_size, cell_fw.output_size]`
                        and outputs_bw is a `Tensor` shaped:
                        `[max_time, batch_size, cell_bw.output_size]`.
        attention_size: Linear size of the Attention weights.
        time_major: The shape format of the `inputs` Tensors.
            If true, these `Tensors` must be shaped `[max_time, batch_size, depth]`.
            If false, these `Tensors` must be shaped `[batch_size, max_time, depth]`.
            Using `time_major = True` is a bit more efficient because it avoids
            transposes at the beginning and end of the RNN calculation.  However,
            most TensorFlow data is batch-major, so by default this function
            accepts input and emits output in batch-major form.
        return_alphas: Whether to return attention coefficients variable along with layer's output.
            Used for visualization purpose.
    Returns:
        The Attention output `Tensor`.
        In case of RNN, this will be a `Tensor` shaped:
            `[batch_size, cell.output_size]`.
        In case of Bidirectional RNN, this will be a `Tensor` shaped:
            `[batch_size, cell_fw.output_size + cell_bw.output_size]`.
    """

    if isinstance(inputs, tuple):
        # In case of Bi-RNN, concatenate the forward and the backward RNN outputs.
        inputs = tf.concat(inputs, 2)

    if time_major:
        # (T,B,D) => (B,T,D)
        inputs = tf.array_ops.transpose(inputs, [1, 0, 2])

    hidden_size = inputs.shape[2].value  # D value - hidden size of the RNN layer

    # Trainable parameters
    w_omega = tf.Variable(tf.random_normal([hidden_size, attention_size], stddev=0.1))
    b_omega = tf.Variable(tf.random_normal([attention_size], stddev=0.1))
    u_omega = tf.Variable(tf.random_normal([attention_size], stddev=0.1))

    with tf.name_scope('v'):
        # Applying fully connected layer with non-linear activation to each of the B*T timestamps;
        #  the shape of `v` is (B,T,D)*(D,A)=(B,T,A), where A=attention_size
        v = tf.tanh(tf.tensordot(inputs, w_omega, axes=1) + b_omega)

    # For each of the timestamps its vector of size A from `v` is reduced with `u` vector
    vu = tf.tensordot(v, u_omega, axes=1, name='vu')  # (B,T) shape
    alphas = tf.nn.softmax(vu, name='alphas')         # (B,T) shape

    # Output of (Bi-)RNN is reduced with attention vector; the result has (B,D) shape
    output = tf.reduce_sum(inputs * tf.expand_dims(alphas, -1), 1)

    if not return_alphas:
        return output
    else:
        return output, alphas