#!/usr/bin/env python

import sys

import numpy
import h5py

def main():
    in_fname, out_fname = sys.argv[1:3]
    infile = h5py.File(in_fname, 'r')
    dataset = {}
    chain = {}
    data = infile['dataset_connections'][...]
    for i in range(data.shape[0]):
        if data[i, 0] >= data[i, 1]:
            continue
        if data[i, 0] in dataset:
            c = dataset[data[i, 0]]
            cc = chain[c]
            while isinstance(cc, int):
                c = cc
                cc = chain[c]
            if data[i, 1] in dataset:
                d = dataset[data[i, 1]]
                dc = chain[d]
                while isinstance(dc, int):
                    d = dc
                    dc = chain[d]
                if d != c:
                    chain[c] += dc
                    chain[d] = c
            dataset[data[i, 1]] = c
            dataset[data[i, 0]] = c
        else:
            c = len(chain)
            dataset[data[i, 0]] = c
            dataset[data[i, 1]] = c
            chain[c] = []
        chain[c].append(data[i, :])
    outfile = h5py.File(out_fname, 'w')
    i = 0
    for c, value in chain.iteritems():
        if isinstance(value, int):
            continue
        value = numpy.array(value, dtype=numpy.int32)
        order = numpy.lexsort((value[:, 2], value[:, 1], value[:, 0]))
        value = value[order, :]
        outfile.create_dataset(name='chain_%07i' % i, data=value)
        i += 1
    outfile.create_dataset(name='tool_names', data=infile['tool_names'][...])
    outfile.close()
    infile.close()

if __name__ == "__main__":
    main()
