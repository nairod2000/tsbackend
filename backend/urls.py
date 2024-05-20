from django.urls import path
from .views import logout_view, signup_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from . import views 
  
  
urlpatterns = [  
    path('ws/chat/', views.ChatConsumer.as_asgi()),
    path('api/topics/', views.TopicListCreateView.as_view(), name='topic-list-create'),
    path('api/topics/<int:pk>/', views.TopicRetrieveUpdateDeleteView.as_view(), name='topic-retrieve-update-delete'),
    path('api/signup/', signup_view, name='signup'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('api/logout/', logout_view, name='logout'),
]
