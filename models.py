from django.db import models

class Cluster(models.Model):
        #name = models.CharField(unique=True, max_length=200)
        name = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)
	firstseen = models.DateTimeField(blank=True, null=True)
        created = models.DateTimeField(auto_now_add=True)
        modified = models.DateTimeField(auto_now=True)
        def __unicode__(self):
                return self.name
	class Meta:
		ordering = ["name"]

class SubCluster(models.Model):
        #name = models.CharField(unique=True, max_length=200)
        name = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)
	firstseen = models.DateTimeField(blank=True, null=True)
        created = models.DateTimeField(auto_now_add=True)
        modified = models.DateTimeField(auto_now=True)
	cluster = models.ManyToManyField(Cluster)
        def __unicode__(self):
                return self.name
	class Meta:
		ordering = ["name"]

class NodeLabel(models.Model):
        name = models.CharField(unique=True, max_length=200)
        def __unicode__(self):
                return self.name
	class Meta:
		ordering = ["name"]

class PropertyKey(models.Model):
        name = models.CharField(unique=True, max_length=200)
        def __unicode__(self):
                return self.name
	class Meta:
		ordering = ["name"]

class Property(models.Model):
	key = models.ForeignKey(PropertyKey)
	value = models.CharField(max_length=2000)
        def __unicode__(self):
                return str(self.key.name + " - " + self.value)
	class Meta:
		unique_together = (("key", "value"),)

class NodeIndex(models.Model):
	label = models.OneToOneField(NodeLabel)
	property_key = models.ForeignKey(PropertyKey)
        def __unicode__(self):
                return str(self.label.name + " " + self.property_key.name)
	class Meta:
		unique_together = (("label", "property_key"),)

class IOCTerm(models.Model):
	#text = models.CharField(max_length=200, unique=True)
	text = models.CharField(max_length=200)
	index = models.ForeignKey(NodeIndex, blank=True, null=True)
	allow_import = models.BooleanField(default=False)
        def __unicode__(self):
                return self.text

class Node(models.Model):
	label = models.ForeignKey(NodeLabel)
	key_property = models.ForeignKey(Property, related_name="key_property")
	properties = models.ManyToManyField(Property, related_name="node_properties")
	ref = models.PositiveIntegerField(unique=True, blank=True, null=True)
	subcluster = models.ManyToManyField(SubCluster)
        def __unicode__(self):
                return str(self.label.name + " - " + self.key_property.key.name + " - " + self.key_property.value)

class RelType(models.Model):
        name = models.CharField(unique=True, max_length=200)
        def __unicode__(self):
                return self.name
	class Meta:
		ordering = ["name"]

class Relation(models.Model):
	type = models.ForeignKey(RelType)
	properties = models.ManyToManyField(Property, related_name="rel_properties")
	src = models.ForeignKey(Node, related_name="src")
	dst = models.ForeignKey(Node, related_name="dst")
	ref = models.PositiveIntegerField(unique=True, blank=True, null=True)
	subcluster = models.ManyToManyField(SubCluster)
        def __unicode__(self):
                return self.type.name

class RelationTemplate(models.Model):
	src_index = models.ForeignKey(NodeIndex, related_name="src_index")
	type = models.ForeignKey(RelType)
	dst_index = models.ForeignKey(NodeIndex, related_name="dst_index")
        def __unicode__(self):
                return "( " + str(self.src_index) + " ) " + str(self.type) + " ( " + str(self.dst_index) + " )"
