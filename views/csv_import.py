from ..celery import app

from django.shortcuts import redirect
from ..models import *
from ..forms import UploadFileForm
from .db import get_node_on_db

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

def import_cluster(files):
    fieldnames = (
        "name",
        "description",
        "firstseen",
        "tag_key",
        "tag_value",
    )
    reader = csv.DictReader(files)
    for r in reader:
        cluster = None
        if r["name"]:
            cluster, created = Cluster.objects.get_or_create(
                name = r["name"] 
            )
        if cluster:
            if not cluster.description and r["description"]:
                cluster.description = r["description"]
            if not cluster.firstseen and r["firstseen"]:
                cluster.firstseen = r["firstseen"]
            if r["tag_key"] and r["tag_value"]:
                pkey, created = PropertyKey.objects.get_or_create(
                    name = r["tag_key"],
                )
                tag = None
                if pkey:
                    tag, created = Tag.objects.get_or_create(
                        key = pkey,
                        value = r["tag_value"],
                    )
                if tag:
                    cluster.tag.add(tag)
            cluster.save()
    return redirect("/cluster/")

def import_subcluster(files):
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
    reader = csv.DictReader(files)
    for r in reader:
        subcluster, created = SubCluster.objects.get_or_create(
           name = r["sc_name"] 
        )
        if subcluster:
            if not subcluster.description and r["sc_description"]:
                subcluster.description = r["sc_description"]
            if not subcluster.firstseen and r["sc_firstseen"]:
                subcluster.firstseen = r["sc_firstseen"]
            if r["sc_tag_key"] and r["sc_tag_value"]:
                pkey, created = PropertyKey.objects.get_or_create(
                    name = r["sc_tag_key"],
                )
                tag = None
                if pkey:
                    tag, created = Tag.objects.get_or_create(
                        key = pkey,
                        value = r["sc_tag_value"],
                    )
                if tag:
                    subcluster.tag.add(tag)
            subcluster.save()

        cluster = None
        if r["c_name"]:
            cluster, created = Cluster.objects.get_or_create(
               name = r["c_name"] 
            )
        if cluster:
            if not cluster.description and r["c_description"]:
                cluster.description = r["c_description"]
            if not cluster.firstseen and r["c_firstseen"]:
                cluster.firstseen = r["c_firstseen"]
            if r["c_tag_key"] and r["c_tag_value"]:
                pkey, created = PropertyKey.objects.get_or_create(
                    name = r["c_tag_key"],
                )
                tag = None
                if pkey:
                    tag, created = Tag.objects.get_or_create(
                        key = pkey,
                        value = r["c_tag_value"],
                    )
                if tag:
                    cluster.tag.add(tag)
            cluster.save()
            subcluster.cluster.add(cluster)
            subcluster.save()

    return redirect("/cluster/")

@app.task
def import_node(files):
    fieldnames = (
        "node_label",
        "primary_key",
        "primary_value",
        "property_key",
        "property_value",
        "created",
        "subcluster",
        "cluster",
    )
    #reader = csv.DictReader(files, fieldnames)
    reader = csv.DictReader(files)
    for r in reader:
        node = get_node_on_db(
            r["node_label"],
            r["primary_key"],
            r["primary_value"],
        )
        if node:
            if r["created"]:
                node.created = r["created"]
                node.save()
            if r["property_key"] and r["property_value"]:
                node = set_property_to_entity(node, r["property_key"], r["property_value"])
            if r["subcluster"]:
                node = set_subcluster_to_entity(node, r["subcluster"], r["cluster"])
    return redirect("/node/")

@app.task
def import_relation(files):
    fieldnames = (
        "src_label",
        "src_key",
        "src_value",
        "rel_type",
        "firstseen",
        "lastseen",
        "property_key",
        "property_value",
        "dst_label",
        "dst_key",
        "dst_value",
        "subcluster",
        "cluster",
    )
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
                    if r["firstseen"]:
                        rel.firstseen = r["firstseen"]
                        rel.save()
                    if r["lastseen"]:
                        rel.lastseen = r["lastseen"]
                        rel.save()
                    if r["property_key"] and r["property_value"]:
                        rel = set_property_to_entity(rel, r["property_key"], r["property_value"])
                    if r["subcluster"]:
                        rel = set_subcluster_to_entity(rel, r["subcluster"], r["cluster"])        
                        src = set_subcluster_to_entity(src, r["subcluster"], r["cluster"])        
                        dst = set_subcluster_to_entity(dst, r["subcluster"], r["cluster"])        
    return redirect("/relation/")
