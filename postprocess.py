from __future__ import absolute_import

import os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from celery import Celery

from django.conf import settings
app = Celery('postprocess', broker='redis://localhost:6379/')

from myapp.plugins.hostname import parse_hostname
from myapp.plugins.domain import whois_domain
from myapp.plugins.ipaddress import whois_ip

@app.task
def process_node(node, subcluster = None):
	nodetype = str(node.label.name + node.key_property.key.name).lower()
	if re.match("hostname", nodetype):
		parse_hostname(node, subcluster)
	elif re.match("domainname", nodetype):
		whois_domain(node, subcluster)
	elif re.match("ipaddress", nodetype):
		whois_ip(node, subcluster)
