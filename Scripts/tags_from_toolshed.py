#!/usr/bin/env python

import json

infname = 'toolshed_data.json'
data = json.load(open(infname, 'r'))
cats = json.load(open('categories.json', 'r'))
catdict = {}
for cat in cats:
	catdict[cat['id']] = cat['name']
tools = {}
for entry in data:
	if entry['type'] == 'unrestricted':
		cats = entry['category_ids']
		for c in cats:
			cat = catdict[c]
			if cat not in tools:
				tools[cat] = []
			tools[cat].append(entry['name'])
output = open('toolshed_categories.json', 'w')
print >> output, json.dumps(tools)
output.close()


