from django.shortcuts import render_to_response, redirect
from ..models import *
from ..tasks import process_node
from db import get_node_on_db

import re, tldextract
import lxml.objectify

def metadata_to_subcluster(m, cluster):
	"""
	metadata = {}
	metadata["description"] = m.description
	metadata["short_description"] = m.short_description
	return metadata
	"""
        sc, created = SubCluster.objects.get_or_create(
                name = m.short_description,
		description = m.description,
        )
	if sc:
		sc.cluster.add(cluster)
		sc.save()
        return sc

def ii_to_ni(ii):
	search = ii.Context.attrib.get("search")
	content = str(ii.Content).strip()
	ni = None
	if search == "FileItem/Md5sum":
		if re.match("^[a-f,0-9]{32}$", content):
			ni = NodeIndex.objects.get(
				label__name="Malware",
				property_key__name="md5",
			)
	elif search == "DnsEntryItem/RecordName":
	        no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
        	ext = no_fetch_extract(content)
		if ext.domain and ext.suffix:
			ni = NodeIndex.objects.get(
				label__name="Host",
				property_key__name="name",
			)
	elif search == "PortItem/remoteIP":
		if re.match("^([0-9]{1,3}\.){3}[0-9]{1,3}$", content):
			ni = NodeIndex.objects.get(
				label__name="IP",
				property_key__name="address",
			)
	node = None
	if ni:
		node = {
               	        "node_label": ni.label.name,
			"primal_key": ni.property_key.name,
			"primal_value": content
		}
	return node

def indicator_to_node(i, sc):
	"""
	ind = {}
	for ii in i.Indicator.IndicatorItem:
		search = ii.Context.attrib.get("search")
		if not search in ind:
			ind[search] = [ii.Content]
		else:
			if not ii.Content in ind[search]:
				ind[search].append(ii.Content)
	return ind
	"""
        if hasattr(i, "Indicator"):
                ind = set_indicator(i.Indicator, ind)
        if hasattr(i, "IndicatorItem"):
                for ii in i.IndicatorItem:
			n = ii_to_ni(ii)
			if n:
		                node = get_node_on_db(
	        	                n["node_label"],
        	        	        n["primal_key"],
                	        	n["primal_value"],
				)
				if node and sc:
					node.subcluster.add(sc)
					node.save()
					process_node.delay(node, sc)
	#return node

def import_ioc(file, cluster):
	ioco = lxml.objectify.parse(file)
	root = ioco.getroot()
	sc = None
	"""
	if "OpenIOC" in root.tag:
		sc = metadata_to_subcluster(root.metadata)
		if sc:
			sc.cluster.add(cluster)
			sc.save()
			indicator_to_node(root.criteria, sc)
	"""
	if "ioc" in root.tag:
		sc = metadata_to_subcluster(root, cluster)
		indicator_to_node(root.definition, sc)
	if sc:
	        return redirect("/subcluster/" + str(sc.id))
	return redirect("/cluster/" + str(cluster.id))
	"""
	ioc = {
		"metadata":{},
		"indicator":{},
	}
	if "OpenIOC" in root.tag:
		ioc["metadata"] = set_metadata(root.metadata)
		ioc["indicator"] = set_indicator(root.criteria)
	elif "ioc" in root.tag:
		ioc["metadata"] = set_metadata(root)
		ioc["indicator"] = set_indicator(root.definition)
	return ioc
	"""

