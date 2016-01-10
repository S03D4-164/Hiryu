from django_datatables_view.base_datatable_view import BaseDatatableView
from .models import *


class ClusterData(BaseDatatableView):
    model = Cluster
    columns = ['id', 'name', 'description', 'firstseen']
    order_columns = ['id', 'name', 'description', 'firstseen']
    max_display_length = 100

    def get_initial_queryset(self):
        subcluster = self.request.GET.get(u'subcluster', None)
        qs = None
        if subcluster:
            sc = SubCluster.objects.get(id=subcluster)
            qs = sc.cluster.all()
        else:
            qs = Cluster.objects.all()
        return qs

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/cluster/{0}">{0}</a>'.format(row.id)
        elif column == 'description':
            return '<pre>{0}</pre>'.format(row.description)
        else:
            return super(ClusterData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(id__iregex=search) \
                | qs.filter(name__iregex=search) \
                | qs.filter(description__iregex=search) \
                | qs.filter(firstseen__iregex=search)
        return qs.distinct()


class SubClusterData(BaseDatatableView):
    model = SubCluster
    columns = ['id', 'name', 'cluster', 'description', 'firstseen']
    order_columns = ['id', 'name', 'cluster', 'description', 'firstseen']
    #columns = ['id', 'name', 'cluster', 'tag', 'firstseen']
    #order_columns = ['id', 'name', 'cluster', 'tag', 'firstseen']
    max_display_length = 100

    def get_initial_queryset(self):
        cluster = self.request.GET.get(u'cluster', None)
        qs = None
        if cluster:
            qs = SubCluster.objects.filter(cluster__id=cluster)
        else:
            qs = SubCluster.objects.all()
        return qs.distinct()

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/subcluster/{0}">{0}</a>'.format(row.id)
        elif column == 'cluster':
            td = ""
            if row.cluster:
                for i in row.cluster.all():
                    td += '<a href="/cluster/{0}">{1}</a><br>'.format(i.id, i.name)
            return '{0}'.format(td)
        elif column == 'description':
            d = None
            if row.description:
                d = row.description[0:100]
            return '<pre>{0}</pre>'.format(d)
        elif column == 'tag':
            td = ""
            if row.tag:
                for i in row.tag.all():
                    td += '{0}<br>'.format(i)
            return '{0}'.format(td)
        else:
            return super(SubClusterData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(id__iregex=search) \
                | qs.filter(name__iregex=search) \
                | qs.filter(cluster__name__iregex=search) \
                | qs.filter(description__iregex=search) \
                | qs.filter(tag__value__iregex=search) \
                | qs.filter(firstseen__iregex=search)
        return qs.distinct()

class NodeData(BaseDatatableView):
    model = Node
    #columns = ['id', 'ref', 'label', 'key_property.key.name', 'key_property.value', 'subcluster']
    #order_columns = ['id', 'ref', 'label', 'key_property.key.name', 'key_property.value', 'subcluster']
    columns = ['id', 'label', 'key_property.key.name', 'key_property.value', 'subcluster']
    order_columns = ['id', 'label', 'key_property.key.name', 'key_property.value', 'subcluster']
    max_display_length = 100

    def get_initial_queryset(self):
        cluster = self.request.GET.get(u'cluster', None)
        subcluster = self.request.GET.get(u'subcluster', None)
        qs = None
        if cluster:
            qs = Node.objects.filter(subcluster__cluster__id=cluster)
        elif subcluster:
            qs = Node.objects.filter(subcluster__id=subcluster)
        else:
            qs = Node.objects.all()
        return qs

    def render_column(self, row, column):
        if column == 'id':
            #left = '<a class="btn btn-default node_id btn-xs" value="{0}"><span class="glyphicon glyphicon-chevron-left"></span></a>'.format(row.id)
            id = '<a class="btn btn-primary" href="/node/{0}">{0}</a>'.format(row.id)
            #ref = '<a class="btn btn-default ">{0}</a>'.format(row.ref)
            #return left+id+ref
            return id
        elif column == 'subcluster':
            td = "<table>"
            if row.subcluster:
                for s in row.subcluster.all():
                    td += "<tr>"
                    td += '<td><a href="/subcluster/{0}">{1}</a></td>'.format(s.id, s.name)
                    if s.cluster:
                        td += "<td>"
                        for c in s.cluster.all():
                            td += '<a href="/cluster/{0}">{1}</a><br>'.format(c.id, c.name)
                        td += "</td>"
                    td += "</tr>"
            td += "</table>"
            return '{0}'.format(td)
        elif column == 'label':
            return '{0}'.format(row.label.name)
        else:
            return super(NodeData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(id__iregex=search) \
                | qs.filter(label__name__iregex=search) \
                | qs.filter(key_property__key__name__iregex=search) \
                | qs.filter(key_property__value__iregex=search) \
                | qs.filter(subcluster__name__iregex=search) \
                | qs.filter(subcluster__cluster__name__iregex=search)
        return qs.distinct()

class RelationData(BaseDatatableView):
    model = Relation
    #columns = ['id', 'ref', 'src', 'type.name', 'dst', 'subcluster']
    #order_columns = ['id', 'ref', 'src', 'type.name', 'dst', 'subcluster']
    columns = ['id', 'firstseen', 'src.index.icon', 'src.key_property.value', 'type.name', 'dst.index.icon', 'dst.key_property.value', ]
    order_columns = ['id', 'firstseen', 'src.index.icon', 'src.key_property.value', 'type.name', 'dst.index.icon', 'dst.key_property.value', ]
    max_display_length = 100

    def get_initial_queryset(self):
        cluster = self.request.GET.get(u'cluster', None)
        subcluster = self.request.GET.get(u'subcluster', None)
        qs = None
        if cluster:
            qs = Relation.objects.filter(subcluster__cluster__id=cluster)
        elif subcluster:
            qs = Relation.objects.filter(subcluster__id=subcluster)
        else:
            qs = Relation.objects.all()
        return qs

    def render_column(self, row, column):
        if column == 'id':
            #left = '<a class="btn btn-default rel_id btn-xs" value="{0}"><span class="glyphicon glyphicon-chevron-left"></span></a>'.format(row.id)
            id = '<a class="btn btn-primary" href="/relation/{0}">{0}</a>'.format(row.id)
            ref = '<a class="btn btn-default ">{0}</a>'.format(row.ref)
            #return left+id+ref
            return id
        elif column == 'subcluster':
            td = "<table>"
            if row.subcluster:
                td += "<tr>"
                for s in row.subcluster.all():
                    td += '<td><a href="/subcluster/{0}">{1}</a></td>'.format(s.id, s.name)
                    if s.cluster:
                        td += "<td>"
                        for c in s.cluster.all():
                            td += '<a href="/cluster/{0}">{1}</a><br>'.format(c.id, c.name)
                        td += "</td>"
                td += "</tr>"
            td += "</table>"
            return '{0}'.format(td)
        elif column == 'src.index.icon':
            icon = None
            if row.src.index.icon:
                icon = row.src.index.icon
            else:
                icon = 'f096'
            td = '<a title="{2}" href="/node/{0}"><span style="font-family: FontAwesome;">&#x{1}</span></a>'.format(row.src.id, icon, row.src.index)
            return td
        elif column == 'dst.index.icon':
            icon = None
            if row.dst.index.icon:
                icon = row.dst.index.icon
            else:
                icon = 'f096'
            td = '<a title="2" href="/node/{0}"><span style="font-family: FontAwesome;">&#x{1}</span></a>'.format(row.dst.id, icon, row.dst.index)
            return td
        else:
            return super(RelationData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(id__iregex=search) \
                | qs.filter(type__name__iregex=search) \
                | qs.filter(src__label__name__iregex=search) \
                | qs.filter(src__key_property__key__name__iregex=search) \
                | qs.filter(src__key_property__value__iregex=search) \
                | qs.filter(dst__label__name__iregex=search) \
                | qs.filter(dst__key_property__key__name__iregex=search) \
                | qs.filter(dst__key_property__value__iregex=search) \
                | qs.filter(subcluster__name__iregex=search) \
                | qs.filter(subcluster__cluster__name__iregex=search)
        return qs.distinct()
