from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CSVUploadAPIView, CSVStatusAPIView

urlpatterns = [
    path("upload/", CSVUploadAPIView.as_view(), name="csv-upload"),
    path("status/<uuid:id>/", CSVStatusAPIView.as_view(), name="csv-status"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)