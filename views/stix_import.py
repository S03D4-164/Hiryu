from django.shortcuts import redirect
from ..models import *
from ..tasks import process_node
from .db import get_node_on_db

import re, tldextract, ast
import lxml.objectify


def campaign_to_subcluster(c):
    subcluster = {
        "name": c.title,
        #"description": sc.description.value,
        "firstseen": str(c.timestamp),
        #"cluster": cluster,
        #"id": None,
        #"tag":{},
    }
    print subcluster
    """
    for link in m.links.link:
        rel = link.attrib.get("rel")
        subcluster["tag"][rel] = link

    try:
        s = SubCluster.objects.get(name=sc.title)
        subcluster["id"] = s.id
    except:
        pass
    """
    return subcluster


def object_to_node(o):
    node = {"import":True}
    d = o.to_dict()
    p = d["object"]["properties"]
    type = None
    if "xsi:type" in p:
        type = p["xsi:type"]
        node["search"] = type
    index = {}
    if type == "AddressObjectType":
        node["content"] = p["address_value"]
        index["label"] = "IP"
        index["key"] = "address"
    elif type == "HostnameObjectType":
        node["content"] = p["hostname_value"]
        index["label"] = "Host"
        index["key"] = "name"
    elif type == "DomainNameObjectType":
        node["content"] = p["value"]
        #index["label"] = "Domain"
        index["label"] = "Host"
        index["key"] = "name"

    if index:
        node["index"] = index

    """
    search = ii.Context.attrib.get("search")
    content = str(ii.Content).strip()
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
    """

    return node


def obs_to_node(obs, sc):
    for o in obs:
        n = object_to_node(o)
        if not n in sc["node"]:
            sc["node"].append(n)
    #print sc    
            
    """
    if hasattr(i, "IndicatorItem"):
        for ii in i.IndicatorItem:
            n = ii_to_ni(ii)
            if not n in sc["node"]:
                sc["node"].append(n)
    if hasattr(i, "Indicator"):
        i = indicator_to_node(i.Indicator, sc)
    """
    return sc


def pre_import_stix(file, cluster=None):
    from stix.core import STIXPackage  
    pkg = STIXPackage()
    pkg = pkg.from_xml(file)

    reports = pkg.reports
    header = None
    timestamp = ""
    try:
        header = reports[0].header
        timestamp = reports[0].timestamp
    except:
        header = pkg.header
    #sc = header_to_subcluster(header)
    sc = {
        "name": header.title,
        "description": header.description,
        "firstseen": timestamp,
    }

    """
    campaigns= pkg.campaigns
    for campaign in campaigns:
        s = campaign_to_subcluster(campaign)
        if not s in sc:
            sc.append(s)
    """
    #ttp = pkg.ttps
    obs = pkg.observables
    if sc:
        sc["node"] = []
        sc = obs_to_node(obs, sc)
        sc["cluster"] = cluster
        
    return sc
    

def import_stix(request):
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
            for node in d["node"]:
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
                            if "postprocess" in request.POST:
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

