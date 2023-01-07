
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('super/', include('super.urls')),
    path('AdminUser/', include('Admin.urls')),
]
