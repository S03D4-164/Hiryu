from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from ..models import *
from ..forms import *
from .graph import graph_init

def process_request(request):
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
                try:
                    if graph.schema.get_uniqueness_constraints(ln):
                        for k in  graph.schema.get_uniqueness_constraints(ln):
                            graph.schema.drop_uniqueness_constraint(ln, k)
                    graph.schema.create_uniqueness_constraint(ln, kn)
                except:
                    pass
    if "create_ioc" in request.POST:
        tform = IOCTermForm(request.POST)
        print request.POST
        if tform.is_valid():
            term = tform.cleaned_data["iocterm"]
            text = tform.cleaned_data["text"]
            index = tform.cleaned_data["index"]
            allow_import = tform.cleaned_data["allow_import"]
            ioc = None
            if term:
                ioc = term
            elif text:
                ioc, created = IOCTerm.objects.get_or_create(
                    text = text
                )
            print allow_import
            if ioc:
                if index:
                    ioc.index = index
                ioc.allow_import = allow_import
                ioc.save()
    return 

def ioc_schema_list(request):
    iform = IndexForm()
    tform = IOCTermForm()
    if request.method == "POST":
        process_request(request)
        iform = IndexForm(request.POST)
        tform = IOCTermForm(request.POST)
    rc = RequestContext(request, {
        "iform":iform,
        #"rtform":rtform,
        "tform":tform,
        "index":NodeIndex.objects.all(),
        #"reltemplate":RelationTemplate.objects.all(),
        "iocterm":IOCTerm.objects.all(),
    })
    return render_to_response("schema_list.html", rc)



def schema_list(request):
    graph = graph_init()
    iform = IndexForm()
    rtform = RelTemplateForm()
    #tform = IOCTermForm()
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
                    try:
                        if graph.schema.get_uniqueness_constraints(ln):
                            for k in  graph.schema.get_uniqueness_constraints(ln):
                                graph.schema.drop_uniqueness_constraint(ln, k)
                        graph.schema.create_uniqueness_constraint(ln, kn)
                    except:
                        pass
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
        elif "replace_index" in request.POST:
            rtform = RelTemplateForm(request.POST)
            if rtform.is_valid():
                src_index = rtform.cleaned_data["src_index"]
                nodes = Node.objects.filter(label=src_index.label, key_property__key=src_index.property_key)
                dst_index = rtform.cleaned_data["dst_index"]
                for n in nodes:
                    n.index = dst_index
                    n.label = dst_index.label
                    n.key_property.key = dst_index.property_key
                    n.save()

        """
        elif "create_ioc" in request.POST:
            tform = IOCTermForm(request.POST)
            if tform.is_valid():
                text = tform.cleaned_data["text"]
                index = tform.cleaned_data["index"]
                allow_import = tform.cleaned_data["allow_import"]
                ioc, created = IOCTerm.objects.get_or_create(
                    text = text
                )
                if ioc:
                    ioc.index = index
                    ioc.allow_import = allow_import
                    ioc.save()
        """
    rc = RequestContext(request, {
        "iform":iform,
        "rtform":rtform,
        #"tform":tform,
        "index":NodeIndex.objects.all(),
        "reltemplate":RelationTemplate.objects.all(),
        #"iocterm":IOCTerm.objects.all(),
    })
    return render_to_response("schema_list.html", rc)

