from django.contrib import admin
from django.urls import path, include
from .  import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login),
    path('logout/', views.logout_view, name='logout'),
    path('notes/', include('notes.urls')),
]

