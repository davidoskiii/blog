from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

app_name = 'accounts'

urlpatterns = [
    # Passa CustomLoginForm a LoginView
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),

    path('', include('django.contrib.auth.urls')),
    
    path('register/', views.register, name='register'),
]
