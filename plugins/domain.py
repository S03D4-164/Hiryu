from pythonwhois import get_whois

from ..models import *
from ..views.db import get_node_on_db

def whois_domain(domain, subcluster = None):
	d = domain.key_property.value
	w = None
	try:
		w = get_whois(d)
	except:
		return False
	properties = w["contacts"]["registrant"]
	print properties
	if properties:
		if not "email" in properties:
			return False
		reg = get_node_on_db("Registrant", "email", properties["email"])
		if reg:
	        	type, created = RelType.objects.get_or_create(name="registered")
		        if type and reg and domain:
        	        	rel, created = Relation.objects.get_or_create(
                	        	type = type,
                		        src = reg,
                        		dst = domain
                		)
				for k,v in properties.iteritems():
	                                if k and v:
                                       		pk, created = PropertyKey.objects.get_or_create(
                                               		name = k
                                                )
                                                p, created = Property.objects.get_or_create(
                                               		key = pk,
                                                        value = v,
                                                )
                                                rel.properties.add(p)

				if rel and subcluster:
					rel.subcluster.add(subcluster)
					rel.save()
					reg.subcluster.add(subcluster)
					reg.save()

