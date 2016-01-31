from __future__ import absolute_import

import os, re
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
#from django.conf import settings

from .celery import app

from .models import *

from .views.graph import graph_init
from .views.db import get_node_on_db, get_node_on_graph, get_relation_on_graph
from .plugins.hostname import parse_hostname
from .plugins.domain import whois_domain
from .plugins.ipaddress import whois_ip

#@app.task(rate_limit='5/m')
@app.task(soft_time_limit=60)
def process_node(node, subcluster = None):
    #nodetype = str(node.label.name + node.key_property.key.name).lower()
    nodetype = str(node.index.label.name + node.index.property_key.name).lower()
    if re.search("hostname", nodetype):
        parse_hostname(node, subcluster)
    elif re.search("domainname", nodetype):
        whois_domain(node, subcluster)
    elif re.search("ipaddress", nodetype):
        whois_ip(node, subcluster)

def push_node_to_db(node, graph):
    label, = node.labels
    label_key = None
    if graph.schema.get_uniqueness_constraints(str(label)):
       label_key, = graph.schema.get_uniqueness_constraints(str(label))
    n = None
    if label_key:
       label_value = node[label_key]
       ref = node._id
       try:
          n = Node.objects.get(ref=ref)
       except:
          pass
       if n:
          pk,created = PropertyKey.objects.get_or_create(
             name = label_key,
          )
          if pk:
             p, created = Property.objects.get_or_create(
                key = pk,
                value = label_value,
             )
             l, created = NodeLabel.objects.get_or_create(
                name = label
             )
             if p and l:
                n.label = l
                n.key_property = p
                n.properties.add(p)
                n.save()
       else:
          n = get_node_on_db(label, label_key, label_value, node.properties)
          n.ref = ref
          n.save()
    return n

def push_relation_to_db(relation, graph):
    src = push_node_to_db(relation.start_node, graph)
    dst = push_node_to_db(relation.end_node, graph)
    rt, created = RelType.objects.get_or_create(name=relation.type)
    rel = None
    if src and dst and rt:
       rel, created = Relation.objects.get_or_create(type=rt, src=src, dst=dst)
       if rel:
          if relation.properties:
             subcluster = []
             for k, v in relation.properties.iteritems():
                if k == "cluster":
                    if type(v) is list:
                       for i in v:
                          c, created = Cluster.objects.get_or_create(name=i)
                    elif type(v) is str:
                       c, created = Cluster.objects.get_or_create(name=v)
                elif k =="subcluster":
                    if type(v) is list:
                       for i in v:
                          sc, created = SubCluster.objects.get_or_create(name=i)
                          if sc and not sc in subcluster:
                             subcluster.append(sc)
                    elif type(v) is str:
                       sc, created = SubCluster.objects.get_or_create(name=v)
                       if sc and not sc in subcluster:
                          subcluster.append(sc)
                else:
                    pk, created = PropertyKey.objects.get_or_create(name=k)
                    p, created = Property.objects.get_or_create(key=pk, value=v)
                    rel.properties.add(p)
             for s in subcluster:
                rel.subcluster.add(s)
             rel.save()

          rel.ref = int(str(relation.ref).split('/')[1])
          rel.save()
    return rel

@app.task
def push_graph_to_db(postprocess):
    graph = graph_init()
    nodes = graph.cypher.execute("MATCH n return n")
    sg = nodes.to_subgraph()
    for n in sg.nodes:
        node = push_node_to_db(n, graph)
        if node and postprocess:
            for s in node.subcluster.all():
                process_node.delay(node, s)
    relations = graph.cypher.execute("MATCH n-[r]->m return n,r,m")
    for n, r, m in relations:
        rel = push_relation_to_db(r, graph)

@app.task
def push_db_to_graph(entity):
    graph = graph_init()
    nodes = None
    if not entity or entity == "node":
        nodes = Node.objects.all()
    for node in nodes:
       get_node_on_graph(node, graph)

    relations = None
    if not entity == "relation":
        relations = Relation.objects.all()
    for relation in relations:
       get_relation_on_graph(relation, graph)

#if __name__ == '__main__': 
#    app.start()   
