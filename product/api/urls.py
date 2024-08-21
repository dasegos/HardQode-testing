from django.contrib import admin
from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('admin/', admin.site.urls),
]
