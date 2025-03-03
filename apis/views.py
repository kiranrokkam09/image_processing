import os
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import CSVUpload
from .serializers import CSVUploadSerializer, CSVStatusSerializer
from .tasks import process_images 

class CSVUploadAPIView(generics.CreateAPIView):
    queryset = CSVUpload.objects.all()
    serializer_class = CSVUploadSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Start async image processing
        csv_id = response.data["id"]
        process_images.delay(csv_id)

        return response

class CSVStatusAPIView(generics.RetrieveAPIView):
    queryset = CSVUpload.objects.all()
    serializer_class = CSVStatusSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except CSVUpload.DoesNotExist:
            raise NotFound("Request ID not found.")