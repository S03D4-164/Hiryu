from django.shortcuts import render_to_response, redirect
from ..models import *
from ..tasks import process_node
from db import get_node_on_db

import re, tldextract
import lxml.objectify

def metadata_to_subcluster(m, cluster):
        sc, created = SubCluster.objects.get_or_create(
                name = m.short_description,
		description = m.description,
		firstseen = str(m.authored_date),
        )
	if sc:
		if cluster:
			sc.cluster.add(cluster)
		c, created = Cluster.objects.get_or_create(
			name = m.authored_by,
		)
		if c:
			sc.cluster.add(c)
		sc.save()
        return sc

def ii_to_ni(ii):
	search = ii.Context.attrib.get("search")
	content = str(ii.Content).strip()
	s, created = IOCTerm.objects.get_or_create(
		text = search,
	)
	ni = None
	if s.index and s.allow_import:
		ni = s.index
	"""
	if search == "PortItem/remoteIP":
		if re.match("^([0-9]{1,3}\.){3}[0-9]{1,3}$", content):
			ni = NodeIndex.objects.get(
				label__name="IP",
				property_key__name="address",
			)
	elif search == "DnsEntryItem/RecordName" \
		or search == "DnsEntryItem/Host":
	        no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
        	ext = no_fetch_extract(content)
		if ext.domain and ext.suffix:
			ni = NodeIndex.objects.get(
				label__name="Host",
				property_key__name="name",
			)
	elif search == "FileItem/FileName":
		ni = NodeIndex.objects.get(
			label__name="File",
			property_key__name="name",
		)
	elif search == "Email/From":
		if re.match("^[a-z][_a-z0-9-.]+@[a-z0-9-]+\.[a-z]+$", content):
			ni = NodeIndex.objects.get(
				label__name="Attacker",
				property_key__name="email",
			)
	elif search == "FileItem/Md5sum":
		if re.match("^[a-f,0-9]{32}$", content):
			ni = NodeIndex.objects.get(
				label__name="Malware",
				property_key__name="md5",
			)
	"""
	node = None
	if ni:
		node = {
               	        "node_label": ni.label.name,
			"primal_key": ni.property_key.name,
			"primal_value": content
		}
	return node

def indicator_to_node(i, sc):
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
        if hasattr(i, "Indicator"):
                i = indicator_to_node(i.Indicator, sc)
	return i

def import_ioc(file, cluster=None):
	ioco = lxml.objectify.parse(file)
	root = ioco.getroot()
	sc = None
	if "ioc" in root.tag:
		sc = metadata_to_subcluster(root, cluster)
		if sc:
			indicator_to_node(root.definition, sc)
	elif "OpenIOC" in root.tag:
		sc = metadata_to_subcluster(root.metadata, cluster)
		if sc:
			indicator_to_node(root.criteria, sc)
	if sc:
	        return redirect("/subcluster/" + str(sc.id))
	elif cluster:
		return redirect("/cluster/" + str(cluster.id))
	else:
		return redirect("/cluster/")
