from django.db.models import Q
from .models import Post

class PostFilterService:
    """
    Service class to handle post filtering logic.
    Encapsulates the complex query building for searching and filtering posts.
    """
    
    @staticmethod
    def filter_posts(queryset, params):
        """
        Filter the given queryset based on the parameters provided in the dictionary.
        
        Args:
            queryset: The initial queryset to filter.
            params: A dictionary-like object (e.g., request.GET) containing filter criteria.
            
        Returns:
            The filtered queryset.
        """
        search_query = params.get('q', '')
        item_type = params.get('item_type', '')
        category = params.get('category', '')
        location = params.get('location', '')
        status = params.get('status', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            )
        
        if item_type:
            queryset = queryset.filter(item_type=item_type)
            
        if category:
            queryset = queryset.filter(category=category)
            
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
