'''
Created on May 4, 2012

@author: nils
'''

from GuardianTastypieAuthz import GuardianAuthorization
from core.models import Project, NodeSet, NodeRelationship, NodePair, Workflow, \
    WorkflowInputRelationships, Analysis, DataSet
from data_set_manager.api import StudyResource, AssayResource
from data_set_manager.models import Node, Study
from django.conf.urls.defaults import url
from django.core.serializers import json
from django.db.models.aggregates import Count
from django.utils import simplejson
from file_store.models import FileStoreItem
from tastypie import fields
from tastypie.authentication import SessionAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.bundle import Bundle
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
import logging
import re
import json


logger = logging.getLogger(__name__)


class PrettyJSONSerializer(Serializer):
    '''Adds indentations and newlines to JSON output
    Source: http://django-tastypie.readthedocs.org/en/latest/cookbook.html#pretty-printed-json-serialization

    '''
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)


class DataSetResource(ModelResource):
    class Meta:
        queryset = DataSet.objects.all()
        detail_uri_name = 'uuid'    # for using UUIDs instead of pk in URIs
        allowed_methods = ['get']
        resource_name = 'data_set'
        filtering = {'uuid': ALL}
        fields = ['uuid']


class AnalysisResource(ModelResource):
    data_set = fields.ToOneField(DataSetResource, 'data_set', use_in='detail')
    uuid = fields.CharField(attribute='uuid', use_in='all')
    name = fields.CharField(attribute='name', use_in='all')
    creation_date = fields.CharField(attribute='creation_date', use_in='all')
    workflow_steps_num = fields.IntegerField(attribute='workflow_steps_num',
                                             blank=True, null=True, use_in='detail')
    workflow_copy = fields.CharField(attribute='workflow_copy',
                                     blank=True, null=True, use_in='detail')
    history_id = fields.CharField(attribute='history_id', blank=True, null=True,
                                  use_in='detail')
    workflow_galaxy_id = fields.CharField(attribute='workflow_galaxy_id',
                                          blank=True, null=True, use_in='detail')
    library_id = fields.CharField(attribute='library_id', blank=True, null=True,
                                  use_in='detail')
    time_start = fields.DateTimeField(attribute='time_start', blank=True, null=True,
                                      use_in='detail')
    time_end = fields.DateTimeField(attribute='time_end', blank=True, null=True,
                                    use_in='detail')
    status = fields.CharField(attribute='status', default=Analysis.INITIALIZED_STATUS,
                              blank=True, null=True, use_in='detail')

    class Meta:
        queryset = Analysis.objects.all()
        resource_name = Analysis._meta.module_name
        detail_uri_name = 'uuid'    # for using UUIDs instead of pk in URIs
        authentication = SessionAuthentication()
        authorization = GuardianAuthorization()
        allowed_methods = ["get"]
        fields = ['data_set', 'creation_date', 'history_id', 'library_id', 'name',
                'resource_uri', 'status', 'time_end', 'time_start', 'uuid',
                'workflow_copy', 'workflow_galaxy_id', 'workflow_steps_num']
        filtering = {'data_set': ALL_WITH_RELATIONS}
        ordering = ['name', 'creation_date']


class ProjectResource(ModelResource):
    class Meta:
        #authentication = ApiKeyAuthentication()
        queryset = Project.objects.all()


class NodeResource(ModelResource):
    class Meta:
        queryset = Node.objects.all()
        resource_name = 'node'
        detail_uri_name = 'uuid'    # for using UUIDs instead of pk in URIs
        authentication = SessionAuthentication()
        authorization = GuardianAuthorization()
        serializer = PrettyJSONSerializer()
        allowed_methods = ["get" ]
        fields = ['name', 'uuid', 'file_uuid', 'file_url', 'study', 'assay' ]
        filtering = { 'uuid': ALL }
        #filtering = { "study": ALL_WITH_RELATIONS, "assay": ALL_WITH_RELATIONS }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$" %
                    self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]


    def dehydrate(self, bundle):
        # return download URL of file if a file is associated with the node
        
        if bundle.obj.file_uuid is not None and bundle.obj.file_uuid != "":
            try:
                bundle.data['file_url'] = FileStoreItem.objects.get( uuid=bundle.obj.file_uuid ).get_full_url()
            except:
                logger.warning( 'Unable to find file store item with UUID "' + bundle.obj.file_uuid + '".' )
                bundle.data['file_url'] = None
        else:
            bundle.data['file_url'] = None
           
        return bundle
    

