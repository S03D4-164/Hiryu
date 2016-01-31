from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


class PropertyKey(models.Model):
    name = models.CharField(unique=True, max_length=200)
    def __str__(self):
        return self.name.encode("utf-8")
    class Meta:
        ordering = ["name"]

class Property(models.Model):
    key = models.ForeignKey(PropertyKey)
    value = models.CharField(max_length=2000)
    def __str__(self):
        return str(self.key.name + " - " + self.value.encode("utf-8"))
    class Meta:
        unique_together = (("key", "value"),)
        ordering = ["key", "value"]

class Tag(models.Model):
    key = models.ForeignKey(PropertyKey)
    value = models.CharField(max_length=2000)
    def __str__(self):
        return str(self.key.name + " - " + self.value.encode("utf-8"))
    class Meta:
        unique_together = (("key", "value"),)
        ordering = ["key", "value"]


class Cluster(models.Model):
    #name = models.CharField(unique=True, max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    firstseen = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tag = models.ManyToManyField(Tag)
    def __str__(self):
        return self.name.encode("utf-8")
    class Meta:
        ordering = ["name"]

class Reference(models.Model):
    location = models.URLField(max_length=2000)
    def __str__(self):
        return self.location.encode("utf-8")
    class Meta:
        ordering = ["location"]

class Event(models.Model):
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

class SubCluster(models.Model):
    #name = models.CharField(unique=True, max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    firstseen = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    cluster = models.ManyToManyField(Cluster)
    reference = models.ManyToManyField(Reference)
    tag = models.ManyToManyField(Tag)
    def __str__(self):
        return self.name.encode("utf-8")
    class Meta:
        ordering = ["name"]

class NodeLabel(models.Model):
    name = models.CharField(unique=True, max_length=200)
    def __str__(self):
        return self.name.encode("utf-8")
    class Meta:
        ordering = ["name"]

class NodeIndex(models.Model):
    label = models.OneToOneField(NodeLabel)
    property_key = models.ForeignKey(PropertyKey)
    icon = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        #return str(self.label.name + " " + self.property_key.name)
        #return str(self.label.name.encode("utf-8") + " " + self.property_key.name.encode("utf-8"))
        
        l = self.label.name.encode("utf-8")
        k = self.property_key.name.encode("utf-8")
        return str(l) + str(" ") + str(k)
    class Meta:
        unique_together = (("label", "property_key"),)

class IOCTerm(models.Model):
    #text = models.CharField(max_length=200, unique=True)
    text = models.CharField(max_length=200)
    index = models.ForeignKey(NodeIndex, blank=True, null=True)
    allow_import = models.BooleanField(default=False)
    allow_export = models.BooleanField(default=False)
    def __str__(self):
        return self.text.encode("utf-8")

class CybOXObj(models.Model):
    #text = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    index = models.ForeignKey(NodeIndex, blank=True, null=True)
    allow_import = models.BooleanField(default=False)
    allow_export = models.BooleanField(default=False)
    def __str__(self):
        return self.name.encode("utf-8")

class Node(models.Model):
    index = models.ForeignKey(NodeIndex, related_name="node_index")
    value = models.CharField(max_length=2000)
    #label = models.ForeignKey(NodeLabel)
    #key_property = models.ForeignKey(Property, related_name="key_property")
    properties = models.ManyToManyField(Property, related_name="node_properties")
    ref = models.PositiveIntegerField(unique=True, blank=True, null=True)
    subcluster = models.ManyToManyField(SubCluster)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    #def __str__(self):
    #    return str(self.label.name + " - " + self.key_property.key.name + " - " + self.key_property.value.encode("utf-8"))
    #class Meta:
    #    unique_together = (("label", "key_property"),)
    def __str__(self):
        return str(self.index) + str(" - ") + self.value.encode("utf-8")
    class Meta:
        unique_together = (("index", "value"),)

class RelType(models.Model):
    name = models.CharField(unique=True, max_length=200)
    def __str__(self):
        return self.name.encode("utf-8")
    class Meta:
        ordering = ["name"]

class Relation(models.Model):
    type = models.ForeignKey(RelType)
    properties = models.ManyToManyField(Property, related_name="rel_properties")
    src = models.ForeignKey(Node, related_name="src")
    dst = models.ForeignKey(Node, related_name="dst")
    ref = models.PositiveIntegerField(unique=True, blank=True, null=True)
    subcluster = models.ManyToManyField(SubCluster)
    firstseen = models.DateTimeField(blank=True, null=True)
    lastseen = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.type.name
    class Meta:
        unique_together = (("type", "src", "dst"),)

class RelationTemplate(models.Model):
    src_index = models.ForeignKey(NodeIndex, related_name="src_index")
    type = models.ForeignKey(RelType)
    dst_index = models.ForeignKey(NodeIndex, related_name="dst_index")
    def __str__(self):
        #return "( " + str(self.src_index) + " ) " + str(self.type) + " ( " + str(self.dst_index) + " )"
        s = self.src_index.label.name + u" " + self.src_index.property_key.name
        t = self.type.name
        d = self.dst_index.label.name + u" " + self.dst_index.property_key.name
        r = s + u" - " + t + u" - " + d
        return r.encode("utf-8")
    class Meta:
        unique_together = (("src_index", "type", "dst_index"),)

