#!/usr/bin/python
import sys
import lxml.objectify
from pprint import pprint

def set_metadata(m, metadata):
    metadata["description"] = m.description
    metadata["short_description"] = m.short_description
    metadata["authored_by"] = m.authored_by
    metadata["authored_date"] = m.authored_date
    return metadata


def set_indicator(i, ind):
    d = {
        "id": i.attrib.get("id"),
        "operator": i.attrib.get("operator"),
        "item":[],
        "indicator":[]
    }
    if hasattr(i, "IndicatorItem"):
        for ii in i.IndicatorItem:
            item = {
                "id": ii.attrib.get("id"),
                "condition": ii.attrib.get("condition"),
                "context":None,
                "content":None,
            }
            item["context"] = {
                "document": ii.Context.attrib.get("document"),
                "search": ii.Context.attrib.get("search"),
                "type": ii.Context.attrib.get("type"),
            }
            content = {}
            ctype = ii.Content.attrib.get("type")
            content[ctype] = ii.Content
            item["content"] = content
            if not item in d["item"]:
                d["item"].append(item)
        if not d in ind:
            ind.append(d)
        #if hasattr(i, "Indicator"):
        #    for indicator in i.Indicator:
        #        d["indicator"] = set_indicator(indicator, d["indicator"])
    if hasattr(i, "Indicator"):
        for indicator in i.Indicator:
            #ind = set_indicator(indicator, ind)
            d["indicator"] = set_indicator(indicator, d["indicator"])
    return ind

def main(file):
    ioco=lxml.objectify.parse(sys.argv[1])
    root=ioco.getroot()
    metadata = {}
    indicator = []
    if "OpenIOC" in root.tag:
        metadata = set_metadata(root.metadata)
        indicator = set_indicator(root.criteria, indicator)
    elif "ioc" in root.tag:
        metadata = set_metadata(root, metadata)
        #indicator = set_indicator(root.definition, indicator)
        indicator = set_indicator(root.definition.Indicator, indicator)
    ioc = {
        "metadata":metadata,
        "indicator":indicator,
    }
    return ioc

if __name__ == '__main__':
    file = sys.argv[1]
    ioc = main(file)
    pprint(ioc)
