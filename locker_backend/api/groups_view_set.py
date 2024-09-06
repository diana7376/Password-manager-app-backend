from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import Groups
from api.serializers import GroupsSerializer


class GroupsViewSet(viewsets.ModelViewSet):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer

    @action(methods=['get'], detail=True)
    def get_groups(self, request):
        groups = Groups.objects.all()
        serializer = GroupsSerializer(groups, many=True)
        return Response(serializer.data)


    @action(methods=['post'], detail=True)
    def create_groups(self, request):
        serializer = GroupsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @action(methods=['get'], detail=True)
    def get_specific_groups(self, request, pk=None):
        queryset = Groups.objects.filter()
        groups = get_object_or_404(queryset, pk=pk)
        serializer = GroupsSerializer(groups)
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def put_groups(self, request, pk = None):
        queryset = Groups.objects.filter()
        groups = get_object_or_404(queryset, pk=pk)

        serializer = GroupsSerializer(groups,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def delete_groups(self, request, pk = None):
        queryset = Groups.objects.filter()
        groups = get_object_or_404(queryset, pk=pk)

        groups.delete()