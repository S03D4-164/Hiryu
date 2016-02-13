from django.shortcuts import redirect
from ..models import *

import os, logging, datetime

from ioc_writer import ioc_api

log = logging.getLogger(__name__)

appdir =  os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def export_ioc(request, model, id):
    c = None
    nodes = []
    if model == "cluster":
        c = Cluster.objects.get(pk=id)
        nodes = Node.objects.filter(subcluster__cluster=c)
    elif model == "subcluster":
        c = SubCluster.objects.get(pk=id)
        nodes = Node.objects.filter(subcluster=c)
    ioc = None
    if c:
        ioc = ioc_api.IOC(
            name = c.name,
            description = c.description,
            author = None,
        )
        for t in c.tag.all():
            rel = t.key.name
            value = t.value
            ioc.add_link(rel, value)
        top_level_or_node = ioc.top_level_indicator
        for n in nodes:
            index = n.index
            terms = IOCTerm.objects.filter(index=index)
            for term in terms:
                search = term.text
                document = search.split("/")[0]
                condition = "is"
                #content = n.key_property.value
                content = n.value
                content_type = "string"
                ii_node = ioc_api.make_indicatoritem_node(condition, document, search, content_type, content)
                top_level_or_node.append(ii_node)

    out = "/static/export/openioc_" + model + id + ".xml"
    fh = open(appdir + out, "wb")
    xml = ioc.write_ioc_to_string()
    fh.write(xml)
    fh.close()

    return redirect(out)

