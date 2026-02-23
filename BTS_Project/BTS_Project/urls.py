from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('tourister/', include('tourister.urls')),
    path('admin_site/', include('admin_panel.urls')),
    path('depot/', include('depot_management.urls')),
    path('hotel/', include('hotel_management.urls')),
    path('payment/', include('payment.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)