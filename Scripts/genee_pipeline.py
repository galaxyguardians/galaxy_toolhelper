#!/usr/bin/env python

import sys
import json

import numpy


def main():
    in_fname, chains_fname, triplets_fname = sys.argv[1:4]
    data, tool_names = load_csv(in_fname)
    tool_chains = parse_dataset(data)
    #write_tool_chains(tool_chains, tool_names, chains_fname)
    triplets = parse_chains(tool_chains, tool_names)
    write_triplets(triplets, triplets_fname)

def load_csv(fname):
    """Read in the csv data file into a numpy array"""
    data = []
    tools = {}
    tool_names = []
    version_stripper = {}
    line_num = 0
    print >> sys.stderr, ("\n"),
    for line in open(fname):
        print >> sys.stderr, ("\rReading line: %i") % (line_num),
        line_num += 1
        # parse file line
        dataset1, dataset2, tool = line.rstrip('\n').split(',')[:3]
        # check if our tool has been stripped of version before
        if tool not in version_stripper:
            tool_split = tool.split('/')
            if len(tool_split) > 1:
                stripped = '/'.join(tool_split[:-1])
            else:
                stripped = tool
            version_stripper[tool] = stripped
            # check if tool exists in our tool list yet. If not, add it
            if stripped not in tools:
                tools[stripped] = len(tools)
                tool_names.append(stripped)
        # add datasets and tool index to data
        data.append([int(dataset1), int(dataset2), tools[version_stripper[tool]]])
    data = numpy.array(data, dtype=numpy.int32)
    print >> sys.stderr, ("\rFinished reading csv file\n"),
    return [data, tool_names]

def parse_dataset(data):
    """Parse the data array into tool chains"""
    dataset = {}
    chains = {}
    # for each dataset-tool-dataset connection, see if either dataset appears in our dataset group dict
    for i in range(data.shape[0]):
        print >> sys.stderr, ("\rParsing dataset line: %08i of %08i") % (i, data.shape[0]),
        # tools should eonly produce datasets of a higher value than their input
        if data[i, 0] >= data[i, 1]:
            continue
        chain_number1 = None
        chain_number2 = None
        # if dataset has previously been seen, assign this connection to the same chain
        if data[i, 0] in dataset:
            chain_number1 = dataset[data[i, 0]]
            chain_list1 = chains[chain_number1]
            # if this chain has been collapsed with another chain, we need to follow it to the main chain
            while isinstance(chain_list1, int):
                chain_number1 = chain_list1
                chain_list1 = chains[chain_number1]
        # see if the second dataset has been observed yet
        if data[i, 1] in dataset:
            chain_number2 = dataset[data[i, 1]]
            chain_list2 = chains[chain_number2]
            # if the second dataset has been seen before and its chain has been collapsed with another chain,
            # we need to follow it to the main chain
            while isinstance(chain_list2, int):
                chain_number2 = chain_list2
                chain_list2 = chains[chain_number2]
            # check if both datasets already have chains
            if chain_number1 is not None:
                # check if they belong to different chains. If so, collapse these chains into one
                if chain_number1 != chain_number2:
                    chains[chain_number1] += chain_list2
                    chains[chain_number2] = chain_number1
                chain_number = chain_number1
            else:
            # if only the second dataset was observed, use its chain
                chain_number = chain_number2
        elif chain_number1 is not None:
            # if only the first dataset was observed, use its chain
            chain_number = chain_number1
        else:
            # neither dataset has been observed before, start a new chain
            chain_number = len(chains)
            chains[chain_number] = []
        # mark which chain each dataset is associated with
        dataset[data[i, 1]] = chain_number
        dataset[data[i, 0]] = chain_number
        chains[chain_number].append(data[i, :])
    # create a temporary array for remapping dataset IDs
    mapping = numpy.zeros(numpy.amax(data[:, :2] + 1), dtype=numpy.int32)
    # for each chain, removed placeholders, sort, renumber datasets, and remove duplicate entries
    filtered_chains = []
    line_num = 0
    total = len(chains)
    print >> sys.stderr, ("\r%s\r") % (' ' * 80),
    for chain, entries in chains.iteritems():
        print >> sys.stderr, ("\rCleaning chain: %06i of %06i") % (line_num, total),
        line_num += 1
        # remove placeholders
        if isinstance(entries, int):
            continue
        # create numpy array
        entries = numpy.array(entries, dtype=numpy.int32)
        # sort in order or first and then second dataset
        order = numpy.lexsort((entries[:, 1], entries[:, 1]))
        entries = entries[order, :]
        # remove duplicate entries
        unique = numpy.where(1 -
            numpy.equal(entries[:-1, 0], entries[1:, 0]) *
            numpy.equal(entries[:-1, 1], entries[1:, 1]) *
            numpy.equal(entries[:-1, 2], entries[1:, 2]))[0]
        entries = numpy.vstack((entries[unique, :], entries[-1, :].reshape(1, -1)))
        # renumber datasets
        dataset_ids = numpy.union1d(entries[:, 0], entries[:, 1])
        mapping[dataset_ids] = numpy.arange(dataset_ids.shape[0])
        entries[:, 0] = mapping[entries[:, 0]]
        entries[:, 1] = mapping[entries[:, 1]]
        filtered_chains.append(entries)
    print >> sys.stderr, ("\rFinished parsing dataset into chains               \n"),
    return filtered_chains

