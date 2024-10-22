from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('userauth.urls')),
    path('api/', include('hostel.urls')),
    path('api/', include('superadmin.urls')),
    path('api/', include('chatbot.urls')),
    path('api/', include('issue.urls')),
    path('api/', include('rooms.urls')),
    path('api/', include('adminapp.urls')),
    path('api/', include('student.urls')),
    path('api/', include('staff.urls')),
    path('api/', include('inventory.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
