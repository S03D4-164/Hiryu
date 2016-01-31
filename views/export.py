from django.shortcuts import redirect
from ..models import Cluster, SubCluster, Node, Relation

import csv, os

appdir =  os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def export_cluster(request, id=None):
    cluster = Cluster.objects.all()
    fieldnames = (
        "name",
        "description",
        "firstseen",
        "tag_key",
        "tag_value",
    )
    out = "/static/export/cluster_all.csv"
    writer = csv.DictWriter(open(appdir + out, "wb"), fieldnames)
    writer.writeheader()
    for c in cluster:
        dict = {
            "name":c.name.encode("utf8"),
            "description":None,
            "firstseen":c.firstseen,
            "tag_key":None,
            "tag_value":None,
        }
        if c.description:
            dict["description"] = c.description.encode("utf-8")
        tag = c.tag.all()
        if tag:
            for t in tag:
                dict["tag_key"] = t.key.name.encode("utf-8")
                dict["tag_value"] = t.value.encode("utf-8")
                writer.writerow(dict)
        else:
            writer.writerow(dict)
    return redirect(out)

    
def export_subcluster(request, id=None):
    subcluster = SubCluster.objects.all()
    fieldnames = (
        "sc_name",
        "sc_description",
        "sc_firstseen",
        "sc_tag_key",
        "sc_tag_value",
        "c_name",
        "c_description",
        "c_firstseen",
        "c_tag_key",
        "c_tag_value",
    )
    out = "/static/export/subcluster_all.csv"
    writer = csv.DictWriter(open(appdir + out, "wb"), fieldnames)
    writer.writeheader()
    for s in subcluster:
        dict = {
            "sc_name":s.name.encode("utf8"),
            "sc_description":None,
            "sc_firstseen":s.firstseen,
            "sc_tag_key":None,
            "sc_tag_value":None,
            "c_name":None,
            "c_description":None,
            "c_firstseen":None,
            "c_tag_key":None,
            "c_tag_value":None,
        }
        if s.description:
            dict["sc_description"] = s.description.encode("utf-8")
        tag = s.tag.all()
        if tag:
            for t in tag:
                dict["sc_tag_key"] = t.key.name.encode("utf-8")
                dict["sc_tag_value"] = t.value.encode("utf-8")
                writer.writerow(dict)
        else:
            writer.writerow(dict)
        dict["sc_tag_key"] = None
        dict["sc_tag_value"] = None
        cluster = s.cluster.all()
        if cluster:
            for c in cluster:
                dict["c_name"] = c.name.encode("utf-8")
                dict["c_firstseen"] = c.firstseen
                if c.description:
                    dict["c_description"] = c.description.encode("utf-8")
                if c.tag.all():
                    for t in c.tag.all():
                        dict["c_tag_key"] = t.key.name.encode("utf-8")
                        dict["c_tag_value"] = t.value.encode("utf-8")
                        writer.writerow(dict)
                else:
                    writer.writerow(dict)
        else:
                writer.writerow(dict)
    return redirect(out)


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
        "primary_key",
        "primary_value",
        "property_key",
        "property_value",
        "subcluster",
        "cluster",
    )
    out = None
    if not model:
        out = "/static/export/node_all.csv"
    else:
        out = "/static/export/node_" + model + id + ".csv"
    writer = csv.DictWriter(open(appdir + out, "wb"), fieldnames)
    writer.writeheader()
    for n in node:
        dict = {
            #"node_label":n.label.name.encode("utf8"),
            "node_label":n.index.label.name.encode("utf8"),
            "primary_key":n.index.property_key.name.encode("utf8"),
            "primary_value":n.value.encode("utf8"),
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
    out = None
    if not model:
        out = "/static/export/relation_all.csv"
    else:
        out = "/static/export/relation_" + model + id + ".csv"
    writer = csv.DictWriter(open(appdir + out, "wb"), fieldnames)
    writer.writeheader()
    for r in rel:
        dict = {
            "src_label":r.src.index.label.name.encode("utf8"),
            "src_key":r.src.index.property_key.name.encode("utf8"),
            "src_value":r.src.value.encode("utf8"),
            "rel_type":r.type.name.encode("utf8"),
            "property_key":None,
            "property_value":None,
            "dst_label":r.dst.index.label.name.encode("utf8"),
            "dst_key":r.dst.index.property_key.name.encode("utf8"),
            "dst_value":r.dst.value.encode("utf8"),
            "subcluster":None,
            "cluster":None,
        }
        write_entity_to_csv(cluster, subcluster, r, dict, writer)
    return redirect(out)
