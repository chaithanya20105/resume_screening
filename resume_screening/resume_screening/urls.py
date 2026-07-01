from django.contrib import admin
from django.urls import path
from core.views import screen_resumes, show_results
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Upload page (also home)
    path('', screen_resumes, name='screen_resumes'),

    # Results page (for PRG pattern)
    path('results/', show_results, name='show_results'),
]

# Serve uploaded/media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
