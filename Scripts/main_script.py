#!/usr/bin/env python
import numpy
import h5py
import sys


def csv2hdf5(infname, outfname):
    """
    Convert main tool_connection.csv file to hdf5 file
    """
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
    # output = h5py.File('filtered_data.hdf5', 'w')
    output = h5py.File(outfname, 'w')
    output.create_dataset(name='dataset_connections', data=data)
    tool_names = []
    for i in range(len(tools)):
        tool_names.append('')
    for name, i in tools.iteritems():
        tool_names[i] = name
    tool_names = numpy.array(tool_names)
    output.create_dataset(name='tool_names', data=tool_names)
    output.close()
    return


def parse_dataset_chains(in_fname, out_fname):
    """
    Parse tool_connection hdf5 file and get categories for tools
    """
    # in_fname, out_fname = sys.argv[1:3]
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
    return


if __name__ == '__main__':
    csv2hdf5('tool_connections_uniq.csv', 'filtered_data_uniq.hdf5')
    parse_dataset_chains('filtered_data_uniq.hdf5','chain_categories_uniq.hdf5')
