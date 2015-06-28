from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..models import *
from ..forms import *
from graph import graph_init

def schema_list(request):
	graph = graph_init()
	iform = IndexForm()
	rtform = RelTemplateForm()
	if request.method == "POST":
		if "create_index" in request.POST:
			iform = IndexForm(request.POST)
			if iform.is_valid():
				label = iform.cleaned_data["label"]
				key = iform.cleaned_data["property_key"]
				i = None
				if label and key:
					try:
						i = NodeIndex.objects.get(
							label = label,
						)
						i.property_key = key
						i.save()
					except:
						i = NodeIndex.objects.create(
							label = label,
							property_key = key,
						)
					ln = label.name
					kn = key.name
					if graph.schema.get_uniqueness_constraints(ln):
						for k in  graph.schema.get_uniqueness_constraints(ln):
							graph.schema.drop_uniqueness_constraint(ln, k)
                        		graph.schema.create_uniqueness_constraint(ln, kn)
		elif "rename_label" in request.POST:
			iform = IndexForm(request.POST)
			if iform.is_valid():
				label = iform.cleaned_data["label"]
				new_label = iform.cleaned_data["new_label"].strip()
				if label and new_label:
					if not NodeLabel.objects.filter(name=new_label):
						label.name = new_label
						label.save()
		elif "delete_label" in request.POST:
			iform = IndexForm(request.POST)
			if iform.is_valid():
				label = iform.cleaned_data["label"]
				return redirect("/delete/label/" + str(label.id))
		elif "rename_key" in request.POST:
			iform = IndexForm(request.POST)
			if iform.is_valid():
				key = iform.cleaned_data["property_key"]
				new_key = iform.cleaned_data["new_key"].strip()
				if key and new_key:
					if not PropertyKey.objects.filter(name=new_key):
						key.name = new_key
						key.save()
		elif "delete_key" in request.POST:
			iform = IndexForm(request.POST)
			if iform.is_valid():
				key = iform.cleaned_data["property_key"]
				return redirect("/delete/property_key/" + str(key.id))
		elif "delete_index" in request.POST:
			rtform = RelTemplateForm(request.POST)
			if rtform.is_valid():
				index = rtform.cleaned_data["src_index"]
				return redirect("/delete/index/" + str(index.id))
		elif "rename_reltype" in request.POST:
			rtform = RelTemplateForm(request.POST)
			if rtform.is_valid():
				type = rtform.cleaned_data["type"]
				new_type = rtform.cleaned_data["new_type"].strip()
				if type and new_type:
					if not RelType.objects.filter(name=new_type):
						type.name = new_type
						type.save()
		elif "delete_reltype" in request.POST:
			rtform = RelTemplateForm(request.POST)
			if rtform.is_valid():
				type = rtform.cleaned_data["type"]
				return redirect("/delete/reltype/" + str(type.id))
		elif "create_template" in request.POST:
			rtform = RelTemplateForm(request.POST)
			if rtform.is_valid():
				src_index = rtform.cleaned_data["src_index"]
				type = rtform.cleaned_data["type"]
				dst_index = rtform.cleaned_data["dst_index"]
				rt, created = RelationTemplate.objects.get_or_create(
					src_index = src_index,
					type = type,
					dst_index = dst_index,
				)
	rc = RequestContext(request, {
                "iform":iform,
                "rtform":rtform,
		"index":NodeIndex.objects.all(),
		"reltemplate":RelationTemplate.objects.all(),
        })
        return render_to_response("schema_list.html", rc)

