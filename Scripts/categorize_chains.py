#!/usr/bin/env python

import sys

import h5py
import numpy


def main():
    cat_fname, chain_fname, out_fname = sys.argv[1:4]
    temp = open(cat_fname)
    categories = eval(temp.read())
    cat_names = categories.keys()
    cat_names.sort()
    temp.close()
    infile = h5py.File(chain_fname, 'r')
    tool2index = {}
    tool_names = infile['tool_names'][...]
    for i in range(tool_names.shape[0]):
        tool2index[tool_names[i]] = i
    tools = numpy.zeros((tool_names.shape[0], len(categories)), dtype=numpy.int32)
    i = 0
    for key in cat_names:
        toollist = categories[key]
        for tool in toollist:
            for tool2 in tool_names:
                if tool2.count(tool) > 0:
                    tools[tool2index[tool2], i] = 1
        i += 1
    cats = []
    for key in infile.keys():
        if key[0] == 't':
            continue
        data = infile[key][...]
        temp = numpy.sum(tools[data[:, 2], :], axis=0)
        if numpy.sum(temp) > 0:
            cats.append(tuple([key] + list(temp)))
    infile.close()
    dtype = [('name','S13')]
    for key in cat_names:
        dtype.append((key, numpy.int32))
    cats = numpy.array(cats, dtype=dtype)
    cat_names = numpy.array(cat_names)
    outfile = h5py.File('%s.hdf5' % out_fname, 'w')
    outfile.create_dataset(name='chain_categories', data=cats)
    outfile.create_dataset(name='categories', data=cat_names)
    outfile.close()
    outfile = open('%s.txt' % out_fname, 'w')
    print >> outfile, '\t'.join(['name'] + list(cat_names))
    for i in range(cats.shape[0]):
        temp = list(cats[i])
        for j in range(len(temp)):
            temp[j] = str(temp[j])
        print >> outfile, '\t'.join(temp)
    outfile.close()

if __name__ == "__main__":
    main()
