from django.shortcuts import render_to_response, redirect
from ..models import Cluster, SubCluster, Node, Relation

import csv, os

def export_node(request, model=None, id=None):
	node = None
	subcluster = None
	cluster = None
	if model == "subcluster":
		subcluster = SubCluster.objects.get(pk=id)
                node = Node.objects.filter(subcluster__id=id)
	elif model == "cluster":
		cluster = Cluster.objects.get(pk=id)
                node = Node.objects.filter(subcluster__cluster__id=id)
	else:
                node = Node.objects.all()
	
	fieldnames = (
		"node_label",
		"primal_key",
		"primal_value",
		"property_key",
		"property_value",
		"subcluster",
		"cluster",
	)
	import myapp
	appdir = os.path.dirname(myapp.__file__)
	out = None
	if not model:
		out = "/static/export/node_all.csv"
	else:
		out = "/static/export/node_" + model + id + ".csv"
	writer = csv.DictWriter(open(appdir + out, "wb"), fieldnames)
	writer.writeheader()
	for n in node:
		dict = {
			"node_label":n.label.name.encode("utf8"),
			"primal_key":n.key_property.key.name.encode("utf8"),
			"primal_value":n.key_property.value.encode("utf8"),
			"property_key":None,
			"property_value":None,
			"subcluster":None,
			"cluster":None,
		}
		write_entity_to_csv(cluster, subcluster, n, dict, writer)
	return redirect(out)

def write_entity_to_csv(cluster, subcluster, e, dict, writer):
	if e.properties.all():
		for p in e.properties.all():
			dict["property_key"] = p.key.name.encode("utf8")
			dict["property_value"] = p.value.encode("utf8")
			if subcluster:
				dict["subcluster"] = subcluster.name.encode("utf8")
				if subcluster.cluster.all():
					for c in subcluster.cluster.all():
						dict["cluster"] = c.name.encode("utf8")
						writer.writerow(dict)
				else:
					writer.writerow(dict)
			elif cluster:
				dict["cluster"] = cluster.name.encode("utf8")
				if e.subcluster.all():
					for s in e.subcluster.all():
						dict["subcluster"] = s.name.encode("utf8")
						writer.writerow(dict)
				else:
					writer.writerow(dict)
			else:
				if e.subcluster.all():
					for s in e.subcluster.all():
						dict["subcluster"] = s.name.encode("utf8")
						for c in s.cluster.all():
							dict["cluster"] = c.name.encode("utf8")
				writer.writerow(dict)
				
	else:
		if subcluster:
			dict["subcluster"] = subcluster.name.encode("utf8")
			if subcluster.cluster.all():
				for c in subcluster.cluster.all():
					dict["cluster"] = c.name.encode("utf8")
					writer.writerow(dict)
			else:
				writer.writerow(dict)
		elif cluster:
			dict["cluster"] = cluster.name.encode("utf8")
			if e.subcluster.all():
				for s in e.subcluster.all():
					dict["subcluster"] = s.name.encode("utf8")
					writer.writerow(dict)
			else:
				writer.writerow(dict)
		else:
			if e.subcluster.all():
				for s in e.subcluster.all():
					dict["subcluster"] = s.name.encode("utf8")
					for c in s.cluster.all():
						dict["cluster"] = c.name.encode("utf8")
			writer.writerow(dict)

def export_relation(request, model=None, id=None):
	node = None
	subcluster = None
	cluster = None
	if model == "subcluster":
		subcluster = SubCluster.objects.get(pk=id)
                rel = Relation.objects.filter(subcluster__id=id)
	elif model == "cluster":
		cluster = Cluster.objects.get(pk=id)
                rel = Relation.objects.filter(subcluster__cluster__id=id)
	else:
                rel = Relation.objects.all()
	fieldnames = (
		"src_label",
		"src_key",
		"src_value",
		"rel_type",
		"property_key",
		"property_value",
		"dst_label",
		"dst_key",
		"dst_value",
		"subcluster",
		"cluster",
	)
	import myapp
	appdir = os.path.dirname(myapp.__file__)
	out = None
	if not model:
		out = "/static/export/relation_all.csv"
	else:
		out = "/static/export/relation_" + model + id + ".csv"
	writer = csv.DictWriter(open(appdir + out, "wb"), fieldnames)
	writer.writeheader()
	for r in rel:
		dict = {
			"src_label":r.src.label.name.encode("utf8"),
			"src_key":r.src.key_property.key.name.encode("utf8"),
			"src_value":r.src.key_property.value.encode("utf8"),
			"rel_type":r.type.name.encode("utf8"),
			"property_key":None,
			"property_value":None,
			"dst_label":r.dst.label.name.encode("utf8"),
			"dst_key":r.dst.key_property.key.name.encode("utf8"),
			"dst_value":r.dst.key_property.value.encode("utf8"),
			"subcluster":None,
			"cluster":None,
		}
		write_entity_to_csv(cluster, subcluster, r, dict, writer)
	return redirect(out)
