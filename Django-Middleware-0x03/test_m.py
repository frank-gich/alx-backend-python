# test_middleware.py
"""
Test script to verify middleware functionality.
Run this after setting up your Django project with the middleware.
"""

import requests
import time
from datetime import datetime

# Base URL of your Django development server
BASE_URL = "http://127.0.0.1:8000"

def test_request_logging():
    """Test the RequestLoggingMiddleware"""
    print("Testing Request Logging Middleware...")
    
    # Make a few test requests
    endpoints = ['/chat/', '/message/', '/admin/']
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"Request to {endpoint}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request to {endpoint}: Failed - {e}")
    
    print("Check 'user_requests.log' file for logged requests\n")

def test_time_restriction():
    """Test the RestrictAccessByTimeMiddleware"""
    print("Testing Time Restriction Middleware...")
    
    current_hour = datetime.now().hour
    
    if 9 <= current_hour <= 18:
        print("Current time is within allowed hours (9AM-6PM)")
        print("Time restriction middleware should allow access")
    else:
        print("Current time is outside allowed hours (9AM-6PM)")
        print("Time restriction middleware should block access")
    
    try:
        response = requests.get(f"{BASE_URL}/chat/")
        print(f"Chat access response: {response.status_code}")
        if response.status_code == 403:
            print(f"Access blocked: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    print()

def test_rate_limiting():
    """Test the OffensiveLanguageMiddleware rate limiting"""
    print("Testing Rate Limiting (OffensiveLanguageMiddleware)...")
    
    # Send multiple POST requests quickly
    for i in range(7):  # Send 7 requests (limit is 5 per minute)
        try:
            response = requests.post(f"{BASE_URL}/chat/", data={'message': f'Test message {i+1}'})
            print(f"Message {i+1}: Status {response.status_code}")
            
            if response.status_code == 403:
                print(f"Rate limit hit: {response.text}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i+1} failed: {e}")
        
        time.sleep(0.1)  # Small delay between requests
    
    print()

def test_offensive_language():
    """Test offensive language detection"""
    print("Testing Offensive Language Detection...")
    
    # Test with offensive content
    offensive_messages = [
        "This is a normal message",
        "This contains spam content",
        "Another offensive message with hate"
    ]
    
    for msg in offensive_messages:
        try:
            response = requests.post(f"{BASE_URL}/chat/", data={'message': msg})
            print(f"Message '{msg[:20]}...': Status {response.status_code}")
            
            if response.status_code == 403:
                print(f"Blocked: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
    
    print()

def test_role_permissions():
    """Test the RolePermissionMiddleware"""
    print("Testing Role Permission Middleware...")
    print("Note: This test requires authentication. Make sure you have:")
    print("1. Created a superuser: python manage.py createsuperuser")
    print("2. Created a regular user through Django admin")
    print("3. Test both authenticated and unauthenticated access")
    
    # Test unauthenticated access
    try:
        response = requests.get(f"{BASE_URL}/chat/")
        print(f"Unauthenticated access: Status {response.status_code}")
        if response.status_code == 403:
            print(f"Access denied: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("=== Django Middleware Testing ===\n")
    print("Make sure your Django server is running: python manage.py runserver\n")
    
    test_request_logging()
    test_time_restriction()
    test_rate_limiting()
    test_offensive_language()
    test_role_permissions()
    
    print("=== Testing Complete ===")
    print("\nTo run the server and test:")
    print("1. python manage.py runserver")
    print("2. python test_middleware.py")
    print("3. Check user_requests.log for logged requests")