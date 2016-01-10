from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext

from ..models import *
from ..forms import *
from .graph import graph_init
from .db import push_all_to_graph
from .subcluster import create_subcluster
from .ioc_import import import_ioc, pre_import_ioc
from .csv_import import import_cluster

def cluster_list(request):
    form = ClusterForm()
    iform = UploadFileForm()
    if request.method == "POST":
        if "create" in request.POST:
            form = ClusterForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"].strip()
                description = form.cleaned_data["description"]
                firstseen = form.cleaned_data["firstseen"]
                tag = form.cleaned_data["tag"]
                c, created = Cluster.objects.get_or_create(
                    name = name
                )
                if c and created:
                    if description:
                        c.description = description
                    if firstseen:
                        c.firstseen = firstseen
                    if tag:
                        c.tag = tag
                    c.save()
        elif "delete" in request.POST:
            return redirect("/delete/cluster")
        elif "import_csv" in request.POST:
            iform = UploadFileForm(request.POST, request.FILES)
            if iform.is_valid():
                import_cluster(request.FILES['file'])
        elif "import_ioc" in request.POST:
            iform = UploadFileForm(request.POST, request.FILES)
            if iform.is_valid():
                sc = pre_import_ioc(request.FILES['file'])
                if sc:
                    context = {
                        "subcluster":sc,
                        "cluster":sc["cluster"],
                        "node":sc["node"],
                    }
                    return render(request, "import_view.html", context)

    c = {
       "form":form,
       "iform":iform,
    }
    return render(request, "cluster_list.html", c)


def cluster_view(request, id):
    graph = graph_init()
    cluster = Cluster.objects.get(id=id)
    subcluster = SubCluster.objects.filter(cluster=cluster)
    nodes = Node.objects.filter(subcluster__cluster=cluster).distinct()
    relations = Relation.objects.filter(subcluster__cluster=cluster).distinct()
    form = ClusterForm(instance=cluster)
    scform = SubClusterForm()
    iform = UploadFileForm()
    if request.method == "POST":
        if "update" in request.POST:
            form = ClusterForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"].strip()
                description = form.cleaned_data["description"]
                firstseen = form.cleaned_data["firstseen"]
                tag = form.cleaned_data["tag"]
                if name and not name == cluster.name:
                    cluster.name = name
                cluster.description = description
                if firstseen:
                    cluster.firstseen = firstseen
                cluster.tag.clear()
                cluster.tag = tag
                cluster.save()
        elif "delete" in request.POST:
            return redirect("/delete/cluster/" + id)
        elif "push_all" in request.POST:
            push_all_to_graph(nodes, relations, graph)
        elif "create_subcluster" in request.POST:
            scform = SubClusterForm(request.POST)
            if scform.is_valid():
                s = create_subcluster(scform)
                if s:
                    s.cluster.add(cluster)
        elif "import_ioc" in request.POST:
            iform = UploadFileForm(request.POST, request.FILES)
            if iform.is_valid():
                #import_ioc(request.FILES['file'], cluster)
                sc = pre_import_ioc(request.FILES['file'])
                if sc:
                    context = {
                        "subcluster":sc,
                        #"cluster":sc["cluster"],
                        "cluster":cluster,
                        "node":sc["node"],
                    }
                    return render(request, "import_view.html", context)

    c = {
        "form":form,
        "scform":scform,
        "iform":iform,
        "cluster":cluster,
        "subcluster":subcluster,
        "nodes":nodes,
        "relations":relations,
        "model":"cluster",
    }
    return render(request, "cluster_view.html", c)

