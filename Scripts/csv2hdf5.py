#!/usr/bin/env python

import sys

import networkx as nx
import numpy
import matplotlib.pyplot as plt
import h5py

infname = 'tool_connections.csv'
data = []
tools = {}
for line in open(infname):
    temp = line[:-1].split(',')
    temp1 = temp[2].split('/')
    if len(temp1) == 1:
    	tool = temp1[0]
    else:
    	tool = temp1[-2]
    if tool not in tools:
        tools[tool] = len(tools)
    data.append([int(temp[0]), int(temp[1]), tools[tool]])
data = numpy.array(data, dtype=numpy.int32)
intersection = numpy.intersect1d(data[:, 0], data[:, 1])
mapping = numpy.zeros(max(numpy.amax(data[:, 0]), numpy.amax(data[:, 1])) + 1, dtype=numpy.int32)
mapping[intersection] = 1
data = data[numpy.where(mapping[data[:, 0]] + mapping[data[:, 1]])[0], :]
output = h5py.File('filtered_data.hdf5', 'w')
output.create_dataset(name='dataset_connections', data=data)
tool_names = []
for i in range(len(tools)):
    tool_names.append('')
for name, i in tools.iteritems():
    tool_names[i] = name
tool_names = numpy.array(tool_names)
output.create_dataset(name='tool_names', data=tool_names)
output.close()
