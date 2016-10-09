# Author: xiaotaw@qq.com (Any bug report is welcome)
# Time: Aug 2016
# Addr: Shenzhen
# Description: define functions and parameters related to input data


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy
import cPickle
import random # for random.shuffle()

import tensorflow as tf


data_dir = "data_files"
mgfp_dir = "mgfp_files" 

record_bytes = 2048


def dense_to_one_hot(labels_dense, num_classes=2, dtype=numpy.int):
  """Convert class labels from scalars to one-hot vectors.
  """
  num_labels = labels_dense.shape[0]
  index_offset = numpy.arange(num_labels) * num_classes
  labels_one_hot = numpy.zeros((num_labels, num_classes))
  labels_one_hot.flat[index_offset + labels_dense.ravel().astype(dtype)] = 1
  # print(labels_one_hot)
  return labels_one_hot


class DataSet(object):
  """dataset class, contains compds and labels, 
     and also provides method to generate a next batch of data. 
  """
  def __init__(self, compds, labels, to_one_hot=True, dtype=numpy.float32, norm=False):
    assert compds.shape[0] == labels.shape[0], "shape don't match"
    self.compds = compds.astype(dtype)
    if to_one_hot:
      self.labels = dense_to_one_hot(labels)
    else:
      self.labels = labels
    self.size = compds.shape[0]
    self.begin = 0
    self.end = 0
    if norm:
      self.normalize()

  def generate_batch(self, batch_size):
    assert self.compds.shape[0] == self.labels.shape[0], "shape don't match"
    assert batch_size <= self.size, "too big batch_size"
    self.end = self.begin + batch_size
    if self.end > self.size:
      self.shuffle()
      self.begin = 0
      self.end = batch_size
    compds_batch = self.compds[self.begin: self.end]
    labels_batch = self.labels[self.begin: self.end]
    self.begin = self.end
    return compds_batch, labels_batch
  
  def shuffle(self):
    perm = range(self.size)
    random.shuffle(perm)
    self.compds = self.compds[perm]
    self.labels = self.labels[perm]

  def normalize(self):
    self.compds = self.compds / self.compds.max(axis=1).reshape([self.compds.shape[0],1])
      

def dense_to_one_hot(labels_dense, num_classes=2, dtype=numpy.int):
  """Convert class labels from scalars to one-hot vectors.
  """
  num_labels = labels_dense.shape[0]
  index_offset = numpy.arange(num_labels) * num_classes
  labels_one_hot = numpy.zeros((num_labels, num_classes))
  labels_one_hot.flat[index_offset + labels_dense.ravel().astype(dtype)] = 1
  # print(labels_one_hot)
  return labels_one_hot

def get_inputs_by_cpickle(pkl_filename, clip=True):
  """read dataset from file according to target name
     note: target.pkl are 2048 length mgfp code files, which were generated by 'cPickle.dump'.
  Args:
    target: a string of the protein kinase target name
  """
  with open(pkl_filename, "rb") as pkl_file:
    data = cPickle.load(pkl_file)
    if clip:
      numpy.clip(data, 0, 1, out=data)
      return DataSet(data[:, 1:], data[:, :1], to_one_hot=True)
    else:
      return DataSet(data[:, 1:], data[:, :1], to_one_hot=True, norm=True)
    

""" not used 
def get_compds_by_filequeue(batch_size):
  """"""
  target_list = ["cdk2", "egfr_erbB1", "gsk3b", "hgfr", "map_k_p38a", 
                 "tpk_lck", "tpk_src", "vegfr2", "pubchem_neg_sample"]
  reader = tf.FixedLengthRecordReader(record_bytes=record_bytes)
  fq = {}
  value = {}
  records = {}
  for t in target_list:
    fq[t] = tf.train.string_input_producer(["data_files/" + t + ".bin"])
    _, value[t] = reader.read(fq[t])
    records[t] = tf.decode_raw(value[t], tf.uint8)

  compds = tf.train.batch(records, batch_size=batch_size, num_threads=1, capacity=1000 + 3 * batch_size, shapes=[(2048,)] * len(records))

  return compds
"""

