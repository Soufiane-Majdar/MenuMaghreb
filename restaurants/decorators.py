from functools import wraps
from django.core.cache import cache
from django.utils.cache import get_cache_key
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def cache_page_for_restaurant(timeout=300):
    """
    Cache a view for a specific restaurant. The cache key includes the restaurant ID
    to ensure each restaurant has its own cached version.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                # Get restaurant ID from kwargs
                restaurant_id = kwargs.get('restaurant_id') or kwargs.get('pk')
                if not restaurant_id:
                    return view_func(request, *args, **kwargs)

                # Create a cache key based on the full URL and restaurant ID
                cache_key = f'restaurant_view_{restaurant_id}_{request.path}'
                
                # Try to get the cached response
                response = cache.get(cache_key)
                if response is None:
                    response = view_func(request, *args, **kwargs)
                    try:
                        cache.set(cache_key, response, timeout)
                    except Exception as e:
                        logger.warning(f"Failed to set cache: {str(e)}")
                
                return response
            except Exception as e:
                # If there's any caching error, just execute the view normally
                logger.warning(f"Cache error in cache_page_for_restaurant: {str(e)}")
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def cache_menu_page(timeout=3600):
    """
    Cache the menu page for a specific restaurant. This cache has a longer timeout
    since menu content changes less frequently.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                # Get restaurant ID from kwargs
                restaurant_id = kwargs.get('restaurant_id')
                if not restaurant_id:
                    return view_func(request, *args, **kwargs)

                # Create a cache key that includes any query parameters
                cache_key = f'menu_view_{restaurant_id}_{request.path}_{request.GET.urlencode()}'
                
                # Try to get the cached response
                response = cache.get(cache_key)
                if response is None:
                    response = view_func(request, *args, **kwargs)
                    try:
                        cache.set(cache_key, response, timeout)
                    except Exception as e:
                        logger.warning(f"Failed to set cache: {str(e)}")
                
                return response
            except Exception as e:
                # If there's any caching error, just execute the view normally
                logger.warning(f"Cache error in cache_menu_page: {str(e)}")
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
