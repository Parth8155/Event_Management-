from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import EventViewSet, RegisterView

router = DefaultRouter()
router.register(r'events', EventViewSet)

router.APIRootView.permission_classes = [permissions.AllowAny]

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]