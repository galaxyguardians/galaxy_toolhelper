#!/usr/bin/env python

import sys

import numpy
import h5py


def main():
    in_fname, out_fname = sys.argv[1:3]
    infile = h5py.File(in_fname, 'r')
    mapping = numpy.zeros(20000000, dtype=numpy.int32)
    outfile = h5py.File(out_fname, 'w')
    outfile.create_dataset(name='tool_names', data=infile['tool_names'])
    for key in infile.keys():
        if key[0] == 't':
            continue
        if infile[key].shape[0] == 1:
            continue
        data = infile[key][...]
        unique = numpy.union1d(data[:, 0], data[:, 1])
        if unique[-1] >= mapping.shape[0]:
            mapping = numpy.zeros(unique[-1] + 10, dtype=numpy.int32)
        mapping[unique] = numpy.arange(unique.shape[0])
        data[:, 0] = mapping[data[:, 0]]
        data[:, 1] = mapping[data[:, 1]]
        count = numpy.bincount(data[:, 0])
        if numpy.sum(count > 0) == 1:
            continue
        outfile.create_dataset(name=key, data=data)
    infile.close()
    outfile.close()

if __name__ == "__main__":
    main()
