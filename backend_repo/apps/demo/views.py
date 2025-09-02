from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Prefetch
from .models import Post, Comment
from .serializers import PostSerializer


class PostPagination(PageNumberPagination):
    """Custom pagination for posts with configurable page size"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostListView(generics.ListAPIView):
    """
    API endpoint for retrieving posts with infinite scrolling support.
    
    Returns posts ordered by timestamp (latest first) with:
    - Post text, timestamp, author username
    - Comment count for each post
    - Up to 3 latest comments per post (with text, timestamp, author username)
    
    Supports pagination for infinite scrolling implementation.
    """
    serializer_class = PostSerializer
    pagination_class = PostPagination
    
    def get_queryset(self):
        """
        Optimized queryset that prefetches related data to minimize database queries.
        Orders posts by timestamp (latest first).
        """
        # Prefetch the latest 3 comments for each post to optimize database queries
        latest_comments_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.select_related('user').order_by('-timestamp')[:3],
            to_attr='latest_comments_cached'
        )
        
        return Post.objects.select_related('user').prefetch_related(
            latest_comments_prefetch,
            'comments'  # For comment count
        ).order_by('-timestamp')


# Answer to follow-up question about random comments:
"""
FOLLOW-UP QUESTION ANSWER:

To fetch 3 random comments instead of latest comments, you would modify the 
get_latest_comments method in PostSerializer:

def get_latest_comments(self, obj):
    '''Get up to 3 random comments for this post'''
    random_comments = obj.comments.select_related('user').order_by('?')[:3]
    return CommentSerializer(random_comments, many=True).data

And update the prefetch in the view's get_queryset method:

random_comments_prefetch = Prefetch(
    'comments',
    queryset=Comment.objects.select_related('user').order_by('?')[:3],
    to_attr='random_comments_cached'
)

Note: Using order_by('?') for randomization can be expensive on large datasets.
For better performance with large comment volumes, consider:
1. Using database-specific random functions
2. Implementing application-level randomization
3. Using a separate random sampling approach
"""