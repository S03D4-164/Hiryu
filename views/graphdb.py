from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from py2neo import watch, Graph, Node, Relationship

from ..forms import *
from ..models import *
from ..postprocess import process_node
from db import get_node_on_db
from graph import  graph_init

import json

def get_node(graph, label, key, value, properties=[]):
	node = None
	if label and key:
		if not graph.find(label):
			graph.schema.create_uniqueness_constraint(label, key)
		if value:
			node = graph.merge_one(label, key, value)
			if node and properties:
				for key in properties:
					node[key] = properties[key]
				node.push()
	return node

def push_node_to_db(node, graph):
	label, = node.labels
	label_key = None
	if graph.schema.get_uniqueness_constraints(str(label)):
		label_key, = graph.schema.get_uniqueness_constraints(str(label))
	n = None
	if label_key:
		label_value = node[label_key]
		ref = node._id
		try:
			n = Node.objects.get(ref=ref)
		except:
			pass
		if n:
			pk,created = PropertyKey.objects.get_or_create(
				name = label_key,
			)
			if pk:
				p, created = Property.objects.get_or_create(
					key = pk,
					value = label_value,
				)
				l, created = NodeLabel.objects.get_or_create(
					name = label
				)
				if p and l:
					n.label = l
					n.key_property = p
					n.properties.add(p)
					n.save()
		else:
			n = get_node_on_db(label, label_key, label_value, node.properties)
			n.ref = ref
			n.save()
	return n

def push_relation_to_db(relation, graph):
	src = push_node_to_db(relation.start_node, graph)
	dst = push_node_to_db(relation.end_node, graph)
	rt, created = RelType.objects.get_or_create(name=relation.type)
	rel = None
	if src and dst and rt:
		rel, created = Relation.objects.get_or_create(type=rt, src=src, dst=dst)
		if rel:
			if relation.properties:
				subcluster = []
				for k, v in relation.properties.iteritems():
					if k == "cluster":
                                        	if type(v) is list:
                                               		for i in v:
                                                        	c, created = Cluster.objects.get_or_create(name=i)
                                                elif type(v) is str:
                                                	c, created = Cluster.objects.get_or_create(name=v)
                                        elif k =="subcluster":
                                                if type(v) is list:
                                                        for i in v:
                                                                sc, created = SubCluster.objects.get_or_create(name=i)
                                                                if sc and not sc in subcluster:
                                                                	subcluster.append(sc)
                                                elif type(v) is str:
                                                        sc, created = SubCluster.objects.get_or_create(name=v)
                                                        if sc and not sc in subcluster:
                                                                subcluster.append(sc)
                                        else:
                                                pk, created = PropertyKey.objects.get_or_create(name=k)
                                                p, created = Property.objects.get_or_create(key=pk, value=v)
						rel.properties.add(p)
                                for s in subcluster:
                                	rel.subcluster.add(s)
                                rel.save()

			rel.ref = int(str(relation.ref).split('/')[1])
			rel.save()
	return rel

