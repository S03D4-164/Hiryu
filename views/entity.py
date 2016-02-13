from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib import messages

from py2neo import watch, Graph, Node, Relationship

from ..forms import *
from ..models import *
from .graph import graph_init
from .csv_import import import_node, import_relation
from .ioc_import import import_ioc, pre_import_ioc
from .stix_import import pre_import_stix
from .db import relform_to_localdb
from .schema import edit_index

from multiprocessing import Process, Queue


def db_list(request):
    if "import_ioc" in request.POST:
        ufform = UploadFileForm(request.POST, request.FILES)
        if ufform.is_valid():
            sc = None
            try:
                sc = pre_import_ioc(request.FILES['file'])
            except Exception as e:
                messages.add_message(request, messages.WARNING, str(type(e)) + ": "+ str(e))
            if sc:
                context = {
                    "subcluster":sc,
                    "cluster":sc["cluster"],
                    "node":sc["node"],
                }
                return render(request, "import_view.html", context)
    elif "import_stix" in request.POST:
        iform = UploadFileForm(request.POST, request.FILES)
        if iform.is_valid():
            sc = pre_import_stix(request.FILES['file'])
            if sc:
                context = {
                    "subcluster":sc,
                    "cluster":sc["cluster"],
                    "node":sc["node"],
                }
                return render(request, "import_stix.html", context)
            else:
                messages.add_message(request, messages.WARNING, "Import failed: Invalid file.")


    c = db_view(request)
    return render(request, "db_list.html", c)

def db_view(request, entity=None):
    graph = graph_init()
    rcform = RelCreateForm()
    rtform = RelTemplateForm()
    esform = EntitySelectForm()
    ufform = UploadFileForm()
    iform = IndexForm()
    if request.method == "POST":
        if "create" in request.POST:
            rcform = RelCreateForm(request.POST)
            if rcform.is_valid():
                src, dst, rel = relform_to_localdb(rcform, graph)
                postprocess = rcform.cleaned_data["postprocess"]
                if postprocess:
                    from ..tasks import process_node
                    if src:
                        process_node.delay(src)
                    if dst:
                        process_node.delay(dst)
        elif "create_index" in request.POST:
            iform = IndexForm(request.POST)
            if iform.is_valid():
                edit_index(request)
        elif "create_template" in request.POST:
            rtform = RelTemplateForm(request.POST)
            if rtform.is_valid():
                edit_index(request)
        elif "import_node" in request.POST:
            ufform = UploadFileForm(request.POST, request.FILES)
            if ufform.is_valid():
                p = ufform.cleaned_data["postprocess"]
                import_node.delay(request.FILES['file'], p)
        elif "import_relation" in request.POST:
            ufform = UploadFileForm(request.POST, request.FILES)
            if ufform.is_valid():
                p = ufform.cleaned_data["postprocess"]
                import_relation.delay(request.FILES['file'], p)
        elif "push" in request.POST:
            esform = EntitySelectForm(request.POST)
            if esform.is_valid():
                push_entity_to_graph(esform, graph)
        elif "delete" in request.POST:
            esform = EntitySelectForm(request.POST)
            if esform.is_valid():
                delete_entity_from_db(esform)
        elif "push_all" in request.POST:
            from ..tasks import push_db_to_graph
            push_db_to_graph.delay(entity)
        elif "delete_all" in request.POST:
            if entity == "node":
                return redirect("/delete/node/")
            elif entity == "relation":
                return redirect("/delete/relation/")
            else:
                return redirect("/delete/db/")
    nodes = None
    if not entity or entity == "node":
        nodes = Node.objects.all().order_by("-id")
    relations = None
    if not entity or entity == "relation":
        relations = Relation.objects.all().order_by("-id")
    """
    index = NodeIndex.objects.all().order_by("-id")
    reltemplate = RelationTemplate.objects.all().order_by("-id")
    """
    if not entity:
        entity = "db"
    c = {
        "rcform":rcform,
        "rtform":rtform,
        "esform":esform,
        "ufform":ufform,
        "iform":iform,
        "nodes":nodes,
        #"index":index,
        "relations":relations,
        "model":entity,
    }
    return c
