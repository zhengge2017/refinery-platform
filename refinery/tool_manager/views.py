import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import HttpResponseBadRequest

from guardian.exceptions import GuardianError
from guardian.shortcuts import get_objects_for_user
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tool_manager.utils import create_tool_definition, validate_tool_annotation

from .models import Tool, ToolDefinition
from .serializers import ToolDefinitionSerializer, ToolSerializer
from .utils import create_tool, validate_tool_launch_configuration

logger = logging.getLogger(__name__)


class ToolDefinitionsViewSet(ModelViewSet):
    """API endpoint that allows for ToolDefinitions to be fetched"""

    queryset = ToolDefinition.objects.all()
    serializer_class = ToolDefinitionSerializer
    lookup_field = 'uuid'
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]


class ToolsViewSet(ModelViewSet):
    """API endpoint that allows for Tools to be fetched and launched"""
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view returns a list of all the Tools that the currently
        authenticated user has read permissions on.
        """
        user_tools = []
        try:
            user_tools.extend(
                get_objects_for_user(
                    self.request.user,
                    "tool_manager.read_workflowtool"
                )
            )
            user_tools.extend(
                get_objects_for_user(
                    self.request.user,
                    "tool_manager.read_visualizationtool"
                )
            )
        except GuardianError as e:
            return HttpResponseBadRequest(e)

        return user_tools

    def create(self, request, *args, **kwargs):
        """
        Create and launch a Tool upon successful validation checks
        """
        try:
            validate_tool_launch_configuration(request.data)
        except RuntimeError as e:
            return HttpResponseBadRequest(e)
        else:
            tool_launch_configuration = request.data
            try:
                with transaction.atomic():
                    tool = create_tool(tool_launch_configuration, request.user)
                    return tool.launch()
            except Exception as e:
                return HttpResponseBadRequest(e)


@staff_member_required
@renderer_classes(JSONRenderer)
@api_view(['POST'])
def tool_definition(request):
    if request.method == 'POST':
        tool_data = request.data

        try:
            validate_tool_annotation(tool_data)
        except RuntimeError as e:
            return Response(e, status=500)
        except Exception as e:
            return Response(
                "Something unexpected happened: {}: {}".format(
                    e.__class__,
                    e
                ),
                status=500
            )
        try:
            create_tool_definition(tool_data)
        except Exception as e:
            return Response(
                "Creation of ToolDefinition failed. Database "
                "rolled back to its state before this "
                "ToolDefinition's attempted creation: {}".format(e),
                status=500
            )
        else:
            return Response(
                "Generated ToolDefinition for Visualization:{}".format(
                    tool_data["name"]
                ),
                status=200
            )
