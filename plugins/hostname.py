import tldextract
import socket

from ..models import *
from ..views.db import get_node_on_db
from .domain import whois_domain
from .ipaddress import whois_ip

ip_key = "IP"
ip_label = "address"
rel_host_ip = "has_ip"

dom_key = "Domain"
dom_label = "name"
rel_host_dom = "has_domain"

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
            #ipn = get_node_on_db("IP", "address", i)
            ipn = get_node_on_db(ip_key, ip_label, i)
            if ipn:
                #h_i = hostname_rel(node, "has_ip", ipn, subcluster)
                h_i = hostname_rel(node, rel_host_ip, ipn, subcluster)
                whois_ip(ipn, subcluster)

    no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
    ext = no_fetch_extract(hostname)
    domain = ext.domain.encode("utf8") + '.'+ ext.suffix.encode("utf8")
    if domain:
        #dn = get_node_on_db("Domain", "name", domain)
        dn = get_node_on_db(dom_key, dom_label, domain)
        if dn:
            #h_d = hostname_rel(node, "has_domain", dn, subcluster)
            h_d = hostname_rel(node, rel_host_dom, dn, subcluster)
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
            if not subcluster in rel.subcluster.all():
                rel.subcluster.add(subcluster)
                rel.save()
            if not subcluster in dst.subcluster.all():
                dst.subcluster.add(subcluster)
                dst.save()
    return rel
