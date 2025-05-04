from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views  
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('main/', include(('main.urls', 'main'), namespace='main')),
    path('', accounts_views.login_view, name='login'),  
]
