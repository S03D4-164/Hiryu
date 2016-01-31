from django.shortcuts import redirect, render
from django.db.models import Q

from ..models import *
from ..forms import *
from .db import get_relation_on_graph, add_property_to_entity, \
    remove_property_from_entity
from .entity import db_view
from .graph import graph_init
from .visualize import create_dataset

def relation_list(request):
    c = db_view(request, "relation")
    return render(request, "db_list.html", c)

def relation_view(request, id):
    graph = graph_init()
    rel = Relation.objects.get(id=id)
    pform = PropertyForm()
    rform = RelEditForm(instance=rel)
    if request.method == "POST":
        if "update" in request.POST:
            rform = RelEditForm(request.POST)
            if rform.is_valid():
                type = rform.cleaned_data["type"]
                if type:
                    rel.type = type
                fs = rform.cleaned_data["firstseen"]
                rel.firstseen = fs
                ls = rform.cleaned_data["lastseen"]
                rel.lastseen = ls
                subcluster = rform.cleaned_data["subcluster"]
                rel.subcluster.clear()
                for s in subcluster:
                    rel.subcluster.add(s)
                    src = rel.src
                    src.subcluster.add(s)
                    src.save()
                    dst = rel.dst
                    dst.subcluster.add(s)
                    dst.save()
                rel.save()
        elif "delete" in request.POST:
            return redirect("/delete/relation/" + id)
        elif "add_property" in request.POST:
            pform = PropertyForm(request.POST)
            if pform.is_valid():
                add_property_to_entity(rel, pform)
        elif "remove_property" in request.POST:
            pform = PropertyForm(request.POST)
            if pform.is_valid():
                remove_property_from_entity(rel, pform)
        elif "push_entity" in request.POST:
            get_relation_on_graph(rel, graph)
    d = None
    if "vis" in request.GET:
        vis = request.GET.get("vis")
        if vis == "1":
            d = create_dataset([rel.src, rel.dst], [rel], "relation", rel)
        elif vis == "2":
            d = create_dataset([rel.src, rel.dst], [rel], "relation", rel, anonymize=True)
    c = {
        "rel":rel,
        "pform":pform,
        "rform":rform,
        "model":"relation",
        "dataset":d,
    }
    return render(request, "relation_view.html", c)
