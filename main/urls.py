from django.urls import path
from . import views
app_name = 'main'

urlpatterns = [
    path('', views.home, name='homepage'),
    path('profile/', views.profile_redirect_view, name='profile'),
    path('logout/', views.logout_view, name='logout')
]