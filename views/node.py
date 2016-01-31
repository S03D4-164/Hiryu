from django.shortcuts import redirect, render
from django.db.models import Q

from ..models import *
from ..forms import *
from .db import add_property_to_entity, remove_property_from_entity, \
    get_node_on_graph
from .entity import db_view
from .graph import graph_init
from .visualize import create_dataset

def node_list(request):
    c = db_view(request, "node")
    return render(request, "db_list.html", c)

def node_view(request, id):
    graph = graph_init()
    node = Node.objects.get(id=id)
    relation = Relation.objects.filter(Q(src=node)|Q(dst=node))
    nform = NodeForm(instance=node)
    pform = PropertyForm()
    if request.method == "POST":
        if "update" in request.POST:
            nform = NodeForm(request.POST)
            if nform.is_valid():
                index = nform.cleaned_data["index"]
                if not node.index == index:
                    node.index = index
                    node.save()
                value = nform.cleaned_data["value"]
                if not node.value == value:
                    node.value = value
                    node.save()
                subcluster = nform.cleaned_data["subcluster"]
                if subcluster:
                    node.subcluster.clear()
                    for s in subcluster:
                        node.subcluster.add(s)
                    node.save()
        elif "delete" in request.POST:
            return redirect("/delete/node/" + id)
        elif "add_property" in request.POST:
            pform = PropertyForm(request.POST)
            if pform.is_valid():
                add_property_to_entity(node, pform)
        elif "remove_property" in request.POST:
            pform = PropertyForm(request.POST)
            if pform.is_valid():
                remove_property_from_entity(node, pform)
        elif "push_entity" in request.POST:
            get_node_on_graph(node, graph)
    d = None
    if "vis" in request.GET:
        vis = request.GET.get("vis")
        if vis == "1":
            d = create_dataset([node], relation, "node", node)
        elif vis == "2":
            d = create_dataset([node], relation, "node", node, anonymize=True)
    c = {
        "node":node,
        "relation":relation,
        "nform":nform,
        "pform":pform,
        "model":"node",
        "dataset":d,
    }
    return render(request, "node_view.html", c)
