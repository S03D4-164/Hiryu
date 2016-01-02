from django.shortcuts import render_to_response, redirect
from ..models import *
from ..tasks import process_node
from db import get_node_on_db

import re, tldextract, ast
import lxml.objectify


def metadata_to_subcluster(m):
    cluster = {
        "name": m.authored_by,
        "id": None,
    }
    try:
        c = Cluster.objects.get(name=m.authored_by)
        cluster["id"] = c.id
    except:
        pass

    subcluster = {
        "name": m.short_description,
        "description": m.description,
        "firstseen": str(m.authored_date),
        "cluster": cluster,
        "id": None,
        "tag":{},
    }
    for link in m.links.link:
        rel = link.attrib.get("rel")
        subcluster["tag"][rel] = link
    try:
        sc = SubCluster.objects.get(name=m.short_description)
        subcluster["id"] = sc.id
    except:
        pass
    return subcluster

def ii_to_ni(ii):
    search = ii.Context.attrib.get("search")
    content = str(ii.Content).strip()
    node = {
        "search": search,
        "content": content,
        "import": False,
        "index": None,
    }
    try:
        it = IOCTerm.objects.get(text=search)
        if it.index:
            ni = it.index
            index = {
                "label": ni.label.name,
                "key": ni.property_key.name,
            }
            node["index"] = index
        if it.allow_import:
            node["import"] = it.allow_import
    except:
        pass

    return node

def indicator_to_node(i, sc):
    if hasattr(i, "IndicatorItem"):
        for ii in i.IndicatorItem:
            n = ii_to_ni(ii)
            if not n in sc["node"]:
                sc["node"].append(n)
    if hasattr(i, "Indicator"):
        i = indicator_to_node(i.Indicator, sc)
    return sc

def pre_import_ioc(file):
    ioco = lxml.objectify.parse(file)
    root = ioco.getroot()
    sc = {}
    if "ioc" in root.tag:
        sc = metadata_to_subcluster(root)
        if sc:
            sc["node"] = []
            sc = indicator_to_node(root.definition, sc)
    elif "OpenIOC" in root.tag:
        sc = metadata_to_subcluster(root.metadata, cluster)
        if sc:
            sc["node"] = []
            sc = indicator_to_node(root.criteria, sc)
    return sc
    

def import_ioc(request):
    if request.method == "POST":
        subcluster = request.POST["subcluster"]
        d = ast.literal_eval(subcluster)
        sc = None
        if "id" in d:
            sid = d["id"]
            try:
                sc = SubCluster.objects.get(pk=sid)
            except:
                pass
        if not sc:
            sc, created = SubCluster.objects.get_or_create(
                name = d["name"],
                description = d["description"],
                firstseen = d["firstseen"],
            )
        for k,v in d["tag"].iteritems():
            key, created = PropertyKey.objects.get_or_create(
                name = k,
            )
            t, created = Tag.objects.get_or_create(
                key = key,
                value = v,
            )
            sc.tag.add(t)
            sc.save()
        if "node" in d:
            nodes = d["node"]
            for node in nodes:
                if "import" in node:
                    if node["import"]:
                        label = None
                        key = None
                        index = None
                        if "index" in node:
                            index = node["index"]
                            if index:
                                if "label" in index:
                                    if index["label"]:
                                        label, created = NodeLabel.objects.get_or_create(
                                            name = index["label"],
                                        )
                                if "key" in index:
                                    if index["key"]:
                                        key, created = PropertyKey.objects.get_or_create(
                                            name = index["key"],
                                        )
                                if key and label:
                                    index, created = NodeIndex.objects.get_or_create(
                                        label = label,
                                        property_key = key,
                                    )
                        property = None
                        if "content" in node:
                            if node["content"]:
                                property, created = Property.objects.get_or_create(
                                    key = key,
                                    value = node["content"],
                                )
                        if label and property and index:
                            n, created = Node.objects.get_or_create(
                                index = index,
                                label = label,
                                key_property = property,
                            )
                            if sc:
                                n.subcluster.add(sc)
                                n.save()
                            from ..tasks import process_node
                            process_node.delay(n, sc)
        if "cluster" in d:
            cluster = d["cluster"]
            c = None
            if "id" in cluster:
                cid = cluster["id"]
                try:
                    c = Cluster.objects.get(pk=cid)
                except:
                    pass
            if not c:
                c, created = Cluster.objects.get_or_create(
                   name = cluster["name"],
                )
            if sc:
                sc.cluster.add(c)
                sc.save()
    return redirect("/subcluster/")

