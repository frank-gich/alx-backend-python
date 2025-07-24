import logging
import time
from datetime import datetime, time as dt_time
from collections import defaultdict
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User

# Configure logging for request logging middleware
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Global storage for rate limiting (in production, use Redis or database)
request_counts = defaultdict(list)
offensive_words = ['spam', 'abuse', 'offensive', 'bad', 'hate']  # Add more as needed


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs each user's requests to a file with timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get user information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to messaging during certain hours (outside 9AM-6PM).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Check if request is for chat/messaging endpoints
        if '/chat' in request.path or '/message' in request.path:
            current_time = datetime.now().time()
            start_time = dt_time(9, 0)  # 9:00 AM
            end_time = dt_time(18, 0)   # 6:00 PM
            
            # Check if current time is outside allowed hours
            if not (start_time <= current_time <= end_time):
                return HttpResponseForbidden(
                    "Chat access is restricted outside business hours (9AM - 6PM)"
                )
        
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that implements rate limiting and offensive language detection.
    Limits users to 5 messages per minute based on IP address.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only check POST requests (messages)
        if request.method == 'POST' and ('/chat' in request.path or '/message' in request.path):
            client_ip = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old entries (older than 1 minute)
            cutoff_time = current_time - 60  # 1 minute ago
            request_counts[client_ip] = [
                timestamp for timestamp in request_counts[client_ip] 
                if timestamp > cutoff_time
            ]
            
            # Check rate limit (5 messages per minute)
            if len(request_counts[client_ip]) >= 5:
                return HttpResponseForbidden(
                    "Rate limit exceeded. Maximum 5 messages per minute allowed."
                )
            
            # Check for offensive language in POST data
            if self.contains_offensive_language(request):
                return HttpResponseForbidden(
                    "Message contains offensive language and has been blocked."
                )
            
            # Add current request timestamp
            request_counts[client_ip].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def contains_offensive_language(self, request):
        """Check if request contains offensive language."""
        # Check POST data
        for key, value in request.POST.items():
            if isinstance(value, str):
                for word in offensive_words:
                    if word.lower() in value.lower():
                        return True
        
        # Check request body if it's JSON or text
        if hasattr(request, 'body'):
            try:
                body_text = request.body.decode('utf-8').lower()
                for word in offensive_words:
                    if word.lower() in body_text:
                        return True
            except:
                pass
        
        return False


class RolePermissionMiddleware(MiddlewareMixin):
    """
    Middleware that checks user roles and restricts access to admin/moderator only.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Check if request is for protected chat endpoints
        if '/chat' in request.path or '/message' in request.path:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden(
                    "Authentication required for chat access."
                )
            
            # Check user role/permissions
            user = request.user
            
            # Check if user is admin or has moderator permissions
            is_admin = user.is_staff or user.is_superuser
            is_moderator = user.groups.filter(name='moderator').exists()
            
            # You can also check custom user profile fields if you have them
            # For example: hasattr(user, 'profile') and user.profile.role in ['admin', 'moderator']
            
            if not (is_admin or is_moderator):
                return HttpResponseForbidden(
                    "Access denied. Admin or moderator privileges required."
                )
        
        response = self.get_response(request)
        return response
