from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """A Post Category only a Superuser can create, it contains Posts"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Post(models.Model):
    """A Post created by a Superuser."""
    title = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    # Users who liked this post
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        verbose_name_plural = 'posts'

    def __str__(self):
        return f"{self.title} - {self.text[:50]}..."

    def total_likes(self):
        return self.likes.count()


class Comment(models.Model):
    """A Comment on a Post by any authenticated user."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
