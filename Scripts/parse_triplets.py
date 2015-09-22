#!/usr/bin/env python

import sys

import numpy
import h5py


def main():
    in_fname, cat_fname, out_fname = sys.argv[1:4]
    infile = h5py.File(in_fname, 'r')
    keys = infile.keys()
    temp = h5py.File(cat_fname, 'r')
    cat_names = temp['categories'][...]
    temp1 = temp['chain_categories'][...]
    temp.close()
    chain_cats = {}
    for i in range(temp1.shape[0]):
        line = numpy.array(list(temp1[i])[1:], dtype=numpy.float)
        maxv = numpy.amax(line)
        if maxv >= 0.7:
            chain_cats[temp1['name'][i]] = numpy.where(line == maxv)[0][0] - 1
    triplets = []
    for i in range(len(cat_names)):
        triplets.append({})
    for key in keys:
        if key[0] == 't':
            continue
        if key not in chain_cats:
            continue
        h = chain_cats[key]
        data = infile[key][...]
        index = numpy.r_[0, numpy.bincount(data[:, 0])]
        for i in range(1, index.shape[0]):
            index[i] += index[0]
        for i in range(data.shape[0]):
            find_triplet(triplets[h], data, index, i, True, data[i, 2])
    infile.close()
    for i in range(len(cat_names)):
        output = open("%s.txt" % cat_names.replace(' ','_').replace('-','_'), 'w')
        output.write(str(triplets[i]))
        output.close()

def find_triplet(triplets, data, index, i, first, key):
    if data[i, 1] >= index.shape[0] - 1:
        return None
    if first:
        for j in range(index[data[i, 1]], index[data[i, 1] + 1]):
            new_key = (key, data[j, 2])
            if new_key not in triplets:
                triplets[new_key] = {}
            find_triplet(triplets, data, index, j, False, new_key)
    else:
        for j in range(index[data[i, 1]], index[data[i, 1] + 1]):
            if data[j, 2] not in triplets[key]:
                triplets[key][data[j, 2]] = 0
            triplets[key][data[j, 2]] += 1
    return None

if __name__ == "__main__":
    main()