class NodeSetResource(ModelResource):
    # https://github.com/toastdriven/django-tastypie/pull/538
    # https://github.com/toastdriven/django-tastypie/issues/526
    # Once the above has been integrated into a tastypie release branch remove NodeSetListResource and
    # use "use_in" instead 
    #nodes = fields.ToManyField(NodeResource, 'nodes', use_in="detail" )
    
    solr_query = fields.CharField(attribute='solr_query', null=True)
    solr_query_components = fields.CharField(attribute='solr_query_components', null=True)
    node_count = fields.IntegerField(attribute='node_count', null=True)
    is_implicit = fields.BooleanField(attribute='is_implicit')
    study = fields.ToOneField(StudyResource, 'study')
    assay = fields.ToOneField(AssayResource, 'assay')

    class Meta:
        # create node count attribute on the fly - node_count field has to be defined on resource
        queryset = NodeSet.objects.all()
        resource_name = 'nodeset'
        detail_uri_name = 'uuid'    # for using UUIDs instead of pk in URIs
        authentication = SessionAuthentication()
        authorization = GuardianAuthorization()
        serializer = PrettyJSONSerializer()
        fields = ['name', 'summary', 'assay', 'study', 'uuid', 'is_implicit', 'node_count', 'solr_query','solr_query_components']
        ordering = ['name', 'summary', 'assay', 'study', 'uuid', 'is_implicit', 'node_count', 'solr_query','solr_query_components']
        allowed_methods = ["get", "post" ]
        filtering = { "study": ALL_WITH_RELATIONS, "assay": ALL_WITH_RELATIONS }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$" %
                    self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]

    def obj_create(self, bundle, **kwargs):
        '''Create a new NodeSet instance and assign current user as owner if
        current user has read permission on the data set referenced by the new NodeSet

        '''
        # get the Study specified by the UUID in the new NodeSet
        study_uri = bundle.data['study']
        match = re.search('[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', study_uri)
        study_uuid = match.group()
        try:
            study = Study.objects.get(uuid=study_uuid)
        except Study.DoesNotExist:
            logger.error("Study '{}' does not exist".format(study_uuid))
            self.unauthorized_result(Unauthorized("You are not allowed to create a new NodeSet."))
        # look up the dataset via InvestigationLink relationship
        # an investigation is only associated with a single data set even though
        # InvestigationLink is a many to many relationship
        try:
            dataset = study.investigation.investigationlink_set.all()[0].data_set
        except IndexError:
            logger.error("Data set not found for study '{}'".format(study.uuid))
            self.unauthorized_result(Unauthorized("You are not allowed to create a new NodeSet."))
        permission = "read_%s" % dataset._meta.module_name
        if not bundle.request.user.has_perm(permission, dataset):
            self.unauthorized_result(Unauthorized("You are not allowed to create a new NodeSet."))
        # if user has the read permission on the data set
        # continue with creating the new NodeSet instance
        bundle = super(NodeSetResource, self).obj_create(bundle, **kwargs)
        bundle.obj.set_owner(bundle.request.user)
        return bundle


class NodeSetListResource(ModelResource):
    study = fields.ToOneField(StudyResource, 'study')
    assay = fields.ToOneField(AssayResource, 'assay')
    node_count = fields.IntegerField(attribute='node_count',readonly=True)
    is_implicit = fields.BooleanField(attribute='is_implicit')

    class Meta:
        # create node count attribute on the fly - node_count field has to be defined on resource
        queryset = NodeSet.objects.all()
        detail_resource_name = 'nodeset' # NG: introduced to get correct resource ids
        resource_name = 'nodesetlist'
        detail_uri_name = 'uuid'    # for using UUIDs instead of pk in URIs
        authentication = SessionAuthentication()
        authorization = GuardianAuthorization()
        fields = ['name', 'summary', 'assay', 'study', 'uuid' ]
        allowed_methods = ["get" ]
        filtering = { "study": ALL_WITH_RELATIONS, "assay": ALL_WITH_RELATIONS }
        ordering = [ 'name', 'node_count' ];
    
    def dehydrate(self, bundle):
        # replace resource URI to point to the nodeset resource instead of the nodesetlist resource        
        bundle.data['resource_uri'] = bundle.data['resource_uri'].replace( self._meta.resource_name, self._meta.detail_resource_name ) 
        return bundle


class NodePairResource(ModelResource):
    node1 = fields.ToOneField(NodeResource, 'node1')
    node2 = fields.ToOneField(NodeResource, 'node2', null=True)
    group = fields.CharField(attribute='group', null=True)
    
    class Meta:
        queryset = NodePair.objects.all()
        detail_resource_name = 'nodepair' 
        resource_name = 'nodepair'
        detail_uri_name = 'uuid'  
 
class NodeRelationshipResource(ModelResource):
    name = fields.CharField(attribute='name', null=True)
    type = fields.CharField(attribute='type', null=True)
    node_pairs = fields.ToManyField(NodePairResource, 'node_pairs')  #, full=True), if you need each attribute for each nodepair
    study = fields.ToOneField(StudyResource, 'study')
    assay = fields.ToOneField(AssayResource, 'assay')
    
    class Meta:
        queryset = NodeRelationship.objects.all()
        detail_resource_name = 'noderelationship' 
        resource_name = 'noderelationship'
        detail_uri_name = 'uuid'  
        
        #fields = ['type', 'study', 'assay', 'node_pairs']
        ordering = ['type', 'node_pairs']
        filtering = { "study": ALL_WITH_RELATIONS, "assay": ALL_WITH_RELATIONS }


class WorkflowResource(ModelResource):
    input_relationships = fields.ToManyField("core.api.WorkflowInputRelationshipsResource", 'input_relationships', full=True)
    
    class Meta:
        queryset = Workflow.objects.filter( is_active=True )
        detail_resource_name = 'workflow' 
        resource_name = 'workflow'
        detail_uri_name = 'uuid'
        allowed_methods = ["get" ]        
        fields = ['name', 'uuid' ]  

    def dehydrate(self, bundle):
        # add graph as json        
        bundle.data['graph'] = json.loads( bundle.obj.graph ) 
        return bundle

        
class WorkflowInputRelationshipsResource(ModelResource):
    #workflow = fields.ToOneField(WorkflowResource, 'workflow')
    
    class Meta:
        queryset = WorkflowInputRelationships.objects.all()
        detail_resource_name = 'workflowrelationships' 
        resource_name = 'workflowrelationships'
        #detail_uri_name = 'uuid'   
        fields = ['category', 'set1', 'set2', 'workflow']  
