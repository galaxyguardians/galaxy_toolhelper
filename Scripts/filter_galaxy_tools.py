#!/usr/bin/env python

import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
# import imp
# tool_parser = imp.load_source("galaxy.tools.parser",\
# "/Users/nturaga/Documents/PR_testing/galaxy/lib/galaxy/tools/parser")


def find_tool_xmlfiles(tool_conf_file, tools_dir):
    """
    Input: Galaxy tools directory
    output: List of xml files
    """
    with open(tool_conf_file, 'r') as tool_conf:
        tree = ET.parse(tool_conf)
    tools = [os.path.join(tools_dir, elem.get('file'))
             for elem in tree.iter()
             if elem.tag == 'tool']
    return tools


def tool_parse(xmlfile):
    """
    Input: One galaxy tool form
    Output: List of [input datatype, output datatype, tool]
    """
    with open(xmlfile, 'r') as tool:
        tree = ET.parse(tool)
        inputs = tree.findall("./inputs//param")
        # attributes = [param.attrib for param in inputs]
        #tool_name = tool.name.split("/")[-1].replace(".xml", "")
	f= minidom.parse(xmlfile)
	items = f.getElementsByTagName("tool")
	tool_name= items[0].attributes['id'].value
    # Find all params
    format_tool_dict = {}
    for param in inputs:
        # If input HAS "format" attribute
        if param.get("format") is not None:
            # Get param's format
            param_format = param.get("format")
            # print param_format
            # print tool_name
            if param_format not in format_tool_dict.keys():
                format_tool_dict[param_format] = [tool_name]
            else:
                format_tool_dict[param_format].append(tool_name)

    # print "Format: Tool Dictionary", format_tool_dict
    return format_tool_dict


def make_tool_dict(tool_conf_file, tools_dir):
    """
    Input: Tools directory
    Output:
    Dict{ Input_datatype : [tool1,tool2,tool3],
          Input_datatype2 : [tool4,tool5]}
    """
    tools = find_tool_xmlfiles(tool_conf_file, tools_dir)
    tool_dict = {}
    for tool in tools:
        # Get Inputs
        dic = tool_parse(tool)
        # Skip if there are no inputs
        if len(dic) == 0:
            continue
        # Add datatype to dictionary
        # print tool
        for datatypes, tools in dic.iteritems():
            # print datatypes.split(","), type(datatypes.split(",")[0])
            # Loop through comma seperated datatypes
            for datatype in datatypes.split(","):
                if datatype not in tool_dict.keys():
                # print "Adding datatype and list of tools"
                # print "Datatype: %s Tools: %s" % (datatype, tools)
                    tool_dict[datatype] = tools
                    tool_dict[datatype] = list(set(tool_dict[datatype]))
                else:
                # print "Need to add pre existing keys in tool_dict"
                # print "Datatype: %s Tools: %s" % (datatype, tools)
                    for elem in tools:
                        tool_dict[datatype].append(elem)
                    tool_dict[datatype] = list(set(tool_dict[datatype]))
                # print "Dictionary after appending: ", tool_dict
    return tool_dict


def make_better_tool_dict(datatype_to_tool, datatype_hierarchy):
    """
    Input: 
    """
    tool_datatypes = {}
    for datatype in datatype_to_tool.keys():
        for tool in datatype_to_tool[datatype]:
            if datatype_hierarchy.get(datatype):
                tool_datatypes[tool] = datatype_hierarchy[datatype]
            else:
                print "Missing datatype %s" % datatype
    return tool_datatypes


if __name__ == "__main__":
    TOOLS_DIR = "/Users/taylorlab/Documents/galaxy/tools"
    tool_conf_file = "/Users/taylorlab/Documents/galaxy/config/tool_conf.xml.sample"
    datatype_tree_file = "../Data/datatype_tree.json"
    with open(datatype_tree_file, 'r') as f:
        datatype_tree = json.load(f)
    tool_dict = make_tool_dict(tool_conf_file, TOOLS_DIR)
    tool_dict2 = make_better_tool_dict(tool_dict, datatype_tree)

    """Jsonify Tool dictionary and write to file"""
    output = open('galaxy_filter_dictionary.json', 'w')
    output.write(json.dumps(tool_dict))
    output.close()

    output = open('tool_datatypes.json', 'w')
    output.write(json.dumps(tool_dict2))
    output.close()
