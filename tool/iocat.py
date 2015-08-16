#!/usr/bin/python
import sys
import lxml.objectify
from pprint import pprint

def set_metadata(m, metadata):
	metadata["description"] = m.description
	metadata["short_description"] = m.short_description
	return metadata

def set_indicator(i, ind):
	if hasattr(i, "IndicatorItem"):
		for ii in i.IndicatorItem:
			#if ii.attrib.get("condition") == "is":
			search = ii.Context.attrib.get("search")
			if not search in ind:
				ind[search] = [ii.Content]
			else:
				if not ii.Content in ind[search]:
					ind[search].append(ii.Content)
	if hasattr(i, "Indicator"):
		ind = set_indicator(i.Indicator, ind)

	return ind

def main(file):
	ioco=lxml.objectify.parse(sys.argv[1])
	root=ioco.getroot()
	metadata = {}
	indicator = {}
	if "OpenIOC" in root.tag:
		metadata = set_metadata(root.metadata)
		indicator = set_indicator(root.criteria, indicator)
	elif "ioc" in root.tag:
		metadata = set_metadata(root, metadata)
		indicator = set_indicator(root.definition, indicator)
		#indicator = set_indicator(root.definition.Indicator, indicator)
	ioc = {
		"metadata":metadata,
		"indicator":indicator,
	}
	return ioc

if __name__ == '__main__':
	file = sys.argv[1]
	ioc = main(file)
	pprint(ioc)
