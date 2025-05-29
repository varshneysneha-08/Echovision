# detection/urls.py
from django.urls import path
from .views import process_image_api
from django.views.generic import TemplateView
from .views import login_view,register_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from . import views

class ClientView(LoginRequiredMixin, TemplateView):
    template_name = 'detection/client.html'
urlpatterns = [
    path('api/process-image/', process_image_api, name='process_image_api'),
    path('client/', ClientView.as_view(), name='client'),
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('routing/', views.routing_page, name='routing'),
    path('get-route/', views.get_route, name='get_route'),
]
