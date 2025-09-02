from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Post, Comment
import json


class PostAPITestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        # Create test posts
        self.post1 = Post.objects.create(text='First post', user=self.user1)
        self.post2 = Post.objects.create(text='Second post', user=self.user2)
        
        # Create test comments
        Comment.objects.create(text='Comment 1 on post 1', post=self.post1, user=self.user2)
        Comment.objects.create(text='Comment 2 on post 1', post=self.post1, user=self.user1)
        Comment.objects.create(text='Comment 3 on post 1', post=self.post1, user=self.user2)
        Comment.objects.create(text='Comment 4 on post 1', post=self.post1, user=self.user1)
        
        Comment.objects.create(text='Comment 1 on post 2', post=self.post2, user=self.user1)

    def test_posts_list_endpoint(self):
        """Test that the posts endpoint returns correct data structure"""
        response = self.client.get('/api/posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)

    def test_posts_ordering(self):
        """Test that posts are ordered by timestamp (latest first)"""
        response = self.client.get('/api/posts/')
        data = response.json()
        
        posts = data['results']
        self.assertEqual(len(posts), 2)
        
        # Posts should be ordered by timestamp, latest first
        # Since post2 was created after post1, it should come first
        self.assertEqual(posts[0]['text'], 'Second post')
        self.assertEqual(posts[1]['text'], 'First post')

    def test_post_structure(self):
        """Test that each post has the required fields"""
        response = self.client.get('/api/posts/')
        data = response.json()
        
        post = data['results'][0]
        required_fields = ['id', 'text', 'timestamp', 'author', 'comment_count', 'latest_comments']
        
        for field in required_fields:
            self.assertIn(field, post)
        
        # Test author structure
        self.assertIn('username', post['author'])

    def test_comment_count(self):
        """Test that comment count is accurate"""
        response = self.client.get('/api/posts/')
        data = response.json()
        
        posts = data['results']
        
        # Find post1 (should have 4 comments)
        post1_data = next(p for p in posts if p['text'] == 'First post')
        self.assertEqual(post1_data['comment_count'], 4)
        
        # Find post2 (should have 1 comment)
        post2_data = next(p for p in posts if p['text'] == 'Second post')
        self.assertEqual(post2_data['comment_count'], 1)

    def test_latest_comments_limit(self):
        """Test that only up to 3 latest comments are returned"""
        response = self.client.get('/api/posts/')
        data = response.json()
        
        posts = data['results']
        
        # Find post1 (has 4 comments, should return only 3)
        post1_data = next(p for p in posts if p['text'] == 'First post')
        self.assertEqual(len(post1_data['latest_comments']), 3)
        
        # Find post2 (has 1 comment, should return 1)
        post2_data = next(p for p in posts if p['text'] == 'Second post')
        self.assertEqual(len(post2_data['latest_comments']), 1)

    def test_comment_structure(self):
        """Test that comments have the required fields"""
        response = self.client.get('/api/posts/')
        data = response.json()
        
        posts = data['results']
        post_with_comments = next(p for p in posts if p['latest_comments'])
        comment = post_with_comments['latest_comments'][0]
        
        required_fields = ['id', 'text', 'timestamp', 'author']
        for field in required_fields:
            self.assertIn(field, comment)
        
        # Test author structure
        self.assertIn('username', comment['author'])

    def test_pagination(self):
        """Test pagination functionality"""
        # Test with small page size
        response = self.client.get('/api/posts/?page_size=1')
        data = response.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['count'], 2)
        self.assertIsNotNone(data['next'])
        self.assertIsNone(data['previous'])