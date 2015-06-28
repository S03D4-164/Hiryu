import tldextract
import socket

from ..models import *
from ..views.db import get_node_on_db
from .domain import whois_domain
from .ipaddress import whois_ip

def create_ip_from_host(hostname):
	addr = None
	try:
		addr = socket.getaddrinfo(hostname, None)
	except:
		return False
	ips = []
	for a in addr:
		ip = a[4][0]
		if not ip in ips:
			ips.append(ip)
	ips = sorted(ips)
	return ips

def parse_hostname(node, subcluster = None):
	hostname =  node.key_property.value


	ips = create_ip_from_host(hostname)
	if ips:
		for i in ips:
			ipn = get_node_on_db("IP", "address", i)
			if ipn:
				h_i = hostname_rel(node, "has_ip", ipn, subcluster)
				whois_ip(ipn, subcluster)

	no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
	ext = no_fetch_extract(hostname)
	domain = ext.domain.encode("utf8") + '.'+ ext.suffix.encode("utf8")
	if domain:
		dn = get_node_on_db("Domain", "name", domain)
		if dn:
			h_d = hostname_rel(node, "has_domain", dn, subcluster)
			w = whois_domain(dn, subcluster)

def hostname_rel(hostname, relname, dst, subcluster):
	type, created = RelType.objects.get_or_create(name=relname)
	rel = None
	if type and hostname and dst:
		rel, created = Relation.objects.get_or_create(
       			type = type,
       			src = hostname,
  		     	dst = dst,
        	)
		if rel and subcluster:
 			rel.subcluster.add(subcluster)
                	rel.save()
                	dst.subcluster.add(subcluster)
                	dst.save()
	return rel
