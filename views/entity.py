from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from py2neo import watch, Graph, Node, Relationship

from ..forms import *
from ..models import *
from .graph import graph_init
from .csv_import import import_node, import_relation
from multiprocessing import Process, Queue

def set_properties_to_node(node, properties):
    cluster = []
    subcluster = []
    for k, v in properties.iteritems():
        if k == "cluster" and v:
            if type(v) is list:
                for i in v:
                    c, created = Cluster.objects.get_or_create(name=i)
                    if c and not c in cluster:
                        cluster.append(c)
            elif type(v) is str:
                c, created = Cluster.objects.get_or_create(name=v)
                if c and not c in cluster:
                    cluster.append(c)
        elif k =="subcluster" and v:
            if type(v) is list:
                for i in v:
                    sc, created = SubCluster.objects.get_or_create(name=i)
                    if sc and not sc in subcluster:
                        subcluster.append(sc)
            elif type(v) is str:
                sc, created = SubCluster.objects.get_or_create(name=v)
                if sc and not sc in subcluster:
                    subcluster.append(sc)
        elif k and v:
            pk, created = PropertyKey.objects.get_or_create(name=k)
            if pk:
                p, created = Property.objects.get_or_create(
                    key = pk,
                    value = v,
                )
                node.properties.add(p)
    for s in subcluster:
        node.subcluster.add(s)
    node.save()
    return node

def get_node_on_db(label, key, value, properties = {}):
    node = None
    nl = None
    if label:
        nl, created = NodeLabel.objects.get_or_create(name=label)
    pk = None
    if key:
        pk, created = PropertyKey.objects.get_or_create(name=key)
    if nl and pk:
        ni, created = NodeIndex.objects.get_or_create(
            label = nl,
            property_key = pk,
        )
        if ni and value:
            pr, created = Property.objects.get_or_create(
                key = pk,
                value = value,
            )
            if pr:
                node, created = Node.objects.get_or_create(
                    index=ni,
                    label=nl,
                    key_property = pr, 
                )
                if not pr in node.properties.all():
                    node.properties.add(pr)
                    node.save()
                if node and properties:
                    node = set_properties_to_node(node, properties)
    return node

def get_node_on_graph(node, graph):
    label = node.label.name
    key = node.key_property.key.name
    value = node.key_property.value
    properties = {}
    for p in node.properties.all():
        properties[p.key.name] = p.value
    sc = []
    c = []
    for subcluster in node.subcluster.all():
        if not subcluster.name in sc:
            sc.append(subcluster.name)
        for cluster in subcluster.cluster.all():
            if not cluster.name in c:
                c.append(cluster.name)
    properties["subcluster"] = None
    if sc:
        properties["subcluster"] = sc
    properties["cluster"] = None
    if c:
        properties["cluster"] = c
    from graphdb import get_node
    n = get_node(graph, label, key, value, properties)
    if n:
        node.ref = n._id
        node.save()
    return n

def relform_to_localdb(relform, graph):
    src_index = relform.cleaned_data["src_index"]
    src_value = relform.cleaned_data["src_value"].strip()
    src_node = None
    if src_index and src_value:
        label = src_index.label
        key = src_index.property_key
        if label and key:
            src_node = get_node_on_db(label, key, src_value)
    src_index = relform.cleaned_data["src_index"]
    dst_index = relform.cleaned_data["dst_index"]
    dst_value = relform.cleaned_data["dst_value"].strip()
    dst_node = None
    if dst_index and dst_value:
        label = dst_index.label
        key = dst_index.property_key
        if label and key:
            dst_node = get_node_on_db(label, key, dst_value)
    src_index = relform.cleaned_data["src_index"]
    reltype = relform.cleaned_data["reltype"]
    rel = None
    if src_node and dst_node and reltype:
        rel, created = Relation.objects.get_or_create(
           type = reltype,
          src = src_node,
          dst = dst_node,
       )
    return src_node, dst_node, rel

