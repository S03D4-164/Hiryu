from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q

from ..models import *
from ..forms import *
from db import get_relation_on_graph, add_property_to_entity, \
		remove_property_from_entity, db_view
from graph import graph_init

def relation_list(request):
        rc = db_view(request, "relation")
        return render_to_response("db_list.html", rc)

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
				subcluster = rform.cleaned_data["subcluster"]
				rel.subcluster.clear()
				for s in subcluster:
					rel.subcluster.add(s)
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
	rc = RequestContext(request, {
		"rel":rel,
		"pform":pform,
		"rform":rform,
		"model":"relation",
	})
        return render_to_response("relation_view.html", rc)
