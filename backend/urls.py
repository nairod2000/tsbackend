from django.urls import path
from .views import logout_view, signup_view, ChatListView, ChatCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from . import views 
  

urlpatterns = [
    path('api/materials/sm2/', views.get_materials_sm2, name='get-materials-sm2'),
    path('api/materials/eval/', views.eval_material, name='eval-material'),
    path('api/chat/', views.chat_view, name='chat-view'),
    path('api/chat/start/', views.chat_start_view, name='chat_start_view'),
    path('api/chats/', ChatListView.as_view(), name='chat-list'),
    path('api/chats/create/', ChatCreateView.as_view(), name='chat-create'),
    path('api/topics/', views.TopicListCreateView.as_view(), name='topic-list-create'),
    path('api/topics/<int:pk>/', views.TopicRetrieveUpdateDeleteView.as_view(), name='topic-retrieve-update-delete'),
    path('api/signup/', signup_view, name='signup'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/logout/', logout_view, name='logout'),
]
