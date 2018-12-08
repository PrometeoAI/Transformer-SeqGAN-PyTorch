# -*- coding: utf-8 -*-

import os
import random
import sys
# sys.path.insert(0, './transformer')
import transformer
import copy
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from data_iter import GenDataIter

class Generator(nn.Module):
    """Generator """
    def __init__(self, num_emb, emb_dim, hidden_dim, seq_len, batch_size, use_cuda):
        super(Generator, self).__init__()
        # Constants Initialization
        self.SOS_Index = 0
        self.EOS_Index = 1
        self.PAD_Index = 2
        
        # Embeddings
        self.emb = nn.Embedding(num_emb, emb_dim)
        self.model = transformer.Transformer(
            self.emb,
            self.PAD_Index,
            self.emb.num_embeddings,
            max_seq_len = max(seq_len, seq_len)
        )
        self.data_loader = GenDataIter('real.data', batch_size)
        self.data_loader.reset()
        """
        self.num_emb = num_emb
        self.emb_dim = emb_dim
        self.hidden_dim = hidden_dim
        self.use_cuda = use_cuda
        self.emb = nn.Embedding(num_emb, emb_dim)
        self.lstm = nn.LSTM(emb_dim, hidden_dim, batch_first=True)
        self.lin = nn.Linear(hidden_dim, num_emb)
        self.softmax = nn.LogSoftmax()
        self.init_params()
        """
    def forward(self, x):
        """
        Args:
            x: (batch_size, seq_len), sequence of tokens generated by generator
        """
        return self.model(x, x)
        """
        emb = self.emb(x)
        h0, c0 = self.init_hidden(x.size(0))
        output, (h, c) = self.lstm(emb, (h0, c0))
        pred = self.softmax(self.lin(output.contiguous().view(-1, self.hidden_dim)))
        return pred
        """

    def step(self, x, h, c):
        """
        Args:
            x: (batch_size,  1), sequence of tokens generated by generator
            h: (1, batch_size, hidden_dim), lstm hidden state
            c: (1, batch_size, hidden_dim), lstm cell state
        """
        emb = self.emb(x)
        output, (h, c) = self.lstm(emb, (h, c))
        pred = F.softmax(self.lin(output.view(-1, self.hidden_dim)))
        return pred, h, c


    def init_hidden(self, batch_size):
        h = Variable(torch.zeros((1, batch_size, self.hidden_dim)))
        c = Variable(torch.zeros((1, batch_size, self.hidden_dim)))
        if self.use_cuda:
            h, c = h.cuda(), c.cuda()
        return h, c
    
    def init_params(self):
        for param in self.parameters():
            param.data.uniform_(-0.05, 0.05)

    def sample(self, batch_size, seq_len, x=None):
        if self.data_loader.idx >= self.data_loader.data_num:
            self.data_loader.reset()
        input_seq = self.data_loader.next()[0]
        input_seq = input_seq.cuda()
        sampled_output = transformer.sample_output(self.model, input_seq, self.EOS_Index, self.PAD_Index, input_seq.shape[1])
        return sampled_output
        """
        res = []
        flag = False # whether sample from zero
        if x is None:
            flag = True
        if flag:
            x = Variable(torch.zeros((batch_size, 1)).long())
        if self.use_cuda:
            x = x.cuda()
        h, c = self.init_hidden(batch_size)
        samples = []
        if flag:
            for i in range(seq_len):
                output, h, c = self.step(x, h, c)
                x = output.multinomial(1)
                samples.append(x)
        else:
            given_len = x.size(1)
            lis = x.chunk(x.size(1), dim=1)
            for i in range(given_len):
                output, h, c = self.step(lis[i], h, c)
                samples.append(lis[i])
            x = output.multinomial(1)
            for i in range(given_len, seq_len):
                samples.append(x)
                output, h, c = self.step(x, h, c)
                x = output.multinomial(1)
        output = torch.cat(samples, dim=1)
        return output
        """