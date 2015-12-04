#!/usr/bin/env python

import sys
import glob
import numpy

def main():
    dir_name, out_fname = sys.argv[1:3]
    # get all datatype file names
    fnames = glob.glob("%s/*.py" % dir_name)
    tree = {}
    for fname in fnames:
        parse_file(fname, tree)
    json_tree = tree_to_json(tree)
    lookup_table = json_to_lookup(json_tree)
    write_results(lookup_table, out_fname)

def parse_file(fname, tree):
    for line in open(fname):
        temp = line.strip('\t \n').split(' ')
        if temp[0] != 'class':
            continue
        subtype = temp[1].split('(')[0].strip(' ')
        if subtype[0] == '_':
            continue
        supertype = line.split('(')[1].split(')')[0].split(',')[0].split('.')[-1].strip(' ')
        if supertype not in tree:
            tree[supertype] = [subtype]
        else:
            tree[supertype].append(subtype)
        if subtype not in tree:
            tree[subtype] = []
    return None

def tree_to_json(tree):
    roots = []
    all_types = numpy.array(tree.keys())
    all_types.sort()
    counts = numpy.zeros(all_types.shape[0], dtype=numpy.int32)
    for key in all_types:
        for subkey in tree[key]:
            counts[numpy.where(subkey == all_types)[0][0]] += 1
    roots = all_types[numpy.where(counts==0)[0]]
    tree['root'] = list(roots)
    json_tree = add_branch('root', tree)
    json_tree = json_tree['object']['Data']
    return json_tree

def add_branch(name, tree):
    new_branch = {}
    for subname in tree[name]:
        new_branch[subname] = add_branch(subname, tree)
    return new_branch

def json_to_lookup(tree):
    lookup = {}
    get_lookups(lookup, tree, [])
    return lookup

def get_lookups(lookup, tree, path):
    for key in tree:
        lookup[key] = list(path) + [key]
        get_lookups(lookup, tree[key], lookup[key])

def write_results(tree, fname):
    output = open(fname, 'w')
    print >> output, "%s" % str(tree).replace("""'""",'"').replace(' ','')
    output.close()

if __name__ == "__main__":
    main()
