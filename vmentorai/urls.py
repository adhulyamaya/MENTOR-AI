from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'), 
    path('user_app/', include('user_app.urls')),
    path('payment_app/', include(('payment_app.urls', 'payment_app'), namespace='payment_app')),
    path('media_handling_app/', include('media_handling_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Ensure this is added at the end
