import string
import secrets
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import PasswordItems, decrypt_password
from api.mypagination import MyPageNumberPagination
from api.serializers import PasswordItemSerializer
from rest_framework.exceptions import ValidationError

class PasswordItemsViewSet(viewsets.ModelViewSet):
    queryset = PasswordItems.objects.all()
    serializer_class = PasswordItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        group_id = self.kwargs.get('groups_pk')

        # Check if the request method is PUT or DELETE
        if self.request.method in ['PUT', 'DELETE']:
            # Convert 'null' to None for PUT and DELETE requests
            if group_id == 'null':
                group_id = None

            # For PUT and DELETE, filter by group_id, allowing for group_id to be None
            if group_id is None:
                return PasswordItems.objects.filter(user_id=user, group_id__isnull=True)
            return PasswordItems.objects.filter(user_id=user, group_id=group_id)

        # For GET and POST requests, use the original behavior
        if group_id:
            return PasswordItems.objects.filter(group_id=group_id)

        return PasswordItems.objects.filter(user_id=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            # Decrypt passwords before paginated response
            for item in serializer.data:
                item['password'] = decrypt_password(item['password'])

            # Return paginated response
            return self.get_paginated_response(serializer.data)

        # If pagination is not applied, return all items (this should not happen)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='unlisted')
    def get_password_items_with_null_group(self, request):
        # Filter for password items where group_id is null
        user = self.request.user
        queryset = PasswordItems.objects.filter(user_id=user, group_id__isnull=True)
        serializer = PasswordItemSerializer(queryset, many=True)

        # Decrypt passwords before returning the response
        for item in serializer.data:
            item['password'] = decrypt_password(item['password'])

        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def create_password_item(self, request):
        # Proceed with the creation using the corrected group_id
        serializer = PasswordItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def get_specific_password_items(self, request, pk=None, groups_pk=None):
        user = request.user
        queryset = PasswordItems.objects.filter(pk=pk, group_id=groups_pk, user_id=user)
        password_item = get_object_or_404(queryset, pk=pk)
        serializer = PasswordItemSerializer(password_item)

        # Decrypt the password before returning
        password_item_data = serializer.data
        password_item_data['password'] = decrypt_password(password_item_data['password'])

        return Response(password_item_data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        groups_pk = self.kwargs.get('groups_pk')

        # Initialize an empty queryset to hold combined results
        queryset = self.queryset.filter(user_id=user)

        # If 'null' is provided as group_id, filter items with group_id=None
        if groups_pk == 'null':
            null_group_items = queryset.filter(group_id__isnull=True)
        else:
            null_group_items = queryset.none()  # No null group items if an actual group is provided

        # If a valid group_id is provided, filter those as well
        if groups_pk and groups_pk != 'null':
            group_items = queryset.filter(group_id=groups_pk)
        else:
            group_items = queryset.none()  # No group items for 'null'

        # Combine the querysets
        password_items = null_group_items | group_items

        # Fetch the item by pk within the combined queryset
        password_item = get_object_or_404(password_items, pk=kwargs.get('pk'))

        serializer = PasswordItemSerializer(password_item)

        # Decrypt the password before returning
        password_item_data = serializer.data
        password_item_data['password'] = decrypt_password(password_item_data['password'])

        return Response(password_item_data)

    @action(methods=['put'], detail=True)
    def put_password_items(self, request, pk=None, groups_pk=None):
        user = request.user
        # Check if 'groups_pk' is a string 'null' and treat it as None
        if groups_pk == 'null':
            groups_pk = None

        # Allow group_id to be None, but ensure the password belongs to the user
        if groups_pk is None:
            queryset = PasswordItems.objects.filter(pk=pk, group_id__isnull=True, user_id=user)
        else:
            queryset = PasswordItems.objects.filter(pk=pk, group_id=groups_pk, user_id=user)

        password_items = get_object_or_404(queryset, pk=pk)

        serializer = PasswordItemSerializer(password_items, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def delete_password_items(self, request, pk=None, groups_pk=None):
        user = request.user
        # Allow deletion without a specific group_id, but ensure the password belongs to the user
        if groups_pk is None:
            queryset = PasswordItems.objects.filter(pk=pk, group_id__isnull=True, user_id=user)
        else:
            queryset = PasswordItems.objects.filter(pk=pk, group_id=groups_pk, user_id=user)

        password_items = get_object_or_404(queryset, pk=pk)
        password_items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='generate')
    def generate_password(self, request):
        try:
            characters = []

            if request.data.get('uppercase', 'false'):
                characters.extend(list(string.ascii_uppercase))
            if request.data.get('lowercase', 'false'):
                characters.extend(list(string.ascii_lowercase))
            if request.data.get('digits', 'false'):
                characters.extend(list(string.digits))
            if request.data.get('symbols', 'false'):
                characters.extend("!#$%&'()*+,-./:;<=>?@[]^_`{|}~")

            length = int(request.data.get('length', 16))

            if not characters:
                return Response({'error': 'No character types selected'}, status=status.HTTP_400_BAD_REQUEST)

            password = ''.join(secrets.choice(characters) for _ in range(length))

            # Print the generated password to the server logs
            print(f"Generated password: {password}")

            return JsonResponse({'generated_password': password})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)