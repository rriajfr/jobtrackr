from django.contrib import admin
from django.urls import path, include
from applications.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', dashboard, name='dashboard'), 
    path('applications/', include('applications.urls')),
]