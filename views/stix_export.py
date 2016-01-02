from django.shortcuts import render_to_response, redirect
from ..models import Cluster, Node

import os
from stix.indicator.indicator import Indicator
from stix.common.information_source import InformationSource

appdir =  os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def create_package():
    from stix.core import STIXPackage
    pkg = STIXPackage()
    return pkg

def create_header(source):
    from stix.core.stix_header import STIXHeader
    header = STIXHeader()
    header.information_source = InformationSource(source)
    return header

def create_report(source=None, intent=None):
    from stix.report import Report
    report = Report()

    from stix.report.header import Header
    header = Header()
    header.information_source = InformationSource(source)
    header.add_intent("Indicators")
    report.header = header

    return report

def create_campaign(title=None, description=None):
    from stix.campaign import Campaign
    campaign = Campaign()
    campaign.title = title
    campaign.add_description(description)
    return campaign

def iplist_indicator(ips=[]):
    iplist = Indicator()
    iplist.add_indicator_type("IP Watchlist")

    from cybox.objects.address_object import Address
    for i in ips:
        address = Address()
        address.address_value = i 
        #address.category="ipv4-addr"
        iplist.add_observable(address)

    return iplist

def hostchars_indicator(hostnames=[]):
    hostchars = Indicator()
    hostchars.add_indicator_type("Host Characteristics")

    from cybox.objects.hostname_object import Hostname
    for h in hostnames:
        hostname = Hostname()
        hostname.hostname_value = h
        hostchars.add_observable(hostname)

    return hostchars

def domainlist_indicator(domains=[]):
    domainlist = Indicator()
    domainlist.add_indicator_type("Domain Watchlist")

    from cybox.objects.domain_name_object import DomainName
    for d in domains:
        domain = DomainName()
        domain.value = d
        domainlist.add_observable(domain)

    return domainlist

def hash_indicator(hashes=[]):
    hashlist = Indicator()
    hashlist.add_indicator_type("File Hash Watchlist")

    from cybox.objects.file_object import File
    from cybox.common.hashes import Hash
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
    from stix.common.related import RelatedIndicator
    for i in indicators:
        r = RelatedIndicator(i)
        campaign.related_indicators.append(r)
    
def add_relcampaign_to_indicators(campaign, indicators):
    from stix.common import CampaignRef
    from stix.common.related import RelatedCampaignRef
    relcampaign = RelatedCampaignRef(CampaignRef(idref=campaign.id_))
    for i in indicators:
        i.related_campaigns.append(relcampaign)
    return indicators

def add_indicators_to_pkg(indicators, pkg):
    for i in indicators:
        pkg.add_indicator(i)
    return pkg

def export_stix(request, model, id):
    c = Cluster.objects.get(pk=id)
    n = Node.objects.filter(subcluster__cluster=c)

    NAMESPACE = {}
    #url = "http://localhost"
    #NAMESPACE[url] = "localhost"
    full_path = ('http', ('', 's')[request.is_secure()], '://', request.META['HTTP_HOST'], request.path)
    url = ''.join(full_path)
    NAMESPACE[url] = request.META['HTTP_HOST'].split(":")[0]
    from stix.utils import set_id_namespace
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
    hosts = n.filter(label__name="Host",key_property__key__name="name")
    for host in hosts:
        h = host.key_property.value
        if not h in hostlist:
            hostlist.append(h)
    
    domainlist = []
    domains = n.filter(label__name="Domain",key_property__key__name="name")
    for domain in domains:
        d = domain.key_property.value
        if not d in domainlist:
            domainlist.append(d)

    iplist = []
    ips = n.filter(label__name="IP",key_property__key__name="address")
    for ip in ips:
        i = ip.key_property.value
        if not i in iplist:
            iplist.append(i)

    indicators = [
        hostchars_indicator(hostlist),
        domainlist_indicator(domainlist),
        iplist_indicator(iplist),
    ]
    indicators = add_relcampaign_to_indicators(campaign, indicators)
    pkg = add_indicators_to_pkg(indicators, pkg)

    out = "/static/export/stix_" + model + id + ".xml"
    fh = open(appdir + out, "wb")
    fh.write(pkg.to_xml())
    fh.close()

    return redirect(out)

