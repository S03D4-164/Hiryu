from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q

from ..models import *
from ..forms import *
from db import add_property_to_entity, remove_property_from_entity, \
		get_node_on_graph, db_view
from graph import graph_init

def node_list(request):
	rc = db_view(request, "node")
        return render_to_response("db_list.html", rc)

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
	rc = RequestContext(request, {
		"node":node,
		"relation":relation,
		"nform":nform,
		"pform":pform,
		"model":"node",
	})
        return render_to_response("node_view.html", rc)
