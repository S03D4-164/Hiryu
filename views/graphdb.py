from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.contrib import messages

from py2neo import watch, Graph, Node, Relationship

from ..forms import *
from ..models import *
from ..tasks import *
from .db import get_node_on_db
from .graph import  graph_init

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
                postprocess = eform.cleaned_data["postprocess"]
                entity = eform.cleaned_data["entity"]
                id = eform.cleaned_data["id"]
                e = None
                if id:
                    if entity == "node":
                        gnode = graph.node(id)
                        node = push_node_to_db(gnode, graph)
                        if node and postprocess:
                            for s in node.subcluster.all():
                                process_node.delay(node, s)
                    elif entity == "rel":
                        relation = graph.relationship(id)
                        rel = push_relation_to_db(relation, graph)
                        if rel:
                            rel.ref = id
                            rel.save()
        elif "push_all" in request.POST:
            postprocess = False
            eform = EntityForm(request.POST)
            if eform.is_valid():
                postprocess = eform.cleaned_data["postprocess"]
            push_graph_to_db.delay(postprocess)
        elif "delete_all" in request.POST:
            return redirect("/delete/graphdb")

    relations = ()
    try:
        relations = graph.cypher.execute("MATCH n-[r]->m return n,r,m")
    except Exception as e:
        messages.add_message(request, messages.WARNING, 'ERROR: ' + str(e))
        return render(request, "graphdb_list.html", {})
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

    #rc = RequestContext(request, {
    c = {
        "form":form,
        "eform":eform,
        "relations":rlist,
        "nodes":nlist,
        "indexes":indexes,
    }
    #return render_to_response("graphdb_list.html", rc)
    return render(request, "graphdb_list.html", c)
