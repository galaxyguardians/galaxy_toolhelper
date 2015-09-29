#!/usr/bin/env python

import os
import json
import xml.etree.ElementTree as ET
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
        tool_name = tool.name.split("/")[-1].replace(".xml", "")
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


if __name__ == "__main__":
    TOOLS_DIR = "/Users/nturaga/Documents/PR_testing/galaxy/tools"
    tool_conf_file = "/Users/nturaga/Documents/PR_testing/galaxy/config/tool_conf.xml.sample"
    tool_dict = make_tool_dict(tool_conf_file, TOOLS_DIR)

    """Jsonify Tool dictionary and write to file"""
    output = open('galaxy_filter_dictionary.json', 'w')
    output.write(json.dumps(tool_dict))
    output.close()