def parse_chains(data, tool_names):
    """Parse tool chains to find tool triplets"""
    triplets = {}
    count = 0
    total = len(data)
    for chain in data:
        print >> sys.stderr, ("\rParsing chain %06i of %06i") % (count, total),
        count += 1
        # create a dataset index array for first column of chain
        index = numpy.r_[0, numpy.bincount(chain[:, 0])]
        for i in range(1, index.shape[0]):
            index[i] += index[i - 1]
        # for each entry in the chain, follow it forward 2 steps if possible to determine tool triplets
        for i in range(chain.shape[0]):
            find_triplet(triplets, chain, index, i, True, chain[i, 2])
    # filter out empty entries and convert counts into percentages
    filtered_triplets = {}
    for triplet, values in triplets.iteritems():
        # remove empty entries
        if len(values) == 0:
            continue
        # find total count
        total = float(sum(values.values()))
        # convert to percentages
        tool_values = {}
        for tool, value in values.iteritems():
            tool_values[tool_names[tool]] = value / total
        # convert tool indices to names
        new_key = "%s,%s" % (tool_names[triplet[0]], tool_names[triplet[1]])
        filtered_triplets[new_key] = tool_values
    print >> sys.stderr, ("\rFinished parsing chains into triplets               \n"),
    return filtered_triplets

def find_triplet(triplets, data, index, i, first, key):
    # if second dataset doesn't serve as the input for any tool, stop looking
    if data[i, 1] >= index.shape[0] - 1:
        return None
    if first:
        # if this is the first step, delve down another level for each connection to the previous output dataset
        for j in range(index[data[i, 1]], index[data[i, 1] + 1]):
            new_key = (key, data[j, 2])
            if new_key not in triplets:
                triplets[new_key] = {}
            find_triplet(triplets, data, index, j, False, new_key)
    else:
        # if this is the second step, return a list of tools applied to the previous output dataset
        for j in range(index[data[i, 1]], index[data[i, 1] + 1]):
            if data[j, 2] not in triplets[key]:
                triplets[key][data[j, 2]] = 0
            triplets[key][data[j, 2]] += 1
    return None

def write_tool_chains(chains, tool_names, out_fname):
    results = {}
    for i, chain in enumerate(chains):
        temp_chain = {'nodes': [], 'edges': []}
        for j in range(numpy.amax(chain[:, :2])):
            temp_chain['nodes'].append({'id': int(j), 'label': str(j)})
        for j in range(chain.shape[0]):
            temp_chain['edges'].append({'from': int(chain[j, 0]), 'to': int(chain[j, 1]),
                                        'label': tool_names[chain[j, 2]]})
        results['chain_%i' % i] = temp_chain
    output = open(out_fname, 'w')
    output.write( "var data = %s;" % json.dumps(results))
    output.close()

def write_triplets(triplets, out_fname):
    """Jsonify triplets and write to file"""
    output = open(out_fname, 'w')
    output.write(json.dumps(triplets))
    output.close()

if __name__ == "__main__":
    main()
