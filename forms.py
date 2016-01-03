from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Select
from .models import *

input_formats = [
            '%Y/%m/%d %H:%M:%S',
            '%y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%y/%m/%d %H:%M',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d',
            '%y/%m/%d',
            '%Y-%m-%d',
        ]

class ClusterForm(forms.ModelForm):
    class Meta:
        model = Cluster
        fields = ["name", "description", "firstseen", "tag"]
    def __init__(self, *args, **kwargs):
        super(ClusterForm, self).__init__(*args, **kwargs)
        self.fields["firstseen"].input_formats = input_formats
        self.fields["tag"].required = False

class SubClusterForm(forms.ModelForm):
    class Meta:
        model = SubCluster
        fields = ["name", "description", "firstseen", "cluster", "tag"]
    def __init__(self, *args, **kwargs):
        super(SubClusterForm, self).__init__(*args, **kwargs)
        self.fields["cluster"].required = False
        self.fields["firstseen"].input_formats = input_formats
        self.fields["tag"].required = False

class VerboseRelForm(forms.Form):
    src_label = forms.CharField(max_length="200", required=False, label="Src Label")
    src_key = forms.CharField(max_length="200", required=False, label="Src Key")
    src_value = forms.CharField(max_length="200", required=False, label="Src Value")
    rel = forms.CharField(max_length="200", required=False, label="Relation")
    dst_label = forms.CharField(max_length="200", required=False, label="Dst Label")
    dst_key = forms.CharField(max_length="200", required=False, label="Dst Key")
    dst_value = forms.CharField(max_length="200", required=False, label="Dst Value")

class IndexForm(forms.ModelForm):
    new_label = forms.CharField(max_length="200", required=False)
    new_key = forms.CharField(max_length="200", required=False)
    """
    node_index = forms.ModelChoiceField(
        queryset=NodeIndex.objects.all(),
        label="Node Index",
        required=False,
    )
    ioc_term = forms.ModelChoiceField(
        queryset=IOCTerm.objects.all(),
        label="OpenIOC Term",
        required=False,
    )
    new_ioc = forms.CharField(max_length="200", required=False)
    ioc_import = forms.BooleanField(required=False)
    """
    class Meta:
        model = NodeIndex
        #fields = ["node_index", "label", "new_label", "property_key", "new_key"]
        fields = ["label", "new_label", "property_key", "new_key"]
    def __init__(self, *args, **kwargs):
        super(IndexForm, self).__init__(*args, **kwargs)
        self.fields["label"].required = False
        self.fields["property_key"].required = False
    def clean(self):
        label = self.cleaned_data["label"]
        l = self.cleaned_data["new_label"].strip()
        if not label and l:
            label, created = NodeLabel.objects.get_or_create(
                name = l
            )
            self.cleaned_data["label"] = label
        pk = self.cleaned_data["property_key"]
        k = self.cleaned_data["new_key"].strip()
        if not pk and k:
            key, created = PropertyKey.objects.get_or_create(
                name = k
            )
            self.cleaned_data["property_key"] = key
        return self.cleaned_data

class RelEditForm(forms.ModelForm):
    new_type = forms.CharField(max_length="200", required=False)
    class Meta:
        model = Relation
        fields = ["type", "new_type", "subcluster"]
    def clean(self):
        t = self.cleaned_data["new_type"].strip()
        if t:
            type, created = RelType.objects.get_or_create(
                name = t
            )
            self.cleaned_data["type"] = type
        return self.cleaned_data

