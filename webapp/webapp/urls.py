# webapp/webapp/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin panel nomini o'zgartirish
admin.site.site_header = "ISFT Bot Admin"
admin.site.site_title = "ISFT Bot"
admin.site.index_title = "Boshqaruv paneli"