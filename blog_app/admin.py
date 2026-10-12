from django.contrib import admin
from .models import Post, Tag, Comment, UserProfile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'is_published')
    list_filter = ('is_published', 'date', 'tags')
    search_fields = ('title', 'text')
    list_editable = ('is_published',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'date')
    search_fields = ('text', 'author__username', 'post__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')
