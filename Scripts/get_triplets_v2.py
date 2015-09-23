#!/usr/bin/env python
import pandas
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def match_with_input_datasets(data, output_dataset):
    """
    Match output_dataset, with input_dataset columns
    Return only rows in which output matches input
    """
    bool_list = data['input_dataset'].str.match(output_dataset)
    rows = data.ix[bool_list, :]
    if len(rows) < 1:
        return None
    return rows


def get_index(triplet_tool, triplet_tool_dicts):
    for (index, d) in enumerate(triplet_tool_dicts):
        if triplet_tool in d:
            return index
    return -1


def find_triplets(data):
    """
    Function is used to find triplets in the data from the galaxy main database
    Triplet is defined as:
    Tool1,tool2,tool3 , where all three tools are meant to be connected by the datasets
    """
    dat = pandas.read_csv(data, dtype=object, nrows=100000)
    tool_chain = {}  # dict to store chains
    logger.info("Start looking for chains")
    for index, row in dat.iterrows():
        # Get first tool
        first_tool = row['tool_id']
        duplet_rows = match_with_input_datasets(dat, row['output_dataset'])
        if duplet_rows is None:
            continue
        # Get second tool
        duplet_tool = duplet_rows['tool_id'].iget(0)
        # Iterate through duplet rows to find all triplets
        for j, rows in duplet_rows.iterrows():
            triplet_list = match_with_input_datasets(dat, rows['output_dataset'])
            if triplet_list is None:
                continue
            # Get Triplet tool
            val_counts = triplet_list['tool_id'].value_counts()
            # Check conditions to
            if (first_tool, duplet_tool) in tool_chain:
                triplet_tool_dicts = tool_chain[(first_tool, duplet_tool)]
                triplet_tool = triplet_list['tool_id'].iget(0)
                tool_index = get_index(triplet_tool, triplet_tool_dicts)
                if tool_index != -1:
                    # print "Triplet tool present in tool chain, need to add count"
                    triplet_tool_dicts[tool_index][triplet_tool] += 1
                else:
                    print "Need to add triplet tool + value count to list", j
                    triplet_tool_dicts.append(dict(val_counts))
            else:
                # print "Add brand new item to tool_chain"
                tool_chain[(first_tool, duplet_tool)] = [dict(val_counts)]
    return tool_chain


if __name__ == "__main__":
    data = '/Users/nturaga/Documents/galaxyproject/galaxy-hack1/tool_connections.csv'
    tool_chain = find_triplets(data)
    import json
    new_tool_chain = json.dumps({str(k): v for k, v in tool_chain.iteritems()})
    with open('tool_chain_100000.json', 'w') as outfile:
        outfile.write(new_tool_chain)
