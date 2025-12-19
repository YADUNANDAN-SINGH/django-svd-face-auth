from django.urls import path
from . import views

urlpatterns = [
    path('', views.notes_list, name='notes_list'),
    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
]
