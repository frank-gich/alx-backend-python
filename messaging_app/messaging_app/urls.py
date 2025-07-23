# # messaging_app/urls.py

# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('chats.urls')),
#     path('api-auth/', include('rest_framework.urls')),  # ✅ for login/logout in DRF
# ]
"""
URL configuration for messaging_app project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from chats.auth import (
    CustomTokenObtainPairView,
    register_user,
    get_user_profile,
    update_user_profile,
    logout_user,
    change_password,
    verify_token,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('api/auth/', include([
        # JWT Token endpoints
        path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('logout/', logout_user, name='logout'),
        path('verify/', verify_token, name='verify_token'),
        
        # User management endpoints
        path('register/', register_user, name='register'),
        path('profile/', get_user_profile, name='get_profile'),
        path('profile/update/', update_user_profile, name='update_profile'),
        path('change-password/', change_password, name='change_password'),
    ])),
    
    # Chat application URLs
    path('api/chats/', include('chats.urls')),
    
    # API root (optional - for browsable API)
    path('api/', include('rest_framework.urls')),
]