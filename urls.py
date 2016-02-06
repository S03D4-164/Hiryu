from django.conf.urls import include, url
from django.contrib import admin
from .views.schema import schema_list, ioc_schema_list, tag_list, stix_schema_list
from .views.entity import db_list
from .views.graphdb import graphdb_view
from .views.visualize import visualize_view, vis_anonymize
from .views.delete import delete_view
from .views.export import export_relation, export_node, export_cluster, export_subcluster
from .views.stix_export import export_stix
from .views.cluster import cluster_list, cluster_view
from .views.subcluster import subcluster_list, subcluster_view
from .views.node import node_view, node_list
from .views.relation import relation_view, relation_list
from .views.ref import ref_view
from .views.ioc_import import import_ioc
from .views.ioc_export import export_ioc
from .tables import ClusterData, SubClusterData, NodeData, RelationData, IndexData, RelTemplateData


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', db_list),
    url(r'^db/$', db_list),
    url(r'^graphdb/$', graphdb_view),
    url(r'^schema/db/$', schema_list),
    url(r'^schema/openioc/$', ioc_schema_list),
    url(r'^schema/stix/$', stix_schema_list),
    url(r'^schema/tag/$', tag_list),
    url(r'^visualize/(?P<model>\w+)/(?P<id>\d+)$', visualize_view),
    url(r'^visualize/(?P<model>\w+)/$', visualize_view),
    url(r'^visualize/$', visualize_view),
    url(r'^vis_anonymize/(?P<model>\w+)/(?P<id>\d+)$', vis_anonymize),
    url(r'^vis_anonymize/(?P<model>\w+)/$', vis_anonymize),
    url(r'^vis_anonymize/$', vis_anonymize),
    url(r'^export/relation/(?P<model>\w+)/(?P<id>\d+)$', export_relation),
    url(r'^export/relation/$', export_relation),
    url(r'^export/node/(?P<model>\w+)/(?P<id>\d+)$', export_node),
    url(r'^export/node/$', export_node),
    url(r'^export/cluster/$', export_cluster),
    url(r'^export/subcluster/$', export_subcluster),
    url(r'^export/stix/(?P<model>\w+)/(?P<id>\d+)$', export_stix),
    url(r'^export/openioc/(?P<model>\w+)/(?P<id>\d+)$', export_ioc),
    url(r'^import/ioc/$', import_ioc),
    url(r'^delete/(?P<model>\w+)/(?P<id>\d+)$', delete_view),
    url(r'^delete/(?P<model>\w+)$', delete_view),
    url(r'^cluster/$', cluster_list),
    url(r'^cluster/data$', ClusterData.as_view(), name='cluster_data'),
    url(r'^cluster/(?P<id>\d+)$', cluster_view),
    url(r'^subcluster/$', subcluster_list),
    url(r'^subcluster/data$', SubClusterData.as_view(), name='subcluster_data'),
    url(r'^subcluster/(?P<id>\d+)$', subcluster_view),
    url(r'^index/data$', IndexData.as_view(), name='index_data'),
    url(r'^node/$', node_list),
    url(r'^node/(?P<id>\d+)$', node_view),
    url(r'^node/data$', NodeData.as_view(), name='node_data'),
    url(r'^relation/$', relation_list),
    url(r'^relation/(?P<id>\d+)$', relation_view),
    url(r'^relation/data$', RelationData.as_view(), name='relation_data'),
    url(r'^reltemplate/data$', RelTemplateData.as_view(), name='reltemplate_data'),
    #url(r'^ref/(?P<id>\d+)$', ref_view),
    url(r'^ref/(?P<model>\w+)/(?P<id>\d+)$', ref_view),
]