class RelTemplateForm(forms.ModelForm):
    new_type = forms.CharField(max_length="200", required=False)
    class Meta:
        model = RelationTemplate
        fields = ["src_index", "dst_index", "type", "new_type"]
        #fields = ["src_index", "type", "new_type", "dst_index"]
        labels = {
            'src_index': _('Source'),
            'dst_index': _('Destination'),
        }
    def __init__(self, *args, **kwargs):
        super(RelTemplateForm, self).__init__(*args, **kwargs)
        self.fields["src_index"].required = False
        self.fields["dst_index"].required = False
        self.fields["type"].required = False
    def clean(self):
        rt = self.cleaned_data["type"]
        t = self.cleaned_data["new_type"].strip()
        if not rt and t:
            type, created = RelType.objects.get_or_create(
                name = t
            )
            self.cleaned_data["type"] = type
        return self.cleaned_data

class TemplateForm(forms.Form):
    rel_template = forms.ModelChoiceField(
        queryset=RelationTemplate.objects.all().order_by("src_index"),
        label="Template"
    )
    src_value = forms.CharField(max_length="200", required=False, label="Source Value")
    dst_value = forms.CharField(max_length="200", required=False, label="Destination Value")
    postprocess = forms.BooleanField(required=False)

class RelCreateForm(forms.Form):
    src_index = forms.ModelChoiceField(
        queryset=NodeIndex.objects.all(),
        label="Src Index"
    )
    src_value = forms.CharField(max_length="200", required=False, label="Source Value")
    dst_index = forms.ModelChoiceField(
        queryset=NodeIndex.objects.all(),
        label="Dst Index",
        required=False,
    )
    dst_value = forms.CharField(max_length="200", required=False, label="Destination Value")
    reltype = forms.ModelChoiceField(
        queryset=RelType.objects.all(),
        label="Relation Type",
        required=False,
    )
    postprocess = forms.BooleanField(required=False)

class EntitySelectForm(forms.Form):
    entity = forms.ChoiceField(
        choices=(
            ("node","Node"),
            ("rel","Relation")
        )
    )
    id = forms.IntegerField(min_value=0, required=True)

class EntityForm(forms.Form):
    entity = forms.ChoiceField(
        choices=(
            ("node","Node"),
            ("rel","Relation")
        )
    )
    id = forms.IntegerField(min_value=0, required=False)
    key = forms.ModelChoiceField(queryset=PropertyKey.objects.all().order_by("name"), required=False, label="Property Key")
    new_key = forms.CharField(max_length="200", required=False, label="New Key")
    value = forms.CharField(max_length="200", required=False, label="Property Value")
    subcluster = forms.ModelMultipleChoiceField(queryset=SubCluster.objects.all().order_by("name"))
    postprocess = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.fields["subcluster"].required = False
    def clean(self):
        key = self.cleaned_data["key"]
        nk = self.cleaned_data["new_key"].strip()
        if not key and nk:
            pk, created = PropertyKey.objects.get_or_create(
                name = nk
            )
            self.cleaned_data["key"] = pk
        return self.cleaned_data

class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ["subcluster"]

class PropertyForm(forms.ModelForm):
    new_key = forms.CharField(max_length="200", required=False, label="New Key")
    class Meta:
        model = Property
        fields = ["key", "new_key", "value"]
    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        self.fields["key"].required = False
        self.fields["value"].required = False
    def clean(self):
        key = self.cleaned_data["key"]
        nk = self.cleaned_data["new_key"].strip()
        if not key and nk:
            pk, created = PropertyKey.objects.get_or_create(
                name = nk
            )
            self.cleaned_data["key"] = pk
        return self.cleaned_data

class UploadFileForm(forms.Form):
    file = forms.FileField()

class IOCTermForm(forms.ModelForm):
    iocterm = forms.ModelChoiceField(
        queryset=IOCTerm.objects.all(),
        label="OpenIOC Term",
        required=False,
    )
    class Meta:
        model = IOCTerm
        fields = ["iocterm", "text", "index", "allow_import"]
    def __init__(self, *args, **kwargs):
        super(IOCTermForm, self).__init__(*args, **kwargs)
        self.fields["text"].label = "New IOC Term"
        self.fields["text"].required = False
        self.fields["allow_import"].widget = Select(choices=((0,"False"),(1,"True")))
