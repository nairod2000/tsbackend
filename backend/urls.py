from django.urls import path  
from . import views  
  
  
urlpatterns = [  
    path('ws/chat/', views.ChatConsumer.as_asgi()),
    path('api/topics/', views.TopicListCreateView.as_view(), name='topic-list-create'),
    path('api/topics/<int:pk>/', views.TopicRetrieveUpdateDeleteView.as_view(), name='topic-retrieve-update-delete'),
]