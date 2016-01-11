from django.shortcuts import redirect, render
from django.db.models import Q

from ..models import *
from ..forms import *
from .graph import graph_init

def delete_view(request, model, id=None):
    target = None
    sc = None
    node = None
    relation = None
    index = None
    property = None
    if model == "cluster":
        if id:
            target = Cluster.objects.get(pk=id)
            sc = SubCluster.objects.filter(cluster=id)
            node = Node.objects.filter(subcluster=sc)
            relation = Relation.objects.filter(subcluster=sc)
        else:
            target = Cluster.objects.all()
    elif model == "subcluster":
        if id:
            target = SubCluster.objects.get(pk=id)
            node = Node.objects.filter(subcluster=target)
            relation = Relation.objects.filter(subcluster=target)
        else:
            target = SubCluster.objects.all()
    elif model == "property_key":
        target = PropertyKey.objects.get(pk=id)
        property = Property.objects.filter(key=target)
        node = Node.objects.filter(key_property__in=property)
    elif model == "label":
        target = NodeLabel.objects.get(pk=id)
        index = NodeIndex.objects.filter(label=target)
        node = Node.objects.filter(label=target)
    elif model == "index":
        target = NodeIndex.objects.get(pk=id)
    elif model == "reltype":
        target = RelType.objects.get(pk=id)
        relation = Relation.objects.filter(type=target)
    elif model == "node":
        if id:
            target = Node.objects.get(pk=id)
            relation = Relation.objects.filter(Q(src=target)|Q(dst=target))
    elif model == "relation":
        if id:
            target = Relation.objects.get(pk=id)
            node = [target.src, target.dst]
    elif model == "db":
        target = {
            "id":"-",
            "name":"Local DB",
        }
    elif model == "graphdb":
        target = {
            "id":"-",
            "name":"Graph DB",
        }
    elif model == "ioc":
        target = OpenIOC.objects.get(pk=id)

    if request.method == "POST":
        if "return" in request.POST:
            if model in ("cluster", "subcluster", "node", "relation"):
                if id:
                    return redirect("/" + model + "/" + id)
                else:
                    return redirect("/" + model + "/")
            elif model == "db" or model == "graphdb":
                return redirect("/" + model)
            else:
                return redirect("/schema/graphdb/")
        elif "delete" in request.POST:
            if id:
                target.delete()
            else:
                if model == "cluster" or model == "db":
                    for c in Cluster.objects.all():
                        c.delete()
                if model == "subcluster" or model == "db":
                    for s in SubCluster.objects.all():
                        s.delete()
                if model == "node" or model == "db":
                    for n in Node.objects.all():
                        n.delete()
                if model == "relation" or model == "db":
                    for r in Relation.objects.all():
                        r.delete()
                if model == "db":
                    for p in Property.objects.all():
                        p.delete()
                if model == "graphdb":
                    graph = graph_init()
                    graph.delete_all()

            if model in ("cluster", "subcluster", "db", "graphdb", "node", "relation"):
                return redirect("/" + model)
            else:
                return redirect("/schema/graphdb/")
    c = {
        "model":model,
        "target":target,
        "sc":sc,
        "node":node,
        "relation":relation,
        "index":index,
        "property":property,
    }
    return render(request, "delete_view.html", c)

