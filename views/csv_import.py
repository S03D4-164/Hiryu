from django.shortcuts import render_to_response, redirect
from ..models import *
from ..forms import UploadFileForm


import csv, os

def set_property_to_entity(e, key, value):
	pkey, created = PropertyKey.objects.get_or_create(
		name = key
	)
	property = None
	if pkey:
		property, created = Property.objects.get_or_create(
			key = pkey,
			value = value
		)
		if property:
			e.properties.add(property)
			e.save()
	return e

def set_subcluster_to_entity(e, subcluster, cluster):
	sc, created = SubCluster.objects.get_or_create(
		name = subcluster
	)
	c = None
	if cluster:
		c, created = Cluster.objects.get_or_create(
			name = cluster
		)
		if sc and c:
			sc.cluster.add(c)
			sc.save()
	if sc:
		e.subcluster.add(sc)
		e.save()
	return e

def import_node(files):
	fieldnames = (
		"node_label",
		"primal_key",
		"primal_value",
		"property_key",
		"property_value",
		"subcluster",
		"cluster",
	)
	from db import get_node_on_db
	#reader = csv.DictReader(files, fieldnames)
	reader = csv.DictReader(files)
	for r in reader:
		node = get_node_on_db(
			r["node_label"],
			r["primal_key"],
			r["primal_value"],
		)
		if node:
			if r["property_key"] and r["property_value"]:
				node = set_property_to_entity(node, r["property_key"], r["property_value"])
			if r["subcluster"]:
				node = set_subcluster_to_entity(node, r["subcluster"], r["cluster"])
	return redirect("/node/")

def import_relation(files):
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
	from db import get_node_on_db
	#reader = csv.DictReader(files, fieldnames)
	reader = csv.DictReader(files)
	for r in reader:
		src = get_node_on_db(
			r["src_label"],
			r["src_key"],
			r["src_value"],
		)
		dst = get_node_on_db(
			r["dst_label"],
			r["dst_key"],
			r["dst_value"],
		)
		if src and dst:
			reltype, created = RelType.objects.get_or_create(
				name = r["rel_type"]
			)
			if reltype:
				rel, created = Relation.objects.get_or_create(
					type = reltype,
					src = src,
					dst = dst,
				)
				if rel:
					if r["property_key"] and r["property_value"]:
						rel = set_property_to_entity(rel, r["property_key"], r["property_value"])
					if r["subcluster"]:
						rel = set_subcluster_to_entity(rel, r["subcluster"], r["cluster"])			
						src = set_subcluster_to_entity(src, r["subcluster"], r["cluster"])			
						dst = set_subcluster_to_entity(dst, r["subcluster"], r["cluster"])			
	return redirect("/relation/")
