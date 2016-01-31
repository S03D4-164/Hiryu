from ipwhois import IPWhois
from datetime import datetime

from ..models import *
from ..views.db import get_node_on_db

def whois_ip(ip, subcluster = None):
    #i = ip.key_property.value
    i = ip.value
    results = None
    try:
        obj = IPWhois(i)
        results = obj.lookup()
    except:
        return False
    if results:
        nets = sorted(results["nets"], key=lambda n:n["cidr"], reverse=True)
        properties = nets[0]
        name = properties["description"].split("\n")[0]
        org = get_node_on_db("Organization", "description", name)
        if org:
            type, created = RelType.objects.get_or_create(name="has_ip")
            if type and org and ip:
                rel, created = Relation.objects.get_or_create(
                    type = type,
                    src = org,
                    dst = ip,
                )
                if created:
                    rel.firstseen = datetime.now()
                    rel.lastseen = datetime.now()
                else:
                    rel.lastseen = datetime.now()
            for k,v in properties.iteritems():
                if k and v:
                    pk, created = PropertyKey.objects.get_or_create(
                       name = k
                    )
                    p, created = Property.objects.get_or_create(
                       key = pk,
                       value = v,
                    )
                    if not p in rel.properties.all():
                        rel.properties.add(p)
                        rel.save()
                if rel and subcluster:
                    if not subcluster in rel.subcluster.all():
                        rel.subcluster.add(subcluster)
                        rel.save()
                    if not subcluster in org.subcluster.all():
                        org.subcluster.add(subcluster)
                        org.save()