def graphdb_view(request):
	graph = graph_init()
	form = RelCreateForm()
	eform = EntityForm()
	if request.method == "POST":
		if "create" in request.POST:
			form = RelCreateForm(request.POST)
			if form.is_valid():
				src_index = form.cleaned_data["src_index"]
				src = {
					"label":src_index.label.name,
					"key":src_index.property_key.name,
					"value":form.cleaned_data["src_value"].strip(),
				}
				src_node = get_node(graph, src["label"], src["key"], src["value"])
				dst_index = form.cleaned_data["dst_index"]
				dst = {
					"label":dst_index.label.name,
					"key":dst_index.property_key.name,
					"value":form.cleaned_data["dst_value"].strip(),
				}
				dst_node = get_node(graph, dst["label"], dst["key"], dst["value"])
				reltype = form.cleaned_data["reltype"]
				rel = reltype.name
				if src_node and dst_node and rel:
					graph.create_unique(Relationship(src_node, rel, dst_node ))
		elif "create_index" in request.POST:
			form = RelCreateForm(request.POST)
			if form.is_valid():
				src_index = form.cleaned_data["src_index"]
				label = src_index.label.name
				key = src_index.property_key.name
				if not key in graph.schema.get_uniqueness_constraints(label):
					graph.schema.create_uniqueness_constraint(label, key)
		elif "delete_index" in request.POST:
			form = RelCreateForm(request.POST)
			if form.is_valid():
				src_index = form.cleaned_data["src_index"]
				label = src_index.label.name
				key = src_index.property_key.name
				for key in graph.schema.get_uniqueness_constraints(label):
					graph.schema.drop_uniqueness_constraint(label, key)
		elif "add_property" in request.POST:
			eform = EntityForm(request.POST)
			if eform.is_valid():
				entity = eform.cleaned_data["entity"]
				id = eform.cleaned_data["id"]
				key = eform.cleaned_data["key"]
				value = eform.cleaned_data["value"].strip()
				subcluster = eform.cleaned_data["subcluster"]
				e = None
				if entity == "node":
					e = graph.node(id)
				elif entity == "rel":
					e = graph.relationship(id)
				if e:
					if key and value:
						k = key.name
						if not k == "subcluster" or not k == "cluster":
							e[k] = value
					if subcluster:
						cluster = []
						sc = []
						for s in subcluster:
							if not s.name in sc:
								sc.append(s.name)
							for c in s.cluster.all():
								if not c.name in cluster:
									cluster.append(c.name)
						e["subcluster"] = sc
						e["cluster"] = cluster
						e.push()
		elif "remove_property" in request.POST:
			eform = EntityForm(request.POST)
			if eform.is_valid():
				entity = eform.cleaned_data["entity"]
				id = eform.cleaned_data["id"]
				key = eform.cleaned_data["key"]
				subcluster = eform.cleaned_data["subcluster"]
				e = None
				if entity == "node":
					e = graph.node(id)
				elif entity == "rel":
					e = graph.relationship(id)
				if e:
					if key:
						k = key.name
						e[k] = None
					if subcluster:
						for s in subcluster.all():
							if s.name in e["subcluster"]:
								e["subcluster"].remove(s.name)
							for c in s.cluster.all():
								if c.name in e["cluster"]:
									e["cluster"].remove(c.name)
					e.push()
		elif "delete" in request.POST:
			eform = EntityForm(request.POST)
			if eform.is_valid():
				entity = eform.cleaned_data["entity"]
				id = eform.cleaned_data["id"]
				e = None
				if entity == "node":
					e = graph.node(id)
				elif entity == "rel":
					e = graph.relationship(id)
				if e:
					try:
						graph.delete(e)
					except:
						if entity == "node":
							messages.add_message(request, messages.ERROR, 'ERROR: Delete Failed. Node has Relation.')
		elif "push" in request.POST:
			eform = EntityForm(request.POST)
			if eform.is_valid():
				entity = eform.cleaned_data["entity"]
				id = eform.cleaned_data["id"]
				e = None
				if id:
					if entity == "node":
						node = graph.node(id)
						n = push_node_to_db(node, graph)
						if n:
							for s in n.subcluster.all():
								process_node.delay(node, s)
					elif entity == "rel":
						relation = graph.relationship(id)
						rel = push_relation_to_db(relation, graph)
						if rel:
							rel.ref = id
							rel.save()
		elif "push_all" in request.POST:
        		nodes = graph.cypher.execute("MATCH n return n")
        		sg = nodes.to_subgraph()
        		for n in sg.nodes:
				node = push_node_to_db(n, graph)
				if node:
					for s in node.subcluster.all():
						process_node.delay(node, s)
			relations = graph.cypher.execute("MATCH n-[r]->m return n,r,m")
			for n, r, m in relations:
				rel = push_relation_to_db(r, graph)
		elif "delete_all" in request.POST:
			return redirect("/delete/graphdb")

	relations = graph.cypher.execute("MATCH n-[r]->m return n,r,m")
	rlist = []
	for n, r, m in relations:
		rlist.append({
			"src":{
				"ref":n._id,
				"labels":n.labels,
				"properties":json.loads(json.dumps(n.properties)),
			},
			"rel":{
				"ref":r._id,
				"type":r.type,
				"properties":json.loads(json.dumps(r.properties)),
			},
			"dst":{
				"ref":m._id,
				"labels":m.labels,
				"properties":json.loads(json.dumps(m.properties)),
			},
		
		})
	rlist = sorted(rlist, key=lambda k:k["rel"]["ref"], reverse=True)

        nodes = graph.cypher.execute("MATCH n return n")
        sg = nodes.to_subgraph()
        nlist = []
        for n in sg.nodes:
                nlist.append({
			"ref":n._id,
                        "labels":n.labels,
                        "properties":json.loads(json.dumps(n.properties)),
                        "degree":n.degree,
                })
        nlist = sorted(nlist, key=lambda k:k["ref"], reverse=True)

	#rel_types = sorted(graph.relationship_types)
	node_labels = sorted(graph.node_labels)
	indexes = []
	for l in node_labels:
		k = graph.schema.get_uniqueness_constraints(l)
		index = {
			"label":l,
			"key":k,
		}
		indexes.append(index)

	rc = RequestContext(request, {
		"form":form,
		"eform":eform,
		"relations":rlist,
		"nodes":nlist,
		"indexes":indexes,
	})
	return render_to_response("graphdb_list.html", rc)
