from django.shortcuts import redirect, render
from django.contrib import messages

from ..models import *
from ..forms import *
from .graph import graph_init

def tag_list(request):
    tform = TagForm()
    if "create_tag" in request.POST:
        tform = TagForm(request.POST)
        if tform.is_valid():
            key = tform.cleaned_data["key"]
            value = tform.cleaned_data["value"]
            if key and value:
                try:
                    t = Tag.objects.get(
                        key = key,
                        value = value,
                    )
                    #if t:
                    #    t.value = value
                    #    t.save()
                except:
                    t = Tag.objects.create(
                        key = key,
                        value = value,
                    )
                
    c = {
        "tform":tform,
        "tag":Tag.objects.all(),
    }
    return render(request, "tag_list.html", c)
    

def edit_index(request, next=None):
    if "create_index" in request.POST:
        iform = IndexForm(request.POST)
        if iform.is_valid():
            label = iform.cleaned_data["label"]
            key = iform.cleaned_data["property_key"]
            icon = iform.cleaned_data["icon"]
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
                if icon:
                    i.icon = icon
                    i.save()
                ln = label.name
                kn = key.name
                try:
                    if graph.schema.get_uniqueness_constraints(ln):
                        for k in  graph.schema.get_uniqueness_constraints(ln):
                            graph.schema.drop_uniqueness_constraint(ln, k)
                    graph.schema.create_uniqueness_constraint(ln, kn)
                except:
                    pass
    elif "delete_label" in request.POST:
        iform = IndexForm(request.POST)
        try:
            if iform.is_valid():
                label = iform.cleaned_data["label"]
                return redirect("/delete/label/" + str(label.id) + "?next=" + next)
        except Exception as e:
            messages.add_message(request, messages.WARNING, "Error: " + str(e))
    elif "delete_key" in request.POST:
        iform = IndexForm(request.POST)
        try:
            if iform.is_valid():
                key = iform.cleaned_data["property_key"]
                return redirect("/delete/property_key/" + str(key.id) + "?next=" + next)
        except Exception as e:
            messages.add_message(request, messages.WARNING, "Error: " + str(e))
    elif "delete_index" in request.POST:
        index = None
        if next == "/schema/graphdb/":
            rtform = RelTemplateForm(request.POST)
            index = rtform.cleaned_data["src_index"]
        elif next == "/schema/openioc/":
            tform = IOCTermForm(request.POST)
            if tform.is_valid():
                index = tform.cleaned_data["index"]
        if index:
            try:
                return redirect("/delete/index/" + str(index.id) + "?next=" + next)
            except Exception as e:
                messages.add_message(request, messages.WARNING, "Error: " + str(e))
    return

def ioc_schema_list(request):
    iform = IndexForm()
    tform = IOCTermForm()
    if request.method == "POST":
        if "create_index" in request.POST:
            edit_index(request)
        elif "delete_label" in request.POST:
            result = edit_index(request, "/schema/openioc/")
            return result
        elif "delete_key" in request.POST:
            return edit_index(request, "/schema/openioc/")
            return result
        elif "delete_index" in request.POST:
            return edit_index(request, "/schema/openioc/")
            return result
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
        elif "delete_ioc" in request.POST:
            tform = IOCTermForm(request.POST)
            if tform.is_valid():
                term = tform.cleaned_data["iocterm"]
                return redirect("/delete/ioc/" + str(term.id) + "?next=/schema/openioc/")
    c = {
        "iform":iform,
        "tform":tform,
        "index":NodeIndex.objects.all(),
        "iocterm":IOCTerm.objects.all(),
    }
    return render(request, "schema_list.html", c)


def schema_list(request):
    graph = graph_init()
    iform = IndexForm()
    rtform = RelTemplateForm()
    if request.method == "POST":
        if "create_index" in request.POST:
            result = edit_index(request)
        elif "delete_label" in request.POST:
            result = edit_index(request, "/schema/graphdb/")
            if result:
                return result
        elif "delete_key" in request.POST:
            result = edit_index(request, "/schema/graphdb/")
            if result:
                return result
        elif "delete_index" in request.POST:
            result = edit_index(request, "/schema/graphdb/")
            if result:
                return result
        elif "rename_label" in request.POST:
            iform = IndexForm(request.POST)
            if iform.is_valid():
                label = iform.cleaned_data["label"]
                new_label = iform.cleaned_data["new_label"].strip()
                if label and new_label:
                    if not NodeLabel.objects.filter(name=new_label):
                        label.name = new_label
                        label.save()
        elif "rename_key" in request.POST:
            iform = IndexForm(request.POST)
            if iform.is_valid():
                key = iform.cleaned_data["property_key"]
                new_key = iform.cleaned_data["new_key"].strip()
                if key and new_key:
                    if not PropertyKey.objects.filter(name=new_key):
                        key.name = new_key
                        key.save()
        elif "create_template" in request.POST:
            rtform = RelTemplateForm(request.POST)
            try:
                if rtform.is_valid():
                    src_index = rtform.cleaned_data["src_index"]
                    type = rtform.cleaned_data["type"]
                    dst_index = rtform.cleaned_data["dst_index"]
                    rt, created = RelationTemplate.objects.get_or_create(
                        src_index = src_index,
                        type = type,
                        dst_index = dst_index,
                    )
            except Exception as e:
                messages.add_message(request, messages.WARNING, "Error: " + str(e))
        elif "rename_reltype" in request.POST:
            rtform = RelTemplateForm(request.POST)
            if rtform.is_valid():
                type = rtform.cleaned_data["type"]
                new_type = rtform.cleaned_data["new_type"].strip()
                if type and new_type:
                    if not RelType.objects.filter(name=new_type):
                        type.name = new_type
                        type.save()
        elif "replace_index" in request.POST:
            rtform = RelTemplateForm(request.POST)
            try:
                if rtform.is_valid():
                    src_index = rtform.cleaned_data["src_index"]
                    nodes = Node.objects.filter(
                        label=src_index.label,
                        key_property__key=src_index.property_key
                    )
                    dst_index = rtform.cleaned_data["dst_index"]
                for n in nodes:
                    n.index = dst_index
                    n.label = dst_index.label
                    n.key_property.key = dst_index.property_key
                    n.save()
            except Exception as e:
                messages.add_message(request, messages.WARNING, "Error: " + str(e))
        elif "delete_reltype" in request.POST:
            rtform = RelTemplateForm(request.POST)
            try:
                if rtform.is_valid():
                    type = rtform.cleaned_data["type"]
                    return redirect("/delete/reltype/" + str(type.id))
            except Exception as e:
                messages.add_message(request, messages.WARNING, "Error: " + str(e))

    c = {
        "iform":iform,
        "rtform":rtform,
        "index":NodeIndex.objects.all(),
        "reltemplate":RelationTemplate.objects.all(),
    }
    return render(request, "schema_list.html", c)

