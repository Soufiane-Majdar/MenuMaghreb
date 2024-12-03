from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that logged-in users shouldn't access
        restricted_urls = [
            reverse('landing'),
            reverse('login'),
            reverse('register'),
            reverse('contact'),
        ]
        
        # URLs that require authentication (only include URLs without parameters)
        auth_required_urls = [
            reverse('dashboard'),
        ]
        
        # Check if user is authenticated and trying to access restricted pages
        if request.user.is_authenticated and request.path in restricted_urls:
            return redirect('dashboard')
            
        # Check if user is not authenticated and trying to access protected pages
        if not request.user.is_authenticated:
            # First check exact matches
            if request.path in auth_required_urls:
                return redirect('login')
            
            # Then check if trying to access any protected URL patterns
            protected_url_patterns = [
                '/restaurant/',  # All restaurant-related URLs
                '/dashboard/',   # Dashboard URLs
            ]
            
            if any(pattern in request.path for pattern in protected_url_patterns):
                return redirect('login')
        
        response = self.get_response(request)
        return response
