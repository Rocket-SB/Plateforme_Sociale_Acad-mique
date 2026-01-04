from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
   

    path('', views.publication_list, name='list'),
    path('create/', views.publication_create, name='create'),
    path('<int:pk>/', views.publication_detail, name='detail'),
    path('<int:pk>/edit/', views.publication_edit, name='edit'),
    path('<int:pk>/delete/', views.publication_delete, name='delete'),

    path('<int:pk>/add-images/', views.add_images, name='add_images'),
    path('<int:pk>/delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    
    # Citations
    path('<int:pk>/add-citation/', views.add_citation, name='add_citation'),
    path('<int:pk>/remove-citation/<int:citation_id>/', views.remove_citation, name='remove_citation'),
]
