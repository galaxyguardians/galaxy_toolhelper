#!/usr/bin/env python

import sys

import networkx as nx
import numpy
import matplotlib.pyplot as plt
import h5py

infname = 'connected_data.hdf5'
infile = h5py.File(infname, 'r')
data = infile['tool_connections'][...]
tools = infile['tool_names'][...]
infile.close()
output = open('connected_data.csv','w')
for i in range(data.shape[0]):
	print >> output, "%s,%s,%i" % (tools[data[i, 0]], tools[data[i, 1]], data[i, 2])
output.close()