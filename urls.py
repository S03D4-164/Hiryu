from django.conf.urls import patterns, include, url
from django.contrib import admin
from views.schema import schema_list
from views.db import db_list
from views.graphdb import graphdb_view
from views.visualize import visualize_view, vis_anonymize
from views.delete import delete_view
from views.export import export_relation, export_node
from views.stix_export import export_stix
from views.cluster import cluster_list, cluster_view
from views.subcluster import subcluster_list, subcluster_view
from views.node import node_view, node_list
from views.relation import relation_view, relation_list

urlpatterns = patterns('',
	url(r'^graphdb/$', graphdb_view),
	url(r'^schema/$', schema_list),
	url(r'^node/$', node_list),
	url(r'^relation/$', relation_list),
	url(r'^db/$', db_list),
	url(r'^visualize/(?P<model>\w+)/(?P<id>\d+)$', visualize_view),
	url(r'^visualize/(?P<model>\w+)/$', visualize_view),
	url(r'^visualize/$', visualize_view),
	url(r'^vis_anonymize/(?P<model>\w+)/(?P<id>\d+)$', vis_anonymize),
	url(r'^vis_anonymize/(?P<model>\w+)/$', vis_anonymize),
	url(r'^vis_anonymize/$', vis_anonymize),
	url(r'^$', vis_anonymize),
	#url(r'^$', visualize_view),
	url(r'^export/relation/(?P<model>\w+)/(?P<id>\d+)$', export_relation),
	url(r'^export/relation/$', export_relation),
	url(r'^export/node/(?P<model>\w+)/(?P<id>\d+)$', export_node),
	url(r'^export/node/$', export_node),
	url(r'^delete/(?P<model>\w+)/(?P<id>\d+)$', delete_view),
	url(r'^delete/(?P<model>\w+)$', delete_view),
	url(r'^cluster/$', cluster_list),
	url(r'^subcluster/$', subcluster_list),
	url(r'^cluster/(?P<id>\d+)$', cluster_view),
	url(r'^subcluster/(?P<id>\d+)$', subcluster_view),
	url(r'^node/(?P<id>\d+)$', node_view),
	url(r'^relation/(?P<id>\d+)$', relation_view),
	url(r'^export/stix/(?P<model>\w+)/(?P<id>\d+)$', export_stix),
)