def get_relation_on_graph(relation, graph):
    rel = relation.type.name
    src_node = get_node_on_graph(relation.src, graph)
    dst_node = get_node_on_graph(relation.dst, graph)
    r = None
    if src_node and dst_node and rel:
        r, = graph.create_unique(Relationship(src_node, rel, dst_node ))
        if r:
            properties = {}
            for p in relation.properties.all():
                properties[p.key.name] = p.value

            properties["subcluster"] = None
            sc = []
            for s in relation.subcluster.all():
                if s.name not in sc:
                    sc.append(s.name)
            if sc:
                properties["subcluster"] = sc

            properties["cluster"] = None
            cluster = []
            for s in relation.subcluster.all():
                for c in s.cluster.all():
                    if c.name not in cluster:
                        cluster.append(c.name)
            if cluster:
                properties["cluster"] = cluster
            for key in properties:
                r[key] = properties[key]
            r.push()
            relation.ref = int(str(r.ref).split('/')[1])
            relation.save()
    return r

def push_entity_to_graph(eform, graph):
    entity = eform.cleaned_data["entity"]
    id = eform.cleaned_data["id"]
    if entity and id:
        e = None
        if entity == "node":
            node = Node.objects.get(id=id)
            e = get_node_on_graph(node, graph)
        elif entity == "rel":
            rel = Relation.objects.get(id=id)
            e = get_relation_on_graph(rel, graph)
    return e

def delete_entity_from_db(eform, subcluster=None):
    entity = eform.cleaned_data["entity"]
    id = eform.cleaned_data["id"]
    if id:
        e = None
        if entity == "node":
            e = Node.objects.get(id=id)
        elif entity == "rel":
            e = Relation.objects.get(id=id)
        if e:
            if subcluster:
                if subcluster in e.subcluster.all():
                    e.subcluster.remove(subcluster)
                    e.save()
            else:
                e.delete()

def push_all_to_graph(nodes, relations, graph):
    for node in nodes:
        get_node_on_graph(node, graph)
    for relation in relations:
        get_relation_on_graph(relation, graph)

def add_property_to_entity(e, pform):
    key = pform.cleaned_data["key"]
    value = pform.cleaned_data["value"].strip()
    if key and value:
        k, created = PropertyKey.objects.get_or_create(name=key)
        if k:
            property, created = Property.objects.get_or_create(
                key = k,
                value = value,
            )
            for p in e.properties.all():
                if p.key == k:
                    e.properties.remove(p)
            e.properties.add(property)
    e.save()
    return e

def remove_property_from_entity(e, pform):
    key = pform.cleaned_data["key"]
    if key:
        for p in e.properties.all():
            if p.key == key:
                e.properties.remove(p)
    e.save()
    return e

def db_list(request):
    rc = db_view(request)
    return render_to_response("db_list.html", rc)

def db_view(request, entity=None):
    graph = graph_init()
    form = RelCreateForm()
    eform = EntitySelectForm()
    iform = UploadFileForm()
    if request.method == "POST":
        if "create" in request.POST:
            form = RelCreateForm(request.POST)
            if form.is_valid():
                src, dst, rel = relform_to_localdb(form, graph)
                postprocess = form.cleaned_data["postprocess"]
                if postprocess:
                    from ..tasks import process_node
                    if src:
                        process_node.delay(src)
                    if dst:
                        process_node.delay(dst)
        elif "import" in request.POST:
            iform = UploadFileForm(request.POST, request.FILES)
            if iform.is_valid():
                if entity == "node":
                    import_node(request.FILES['file'])
                elif entity == "relation":
                    import_relation(request.FILES['file'])
        elif "push" in request.POST:
            eform = EntitySelectForm(request.POST)
            if eform.is_valid():
                push_entity_to_graph(eform, graph)
        elif "delete" in request.POST:
            eform = EntitySelectForm(request.POST)
            if eform.is_valid():
                delete_entity_from_db(eform)
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
    if not entity:
        entity = "db"
    c = {
        "form":form,
        "iform":iform,
        "eform":eform,
        "nodes":nodes,
        "relations":relations,
        "model":entity,
    }
    return c
