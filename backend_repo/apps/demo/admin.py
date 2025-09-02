from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['text', 'user', 'timestamp']
    list_filter = ['timestamp', 'user']
    search_fields = ['text', 'user__username']
    ordering = ['-timestamp']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'post', 'user', 'timestamp']
    list_filter = ['timestamp', 'user', 'post']
    search_fields = ['text', 'user__username', 'post__text']
    ordering = ['-timestamp']