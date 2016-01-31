from django.shortcuts import redirect, render
from django.db.models import Q
from django.utils.safestring import SafeString

from ..models import Relation, SubCluster, Cluster, Node

import json

def vis_anonymize(request, model=None, id=None):
    c = visualize_view(request, model, id, anonymize=True)
    return render(request, 'visualize_view.html', c)

def visualize_view(request, model=None, id=None, anonymize=False):
    rel = None
    node = None
    target = None
    if model == "subcluster":
        if id:
            target = SubCluster.objects.get(pk=id)
            rel = Relation.objects.filter(subcluster__id=id)
            node = Node.objects.filter(subcluster__id=id)
        else:
            target = SubCluster.objects.all()
            rel = Relation.objects.filter(subcluster__in=target)
            node = Node.objects.filter(subcluster__in=target)
            target = "All SubCluster"
    elif model == "cluster":
        if id:
            target = Cluster.objects.get(pk=id)
            rel = Relation.objects.filter(subcluster__cluster__id=id)
            node = Node.objects.filter(subcluster__cluster__id=id)
        else:
            target = Cluster.objects.all()
            rel = Relation.objects.filter(subcluster__cluster__in=target)
            node = Node.objects.filter(subcluster__cluster__in=target)
            target = "All Cluster"
    elif model == "node":
        if id:
            target = Node.objects.get(pk=id)
            rel = Relation.objects.filter(Q(src=target)|Q(dst=target))
            node = [target]
    elif model == "relation":
        if id:
            target = Relation.objects.get(pk=id)
            rel = [target]
            node = [target.src, target.dst]
    else:
        target = "All Node/Relation"
        rel = Relation.objects.all()
        node = Node.objects.all()

    dataset = {}
    if node and rel:
        dataset = create_dataset(node, rel, model, target, anonymize)
    if anonymize:
        return dataset
    return render(request, "visualize_view.html", dataset)


def create_dataset(node, rel, model, target, anonymize=None):
    nodes = []
    edges = []
    for i in node:
        n = {
            'id': i.id,
            #'label': i.key_property.value.encode("utf8"),
            'label': i.value.encode("utf8"),
            #'group': i.label.name.encode("utf8"),
            'group': i.index.label.name.encode("utf8"),
            'title':[],
            'scid': [],
            'cid': [],
        }
        for sc in i.subcluster.all():
            if not sc.id in n["scid"]:
                n["scid"].append(sc.id)
            for c in sc.cluster.all():
                if not c.id in n["cid"]:
                    n["cid"].append(c.id)
        if anonymize:
            #n["label"] = str(i.id)
            n["label"] = ""
        else:
            for p in i.properties.all():
                line = p.key.name.encode("utf8") + " : " + p.value.encode("utf8")
                n["title"].append(line)
        if not n in nodes:
            nodes.append(n)
    for r in rel:
        s = {
            'id': r.src.id,
            #'label': r.src.key_property.value.encode("utf8"),
            'label': r.src.value.encode("utf8"),
            #'group': r.src.label.name.encode("utf8"),
            'group': r.src.index.label.name.encode("utf8"),
            'title':[],
            'scid': [],
            'cid': [],
        }
        for sc in r.src.subcluster.all():
            if not sc.id in s["scid"]:
                s["scid"].append(sc.id)
            for c in sc.cluster.all():
                if not c.id in s["cid"]:
                    s["cid"].append(c.id)
        if anonymize:
            #s["label"] = str(r.src.id)
            s["label"] = ""
        else:
            for p in r.src.properties.all():
                line = p.key.name.encode("utf8") + " : " + p.value.encode("utf8")
                s["title"].append(line)
        if not s in nodes:
            nodes.append(s)
        d = {
            'id': r.dst.id,
            #'label': r.dst.key_property.value.encode("utf8"),
            'label': r.dst.value.encode("utf8"),
            #'group': r.dst.label.name.encode("utf8"),
            'group': r.dst.index.label.name.encode("utf8"),
            'title':[],
            'scid': [],
            'cid': [],
        }
        for sc in r.dst.subcluster.all():
            if not sc.id in d["scid"]:
                d["scid"].append(sc.id)
            for c in sc.cluster.all():
                if not c.id in d["cid"]:
                    d["cid"].append(c.id)
        if anonymize:
            #d["label"] = str(r.dst.id)
            d["label"] = ""
        else:
            for p in r.dst.properties.all():
                line = p.key.name.encode("utf8") + " : " + p.value.encode("utf8")
                d["title"].append(line)
        if not d in nodes:
            nodes.append(d)
        e = {
            'from': r.src.id,
            'to': r.dst.id,
            'label': r.type.name.encode("utf8"),
            'title':[],
            'scid': [],
            'cid': [],
        }
        for sc in r.subcluster.all():
            if not sc.id in e["scid"]:
                e["scid"].append(sc.id)
            for c in sc.cluster.all():
                if not c.id in e["cid"]:
                    e["cid"].append(c.id)
        if anonymize:
            #s["label"] = str(r.src.id)
            e["title"] = ""
        else:
            for p in r.properties.all():
                line = p.key.name.encode("utf8") + " : " + p.value.encode("utf8")
                e["title"].append(line)
        if not e in edges:
            edges.append(e)

    c = {
        'model':model,
        'target':target,
        'nodes': nodes,
        'edges': edges,
    }
    #if anonymize:
    return c
    #return render(request, 'visualize_view.html', c)
