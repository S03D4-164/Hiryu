from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..models import *
from ..forms import *
from ..postprocess import process_node
from db import push_all_to_graph, get_node_on_db, relform_to_localdb
from graph import graph_init

def create_subcluster(form):
	name = form.cleaned_data["name"].strip()
	description = form.cleaned_data["description"]
	firstseen = form.cleaned_data["firstseen"]
	cluster = form.cleaned_data["cluster"]
	s, created = SubCluster.objects.get_or_create(
		name = name
	)
	if s:
		if description:
			s.description = description
		if firstseen:
			s.firstseen = firstseen
		s.cluster.clear()
		for c in cluster:
			s.cluster.add(c)
		s.save()
	return s

def subcluster_list(request):
	form = SubClusterForm()
	if request.method == "POST":
		if "create" in request.POST:
			form = SubClusterForm(request.POST)
			if form.is_valid():
				s = create_subcluster(form)
	subcluster = SubCluster.objects.all().order_by("-id")
	rc = RequestContext(request, {
                "form":form,
                "subcluster":subcluster,
        })
        return render_to_response("subcluster_list.html", rc)

def subcluster_view(request, id):
	subcluster = SubCluster.objects.get(id=id)
	nodes = Node.objects.filter(subcluster=subcluster)
	relations = Relation.objects.filter(subcluster=subcluster)
	form = SubClusterForm(instance=subcluster)
	eform = EntityForm()
        tform = TemplateForm()
        relform = RelCreateForm()
	graph = graph_init()
	if request.method == "POST":
		if "update" in request.POST:
			form = SubClusterForm(request.POST)
			if form.is_valid():
				name = form.cleaned_data["name"].strip()
				description = form.cleaned_data["description"]
				firstseen = form.cleaned_data["firstseen"]
				cluster = form.cleaned_data["cluster"]
				if name and not name == subcluster.name:
					subcluster.name = name
				if description:
					subcluster.description = description
				if firstseen:
					subcluster.firstseen = firstseen
				subcluster.cluster.clear()
				for c in cluster:
					subcluster.cluster.add(c)
				subcluster.save()
		elif "delete" in request.POST:
			return redirect("/delete/subcluster/" + id)
		elif "create" in request.POST:
			relform = RelCreateForm(request.POST)
			if relform.is_valid():
				src_node, dst_node, rel = relform_to_localdb(relform, graph)
				postprocess = relform.cleaned_data["postprocess"]
				if src_node:
					src_node.subcluster.add(subcluster)
					src_node.save()
					if postprocess:
						process_node.delay(src_node, subcluster)
				if dst_node:
					dst_node.subcluster.add(subcluster)
					dst_node.save()
					if postprocess:
						process_node.delay(dst_node, subcluster)
			        if rel:
                        		rel.subcluster.add(subcluster)
                        		rel.save()
		elif "create_relation" in request.POST:
			tform = TemplateForm(request.POST)
			if tform.is_valid():
				rel_template = tform.cleaned_data["rel_template"]
				src_value = tform.cleaned_data["src_value"].strip()
				dst_value = tform.cleaned_data["dst_value"].strip()
				postprocess = tform.cleaned_data["postprocess"]
				src = {
					"label":rel_template.src_index.label.name,
					"key":rel_template.src_index.property_key.name,
					"value":src_value,
				}
				src_node = get_node_on_db(src["label"], src["key"], src["value"])
				if src_node:
					src_node.subcluster.add(subcluster)
					src_node.save()
					if postprocess:
						process_node.delay(src_node, subcluster)
				dst = {
					"label":rel_template.dst_index.label.name,
					"key":rel_template.dst_index.property_key.name,
					"value":dst_value,
				}
				dst_node = get_node_on_db(dst["label"], dst["key"], dst["value"])
				if dst_node:
					dst_node.subcluster.add(subcluster)
					dst_node.save()
					if postprocess:
						process_node.delay(dst_node, subcluster)
        			rel = rel_template.type.name
        			if src_node and dst_node and rel:
					rt, created = RelType.objects.get_or_create(name=rel)
					if rt:
						relation, created = Relation.objects.get_or_create(
							type = rt,
							src = src_node,
							dst = dst_node,
						)
						if relation:
							relation.subcluster.add(subcluster)
							relation.save()
                elif "remove_all" in request.POST:
			for n in nodes:
				n.subcluster.remove(subcluster)
				n.save()
			for r in relations:
				r.subcluster.remove(subcluster)
				r.save()
                elif "delete_all" in request.POST:
			for n in nodes:
				n.subcluster.remove(subcluster)
				if not n.subcluster.all():
					n.delete()
			for r in relations:
				r.subcluster.remove(subcluster)
				if not r.subcluster.all():
					r.delete()
			return redirect("/subcluster/"+str(id))
                elif "push_all" in request.POST:
			push_all_to_graph(nodes, relations, graph)
	rc = RequestContext(request, {
                "form":form,
                "tform":tform,
                "relform":relform,
                "cluster":subcluster,
                "nodes":nodes,
                "relations":relations,
                "model":"subcluster",
        })
        return render_to_response("subcluster_view.html", rc)
