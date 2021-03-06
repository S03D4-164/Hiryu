from django.shortcuts import redirect
from ..models import *

import os
from stix.indicator.indicator import Indicator
from stix.common.information_source import InformationSource

from stix.core import STIXPackage
from stix.core.stix_header import STIXHeader
from stix.report import Report
from stix.report.header import Header
from stix.campaign import Campaign
from cybox.objects.address_object import Address
from cybox.objects.hostname_object import Hostname
from cybox.objects.domain_name_object import DomainName
from cybox.objects.file_object import File
from cybox.common.hashes import Hash
from stix.common.related import RelatedIndicator
from stix.common import CampaignRef
from stix.common.related import RelatedCampaignRef
from stix.utils import set_id_namespace
#from mixbox.idgen import IDGenerator, set_id_namespace
#from mixbox.namespaces import Namespace

appdir =  os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def create_package():
    pkg = STIXPackage()
    return pkg


def create_header(source):
    header = STIXHeader()
    header.information_source = InformationSource(source)
    return header


def create_report(source=None, intent=None):
    report = Report()

    header = Header()
    header.information_source = InformationSource(source)
    header.add_intent("Indicators")
    report.header = header

    return report


def create_campaign(title=None, description=None):
    campaign = Campaign()
    campaign.title = title
    campaign.add_description(description)
    return campaign


def iplist_indicator(ips=[]):
    iplist = Indicator()
    iplist.add_indicator_type("IP Watchlist")

    for i in ips:
        address = Address()
        address.address_value = i 
        #address.category="ipv4-addr"
        iplist.add_observable(address)

    return iplist


def hostchars_indicator(hostnames=[]):
    hostchars = Indicator()
    hostchars.add_indicator_type("Host Characteristics")

    for h in hostnames:
        hostname = Hostname()
        hostname.hostname_value = h
        hostchars.add_observable(hostname)

    return hostchars


def domainlist_indicator(domains=[]):
    domainlist = Indicator()
    domainlist.add_indicator_type("Domain Watchlist")

    for d in domains:
        domain = DomainName()
        domain.value = d
        domainlist.add_observable(domain)

    return domainlist


def hash_indicator(hashes=[]):
    hashlist = Indicator()
    hashlist.add_indicator_type("File Hash Watchlist")

    for h in hashes:
        file = File()
        hash = Hash(
            hash_value = h,
            #type_ = "MD5",
        )
        file.add_hash(hash)
        hashlist.add_observable(file)

    return hashlist


def add_relindicators_to_campaign(indicators, campaign):
    for i in indicators:
        r = RelatedIndicator(i)
        campaign.related_indicators.append(r)
    

def add_relcampaign_to_indicators(campaign, indicators):
    relcampaign = RelatedCampaignRef(CampaignRef(idref=campaign.id_))
    for i in indicators:
        i.related_campaigns.append(relcampaign)
    return indicators


def add_indicators_to_pkg(indicators, pkg):
    for i in indicators:
        pkg.add_indicator(i)
    return pkg


def add_obs_to_pkg(obs, pkg):

    if "ip" in obs:
        for i in obs["ip"]:
            address = Address()
            address.address_value = i 
            pkg.add_observable(address)
    if "host" in obs:
        for h in obs["host"]:
            hostname = Hostname()
            hostname.hostname_value = h
            pkg.add_observable(hostname)
    if "domain" in obs:
        for d in obs["domain"]:
            domain = DomainName()
            domain.value = d
            pkg.add_observable(domain)

    return pkg


def export_stix(request, model, id):
    c = None
    if model == "cluster":
        c = Cluster.objects.get(pk=id)
        n = Node.objects.filter(subcluster__cluster=c)
        r = Relation.objects.filter(subcluster__cluster=c)
    elif model == "subcluster":
        c = SubCluster.objects.get(pk=id)
        n = Node.objects.filter(subcluster=c)
        r = Relation.objects.filter(subcluster=c)

    NAMESPACE = {}
    url = "http://localhost"
    prefix = "localhost"
    NAMESPACE[url] = prefix

    #ns = Namespace(url, prefix, '')
    #idgen = IDGenerator(namespace=ns)
    #set_id_namespace(ns)

    #full_path = ('http', ('', 's')[request.is_secure()], '://', request.META['HTTP_HOST'], request.path)
    #url = ''.join(full_path)
    #NAMESPACE[url] = request.META['HTTP_HOST'].split(":")[0]
    set_id_namespace(NAMESPACE)
    
    pkg = create_package()

    intent = "Indicators"
    report = create_report(source=url, intent=intent)
    pkg.add_report(report)

    ctitle = c.name
    cdscr = c.description
    campaign = create_campaign(title=ctitle, description=cdscr)
    pkg.add_campaign(campaign)

    hostlist = []
    #hosts = n.filter(label__name="Host",key_property__key__name="name")
    hosts = n.filter(index__label__name="Host",index__property_key__name="name")
    for host in hosts:
        #h = host.key_property.value
        h = host.value
        if not h in hostlist:
            hostlist.append(h)
    
    domainlist = []
    domains = n.filter(index__label__name="Domain",index__property_key__name="name")
    for domain in domains:
        #d = domain.key_property.value
        d = domain.value
        if not d in domainlist:
            domainlist.append(d)

    iplist = []
    ips = n.filter(index__label__name="IP",index__property_key__name="address")
    for ip in ips:
        #i = ip.key_property.value
        i = ip.value
        if not i in iplist:
            iplist.append(i)

    """
    indicators = [
        hostchars_indicator(hostlist),
        domainlist_indicator(domainlist),
        iplist_indicator(iplist),
    ]
    indicators = add_relcampaign_to_indicators(campaign, indicators)
    pkg = add_indicators_to_pkg(indicators, pkg)
    """

    obs = {
        "ip":iplist,
        "domain":domainlist,
        "host":hostlist,
    }
    pkg = add_obs_to_pkg(obs, pkg)

    out = "/static/export/stix_" + model + id + ".xml"
    fh = open(appdir + out, "wb")
    fh.write(pkg.to_xml())
    fh.close()

    return redirect(out)

